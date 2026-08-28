"""RedFox 抖音数据 MCP Server

将 RedFoxHub（红狐数据平台）的抖音数据 API 暴露为 MCP 工具。

认证：stdio 模式读环境变量 REDFOX_API_KEY；HTTP 模式从请求头
X-API-Key（或 Authorization: Bearer <key>）取 key。
获取地址 https://redfox.hk/settings/api-keys?source=mcp
"""

from typing import Any, Dict, Optional

from redfox_mcp_core import call, create_server, get_client, run_task, serve

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


# ─── 广域库 ──────────────────────────────────────────────


@mcp.tool()
def douyin_search_works_wide(keyword: str, start_date: Optional[str] = None,
                             end_date: Optional[str] = None,
                             page_num: int = 1, page_size: int = 10) -> Dict[str, Any]:
    """搜索抖音作品（广域库，覆盖范围大于优质库）。keyword 必填（匹配作品正文）；
    start_date/end_date 格式 yyyy-MM-dd；page_num 从 1 开始，page_size 最大 50。"""
    return call(lambda: get_client().douyin.search_works_wide,
                keyword=keyword, start_date=start_date, end_date=end_date,
                page_num=page_num, page_size=page_size)


@mcp.tool()
def douyin_search_accounts_wide(keyword: str, page_num: int = 1,
                                page_size: int = 10) -> Dict[str, Any]:
    """搜索抖音账号（广域库）。keyword 必填（匹配账号名）；
    page_num 从 1 开始，page_size 最大 50。"""
    return call(lambda: get_client().douyin.search_accounts_wide,
                keyword=keyword, page_num=page_num, page_size=page_size)


@mcp.tool()
def douyin_get_work_wide(video_id: str) -> Dict[str, Any]:
    """获取抖音作品详情（广域库）。video_id 为作品 ID（对应 aweme_id，必填）。"""
    return call(lambda: get_client().douyin.get_work_wide, video_id=video_id)


@mcp.tool()
def douyin_get_user_works_wide(user_id: Optional[str] = None,
                               unique_name: Optional[str] = None,
                               short_id: Optional[str] = None,
                               page_num: int = 1, page_size: int = 10,
                               start_date: Optional[str] = None,
                               end_date: Optional[str] = None) -> Dict[str, Any]:
    """获取抖音账号作品列表（广域库）。user_id（uid）/ unique_name（抖音号）/
    short_id 三选一必填；page_num 从 1 开始，page_size 最大 50；
    start_date/end_date 格式 yyyy-MM-dd。"""
    return call(lambda: get_client().douyin.get_user_works_wide,
                user_id=user_id, unique_name=unique_name, short_id=short_id,
                page_num=page_num, page_size=page_size,
                start_date=start_date, end_date=end_date)


# ─── 榜单 ────────────────────────────────────────────────


@mcp.tool()
def douyin_get_daily_hot_rank(type: Optional[str] = None,
                              start_time: Optional[str] = None,
                              end_time: Optional[str] = None) -> Dict[str, Any]:
    """抖音每日热门作品榜（按点赞排名，日度收录）。type 为类别（如 二次元、美食，
    不传查全部）；start_time/end_time 格式 yyyy-MM-dd，不传默认昨日（每日 10 点后更新）。"""
    return call(lambda: get_client().douyin.get_daily_hot_rank,
                type=type, start_time=start_time, end_time=end_time)


@mcp.tool()
def douyin_get_daily_surge_rank(type: Optional[str] = None,
                                start_time: Optional[str] = None) -> Dict[str, Any]:
    """抖音每日点赞飙升榜（单日新增点赞排名）。type 为分类（如 小剧场、财富理财，
    不传或"全部"查全部分类）；start_time 为榜单日期 yyyy-MM-dd，不传默认昨日（每日 16 点更新）。"""
    return call(lambda: get_client().douyin.get_daily_surge_rank,
                type=type, start_time=start_time)


@mcp.tool()
def douyin_get_weekly_surge_rank(type: Optional[str] = None,
                                 start_time: Optional[str] = None) -> Dict[str, Any]:
    """抖音七日点赞飙升榜（七日新增点赞排名）。type 为分类，不传或"全部"查全部分类；
    start_time 为榜单日期 yyyy-MM-dd，不传默认昨日（每日 16:30 更新）。"""
    return call(lambda: get_client().douyin.get_weekly_surge_rank,
                type=type, start_time=start_time)


@mcp.tool()
def douyin_get_hot_accounts(date_type: str, rank_date: str,
                            type: str) -> Dict[str, Any]:
    """抖音热门账号推荐（日/周/月榜）。date_type：days=日、weeks=周、months=月；
    rank_date 格式 yyyy-MM-dd（日榜传当日日期、周榜传周一日期、月榜传一号）；
    type 为类别（如 全部、个人才艺、美食）。"""
    return call(lambda: get_client().douyin.get_hot_accounts,
                date_type=date_type, rank_date=rank_date, type=type)


# ─── 视频提文案 ───────────────────────────────────────────


@mcp.tool()
def douyin_transcript(url: str, timeout_seconds: int = 240) -> Dict[str, Any]:
    """抖音视频提文案：提取视频完整文案（含带时间戳分句），提交后自动等待并返回结果。
    url 为视频链接（支持口令分享文本）；超时未完成时返回 taskId，可用 douyin_transcript_result 再查。"""
    return run_task(lambda: get_client().douyin.transcript_submit,
                    lambda: get_client().douyin.transcript_result,
                    timeout_seconds, url=url)


@mcp.tool()
def douyin_transcript_result(task_id: str) -> Dict[str, Any]:
    """查询抖音视频提文案任务结果。仅在 douyin_transcript 超时返回 taskId 后使用。"""
    return call(lambda: get_client().douyin.transcript_result, task_id=task_id)


def main() -> None:
    serve(mcp, prog="redfox-douyin-mcp", description="RedFox 抖音数据 MCP server")


if __name__ == "__main__":
    main()
