"""RedFox TikTok 数据 MCP Server

将 RedFoxHub（红狐数据平台）的 TikTok 数据 API 暴露为 MCP 工具。

认证：stdio 模式读环境变量 REDFOX_API_KEY；HTTP 模式从请求头
X-API-Key（或 Authorization: Bearer <key>）取 key。
获取地址 https://redfox.hk/settings/api-keys?source=mcp
"""

from typing import Any, Dict, Optional

from redfox_mcp_core import call, create_server, get_client, serve

from redfox_tiktok_mcp import __version__

mcp = create_server("redfox-tiktok", __version__)


@mcp.tool()
def tiktok_search_users(keyword: str, cursor: int = 0,
                        rid: Optional[str] = None) -> Dict[str, Any]:
    """搜索 TikTok 账号。keyword 必填；cursor 翻页游标第一页为 0、每页 +10；
    rid 为上一页数据返回的 rid，翻页时传入。返回含 cursor/hasMore/userList。"""
    return call(lambda: get_client().tiktok.search_users,
                keyword=keyword, cursor=cursor, rid=rid)


def main() -> None:
    serve(mcp, prog="redfox-tiktok-mcp", description="RedFox TikTok 数据 MCP server")


if __name__ == "__main__":
    main()
