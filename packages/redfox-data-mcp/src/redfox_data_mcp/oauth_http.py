"""在本服务上挂载 OAuth，而不是依赖 main 分支 core 的 serve()。

REDFOX_MCP_AUTH_MODE=oauth 或 multi 时启用。OAuth 端点不要求 API Key。
/mcp 同时接受 OAuth access token 和原来的 REDFOX_API_KEY 请求头。
"""

from __future__ import annotations

import argparse
import os

from starlette.requests import Request
from starlette.types import ASGIApp, Receive, Scope, Send

from redfox_mcp_core.runtime import set_transport

from redfox_data_mcp.oauth import build_auth, handle_oauth_resume


class AcceptApiKeyMiddleware:
    """请求头里已有 API Key 时，不再强制 OAuth Bearer。"""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope.get("type") == "http" and _api_key_header(scope) and hasattr(self.app, "app"):
            await self.app.app(scope, receive, send)
            return
        await self.app(scope, receive, send)


def _api_key_header(scope: Scope) -> bool:
    headers = {
        key.decode("latin1").lower(): value.decode("latin1")
        for key, value in scope.get("headers") or []
    }
    return bool(headers.get("redfox_api_key") or headers.get("x-api-key"))


def _wrap_mcp_route(app) -> None:
    for route in getattr(app, "routes", []):
        if getattr(route, "path", None) == "/mcp":
            route.app = AcceptApiKeyMiddleware(route.app)
            return


def build_app(mcp):
    configure(mcp)
    app = mcp.http_app(path="/mcp", stateless_http=False, transport="streamable-http")
    _wrap_mcp_route(app)
    return app


def configure(mcp) -> None:
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
