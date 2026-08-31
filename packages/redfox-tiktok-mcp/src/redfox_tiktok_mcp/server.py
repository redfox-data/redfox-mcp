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


@mcp.tool()
def tiktok_search_videos(keyword: str, offset: str = "0", count: str = "20",
                         sort_type: str = "0", publish_time: str = "0",
                         region: str = "US") -> Dict[str, Any]:
    """TikTok 关键词视频搜索。keyword 必填；
    sort_type：0=相关度，1=最多点赞；
    publish_time：0=不限，1=最近一天，7=最近一周，30=最近一个月，90=最近三个月，180=最近半年；
    region 默认 US（美国），参考 ISO 3166-1 alpha-2 国家代码。"""
    return call(lambda: get_client().tiktok.search_videos,
                keyword=keyword, offset=offset, count=count,
                sort_type=sort_type, publish_time=publish_time, region=region)


@mcp.tool()
def tiktok_get_work(aweme_id: str) -> Dict[str, Any]:
    """获取 TikTok 单个作品数据。aweme_id 为作品 ID（必填）。"""
    return call(lambda: get_client().tiktok.get_work, aweme_id=aweme_id)


@mcp.tool()
def tiktok_get_user_works(sec_user_id: str) -> Dict[str, Any]:
    """获取 TikTok 用户主页作品数据。sec_user_id 为用户 ID（必填）。"""
    return call(lambda: get_client().tiktok.get_user_works, sec_user_id=sec_user_id)


def main() -> None:
    serve(mcp, prog="redfox-tiktok-mcp", description="RedFox TikTok 数据 MCP server")


if __name__ == "__main__":
    main()
