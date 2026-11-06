"""从 redfox-mcp-core 迁入的 OAuth 授权层。协议逻辑复用 fastmcp，状态落后台。

线上 main 的 core 没有这个模块，所以放在本服务里。
模型 A：OAuth token → user_id → 红狐既有 API Key。

启用条件：仅当 REDFOX_MCP_AUTH_MODE=oauth|multi 时由 serve() 挂载；默认 apikey
模式下本模块完全不参与，现有 API Key 鉴权行为逐字节不变。

动态注册客户端、同意页事务、授权码、访问/刷新令牌全部经
HttpOAuthStateStore 落账号侧后台表（函数计算多实例 + 内存随时清空，不能存内存）。
接口约定见 oauth_store.py。

测试期身份为 **stub**：/authorize 直接复用 fastmcp 内置的“自动发码”，并绑定一个
固定测试用户；API Key 从环境变量解析。
生产接入时只需替换两处、协议逻辑零改动：
    - _stub_user_id()  →  从真实红狐登录 / SSO 会话取 user_id；
    - 取 Key 已接账号侧 GET /story/web/apiKey/queryKey?uuid={ticket}。
"""

from __future__ import annotations

import json
import os
import secrets
import time
from typing import Any, Dict, Optional, Protocol
from urllib.parse import parse_qsl, quote, urlencode, urlsplit, urlunsplit
from urllib.request import Request as UrlRequest
from urllib.request import urlopen

from mcp.server.auth.provider import (
    AccessToken,
    AuthorizationCode,
    AuthorizationParams,
    AuthorizeError,
    RefreshToken,
    TokenError,
    construct_redirect_uri,
)
from mcp.server.auth.settings import ClientRegistrationOptions, RevocationOptions
from mcp.shared.auth import OAuthClientInformationFull, OAuthToken
from pydantic import AnyHttpUrl, AnyUrl
from starlette.requests import Request
from starlette.responses import PlainTextResponse, RedirectResponse, Response

from fastmcp.server.auth.providers.in_memory import InMemoryOAuthProvider

from redfox_data_mcp.oauth_store import HttpOAuthStateStore, build_state_store


# ---------------------------------------------------------------------------
# 模型 A：user_id -> 红狐 API Key 解析器
# ---------------------------------------------------------------------------
class KeyResolver(Protocol):
    """把一个红狐 user_id 解析成可用于调用数据 API 的 API Key。"""

    def resolve(self, user_id: str) -> Optional[str]:  # pragma: no cover - 协议
        ...


class EnvKeyResolver:
    """测试用解析器：从环境变量取 Key（生产替换为账号侧接口实现）。

    读取优先级：
      1. REDFOX_OAUTH_USER_KEY_MAP：可选，JSON {"<user_id>": "<api_key>"}，
         支持配置多个测试用户各自的 Key；
      2. REDFOX_OAUTH_TEST_API_KEY：单一测试 Key；
      3. REDFOX_API_KEY：回退到通用 Key（与 stdio/header 模式同一个环境变量）。
    """

    def __init__(self) -> None:
        self._map: Dict[str, str] = self._load_map()

    @staticmethod
    def _load_map() -> Dict[str, str]:
        raw = os.getenv("REDFOX_OAUTH_USER_KEY_MAP", "").strip()
        if not raw:
            return {}
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return {}
        if not isinstance(data, dict):
            return {}
        return {str(k): str(v) for k, v in data.items() if v}

    def resolve(self, user_id: str) -> Optional[str]:
        key = self._map.get(user_id)
        if key:
            return key
        return (
            os.getenv("REDFOX_OAUTH_TEST_API_KEY")
            or os.getenv("REDFOX_API_KEY")
            or None
        )


_QUERY_KEY_URL = "https://redfox.hk/story/web/apiKey/queryKey"
_QUERY_KEY_OK = {0, 200, 2000}


def _extract_api_key(data: Any) -> Optional[str]:
    """从 queryKey 的 data 里取出 API Key。"""
    if isinstance(data, str) and data.strip():
        return data.strip()
    if isinstance(data, dict):
        for field in ("apiKey", "api_key", "key"):
            value = data.get(field)
            if isinstance(value, str) and value.strip():
                return value.strip()
        return None
    if isinstance(data, list):
        enabled = [
            item
            for item in data
            if not isinstance(item, dict) or item.get("status") in (None, 1, "1")
        ]
        for item in enabled or data:
            found = _extract_api_key(item)
            if found:
                return found
    return None


class TicketKeyResolver:
    """用同意回调带来的 ticket 调账号侧查 Key。

    GET https://redfox.hk/story/web/apiKey/queryKey?uuid={ticket}
    ticket 存在 access token 的 claims.redfox_user_id 里。
    账号侧没有返回 Key 时，回退到环境变量，本地自检仍可用固定测试 Key。
    """

    def __init__(self) -> None:
        self._fallback = EnvKeyResolver()

    def resolve(self, user_id: str) -> Optional[str]:
        key = _query_key_by_ticket(user_id)
        if key:
            return key
        return self._fallback.resolve(user_id)


def _query_key_by_ticket(ticket: str) -> Optional[str]:
    ticket = (ticket or "").strip()
    if not ticket:
        return None
    url = f"{_QUERY_KEY_URL}?uuid={quote(ticket, safe='')}"
    request = UrlRequest(url, method="GET", headers={"Accept": "application/json"})
    try:
        with urlopen(request, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except Exception:
        return None
    if not isinstance(payload, dict) or payload.get("code") not in _QUERY_KEY_OK:
        return None
    return _extract_api_key(payload.get("data"))


# 全局解析器：runtime.get_client() 通过 resolve_api_key() 使用；可被覆盖为生产实现。
_key_resolver: KeyResolver = TicketKeyResolver()


def set_key_resolver(resolver: KeyResolver) -> None:
    """替换全局 KeyResolver（生产接入账号侧实现时调用）。"""
    global _key_resolver
    _key_resolver = resolver


def resolve_api_key(user_id: str) -> Optional[str]:
    """按 user_id 解析 API Key；解析不到返回 None。"""
    if not user_id:
        return None
    return _key_resolver.resolve(user_id)


# ---------------------------------------------------------------------------
# stub 登录：测试期返回固定用户
# ---------------------------------------------------------------------------
def _stub_user_id() -> str:
    """测试期身份：固定用户。生产环境替换为从登录会话 / SSO 回调取真实 user_id。"""
    return os.getenv("REDFOX_OAUTH_STUB_USER_ID", "redfox-test-user")


_AUTH_CODE_TTL_SECONDS = 5 * 60
_ACCESS_TOKEN_TTL_SECONDS = 60 * 60


class _PendingConsent:
    """一次 /authorize 暂存的原始参数，等同意页带着 ticket 回来再发 code。"""

    def __init__(
        self, client: OAuthClientInformationFull, params: AuthorizationParams
    ) -> None:
        scopes = list(params.scopes or [])
        if client.scope:
            allowed = set(client.scope.split())
            scopes = [item for item in scopes if item in allowed]
        self.client_id = client.client_id or ""
        self.redirect_uri = str(params.redirect_uri)
        self.redirect_uri_provided_explicitly = params.redirect_uri_provided_explicitly
        self.state = params.state
        self.scopes = scopes
        self.code_challenge = params.code_challenge
        self.resource = params.resource

    def to_payload(self) -> Dict[str, Any]:
        return {
            "client_id": self.client_id,
            "redirect_uri": self.redirect_uri,
            "redirect_uri_provided_explicitly": self.redirect_uri_provided_explicitly,
            "state": self.state,
            "scopes": self.scopes,
            "code_challenge": self.code_challenge,
            "resource": self.resource,
        }

    @classmethod
    def from_payload(cls, payload: Dict[str, Any]) -> "_PendingConsent":
        pending = cls.__new__(cls)
        pending.client_id = str(payload.get("client_id") or "")
        pending.redirect_uri = str(payload.get("redirect_uri") or "")
        pending.redirect_uri_provided_explicitly = bool(
            payload.get("redirect_uri_provided_explicitly")
        )
        pending.state = payload.get("state")
        pending.scopes = [str(item) for item in payload.get("scopes") or []]
        pending.code_challenge = str(payload.get("code_challenge") or "")
        pending.resource = payload.get("resource")
        return pending


# 豆包办公授权页来源，便于红狐侧统计。
CONSENT_SOURCE = "doubaobangong"


def _consent_page_url() -> str:
    return os.getenv("REDFOX_OAUTH_CONSENT_URL", "").strip()


def _with_txn(consent_url: str, txn_id: str) -> str:
    """同意页地址补上 txn_id，并带上 source=doubaobangong。"""
    parts = urlsplit(consent_url)
    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    query.setdefault("source", CONSENT_SOURCE)
    query["txn_id"] = txn_id
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))


# 豆包客户端的回调地址由运行环境临时生成，DCR 与 /authorize 两次提交的不一定一致，
# SDK 默认的精确匹配会拒掉。按豆包接入文档 7.1.3 的临时加白建议，放行该前缀
# （限定 HTTPS、Host 与完整路径前缀，不做通配）。
DOUBAO_CALLBACK_PREFIX = "https://api.doubao-dev.com/api/oauth/v1/callback/personal/cb_ah_"


class _DoubaoCallbackClient(OAuthClientInformationFull):
    """在 SDK 精确匹配之上，额外放行豆包回调地址前缀。"""

    def validate_redirect_uri(self, redirect_uri: AnyUrl | None) -> AnyUrl:
        if redirect_uri is not None and str(redirect_uri).startswith(
            DOUBAO_CALLBACK_PREFIX
        ):
            return redirect_uri
        return super().validate_redirect_uri(redirect_uri)


class RedFoxOAuthProvider(InMemoryOAuthProvider):
    """fastmcp 内置 InMemoryOAuthProvider 之上，把全部状态换成后台远端存储。

    覆盖：register_client/get_client（client）、authorize（txn/code）、
    授权码 load/exchange（code，take 一次有效）、访问/刷新令牌签发与撤销
    （access/refresh）。协议行为与父类一致，只改状态落点。

    设置 REDFOX_OAUTH_CONSENT_URL 后，/authorize 不再直接发码，而是 302 到红狐同意页；
    同意页带回 ticket 后由 /oauth/resume 发 code。未设置时保持 stub 自动发码，自检脚本不受影响。
    """

    def __init__(
        self,
        *args: Any,
        store: Optional[HttpOAuthStateStore] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self._store = store if store is not None else build_state_store()

    # ---- 客户端注册（DCR） ----
    async def register_client(self, client_info: OAuthClientInformationFull) -> None:
        if (
            client_info.scope is not None
            and self.client_registration_options is not None
            and self.client_registration_options.valid_scopes is not None
        ):
            requested_scopes = set(client_info.scope.split())
            valid_scopes = set(self.client_registration_options.valid_scopes)
            if requested_scopes - valid_scopes:
                raise ValueError(
                    f"Requested scopes are not valid: {', '.join(requested_scopes - valid_scopes)}"
                )
        if client_info.client_id is None:
            raise ValueError("client_id is required for client registration")
        await self._store.put(
            "client", client_info.client_id, client_info.model_dump(mode="json")
        )

    async def get_client(self, client_id: str) -> Optional[OAuthClientInformationFull]:
        payload = await self._store.get("client", client_id)
        if payload is None:
            return None
        return _DoubaoCallbackClient.model_validate(payload)

    # ---- 授权（/authorize） ----
    async def authorize(
        self, client: OAuthClientInformationFull, params: AuthorizationParams
    ) -> str:
        consent_url = _consent_page_url()
        if not consent_url:
            # 未接同意页：stub 自动发码，并绑定固定测试用户。
            scopes = self._allowed_scopes(client, params)
            code = await self._issue_code(client, params, scopes, _stub_user_id())
            return construct_redirect_uri(
                str(params.redirect_uri), code=code, state=params.state
            )

        txn_id = secrets.token_urlsafe(24)
        pending = _PendingConsent(client, params)
        await self._store.put("txn", txn_id, pending.to_payload())
        return _with_txn(consent_url, txn_id)

    async def take_pending(self, txn_id: str) -> Optional[Dict[str, Any]]:
        """取走并删除一条同意页事务；不存在或已过期返回 None。"""
        return await self._store.take("txn", txn_id)

    async def finish_consent(self, pending: _PendingConsent, user_id: str) -> str:
        """验过 ticket 后发授权码，并 302 回 OAuth 客户端（豆包回调）。"""
        code = f"test_auth_code_{secrets.token_hex(16)}"
        auth_code = AuthorizationCode(
            code=code,
            client_id=pending.client_id,
            redirect_uri=pending.redirect_uri,
            redirect_uri_provided_explicitly=pending.redirect_uri_provided_explicitly,
            scopes=pending.scopes,
            expires_at=time.time() + _AUTH_CODE_TTL_SECONDS,
            code_challenge=pending.code_challenge,
            resource=pending.resource,
        )
        await self._store.put(
            "code",
            code,
            {"auth_code": auth_code.model_dump(mode="json"), "user_id": user_id},
        )
        return construct_redirect_uri(
            str(pending.redirect_uri), code=code, state=pending.state
        )

    def deny_consent(self, pending: _PendingConsent) -> str:
        return construct_redirect_uri(
            str(pending.redirect_uri),
            error="access_denied",
            state=pending.state,
        )

    # ---- 授权码换令牌（/token，一次有效） ----
    async def load_authorization_code(
        self, client: OAuthClientInformationFull, authorization_code: str
    ) -> Optional[AuthorizationCode]:
        payload = await self._store.get("code", authorization_code)
        if payload is None:
            return None
        auth_code = AuthorizationCode.model_validate(payload.get("auth_code"))
        if auth_code.client_id != client.client_id:
            return None
        if auth_code.expires_at < time.time():
            await self._store.delete("code", authorization_code)
            return None
        return auth_code

    async def exchange_authorization_code(
        self, client: OAuthClientInformationFull, authorization_code: AuthorizationCode
    ) -> OAuthToken:
        payload = await self._store.take("code", authorization_code.code)
        if payload is None:
            raise TokenError(
                "invalid_grant", "Authorization code not found or already used."
            )
        user_id = payload.get("user_id")
        return await self._issue_tokens(client, authorization_code.scopes, user_id)

    # ---- 刷新令牌（/token refresh，轮换） ----
    async def load_refresh_token(
        self, client: OAuthClientInformationFull, refresh_token: str
    ) -> Optional[RefreshToken]:
        payload = await self._store.get("refresh", refresh_token)
        if payload is None:
            return None
        token_obj = RefreshToken.model_validate(payload)
        if token_obj.client_id != client.client_id:
            return None
        if token_obj.expires_at is not None and token_obj.expires_at < time.time():
            await self.revoke_token(token_obj)
            return None
        return token_obj

    async def exchange_refresh_token(
        self,
        client: OAuthClientInformationFull,
        refresh_token: RefreshToken,
        scopes: list[str],
    ) -> OAuthToken:
        original_scopes = set(refresh_token.scopes)
        requested_scopes = set(scopes)
        if not requested_scopes.issubset(original_scopes):
            raise TokenError(
                "invalid_scope",
                "Requested scopes exceed those authorized by the refresh token.",
            )
        # take 保证轮换原子性：两个实例并发刷新时只有一个成功
        payload = await self._store.take("refresh", refresh_token.token)
        if payload is None:
            raise TokenError("invalid_grant", "refresh token does not exist")
        old_access = payload.get("access_token")
        if old_access:
            await self._store.delete("access", old_access)
        return await self._issue_tokens(client, scopes, refresh_token.subject)

    # ---- 访问令牌校验（Bearer） ----
    async def load_access_token(self, token: str) -> Optional[AccessToken]:  # type: ignore[override]
        payload = await self._store.get("access", token)
        if payload is None:
            return None
        token_obj = AccessToken.model_validate(payload)
        if token_obj.expires_at is not None and token_obj.expires_at < time.time():
            await self._store.delete("access", token)
            return None
        return token_obj

    # ---- 撤销（/revoke，连同配对令牌） ----
    async def revoke_token(self, token: AccessToken | RefreshToken) -> None:
        if isinstance(token, AccessToken):
            payload = await self._store.take("access", token.token)
            if payload and payload.get("refresh_token"):
                await self._store.delete("refresh", payload["refresh_token"])
        elif isinstance(token, RefreshToken):
            payload = await self._store.take("refresh", token.token)
            if payload and payload.get("access_token"):
                await self._store.delete("access", payload["access_token"])

    # ---- 内部工具 ----
    def _allowed_scopes(
        self, client: OAuthClientInformationFull, params: AuthorizationParams
    ) -> list[str]:
        scopes = list(params.scopes or [])
        if client.scope:
            allowed = set(client.scope.split())
            scopes = [item for item in scopes if item in allowed]
        return scopes

    async def _issue_code(
        self,
        client: OAuthClientInformationFull,
        params: AuthorizationParams,
        scopes: list[str],
        user_id: str,
    ) -> str:
        if client.client_id is None:
            raise AuthorizeError(
                error="invalid_client", error_description="Client ID is required"
            )
        code = f"test_auth_code_{secrets.token_hex(16)}"
        auth_code = AuthorizationCode(
            code=code,
            client_id=client.client_id,
            redirect_uri=params.redirect_uri,
            redirect_uri_provided_explicitly=params.redirect_uri_provided_explicitly,
            scopes=scopes,
            expires_at=time.time() + _AUTH_CODE_TTL_SECONDS,
            code_challenge=params.code_challenge,
            resource=params.resource,
        )
        await self._store.put(
            "code",
            code,
            {"auth_code": auth_code.model_dump(mode="json"), "user_id": user_id},
        )
        return code

    async def _issue_tokens(
        self,
        client: OAuthClientInformationFull,
        scopes: list[str],
        user_id: Optional[str],
    ) -> OAuthToken:
        if client.client_id is None:
            raise TokenError("invalid_client", "Client ID is required")
        access_token_value = f"test_access_token_{secrets.token_hex(32)}"
        refresh_token_value = f"test_refresh_token_{secrets.token_hex(32)}"
        access_expires_at = int(time.time() + _ACCESS_TOKEN_TTL_SECONDS)
        access = AccessToken(
            token=access_token_value,
            client_id=client.client_id,
            scopes=scopes,
            expires_at=access_expires_at,
        )
        refresh = RefreshToken(
            token=refresh_token_value,
            client_id=client.client_id,
            scopes=scopes,
            expires_at=None,
        )
        if user_id:
            # 资源属主（红狐 user_id）同时写进 subject 与 claims。
            # 注意：fastmcp 的 get_access_token() 把 SDK AccessToken 转成 fastmcp
            # AccessToken 时是逐字段重建，**只保留 claims、丢弃 subject**（见
            # dependencies.py），因此 claims 才是工具调用侧可靠读取 user_id 的通道；
            # subject 一并写入以供令牌内省等直接读取存储对象的场景。
            access.subject = user_id
            access.claims = {"redfox_user_id": user_id}
            refresh.subject = user_id
        # 配对信息一并存进 payload，撤销时删掉成对令牌
        await self._store.put(
            "access",
            access_token_value,
            {**access.model_dump(mode="json"), "refresh_token": refresh_token_value},
        )
        await self._store.put(
            "refresh",
            refresh_token_value,
            {**refresh.model_dump(mode="json"), "access_token": access_token_value},
        )
        return OAuthToken(
            access_token=access_token_value,
            token_type="Bearer",
            expires_in=_ACCESS_TOKEN_TTL_SECONDS,
            refresh_token=refresh_token_value,
            scope=" ".join(scopes),
        )


# ---------------------------------------------------------------------------
# 组装：按 AUTH_MODE 构造 fastmcp auth provider
# ---------------------------------------------------------------------------
def build_oauth_provider(
    base_url: str,
    resource_base_url: Optional[str] = None,
    issuer_url: Optional[str] = None,
    store: Optional[HttpOAuthStateStore] = None,
) -> RedFoxOAuthProvider:
    """构造 OAuth provider。DCR 必须显式 enabled=True，否则 /register 不挂载。

    注意：InMemoryOAuthProvider.__init__ 不接受 issuer_url（仅基类 OAuthProvider 接受），
    故构造后再设 provider.issuer_url；get_routes() 在 run 时才读取，等效于构造期传入。
    根路径部署（测试用隧道）时 issuer_url 默认等于 base_url，无需单独设置。
    """
    provider = RedFoxOAuthProvider(
        base_url=base_url,
        resource_base_url=resource_base_url,
        client_registration_options=ClientRegistrationOptions(enabled=True),
        revocation_options=RevocationOptions(enabled=True),
        store=store,
    )
    if issuer_url:
        provider.issuer_url = (
            AnyHttpUrl(issuer_url) if isinstance(issuer_url, str) else issuer_url
        )
    return provider


def build_auth(
    mode: str,
    base_url: str,
    resource_base_url: Optional[str] = None,
    issuer_url: Optional[str] = None,
) -> Optional[Any]:
    """按 REDFOX_MCP_AUTH_MODE 返回 fastmcp auth provider。

    - "oauth"：仅 OAuth/DCR（豆包工作走这条）；
    - "multi"：目标为 OAuth + 老 API Key 并存，M1 再补 API Key verifier，
      当前与 "oauth" 等价（测试实例独立部署，现有 API Key 客户端在生产不受影响）；
    - 其它：返回 None，调用方保持今天的 RequireApiKeyMiddleware 行为。
    """
    if mode not in {"oauth", "multi"}:
        return None
    return build_oauth_provider(base_url, resource_base_url, issuer_url)


async def handle_oauth_resume(request: Request, provider: RedFoxOAuthProvider) -> Response:
    """同意页回调：ticket 在调试期直接当作红狐 user uuid。

    生产应改为调用账号侧验票接口，用一次性 ticket 换 user_id，不要信任浏览器传来的 uuid。
    事务取走即删，过期事务由后台判断并返回 None。
    """
    txn_id = request.query_params.get("txn_id", "")
    payload = await provider.take_pending(txn_id)
    if payload is None:
        return PlainTextResponse("授权事务不存在或已过期", status_code=400)
    pending = _PendingConsent.from_payload(payload)
    if request.query_params.get("consent") == "deny":
        return RedirectResponse(provider.deny_consent(pending), status_code=302)

    ticket = request.query_params.get("ticket", "").strip()
    if not ticket:
        return PlainTextResponse("缺少 ticket", status_code=400)

    return RedirectResponse(await provider.finish_consent(pending, ticket), status_code=302)
