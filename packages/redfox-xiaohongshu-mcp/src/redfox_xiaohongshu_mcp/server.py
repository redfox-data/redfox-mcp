"""RedFox 小红书数据 MCP Server

将 RedFoxHub（红狐数据平台）的小红书数据 API 暴露为 MCP 工具。

认证：stdio 模式读环境变量 REDFOX_API_KEY；HTTP 模式从请求头
X-API-Key（或 Authorization: Bearer <key>）取 key。
获取地址 https://redfox.hk/settings/api-keys?source=mcp
"""

from typing import Any, Dict, Optional

from redfox_mcp_core import call, create_server, get_client, run_task, serve

from redfox_xiaohongshu_mcp import __version__

mcp = create_server("redfox-xiaohongshu", __version__)


@mcp.tool()
def xiaohongshu_search_articles(keyword: str, offset: int = 0,
                                sort_type: Optional[str] = None) -> Dict[str, Any]:
    """搜索小红书笔记（优质库）。keyword 必填；offset 分页偏移。"""
    return call(lambda: get_client().xiaohongshu.search_articles,
                keyword=keyword, offset=offset, sort_type=sort_type)


@mcp.tool()
def xiaohongshu_search_users(keyword: str, offset: int = 0,
                             sort_type: Optional[str] = None) -> Dict[str, Any]:
    """搜索小红书博主账号（优质库）。keyword 必填；offset 分页偏移。"""
    return call(lambda: get_client().xiaohongshu.search_users,
                keyword=keyword, offset=offset, sort_type=sort_type)


@mcp.tool()
def xiaohongshu_get_account(account_id: str,
                            user_id: Optional[str] = None) -> Dict[str, Any]:
    """获取小红书账号信息（优质库）。account_id 为小红书号（必填），user_id 可选。"""
    return call(lambda: get_client().xiaohongshu.get_account,
                account_id=account_id, user_id=user_id)


@mcp.tool()
def xiaohongshu_get_work(work_id: Optional[str] = None,
                         work_link: Optional[str] = None) -> Dict[str, Any]:
    """获取小红书笔记详情（优质库）。work_id 与 work_link（笔记链接）至少传一个。"""
    return call(lambda: get_client().xiaohongshu.get_work,
                work_id=work_id, work_link=work_link)


@mcp.tool()
def xiaohongshu_search_ai_articles(keyword: str, page_num: int = 1,
                                   page_size: int = 20,
                                   start_time: Optional[str] = None,
                                   end_time: Optional[str] = None,
                                   source: Optional[str] = None) -> Dict[str, Any]:
    """搜索小红书 AI 创作相关笔记（优质库）。keyword 必填；
    start_time/end_time 格式如 "2026-06-01 00:00:00"；source 为来源平台（可选）。"""
    return call(lambda: get_client().xiaohongshu.search_ai_articles,
                keyword=keyword, page_num=page_num, page_size=page_size,
                start_time=start_time, end_time=end_time, source=source)


# ─── 账号作品列表 ─────────────────────────────────────────


@mcp.tool()
def xiaohongshu_get_user_works(red_id: Optional[str] = None,
                               userid: Optional[str] = None,
                               offset: int = 0,
                               sort_type: Optional[str] = None,
                               publish_time_start: Optional[str] = None,
                               publish_time_end: Optional[str] = None) -> Dict[str, Any]:
    """查询小红书账号作品列表（优质库）。red_id（小红书号）/ userid（账号主键 id）
    至少传一个；offset 从 0 开始、每页 +20；sort_type：_0=默认，_2=最新，_4=最热；
    publish_time_start/end 格式 yyyy-MM-dd。"""
    return call(lambda: get_client().xiaohongshu.get_user_works,
                red_id=red_id, userid=userid, offset=offset, sort_type=sort_type,
                publish_time_start=publish_time_start,
                publish_time_end=publish_time_end)


# ─── 榜单与洞察 ───────────────────────────────────────────


@mcp.tool()
def xiaohongshu_get_daily_hot_rank(rank_date: str, category: str) -> Dict[str, Any]:
    """小红书每日爆款笔记榜单。rank_date 为榜单日期 yyyy-MM-dd；
    category 为分类（如 综合全部、时尚穿搭、美味佳肴）。"""
    return call(lambda: get_client().xiaohongshu.get_daily_hot_rank,
                rank_date=rank_date, category=category)


@mcp.tool()
def xiaohongshu_get_weekly_hot_rank(rank_date: Optional[str] = None,
                                    category: Optional[str] = None) -> Dict[str, Any]:
    """小红书七日爆款笔记。rank_date 为榜单日期 yyyy-MM-dd（每天 19:00 更新昨日榜单）；
    category 为分类（如 综合全部、出行代步），均可不传。"""
    return call(lambda: get_client().xiaohongshu.get_weekly_hot_rank,
                rank_date=rank_date, category=category)


@mcp.tool()
def xiaohongshu_get_hot_accounts(date_type: Optional[int] = None,
                                 rank_date: Optional[str] = None,
                                 type: Optional[str] = None) -> Dict[str, Any]:
    """小红书热门账号推荐（日/周/月榜）。date_type：1=日、2=周、3=月；
    rank_date 格式 yyyy-MM-dd（日榜传当日日期、周榜传周一日期、月榜传一号）；
    type 为类别（如 综合全部）。"""
    return call(lambda: get_client().xiaohongshu.get_hot_accounts,
                date_type=date_type, rank_date=rank_date, type=type)


@mcp.tool()
def xiaohongshu_search_hot_notes(keyword: Optional[str] = None,
                                 page_num: int = 1, page_size: int = 10,
                                 start_date: Optional[str] = None,
                                 end_date: Optional[str] = None) -> Dict[str, Any]:
    """小红书爆款笔记洞察。keyword 可选，不传则按互动数降序返回最热门数据；
    page_num/page_size 在无关键词时生效（page_size 最大 50）；
    start_date/end_date 格式 yyyy-MM-dd。"""
    return call(lambda: get_client().xiaohongshu.search_hot_notes,
                keyword=keyword, page_num=page_num, page_size=page_size,
                start_date=start_date, end_date=end_date)


@mcp.tool()
def xiaohongshu_get_dark_horse_notes(keyword: str, start_date: str) -> Dict[str, Any]:
    """小红书黑马爆文榜（低粉账号爆款笔记）。keyword 必填，多个关键词用逗号分隔、
    最多 5 个、总长度不超过 200；start_date 为开始日期 yyyy-MM-dd（最长最近 30 天）。"""
    return call(lambda: get_client().xiaohongshu.get_dark_horse_notes,
                keyword=keyword, start_date=start_date)


# ─── 评论（异步任务） ──────────────────────────────────────


@mcp.tool()
def xiaohongshu_get_comments(opus_id: str, data_num: int,
                             timeout_seconds: int = 240) -> Dict[str, Any]:
    """获取小红书笔记一级评论（广域库），提交后自动等待并返回结果。
    opus_id 为作品 id（笔记链接 explore/ 后的部分）；data_num 为所需条数，-1=全部；
    超时未完成时返回 taskId，可用 xiaohongshu_get_comments_result 再查。"""
    return run_task(lambda: get_client().xiaohongshu.comment_submit,
                    lambda: get_client().xiaohongshu.comment_result,
                    timeout_seconds, opus_id=opus_id, data_num=data_num)


@mcp.tool()
def xiaohongshu_get_comments_result(task_id: str) -> Dict[str, Any]:
    """查询小红书评论任务结果。仅在 xiaohongshu_get_comments 超时返回 taskId 后使用。"""
    return call(lambda: get_client().xiaohongshu.comment_result, task_id=task_id)


# ─── 视频提文案（异步任务） ─────────────────────────────────


@mcp.tool()
def xiaohongshu_transcript(url: str, timeout_seconds: int = 240) -> Dict[str, Any]:
    """小红书视频提文案：提取视频完整文案，提交后自动等待并返回结果。
    url 为笔记/视频链接；超时未完成时返回 taskId，可用 xiaohongshu_transcript_result 再查。"""
    return run_task(lambda: get_client().xiaohongshu.transcript_submit,
                    lambda: get_client().xiaohongshu.transcript_result,
                    timeout_seconds, url=url)


@mcp.tool()
def xiaohongshu_transcript_result(task_id: str) -> Dict[str, Any]:
    """查询小红书视频提文案任务结果。仅在 xiaohongshu_transcript 超时返回 taskId 后使用。"""
    return call(lambda: get_client().xiaohongshu.transcript_result, task_id=task_id)


def main() -> None:
    serve(mcp, prog="redfox-xiaohongshu-mcp", description="RedFox 小红书数据 MCP server")


if __name__ == "__main__":
    main()
