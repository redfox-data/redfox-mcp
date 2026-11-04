"""RedFox TikTok 数据 MCP Server

将 RedFoxHub（红狐数据平台）的 TikTok 数据 API 暴露为 MCP 工具。

认证：stdio 模式读环境变量 REDFOX_API_KEY；HTTP 模式从请求头
REDFOX_API_KEY（或 Authorization: Bearer <key>）取 key。
获取地址 https://redfox.hk/settings/api-keys?source=mcp
"""

from typing import Annotated, Any, Dict, Optional
from pydantic import Field

from redfox_mcp_core import call, create_server, get_client, serve

from redfox_tiktok_mcp import __version__

mcp = create_server("redfox-tiktok", __version__)


@mcp.tool()
def tiktok_search_users(keyword: Annotated[str, Field(description="必填，关键词，[必填]，示例: 南浔")], offset: Annotated[str, Field(description="必填，偏移量，[可选]，示例: 0")] = "0", count: Annotated[str, Field(description="必填，数量，[可选]，示例: 20")] = "20",
                        follower_count_filter: Annotated[Optional[int], Field(description="粉丝数筛选：空-不限制/1-0~1K/2-1K~10K/3-10K~100K/4-100K以上，[可选]")] = None,
                        profile_type_filter: Annotated[Optional[int], Field(description="账号类型筛选：空-不限制/1-认证用户，[可选]")] = None,
                        other_pref_filter: Annotated[Optional[int], Field(description="其他偏好：空-不限制/1-按用户名相关性，[可选]")] = None) -> Dict[str, Any]:
    """搜索 TikTok 账号。keyword 必填；offset 偏移量从 0 开始、翻页 +count；
    count 每页数量默认 20；follower_count_filter 粉丝数筛选：1=0~1K，2=1K~10K，
    3=10K~100K，4=100K 以上；profile_type_filter：1=认证用户；
    other_pref_filter：1=按用户名相关性；三个筛选不传则不限制。

接口: POST /story/api/tiktok/ability/searchUser"""
    return call(lambda: get_client().tiktok.search_users,
                keyword=keyword, offset=offset, count=count,
                follower_count_filter=follower_count_filter,
                profile_type_filter=profile_type_filter,
                other_pref_filter=other_pref_filter,
                source="搜索 TikTok 账号-MCP")


@mcp.tool()
def tiktok_search_videos(keyword: Annotated[str, Field(description="关键词，示例：\"NVIDIA\"，[必填]，示例: NVIDIA")], offset: Annotated[str, Field(description="偏移量，示例：\"0\"，[可选]，示例: 0")] = "0", count: Annotated[str, Field(description="数量，示例：\"20\"，[可选]，示例: 20")] = "20",
                         sort_type: Annotated[str, Field(description="排序方式：0-相关度，1-最多点赞，示例：\"0\"，[可选]，示例: 0")] = "0", publish_time: Annotated[str, Field(description="发布时间：0-不限制，1-最近一天，7-最近一周，30-最近一个月，90-最近三个月，180-最近半年，示例：\"0\"，[可选]，示例: 0")] = "0",
                         region: Annotated[str, Field(description="地区，默认为US-美国，可选值参考TikTok地区代码或ISO 3166-1 alpha-2国家代码，示例：\"US\"，[可选]，示例: US")] = "US") -> Dict[str, Any]:
    """TikTok 关键词视频搜索。keyword 必填；
    sort_type：0=相关度，1=最多点赞；
    publish_time：0=不限，1=最近一天，7=最近一周，30=最近一个月，90=最近三个月，180=最近半年；
    region 默认 US（美国），参考 ISO 3166-1 alpha-2 国家代码。

接口: POST /story/api/tiktok/ability/searchVideo"""
    return call(lambda: get_client().tiktok.search_videos,
                keyword=keyword, offset=offset, count=count,
                sort_type=sort_type, publish_time=publish_time, region=region, source="TikTok 关键词视频搜索-MCP")


@mcp.tool()
def tiktok_get_work(aweme_id: Annotated[str, Field(description="作品ID（aweme_id），[必填]，示例: 7350810998023949599")]) -> Dict[str, Any]:
    """获取 TikTok 单个作品数据。aweme_id 为作品 ID（必填）。

接口: POST /story/api/tiktok/ability/awemeDetail"""
    return call(lambda: get_client().tiktok.get_work, aweme_id=aweme_id, source="获取 TikTok 单个作品数据-MCP")


@mcp.tool()
def tiktok_get_user_works(sec_user_id: Annotated[str, Field(description="用户ID（sec_user_id），[必填]，示例: MS4wLjABAAAAv7iSuuXDJGDvJkmH_vz1qkDZYo1apxgzaxdBSeIuPiM")]) -> Dict[str, Any]:
    """获取 TikTok 用户主页作品数据。sec_user_id 为用户 ID（必填）。

接口: POST /story/api/tiktok/ability/userAwemeList"""
    return call(lambda: get_client().tiktok.get_user_works, sec_user_id=sec_user_id, source="获取 TikTok 用户主页作品数据-MCP")


def main() -> None:
    serve(mcp, prog="redfox-tiktok-mcp", description="RedFox TikTok 数据 MCP server")


if __name__ == "__main__":
    main()
