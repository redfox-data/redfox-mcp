"""RedFox 公众号数据 MCP Server

将 RedFoxHub（红狐数据平台）的公众号数据 API 暴露为 MCP 工具。

认证：stdio 模式读环境变量 REDFOX_API_KEY；HTTP 模式从请求头
X-API-Key（或 Authorization: Bearer <key>）取 key。
获取地址 https://redfox.hk/settings/api-keys?source=mcp
"""

from typing import Any, Dict, Optional

from redfox_mcp_core import call, create_server, get_client, serve

from redfox_wechat_mcp import __version__

mcp = create_server("redfox-wechat", __version__)


@mcp.tool()
def wechat_search_articles(keyword: str, offset: int = 0,
                           sort_type: Optional[str] = None) -> Dict[str, Any]:
    """搜索公众号文章（优质库）。keyword 必填；offset 从 0 开始、每页 +20。"""
    return call(lambda: get_client().wechat.search_articles,
                keyword=keyword, offset=offset, sort_type=sort_type)


@mcp.tool()
def wechat_search_users(keyword: str, offset: int = 0,
                        sort_type: Optional[str] = None) -> Dict[str, Any]:
    """搜索公众号账号（优质库）。keyword 必填；sort_type：_0=默认，_2=最新，_4=最热。"""
    return call(lambda: get_client().wechat.search_users,
                keyword=keyword, offset=offset, sort_type=sort_type)


@mcp.tool()
def wechat_get_account(account: str,
                       account_name: Optional[str] = None) -> Dict[str, Any]:
    """获取公众号账号信息（优质库）。account 为公众号微信号（必填），
    account_name 为公众号名称（可选）。"""
    return call(lambda: get_client().wechat.get_account,
                account=account, account_name=account_name)


@mcp.tool()
def wechat_get_user_works(account: str, account_name: Optional[str] = None,
                          offset: int = 0, sort_type: Optional[str] = None,
                          publish_time_start: Optional[str] = None,
                          publish_time_end: Optional[str] = None) -> Dict[str, Any]:
    """获取公众号文章列表（优质库）。account 为公众号微信号（必填）；
    sort_type：_0=默认，_2=最新，_4=最热；publish_time_start/end 格式如 "2026-07-01"。"""
    return call(lambda: get_client().wechat.get_user_works,
                account=account, account_name=account_name, offset=offset,
                sort_type=sort_type, publish_time_start=publish_time_start,
                publish_time_end=publish_time_end)


@mcp.tool()
def wechat_get_work(work_uuid: str) -> Dict[str, Any]:
    """根据作品 UUID 获取公众号文章元数据（优质库）。"""
    return call(lambda: get_client().wechat.get_work, work_uuid=work_uuid)


@mcp.tool()
def wechat_get_article_detail(url: str) -> Dict[str, Any]:
    """根据文章链接获取公众号文章详情，支持全文内容（优质库）。
    url 形如 https://mp.weixin.qq.com/s/..."""
    return call(lambda: get_client().wechat.get_article_detail, url=url)


@mcp.tool()
def wechat_search_ai_articles(keyword: str, page_num: int = 1, page_size: int = 20,
                              start_time: Optional[str] = None,
                              end_time: Optional[str] = None) -> Dict[str, Any]:
    """搜索公众号 AI 创作相关文章（优质库）。keyword 必填；
    start_time/end_time 格式如 "2026-06-01 00:00:00"。"""
    return call(lambda: get_client().wechat.search_ai_articles,
                keyword=keyword, page_num=page_num, page_size=page_size,
                start_time=start_time, end_time=end_time)


def main() -> None:
    serve(mcp, prog="redfox-wechat-mcp", description="RedFox 公众号数据 MCP server")


if __name__ == "__main__":
    main()
