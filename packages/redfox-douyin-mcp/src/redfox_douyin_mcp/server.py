"""RedFox 抖音数据 MCP Server

将 RedFoxHub（红狐数据平台）的抖音数据 API 暴露为 MCP 工具。

认证：stdio 模式读环境变量 REDFOX_API_KEY；HTTP 模式从请求头
X-API-Key（或 Authorization: Bearer <key>）取 key。
获取地址 https://redfox.hk/settings/api-keys?source=mcp
"""

from typing import Any, Dict, Optional

from redfox_mcp_core import call, create_server, get_client, serve

from redfox_douyin_mcp import __version__

mcp = create_server("redfox-douyin", __version__)


@mcp.tool()
def douyin_search_articles(keyword: str, offset: int = 0,
                           sort_type: Optional[str] = None) -> Dict[str, Any]:
    """搜索抖音作品（优质库）。keyword 必填；offset 分页偏移从 0 开始、每次 +20；
    sort_type 排序方式，如 "default"。返回含 total/hasMore/list。"""
    return call(lambda: get_client().douyin.search_articles,
                keyword=keyword, offset=offset, sort_type=sort_type)


@mcp.tool()
def douyin_search_users(keyword: str, offset: int = 0,
                        sort_type: Optional[str] = None) -> Dict[str, Any]:
    """搜索抖音账号（优质库）。keyword 必填；offset 分页偏移从 0 开始。"""
    return call(lambda: get_client().douyin.search_users,
                keyword=keyword, offset=offset, sort_type=sort_type)


@mcp.tool()
def douyin_get_user(account_id: str) -> Dict[str, Any]:
    """获取抖音账号信息（优质库）。account_id 为抖音账号 ID，
    支持 unique_id、short_id、uid 任一匹配。"""
    return call(lambda: get_client().douyin.get_user, account_id=account_id)


@mcp.tool()
def douyin_get_user_works(account_id: Optional[str] = None,
                          author_url: Optional[str] = None,
                          sec_user_id: Optional[str] = None,
                          offset: int = 0,
                          sort_type: Optional[str] = None) -> Dict[str, Any]:
    """获取抖音账号作品列表（优质库）。account_id（抖音号）/ author_url（主页链接）/
    sec_user_id 至少传一个；offset 每页 +20；sort_type：0=默认，2=最新，4=最热。"""
    return call(lambda: get_client().douyin.get_user_works,
                account_id=account_id, author_url=author_url,
                sec_user_id=sec_user_id, offset=offset, sort_type=sort_type)


@mcp.tool()
def douyin_get_work(work_id: Optional[str] = None,
                    work_url: Optional[str] = None) -> Dict[str, Any]:
    """获取抖音作品详情（优质库）。work_id 与 work_url（作品链接）至少传一个，
    返回互动数据、作者信息等。"""
    return call(lambda: get_client().douyin.get_work, work_id=work_id, work_url=work_url)


@mcp.tool()
def douyin_search_ai_articles(keyword: str, page_num: int = 1, page_size: int = 20,
                              start_time: Optional[str] = None,
                              end_time: Optional[str] = None) -> Dict[str, Any]:
    """搜索抖音 AI 相关作品（优质库）。keyword 必填；
    start_time/end_time 格式如 "2026-06-01 00:00:00"。"""
    return call(lambda: get_client().douyin.search_ai_articles,
                keyword=keyword, page_num=page_num, page_size=page_size,
                start_time=start_time, end_time=end_time)


def main() -> None:
    serve(mcp, prog="redfox-douyin-mcp", description="RedFox 抖音数据 MCP server")


if __name__ == "__main__":
    main()
