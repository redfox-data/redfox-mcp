"""RedFox Instagram 数据 MCP Server

将 RedFoxHub（红狐数据平台）的 Instagram 数据 API 暴露为 MCP 工具。

认证：stdio 模式读环境变量 REDFOX_API_KEY；HTTP 模式从请求头
REDFOX_API_KEY（或 Authorization: Bearer <key>）取 key。
获取地址 https://redfox.hk/settings/api-keys?source=mcp
"""

from typing import Annotated, Any, Dict, Optional
from pydantic import Field

from redfox_mcp_core import call, create_server, get_client, serve

from redfox_instagram_mcp import __version__

mcp = create_server("redfox-instagram", __version__)


@mcp.tool()
def instagram_search(keyword: Annotated[str, Field(description="关键词，必填 例：新闻联播、南浔，[必填]，示例: 南浔")],
                     pagination_token: Annotated[Optional[str], Field(description="分页token，非必填 从上一次响应获取，用于翻页，[可选]")] = None) -> Dict[str, Any]:
    """Instagram 关键词搜索。keyword 必填；pagination_token 用于翻页。

接口: POST /story/api/ins/search"""
    return call(lambda: get_client().instagram.search,
                keyword=keyword, pagination_token=pagination_token, source="Instagram 关键词搜索-MCP")


@mcp.tool()
def instagram_get_post(code_or_url: Annotated[str, Field(description="帖子Shortcode或完整URL（必填） 例：DRhvwVLAHAG 或 https://www.instagram.com/reel/DPi5REKCali/，[必填]，示例: DPi5REKCali")]) -> Dict[str, Any]:
    """获取 Instagram 单个帖子详情。code_or_url 为帖子 code 或完整链接（必填）。

接口: POST /story/api/ins/postDetail"""
    return call(lambda: get_client().instagram.get_post, code_or_url=code_or_url, source="获取 Instagram 单个帖子详情-MCP")


@mcp.tool()
def instagram_get_comments(code_or_url: Annotated[str, Field(description="帖子Shortcode或完整URL（必填） 例：DRhvwVLAHAG 或 https://www.instagram.com/reel/DPi5REKCali/，[必填]，示例: DPi5REKCali")], sort_by: Annotated[str, Field(description="排序方式（必填），\"recent\"（最新）或\"popular\"（热门），默认recent，[可选]，示例: recent")] = "recent",
                           pagination_token: Annotated[Optional[str], Field(description="分页token（pagination_token），非必填 从上一次响应获取，用于翻页，[可选]")] = None) -> Dict[str, Any]:
    """获取 Instagram 帖子评论。code_or_url 必填；sort_by：recent=最新/top=最热；
    pagination_token 用于翻页。

接口: POST /story/api/ins/postComment"""
    return call(lambda: get_client().instagram.get_comments,
                code_or_url=code_or_url, sort_by=sort_by,
                pagination_token=pagination_token, source="获取 Instagram 帖子评论-MCP")


@mcp.tool()
def instagram_get_user(username: Annotated[Optional[str], Field(description="username 和 userId 至少传一个，若同时传入则优先使用 userId（二选一），[可选]，示例: nbaplaytalk")] = None,
                       user_id: Annotated[Optional[str], Field(description="用户ID（如 18527），传入后会忽略 username （二选一），[可选]")] = None) -> Dict[str, Any]:
    """获取 Instagram 用户信息。username 与 user_id 至少传一个，user_id 优先。

接口: POST /story/api/ins/userInfo"""
    return call(lambda: get_client().instagram.get_user,
                username=username, user_id=user_id, source="获取 Instagram 用户信息-MCP")


def main() -> None:
    serve(mcp, prog="redfox-instagram-mcp", description="RedFox Instagram MCP server")


if __name__ == "__main__":
    main()
