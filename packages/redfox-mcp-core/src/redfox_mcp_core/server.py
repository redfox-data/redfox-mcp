"""RedFox MCP 共享 server 工厂与启动入口"""

import argparse
import os

from fastmcp import FastMCP
from starlette.middleware import Middleware
from starlette.responses import JSONResponse

from redfox_mcp_core.http_auth import RequireApiKeyMiddleware
from redfox_mcp_core.runtime import set_transport


def create_server(name: str, version: str) -> FastMCP:
    """创建一个带 /health 路由的 FastMCP 实例，各平台 server 共用"""
    mcp = FastMCP(name)

    @mcp.custom_route("/health", methods=["GET"])
    async def _health(_request):
        return JSONResponse({"status": "ok", "server": name, "version": version})

    return mcp


def serve(mcp: FastMCP, prog: str, description: str) -> None:
    """启动 MCP server：默认 stdio（本地客户端），--transport http 切换为远程多租户模式。

    HTTP 鉴权模式由 REDFOX_MCP_AUTH_MODE 决定：
      - apikey（默认）：挂 RequireApiKeyMiddleware，行为与既往逐字节一致；
      - oauth / multi：改由 fastmcp 内置 OAuth 授权层接管（见 redfox_mcp_core.oauth），
        不再挂 RequireApiKeyMiddleware，以免把 OAuth 端点与 Bearer 请求一并 401。
    stdio 分支不受影响（fastmcp 对 stdio 走 skip_auth）。
    """
    parser = argparse.ArgumentParser(prog=prog, description=description)
    parser.add_argument("--transport", choices=["stdio", "http"],
                        default=os.getenv("REDFOX_MCP_TRANSPORT", "stdio"))
    parser.add_argument("--host", default=os.getenv("REDFOX_MCP_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.getenv("REDFOX_MCP_PORT", "8000")))
    parser.add_argument("--path", default=os.getenv("REDFOX_MCP_PATH", "/mcp"))
    args = parser.parse_args()
    if args.transport == "http":
        set_transport("http")
        auth_mode = os.getenv("REDFOX_MCP_AUTH_MODE", "apikey").strip().lower()
        middleware = [Middleware(RequireApiKeyMiddleware)]
        if auth_mode in {"oauth", "multi"}:
            from redfox_mcp_core.oauth import build_auth

            # base_url 必须是客户端（豆包）可见的公网地址；本地默认仅作兜底。
            base_url = (
                os.getenv("REDFOX_MCP_OAUTH_BASE_URL")
                or f"http://{args.host}:{args.port}"
            )
            provider = build_auth(
                auth_mode,
                base_url,
                resource_base_url=os.getenv("REDFOX_MCP_OAUTH_RESOURCE_BASE_URL") or None,
                issuer_url=os.getenv("REDFOX_MCP_OAUTH_ISSUER_URL") or None,
            )
            mcp.auth = provider
            # 同意页跳回：验 ticket → 发 code → 302 回客户端回调。调试期 ticket=用户 uuid。
            from starlette.requests import Request

            from redfox_mcp_core.oauth import handle_oauth_resume

            @mcp.custom_route("/oauth/resume", methods=["GET"])
            async def _oauth_resume(request: Request):
                return await handle_oauth_resume(request, provider)

            # OAuth 模式由 fastmcp 的 RequireAuthMiddleware 接管，撤掉 API Key 中间件。
            middleware = []
        mcp.run(
            transport="streamable-http",
            host=args.host,
            port=args.port,
            path=args.path,
            middleware=middleware,
        )
    else:
        mcp.run()
