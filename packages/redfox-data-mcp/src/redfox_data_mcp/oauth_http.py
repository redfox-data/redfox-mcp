"""在本服务上挂载 OAuth，而不是依赖 main 分支 core 的 serve()。

REDFOX_MCP_AUTH_MODE=oauth 或 multi 时启用。OAuth 端点不要求 API Key。
/mcp 同时接受 OAuth access token 和原来的 REDFOX_API_KEY 请求头。
"""

from __future__ import annotations

import argparse
import hmac
import json
import os

from starlette.requests import Request
from starlette.types import ASGIApp, Receive, Scope, Send

from redfox_mcp_core.runtime import set_transport

from redfox_data_mcp.oauth import build_auth, handle_oauth_resume

# 公开客户端换令牌不带 client_secret。SDK 的元数据只公布带密钥的两种方式，
# 豆包审核要求 token_endpoint_auth_methods_supported 包含 none。
_PUBLIC_CLIENT_AUTH_METHOD = "none"


class AcceptApiKeyMiddleware:
    """请求头里的 API Key 与 REDFOX_API_KEY 一致时，不再强制 OAuth Bearer。

    Key 不匹配（或服务端未配置 REDFOX_API_KEY）一律 401，不能让任意 x-api-key 头绕过鉴权。
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app
        self._expected_key = os.getenv("REDFOX_API_KEY", "").strip()

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope.get("type") == "http" and _api_key_value(scope) and hasattr(self.app, "app"):
            if not self._expected_key or not hmac.compare_digest(
                _api_key_value(scope), self._expected_key
            ):
                await _send_unauthorized(send)
                return
            await self.app.app(scope, receive, send)
            return
        await self.app(scope, receive, send)


def _api_key_value(scope: Scope) -> str:
    headers = {
        key.decode("latin1").lower(): value.decode("latin1")
        for key, value in scope.get("headers") or []
    }
    return headers.get("redfox_api_key") or headers.get("x-api-key") or ""


async def _send_unauthorized(send: Send) -> None:
    await send(
        {
            "type": "http.response.start",
            "status": 401,
            "headers": [
                (b"content-length", b"0"),
                (b"www-authenticate", b'Bearer error="invalid_token"'),
            ],
        }
    )
    await send({"type": "http.response.body", "body": b""})


def _wrap_mcp_route(app) -> None:
    for route in getattr(app, "routes", []):
        if getattr(route, "path", None) == "/mcp":
            route.app = AcceptApiKeyMiddleware(route.app)
            return


def _advertise_public_client(metadata):
    """在授权服务器元数据末尾补上 none，不改变已有方式的顺序。"""
    methods = list(getattr(metadata, "token_endpoint_auth_methods_supported", None) or [])
    if _PUBLIC_CLIENT_AUTH_METHOD not in methods:
        methods.append(_PUBLIC_CLIENT_AUTH_METHOD)
        metadata.token_endpoint_auth_methods_supported = methods
    return metadata


def install_public_client_metadata() -> None:
    """让 /.well-known/oauth-authorization-server 公布公开客户端。

    SDK 在 build_metadata 里写死了 client_secret_post 和 client_secret_basic，
    这里补上 none。三种方式都已实现：显式声明按声明值注册（见
    _RegisterBodyMiddleware），未声明的归一为 none。
    """
    import mcp.server.auth.routes as routes

    current = routes.build_metadata
    if getattr(current, "_redfox_public_client", False):
        return
    original = current

    def build_metadata(*args, **kwargs):
        return _advertise_public_client(original(*args, **kwargs))

    build_metadata._redfox_public_client = True  # type: ignore[attr-defined]
    routes.build_metadata = build_metadata


class _PublicClientMetadataMiddleware:
    """改写授权服务器元数据响应，保证对外公布 none。"""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope.get("type") != "http":
            await self.app(scope, receive, send)
            return
        start: dict | None = None
        body = bytearray()

        async def buffer_send(message: dict) -> None:
            nonlocal start
            if message["type"] == "http.response.start":
                start = message
                return
            if message["type"] != "http.response.body":
                await send(message)
                return
            body.extend(message.get("body") or b"")
            if message.get("more_body"):
                return
            payload = _inject_public_client(bytes(body))
            headers = [
                (key, value)
                for key, value in (start or {}).get("headers") or []
                if key.lower() != b"content-length"
            ]
            headers.append((b"content-length", str(len(payload)).encode()))
            await send({**(start or {"type": "http.response.start", "status": 200}), "headers": headers})
            await send({"type": "http.response.body", "body": payload})

        await self.app(scope, receive, buffer_send)


def _inject_public_client(body: bytes) -> bytes:
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        return body
    if not isinstance(payload, dict):
        return body
    methods = list(payload.get("token_endpoint_auth_methods_supported") or [])
    if _PUBLIC_CLIENT_AUTH_METHOD not in methods:
        methods.append(_PUBLIC_CLIENT_AUTH_METHOD)
        payload["token_endpoint_auth_methods_supported"] = methods
        return json.dumps(payload, separators=(",", ":")).encode()
    return body


class _RegisterBodyMiddleware:
    """DCR 请求体未声明 token_endpoint_auth_method 时补写成 none。

    SDK 对未声明的方式默认 client_secret_post 并颁发 secret，而豆包自定义链接
    客户端换令牌不带 secret；显式声明 client_secret_basic / client_secret_post
    的请求原样放行，按机密客户端注册（豆包连接器预检要求注册响应原样回显）。
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope.get("type") != "http" or scope.get("method") != "POST":
            await self.app(scope, receive, send)
            return
        chunks = bytearray()
        while True:
            message = await receive()
            if message["type"] != "http.request":
                break
            chunks.extend(message.get("body") or b"")
            if not message.get("more_body"):
                break
        body = _normalize_register_body(bytes(chunks))
        if len(body) != len(chunks):
            headers = [
                (key, value)
                for key, value in scope.get("headers") or []
                if key.lower() != b"content-length"
            ]
            headers.append((b"content-length", str(len(body)).encode()))
            scope = {**scope, "headers": headers}
        sent = False

        async def replay() -> dict:
            nonlocal sent
            if sent:
                return {"type": "http.disconnect"}
            sent = True
            return {"type": "http.request", "body": body, "more_body": False}

        await self.app(scope, replay, send)


def _normalize_register_body(body: bytes) -> bytes:
    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        return body
    if not isinstance(payload, dict):
        return body
    if payload.get("token_endpoint_auth_method") is not None:
        return body
    payload["token_endpoint_auth_method"] = _PUBLIC_CLIENT_AUTH_METHOD
    return json.dumps(payload, separators=(",", ":")).encode()


def _wrap_authorization_metadata(app) -> None:
    for route in getattr(app, "routes", []):
        if getattr(route, "path", None) == "/.well-known/oauth-authorization-server":
            route.app = _PublicClientMetadataMiddleware(route.app)
            return


def _wrap_register_route(app) -> None:
    for route in getattr(app, "routes", []):
        if getattr(route, "path", None) == "/register":
            route.app = _RegisterBodyMiddleware(route.app)
            return


def build_app(mcp):
    configure(mcp)
    app = mcp.http_app(path="/mcp", stateless_http=False, transport="streamable-http")
    _wrap_mcp_route(app)
    _wrap_authorization_metadata(app)
    _wrap_register_route(app)
    return app


def configure(mcp) -> None:
    install_public_client_metadata()
    mode = os.getenv("REDFOX_MCP_AUTH_MODE", "apikey").strip().lower()
    base_url = os.getenv("REDFOX_MCP_OAUTH_BASE_URL") or "https://mcp.redfox.hk"
    provider = build_auth(
        mode,
        base_url,
        resource_base_url=os.getenv("REDFOX_MCP_OAUTH_RESOURCE_BASE_URL") or None,
        issuer_url=os.getenv("REDFOX_MCP_OAUTH_ISSUER_URL") or None,
    )
    if provider is None:
        raise RuntimeError("OAuth 未启用")
    mcp.auth = provider

    @mcp.custom_route("/oauth/resume", methods=["GET"])
    async def _oauth_resume(request: Request):
        return await handle_oauth_resume(request, provider)


def serve(mcp) -> None:
    parser = argparse.ArgumentParser(prog="redfox-data-mcp", description="RedFox 数据 MCP")
    parser.add_argument("--transport", choices=["stdio", "http"], default=os.getenv("REDFOX_MCP_TRANSPORT", "stdio"))
    parser.add_argument("--host", default=os.getenv("REDFOX_MCP_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.getenv("REDFOX_MCP_PORT", "8000")))
    parser.add_argument("--path", default=os.getenv("REDFOX_MCP_PATH", "/mcp"))
    args = parser.parse_args()
    if args.transport != "http":
        from redfox_mcp_core import serve as core_serve

        core_serve(mcp, prog="redfox-data-mcp", description="RedFox 数据 MCP：find / describe / call / result")
        return
    set_transport("http")
    app = build_app(mcp)
    import uvicorn

    uvicorn.run(app, host=args.host, port=args.port)
