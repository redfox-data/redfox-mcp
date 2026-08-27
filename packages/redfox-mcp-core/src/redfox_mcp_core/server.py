"""RedFox MCP 共享 server 工厂与启动入口"""

import argparse
import os

from fastmcp import FastMCP
from starlette.responses import JSONResponse

from redfox_mcp_core.runtime import set_transport


def create_server(name: str, version: str) -> FastMCP:
    """创建一个带 /health 路由的 FastMCP 实例，各平台 server 共用"""
    mcp = FastMCP(name)

    @mcp.custom_route("/health", methods=["GET"])
    async def _health(_request):
        return JSONResponse({"status": "ok", "server": name, "version": version})

    return mcp


def serve(mcp: FastMCP, prog: str, description: str) -> None:
    """启动 MCP server：默认 stdio（本地客户端），--transport http 切换为远程多租户模式"""
    parser = argparse.ArgumentParser(prog=prog, description=description)
    parser.add_argument("--transport", choices=["stdio", "http"],
                        default=os.getenv("REDFOX_MCP_TRANSPORT", "stdio"))
    parser.add_argument("--host", default=os.getenv("REDFOX_MCP_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.getenv("REDFOX_MCP_PORT", "8000")))
    parser.add_argument("--path", default=os.getenv("REDFOX_MCP_PATH", "/mcp"))
    args = parser.parse_args()
    if args.transport == "http":
        set_transport("http")
        mcp.run(transport="streamable-http", host=args.host, port=args.port, path=args.path)
    else:
        mcp.run()
