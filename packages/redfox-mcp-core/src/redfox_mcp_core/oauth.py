"""RedFox MCP OAuth 授权层（模型 A：OAuth token → user_id → 红狐既有 API Key）

启用条件：仅当 REDFOX_MCP_AUTH_MODE=oauth|multi 时由 serve() 挂载；默认 apikey
模式下本模块完全不参与，现有 API Key 鉴权行为逐字节不变。

测试期身份为 **stub**：/authorize 直接复用 fastmcp 内置的“自动发码”，并绑定一个
固定测试用户；API Key 从环境变量解析。DCR / PKCE / token 签发 / refresh / revoke
全部复用 fastmcp 的 InMemoryOAuthProvider，本模块只补两件事：
    1) authorize 时把 user_id 绑定到授权码；
    2) 换 token 时把 user_id 写进 AccessToken.subject（RFC 7662 的资源属主）。

生产接入时只需替换两处、协议逻辑零改动：
    - _stub_user_id()  →  从真实红狐登录 / SSO 会话取 user_id；
    - EnvKeyResolver   →  调用账号侧 get_api_key_by_user(user_id) 的实现。
"""

from __future__ import annotations

import json
import os
from typing import Any, Dict, Optional, Protocol
from urllib.parse import parse_qs, urlparse

from mcp.server.auth.provider import AuthorizationCode, AuthorizationParams
from mcp.server.auth.settings import ClientRegistrationOptions, RevocationOptions
from mcp.shared.auth import OAuthClientInformationFull, OAuthToken
from pydantic import AnyHttpUrl

from fastmcp.server.auth.providers.in_memory import InMemoryOAuthProvider

# 测试期授权码/访问令牌内存态；生产需子类化落 DB/Redis（见模块 docstring）。


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


# 全局解析器：runtime.get_client() 通过 resolve_api_key() 使用；可被覆盖为生产实现。
_key_resolver: KeyResolver = EnvKeyResolver()


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


def _extract_code(redirect_uri: str) -> Optional[str]:
    """从 authorize() 返回的重定向 URI 里解析出 code，用于绑定 user_id。"""
    try:
        query = parse_qs(urlparse(redirect_uri).query)
    except Exception:
        return None
    values = query.get("code")
    return values[0] if values else None


class RedFoxOAuthProvider(InMemoryOAuthProvider):
    """在 fastmcp 内置 InMemoryOAuthProvider 之上补“身份绑定”。

    继承：register_client(DCR) / authorize+PKCE / token 签发 / refresh / revoke。
    新增：授权码 → user_id 绑定，并把 user_id 写入 AccessToken.subject。
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self._code_to_user: Dict[str, str] = {}

    async def authorize(
        self, client: OAuthClientInformationFull, params: AuthorizationParams
    ) -> str:
        # 测试期：直接复用父类“自动发码”（无登录页）；生产在此接入红狐登录/SSO。
        redirect = await super().authorize(client, params)
        user_id = _stub_user_id()
        code = _extract_code(redirect)
        if code:
            self._code_to_user[code] = user_id
        return redirect

    async def exchange_authorization_code(
        self, client: OAuthClientInformationFull, authorization_code: AuthorizationCode
    ) -> OAuthToken:
        user_id = self._code_to_user.pop(authorization_code.code, None)
        token = await super().exchange_authorization_code(client, authorization_code)
        if user_id:
            stored = self.access_tokens.get(token.access_token)
            if stored is not None:
                # 资源属主（红狐 user_id）同时写进 subject 与 claims。
                # 注意：fastmcp 的 get_access_token() 把 SDK AccessToken 转成 fastmcp
                # AccessToken 时是逐字段重建，**只保留 claims、丢弃 subject**（见
                # dependencies.py），因此 claims 才是工具调用侧可靠读取 user_id 的通道；
                # subject 一并写入以供令牌内省等直接读取存储对象的场景。
                patch = {"subject": user_id, "claims": {"redfox_user_id": user_id}}
                try:
                    stored.subject = user_id
                    stored.claims = {"redfox_user_id": user_id}
                except Exception:  # 模型若禁止赋值则整体替换
                    self.access_tokens[token.access_token] = stored.model_copy(
                        update=patch
                    )
        return token


# ---------------------------------------------------------------------------
# 组装：按 AUTH_MODE 构造 fastmcp auth provider
# ---------------------------------------------------------------------------
def build_oauth_provider(
    base_url: str,
    resource_base_url: Optional[str] = None,
    issuer_url: Optional[str] = None,
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
