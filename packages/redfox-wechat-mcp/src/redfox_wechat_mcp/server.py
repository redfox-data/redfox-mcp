"""RedFox 公众号数据 MCP Server

将 RedFoxHub（红狐数据平台）的公众号数据 API 暴露为 MCP 工具。

认证：stdio 模式读环境变量 REDFOX_API_KEY；HTTP 模式从请求头
REDFOX_API_KEY（或 Authorization: Bearer <key>）取 key。
获取地址 https://redfox.hk/settings/api-keys?source=mcp
"""

from typing import Annotated, Any, Dict, Optional
from pydantic import Field

from redfox_mcp_core import call, create_server, get_client, serve

from redfox_wechat_mcp import __version__

mcp = create_server("redfox-wechat", __version__)


@mcp.tool()
def wechat_search_articles(keyword: Annotated[str, Field(description="搜索关键词，[必填]，示例: 人工智能")], offset: Annotated[int, Field(description="offset:偏移量，从0开始，每页+20，[可选]，示例: 0")] = 0,
                           sort_type: Annotated[Optional[str], Field(description="排序方式 _0: 默认（相关性排序） _2: 最新（按发布时间倒序） _4: 最热（按阅读数倒序），[可选]，示例: _0")] = None) -> Dict[str, Any]:
    """搜索公众号文章（优质库）。keyword 必填；offset 从 0 开始、每页 +20。

接口: POST /story/api/gzhData/searchArticle"""
    return call(lambda: get_client().wechat.search_articles,
                keyword=keyword, offset=offset, sort_type=sort_type, source="搜索公众号文章-MCP")


@mcp.tool()
def wechat_search_users(keyword: Annotated[str, Field(description="搜索关键词，[必填]，示例: 人工智能")], offset: Annotated[int, Field(description="offset:偏移量，从0开始，每页+20，[可选]，示例: 0")] = 0,
                        sort_type: Annotated[Optional[str], Field(description="排序方式 _0: 默认（相关性排序） _2: 最新（按发布时间倒序） _4: 最热（按阅读数倒序），[可选]，示例: _0")] = None) -> Dict[str, Any]:
    """搜索公众号账号（优质库）。keyword 必填；sort_type：_0=默认，_2=最新，_4=最热。

接口: POST /story/api/gzhData/searchUser"""
    return call(lambda: get_client().wechat.search_users,
                keyword=keyword, offset=offset, sort_type=sort_type, source="搜索公众号账号（优质库）-MCP")


@mcp.tool()
def wechat_get_account(account: Annotated[str, Field(description="公众号微信号，[必填]，示例: rmrbwx")],
                       account_name: Annotated[Optional[str], Field(description="公众号名称，[可选]，示例: 科研云")] = None) -> Dict[str, Any]:
    """获取公众号账号信息（优质库）。account 为公众号微信号（必填），
    account_name 为公众号名称（可选）。

接口: POST /story/api/gzhData/queryUser"""
    return call(lambda: get_client().wechat.get_account,
                account=account, account_name=account_name, source="获取公众号账号信息（优质库）-MCP")


@mcp.tool()
def wechat_get_user_works(account: Annotated[str, Field(description="公众号微信号，[必填]，示例: rmrbwx")], account_name: Annotated[Optional[str], Field(description="公众号名称，[可选]，示例: 科研云")] = None,
                          offset: Annotated[int, Field(description="offset:偏移量，从0开始，每页+20，[可选]，示例: 0")] = 0, sort_type: Annotated[Optional[str], Field(description="排序方式 _0: 默认（相关性排序） _2: 最新（按发布时间倒序） _4: 最热（按阅读数倒序），[可选]，示例: _0")] = None,
                          publish_time_start: Annotated[Optional[str], Field(description="发布时间起始（最早2026-04-01，不传则默认2026-04-01），[可选]，示例: 2026-04-01")] = None,
                          publish_time_end: Annotated[Optional[str], Field(description="发布时间结束（不传则默认当前时间），[可选]，示例: 2026-05-01")] = None) -> Dict[str, Any]:
    """获取公众号文章列表（优质库）。account 为公众号微信号（必填）；
    sort_type：_0=默认，_2=最新，_4=最热；publish_time_start/end 格式如 "2026-07-01"。

接口: POST /story/api/gzhData/queryWorkList"""
    return call(lambda: get_client().wechat.get_user_works,
                account=account, account_name=account_name, offset=offset,
                sort_type=sort_type, publish_time_start=publish_time_start,
                publish_time_end=publish_time_end, source="获取公众号文章列表-MCP")


@mcp.tool()
def wechat_get_work(work_uuid: Annotated[str, Field(description="作品uuid，[必填]，示例: 7018B165C5D5BF9BE0B9D3158EBE47EA")]) -> Dict[str, Any]:
    """根据作品 UUID 获取公众号文章元数据（优质库）。

接口: POST /story/api/gzhData/queryWork"""
    return call(lambda: get_client().wechat.get_work, work_uuid=work_uuid, source="根据作品 UUID 获取公众号文章元数据-MCP")


@mcp.tool()
def wechat_get_article_detail(url: str) -> Dict[str, Any]:
    """根据文章链接获取公众号文章详情，支持全文内容（优质库）。
    url 形如 https://mp.weixin.qq.com/s/..."""
    return call(lambda: get_client().wechat.get_article_detail, url=url, source="根据文章链接获取公众号文章详情-MCP")


@mcp.tool()
def wechat_search_ai_articles(keyword: Annotated[str, Field(description="搜索关键词，[必填]，示例: 人工智能")], page_num: Annotated[int, Field(description="页码，[可选]，示例: 1")] = 1, page_size: Annotated[int, Field(description="每页条数，[可选]，示例: 20")] = 20,
                              start_time: Annotated[Optional[str], Field(description="start时间，[可选]，示例: 2026-06-01 00:00:00")] = None,
                              end_time: Annotated[Optional[str], Field(description="结束时间，[可选]，示例: 2026-06-01 23:59:59")] = None) -> Dict[str, Any]:
    """搜索公众号 AI 创作相关文章（优质库）。keyword 必填；
    start_time/end_time 格式如 "2026-06-01 00:00:00"。

接口: POST /story/api/parseWork/queryAiMsgs"""
    return call(lambda: get_client().wechat.search_ai_articles,
                keyword=keyword, page_num=page_num, page_size=page_size,
                start_time=start_time, end_time=end_time, source="搜索公众号 AI 创作相关文章-MCP")


# ─── 广域库 ──────────────────────────────────────────────


@mcp.tool()
def wechat_search_articles_wide(keyword: Annotated[str, Field(description="搜索关键词，[必填]，示例: 人工智能")], offset: Annotated[int, Field(description="偏移量，从0开始，每页+20，[可选]，示例: 0")] = 0,
                                sort_type: Annotated[Optional[str], Field(description="排序方式，0: 默认，2: 最新，4: 最热，[可选]，示例: 0")] = None) -> Dict[str, Any]:
    """搜索公众号作品（广域库，覆盖范围大于优质库）。keyword 必填；
    offset 从 0 开始、每页 +20；sort_type：0=默认，2=最新，4=最热。

接口: POST /story/api/gzh/data/searchArticle"""
    return call(lambda: get_client().wechat.search_articles_wide,
                keyword=keyword, offset=offset, sort_type=sort_type, source="搜索公众号作品-MCP")


@mcp.tool()
def wechat_search_users_wide(keyword: Annotated[str, Field(description="搜索关键词，[必填]，示例: 十点读书")], offset: Annotated[int, Field(description="偏移量，从0开始，每页+20，[可选]，示例: 0")] = 0) -> Dict[str, Any]:
    """搜索公众号账号（广域库）。keyword 必填；offset 从 0 开始、每页 +20。

接口: POST /story/api/gzh/data/searchUser"""
    return call(lambda: get_client().wechat.search_users_wide,
                keyword=keyword, offset=offset, source="搜索公众号账号（广域库）-MCP")


@mcp.tool()
def wechat_get_work_wide(work_uuid: Annotated[str, Field(description="作品ID，[必填]，示例: 361A2B123A064DDA8D842E892D3ABF33")]) -> Dict[str, Any]:
    """根据作品 UUID 获取公众号作品，含正文全文（广域库）。

接口: POST /story/api/gzh/data/workDetail"""
    return call(lambda: get_client().wechat.get_work_wide, work_uuid=work_uuid, source="根据作品 UUID 获取公众号作品-MCP")


@mcp.tool()
def wechat_get_user_works_wide(account: Annotated[Optional[str], Field(description="公众号微信号，非必填，与 wxId、bizInfo 三者选其一，[可选]，示例: duhaoshu")] = None,
                               wx_id: Annotated[Optional[str], Field(description="公众号原始ID，非必填，与 account、bizInfo 三者选其一，[可选]，示例: gh_5c7e8b7f586b")] = None,
                               biz_info: Annotated[Optional[str], Field(description="账号采集用ID，非必填，与 account、wxId 三者选其一，[可选]，示例: MjM5MDMyMzg2MA==")] = None,
                               offset: Annotated[int, Field(description="偏移量，从0开始，每页+20，[可选]，示例: 0")] = 0,
                               sort_type: Annotated[Optional[str], Field(description="排序方式，0: 默认，2: 最新，4: 最热，[可选]，示例: 2")] = None) -> Dict[str, Any]:
    """获取公众号账号作品列表（广域库）。account（微信号）/ wx_id（原始 ID，如 gh_xxx）/
    biz_info（采集用 ID）三者选其一；offset 从 0 开始、每页 +20；
    sort_type：0=默认，2=最新，4=最热。

接口: POST /story/api/gzh/data/queryWorkList"""
    return call(lambda: get_client().wechat.get_user_works_wide,
                account=account, wx_id=wx_id, biz_info=biz_info,
                offset=offset, sort_type=sort_type, source="获取公众号账号作品列表-MCP")


@mcp.tool()
def wechat_get_account_wide(account: Annotated[Optional[str], Field(description="公众号微信号，非必填，与 wxId、bizInfo 三者选其一，[可选]，示例: duhaoshu")] = None,
                            wx_id: Annotated[Optional[str], Field(description="公众号原始ID，非必填，与 account、bizInfo 三者选其一，[可选]，示例: gh_5c7e8b7f586b")] = None,
                            biz_info: Annotated[Optional[str], Field(description="账号唯一ID，非必填，与 account、wxId 三者选其一，[可选]，示例: MjM5MDMyMzg2MA==")] = None) -> Dict[str, Any]:
    """获取公众号账号信息（广域库）。account（微信号）/ wx_id（原始 ID，如 gh_xxx）/
    biz_info（账号唯一 ID）三者选其一。

接口: POST /story/api/gzh/data/accountInfo"""
    return call(lambda: get_client().wechat.get_account_wide,
                account=account, wx_id=wx_id, biz_info=biz_info, source="获取公众号账号信息（广域库）-MCP")


# ─── 榜单 ────────────────────────────────────────────────


@mcp.tool()
def wechat_get_ten_w_rank(type: Annotated[str, Field(description="分类：人文资讯 知识百科 健康养生 时尚潮流 乐活生活 旅游出行 搞笑幽默 情感心理 体育娱乐 美容美体 文摘精选 财富理财 科技数码 创投商业 汽车交通 房产楼市 职场发展 教育考试 学术研究 企业品牌 总排名，[必填]，示例: 知识百科")], start_date: Annotated[str, Field(description="开始日期，格式：yyyy-MM-dd 每日18:30更新昨日数据 查询区间跨度≤60天，[必填]，示例: 2026-08-23")], end_date: Annotated[str, Field(description="结束日期，格式：yyyy-MM-dd 每日18:30更新昨日数据，[必填]，示例: 2026-08-24")]) -> Dict[str, Any]:
    """公众号 10W+ 阅读文章推荐。type 为分类（如 知识百科、科技数码、总排名）；
    start_date/end_date 格式 yyyy-MM-dd（每日 18:30 更新昨日数据）。

接口: POST /story/api/cozeSkill/getTenWReadingRank"""
    return call(lambda: get_client().wechat.get_ten_w_rank,
                type=type, start_date=start_date, end_date=end_date, source="公众号 10W+ 阅读文章推荐-MCP")


@mcp.tool()
def wechat_get_original_rank(type: Annotated[str, Field(description="分类：人文资讯 知识百科 健康养生 时尚潮流 乐活生活 旅游出行 搞笑幽默 情感心理 体育娱乐 美容美体 文摘精选 财富理财 科技数码 创投商业 汽车交通 房产楼市 职场发展 教育考试 学术研究 企业品牌 总排名，[必填]，示例: 知识百科")], start_date: Annotated[str, Field(description="开始日期，格式：yyyy-MM-dd 每日18:30更新昨日数据，[必填]，示例: 2026-08-23")],
                             end_date: Annotated[str, Field(description="结束日期，格式：yyyy-MM-dd 每日18:30更新昨日数据，[必填]，示例: 2026-08-24")]) -> Dict[str, Any]:
    """公众号原创爆款文章推荐。type 为分类（如 人文资讯、财富理财、总排名）；
    start_date/end_date 格式 yyyy-MM-dd（每日 18:30 更新昨日数据）。

接口: POST /story/api/cozeSkill/getOriginalRank"""
    return call(lambda: get_client().wechat.get_original_rank,
                type=type, start_date=start_date, end_date=end_date, source="公众号原创爆款文章推荐-MCP")


@mcp.tool()
def wechat_get_strength_rank(rank_type: Annotated[str, Field(description="day/week/month，[必填]，示例: day")], rank_date: Annotated[str, Field(description="榜单日期，格式：yyyy-MM-dd 仅支持日榜近7天，周榜近3周，月榜近3月 当日期类型选择days时， 输入所需日的起始时间 (每天14点更新昨日数据) 当日期类型选择weeks 时，输入所需周的周一时 间(每周一更新上周数 据)当日期类型选择 months时，输入所需月的 一号时间(每月一号更新 上月数据)，[必填]，示例: 2026-08-25")],
                             category: Annotated[str, Field(description="人文资讯,知识百科,健康养生,时尚潮流,美食餐饮,乐活生活,旅游出行,搞笑幽默,情感心理,体育娱乐,美容美体,文摘精选,民生资讯,财富理财,科技数码,创投商业,汽车交通,房产楼市,职场发展,教育考试,学术研究,企业品牌,时事新闻,总排名，[必填]，示例: 人文资讯")]) -> Dict[str, Any]:
    """公众号综合实力榜。rank_type：day/week/month；rank_date 为榜单日期 yyyy-MM-dd；
    category 为分类（如 人文资讯、时事新闻、总排名）。

接口: GET /story/api/cozeSkill/getGzhCozeSkillDataIndex"""
    return call(lambda: get_client().wechat.get_strength_rank,
                rank_type=rank_type, rank_date=rank_date, category=category, source="公众号综合实力榜-MCP")


@mcp.tool()
def wechat_get_reading_growth_rank(rank_date: Annotated[str, Field(description="榜单日期，格式：yyyy-MM-dd，[必填]，示例: 2026-08-25")]) -> Dict[str, Any]:
    """公众号阅读增长榜单。rank_date 为榜单日期 yyyy-MM-dd。

接口: GET /story/api/cozeSkill/getGzhCozeSkillDataRaise"""
    return call(lambda: get_client().wechat.get_reading_growth_rank,
                rank_date=rank_date, source="公众号阅读增长榜单-MCP")


def main() -> None:
    serve(mcp, prog="redfox-wechat-mcp", description="RedFox 公众号数据 MCP server")


if __name__ == "__main__":
    main()
