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


# ─── 广域库 ──────────────────────────────────────────────


@mcp.tool()
def wechat_search_articles_wide(keyword: str, offset: int = 0,
                                sort_type: Optional[str] = None) -> Dict[str, Any]:
    """搜索公众号作品（广域库，覆盖范围大于优质库）。keyword 必填；
    offset 从 0 开始、每页 +20；sort_type：0=默认，2=最新，4=最热。"""
    return call(lambda: get_client().wechat.search_articles_wide,
                keyword=keyword, offset=offset, sort_type=sort_type)


@mcp.tool()
def wechat_search_users_wide(keyword: str, offset: int = 0) -> Dict[str, Any]:
    """搜索公众号账号（广域库）。keyword 必填；offset 从 0 开始、每页 +20。"""
    return call(lambda: get_client().wechat.search_users_wide,
                keyword=keyword, offset=offset)


@mcp.tool()
def wechat_get_work_wide(work_uuid: str) -> Dict[str, Any]:
    """根据作品 UUID 获取公众号作品，含正文全文（广域库）。"""
    return call(lambda: get_client().wechat.get_work_wide, work_uuid=work_uuid)


@mcp.tool()
def wechat_get_user_works_wide(account: Optional[str] = None,
                               wx_id: Optional[str] = None,
                               biz_info: Optional[str] = None,
                               offset: int = 0,
                               sort_type: Optional[str] = None) -> Dict[str, Any]:
    """获取公众号账号作品列表（广域库）。account（微信号）/ wx_id（原始 ID，如 gh_xxx）/
    biz_info（采集用 ID）三者选其一；offset 从 0 开始、每页 +20；
    sort_type：0=默认，2=最新，4=最热。"""
    return call(lambda: get_client().wechat.get_user_works_wide,
                account=account, wx_id=wx_id, biz_info=biz_info,
                offset=offset, sort_type=sort_type)


@mcp.tool()
def wechat_get_account_wide(account: Optional[str] = None,
                            wx_id: Optional[str] = None,
                            biz_info: Optional[str] = None) -> Dict[str, Any]:
    """获取公众号账号信息（广域库）。account（微信号）/ wx_id（原始 ID，如 gh_xxx）/
    biz_info（账号唯一 ID）三者选其一。"""
    return call(lambda: get_client().wechat.get_account_wide,
                account=account, wx_id=wx_id, biz_info=biz_info)


# ─── 榜单 ────────────────────────────────────────────────


@mcp.tool()
def wechat_get_ten_w_rank(type: str, start_date: str, end_date: str) -> Dict[str, Any]:
    """公众号 10W+ 阅读文章推荐。type 为分类（如 知识百科、科技数码、总排名）；
    start_date/end_date 格式 yyyy-MM-dd（每日 18:30 更新昨日数据）。"""
    return call(lambda: get_client().wechat.get_ten_w_rank,
                type=type, start_date=start_date, end_date=end_date)


@mcp.tool()
def wechat_get_original_rank(type: str, start_date: str,
                             end_date: str) -> Dict[str, Any]:
    """公众号原创爆款文章推荐。type 为分类（如 人文资讯、财富理财、总排名）；
    start_date/end_date 格式 yyyy-MM-dd（每日 18:30 更新昨日数据）。"""
    return call(lambda: get_client().wechat.get_original_rank,
                type=type, start_date=start_date, end_date=end_date)


@mcp.tool()
def wechat_get_strength_rank(rank_type: str, rank_date: str,
                             category: str) -> Dict[str, Any]:
    """公众号综合实力榜。rank_type：day/week/month；rank_date 为榜单日期 yyyy-MM-dd；
    category 为分类（如 人文资讯、时事新闻、总排名）。"""
    return call(lambda: get_client().wechat.get_strength_rank,
                rank_type=rank_type, rank_date=rank_date, category=category)


@mcp.tool()
def wechat_get_reading_growth_rank(rank_date: str) -> Dict[str, Any]:
    """公众号阅读增长榜单。rank_date 为榜单日期 yyyy-MM-dd。"""
    return call(lambda: get_client().wechat.get_reading_growth_rank,
                rank_date=rank_date)


def main() -> None:
    serve(mcp, prog="redfox-wechat-mcp", description="RedFox 公众号数据 MCP server")


if __name__ == "__main__":
    main()
