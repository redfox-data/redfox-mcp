"""RedFox Instagram 数据 MCP Server

将 RedFoxHub（红狐数据平台）的 Instagram 数据 API 暴露为 MCP 工具。

认证：stdio 模式读环境变量 REDFOX_API_KEY；HTTP 模式从请求头
X-API-Key（或 Authorization: Bearer <key>）取 key。
获取地址 https://redfox.hk/settings/api-keys?source=mcp
"""

from typing import Any, Dict, Optional

from redfox_mcp_core import call, create_server, get_client, serve

from redfox_instagram_mcp import __version__

mcp = create_server("redfox-instagram", __version__)


@mcp.tool()
def instagram_search(keyword: str,
                     pagination_token: Optional[str] = None) -> Dict[str, Any]:
    """Instagram 关键词搜索。keyword 必填；pagination_token 用于翻页。"""
    return call(lambda: get_client().instagram.search,
                keyword=keyword, pagination_token=pagination_token)


@mcp.tool()
def instagram_get_post(code_or_url: str) -> Dict[str, Any]:
    """获取 Instagram 单个帖子详情。code_or_url 为帖子 code 或完整链接（必填）。"""
    return call(lambda: get_client().instagram.get_post, code_or_url=code_or_url)


@mcp.tool()
def instagram_get_comments(code_or_url: str, sort_by: str = "recent",
                           pagination_token: Optional[str] = None) -> Dict[str, Any]:
    """获取 Instagram 帖子评论。code_or_url 必填；sort_by：recent=最新/top=最热；
    pagination_token 用于翻页。"""
    return call(lambda: get_client().instagram.get_comments,
                code_or_url=code_or_url, sort_by=sort_by,
                pagination_token=pagination_token)


@mcp.tool()
def instagram_get_user(username: Optional[str] = None,
                       user_id: Optional[str] = None) -> Dict[str, Any]:
    """获取 Instagram 用户信息。username 与 user_id 至少传一个，user_id 优先。"""
    return call(lambda: get_client().instagram.get_user,
                username=username, user_id=user_id)


def main() -> None:
    serve(mcp, prog="redfox-instagram-mcp", description="RedFox Instagram MCP server")


if __name__ == "__main__":
    main()
