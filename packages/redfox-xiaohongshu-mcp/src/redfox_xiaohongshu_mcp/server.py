"""RedFox 小红书数据 MCP Server

将 RedFoxHub（红狐数据平台）的小红书数据 API 暴露为 MCP 工具。

认证：stdio 模式读环境变量 REDFOX_API_KEY；HTTP 模式从请求头
REDFOX_API_KEY（或 Authorization: Bearer <key>）取 key。
获取地址 https://redfox.hk/settings/api-keys?source=mcp
"""

from typing import Annotated, Any, Dict, Optional
from pydantic import Field

from redfox_mcp_core import call, create_server, get_client, serve

from redfox_xiaohongshu_mcp import __version__

mcp = create_server("redfox-xiaohongshu", __version__)


@mcp.tool()
def xiaohongshu_search_articles(keyword: Annotated[str, Field(description="关键词，[必填]，示例: 美食")], offset: Annotated[int, Field(description="偏移量，从0开始，每页+20，[可选]，示例: 0")] = 0,
                                sort_type: Annotated[Optional[str], Field(description="排序方式： _0: 默认（相关性排序）_2: 最新（按发布时间排序）_4: 最热（按互动数排序），[可选]，示例: _0")] = None) -> Dict[str, Any]:
    """搜索小红书笔记（优质库）。keyword 必填；offset 分页偏移。

接口: POST /story/api/xhsUser/searchArticle"""
    return call(lambda: get_client().xiaohongshu.search_articles,
                keyword=keyword, offset=offset, sort_type=sort_type, source="搜索小红书笔记-MCP")


@mcp.tool()
def xiaohongshu_search_users(keyword: Annotated[str, Field(description="关键词，[必填]，示例: 赵露思")], offset: Annotated[int, Field(description="偏移量，从0开始，每页+20，[可选]，示例: 0")] = 0,
                             sort_type: Annotated[Optional[str], Field(description="排序方式: _0: 默认（相关性排序）_2: 最新（按最近发文时间排序）_4: 最热，[可选]，示例: _0")] = None) -> Dict[str, Any]:
    """搜索小红书博主账号（优质库）。keyword 必填；offset 分页偏移。

接口: POST /story/api/xhsUser/searchUser"""
    return call(lambda: get_client().xiaohongshu.search_users,
                keyword=keyword, offset=offset, sort_type=sort_type, source="搜索小红书博主账号-MCP")


@mcp.tool()
def xiaohongshu_get_account(account_id: Annotated[str, Field(description="小红书号，[必填]，示例: rosy1109")],
                            user_id: Annotated[Optional[str], Field(description="用户ID（用户主页地址 https://www.xiaohongshu.com/user/profile/5a73c5fa4eacab4c4ccc9778中的5a73c5fa4eacab4c4ccc9778），[可选]，示例: 5a73c5fa4eacab4c4ccc9778")] = None) -> Dict[str, Any]:
    """获取小红书账号信息（优质库）。account_id 为小红书号（必填），user_id 可选。

接口: POST /story/api/xhsUser/queryAccountDetail"""
    return call(lambda: get_client().xiaohongshu.get_account,
                account_id=account_id, user_id=user_id, source="获取小红书账号信息-MCP")


@mcp.tool()
def xiaohongshu_get_work(work_id: Annotated[Optional[str], Field(description="作品id（二选一必填），[可选]，示例: 6a03be1b0000000035033163")] = None,
                         work_link: Annotated[Optional[str], Field(description="作品链接（二选一必填），[可选]，示例: https://www.xiaohongshu.com/explore/6a2ac3020000000035022d8e")] = None) -> Dict[str, Any]:
    """获取小红书笔记详情（优质库）。work_id 与 work_link（笔记链接）至少传一个。

接口: POST /story/api/xhsUser/queryWorkDetail"""
    return call(lambda: get_client().xiaohongshu.get_work,
                work_id=work_id, work_link=work_link, source="获取小红书笔记详情-MCP")


@mcp.tool()
def xiaohongshu_search_ai_articles(keyword: Annotated[str, Field(description="关键词，[必填]，示例: AI")], page_num: Annotated[int, Field(description="页码，[可选]，示例: 1")] = 1,
                                   page_size: Annotated[int, Field(description="每页条数，[可选]，示例: 20")] = 20,
                                   start_time: Annotated[Optional[str], Field(description="开始时间，[可选]，示例: 2026-06-01 00:00:00")] = None,
                                   end_time: Annotated[Optional[str], Field(description="结束时间，[可选]，示例: 2026-06-02 00:00:00")] = None) -> Dict[str, Any]:
    """搜索小红书 AI 创作相关笔记（优质库）。keyword 必填；
    start_time/end_time 格式如 "2026-06-01 00:00:00"。

接口: POST /story/api/parseWork/queryXhsAiMsgs"""
    return call(lambda: get_client().xiaohongshu.search_ai_articles,
                keyword=keyword, page_num=page_num, page_size=page_size,
                start_time=start_time, end_time=end_time,
                source="搜索小红书 AI 创作相关笔记-MCP")


# ─── 账号作品列表 ─────────────────────────────────────────


@mcp.tool()
def xiaohongshu_get_user_works(red_id: Annotated[Optional[str], Field(description="账号平台展示id（redId和userid至少传一个），[可选]，示例: rosy1109")] = None,
                               userid: Annotated[Optional[str], Field(description="账号主键id（redId和userid至少传一个），[可选]，示例: 5a73c5fa4eacab4c4ccc9778")] = None,
                               offset: Annotated[int, Field(description="偏移量，从0开始，每页+20，[可选]，示例: 0")] = 0,
                               sort_type: Annotated[Optional[str], Field(description="排序方式 _0: 默认（相关性排序） _2: 最新（按发布时间倒序） _4: 最热（按互动数倒序），[可选]")] = None,
                               publish_time_start: Annotated[Optional[str], Field(description="发布时间起始（格式 yyyy-MM-dd），[可选]，示例: 2026-07-01 00:00:00")] = None,
                               publish_time_end: Annotated[Optional[str], Field(description="发布时间结束（格式 yyyy-MM-dd），[可选]，示例: 2026-08-01 00:00:00")] = None) -> Dict[str, Any]:
    """查询小红书账号作品列表（优质库）。red_id（小红书号）/ userid（账号主键 id）
    至少传一个；offset 从 0 开始、每页 +20；sort_type：_0=默认，_2=最新，_4=最热；
    publish_time_start/end 格式 yyyy-MM-dd。

接口: POST /story/api/xhsUser/queryWorkList"""
    return call(lambda: get_client().xiaohongshu.get_user_works,
                red_id=red_id, userid=userid, offset=offset, sort_type=sort_type,
                publish_time_start=publish_time_start,
                publish_time_end=publish_time_end, source="查询小红书账号作品列表-MCP")


# ─── 榜单与洞察 ───────────────────────────────────────────


@mcp.tool()
def xiaohongshu_get_daily_hot_rank(rank_date: Annotated[str, Field(description="榜单日期，格式：yyyy-MM-dd (每日18:00更新昨日数据) 只能查询近30天以内的数据，[必填]，示例: 2026-08-25")], category: Annotated[str, Field(description="综合全部,出行代步,医疗保健,休闲爱好,综合杂项,婚庆婚礼,居家装修,影视娱乐,星座情感,拍摄记录,学习教育,旅行度假,亲子育儿,日常生活,科学探索,数码科技,时尚穿搭,化妆美容,个人护理,美味佳肴,职业发展,宠物天地,新闻资讯,体育锻炼,潮流鞋包，[必填]，示例: 综合全部")]) -> Dict[str, Any]:
    """小红书每日爆款笔记榜单。rank_date 为榜单日期 yyyy-MM-dd；
    category 为分类（如 综合全部、时尚穿搭、美味佳肴）。

接口: GET /story/api/cozeSkill/getXhsCozeSkillDataOne"""
    return call(lambda: get_client().xiaohongshu.get_daily_hot_rank,
                rank_date=rank_date, category=category, source="小红书每日爆款笔记榜单-MCP")


@mcp.tool()
def xiaohongshu_get_weekly_hot_rank(rank_date: Annotated[Optional[str], Field(description="榜单日期（每天 19:00 更新「昨日」榜单），[可选]，示例: 2026-08-10")] = None,
                                    category: Annotated[Optional[str], Field(description="综合全部、出行代步、医疗保健、休闲爱好、综合杂项、婚庆婚礼、居家装修、影视娱乐、星座情感、拍摄记录、学习教育、旅行度假、亲子育儿、日常生活、科学探索、数码科技、时尚穿搭、化妆美容、个人护理、美味佳肴、职业发展、宠物天地、新闻资讯、体育锻炼、潮流鞋包，[可选]，示例: 综合全部")] = None) -> Dict[str, Any]:
    """小红书七日爆款笔记。rank_date 为榜单日期 yyyy-MM-dd（每天 19:00 更新昨日榜单）；
    category 为分类（如 综合全部、出行代步），均可不传。

接口: GET /story/api/cozeSkill/getXhsCozeSkillDataSeven"""
    return call(lambda: get_client().xiaohongshu.get_weekly_hot_rank,
                rank_date=rank_date, category=category, source="小红书七日爆款笔记-MCP")


@mcp.tool()
def xiaohongshu_get_hot_accounts(date_type: Annotated[Optional[int], Field(description="日期类型： 1-日 2-周 3-月，[可选]，示例: 1")] = None,
                                 rank_date: Annotated[Optional[str], Field(description="日期格式：yyyy-MM-dd 当日期类型选择1时，输入所需日的起始时间（每晚8点更新昨日数据） 当日期类型选择2时，输入所需周的周一时间（每周一更新上周数据） 当日期类型选择3时，输入所需月的一号时间（每月一号更新上月数据），[可选]，示例: 2026-08-16")] = None,
                                 type: Annotated[Optional[str], Field(description="类别：综合全部、出行代步、医疗保健、休闲爱好、综合杂项、婚庆婚礼、居家装修、影视娱乐、星座情感、拍摄记录、学习教育、旅行度假、亲子育儿、日常生活、科学探索、数码科技、时尚穿搭、化妆美容、个人护理、美味佳肴、职业发展、宠物天地、新闻资讯、体育锻炼、潮流鞋包，[可选]，示例: 综合全部")] = None) -> Dict[str, Any]:
    """小红书热门账号推荐（日/周/月榜）。date_type：1=日、2=周、3=月；
    rank_date 格式 yyyy-MM-dd（日榜传当日日期、周榜传周一日期、月榜传一号）；
    type 为类别（如 综合全部）。

接口: POST /story/api/xhsData/query"""
    return call(lambda: get_client().xiaohongshu.get_hot_accounts,
                date_type=date_type, rank_date=rank_date, type=type, source="小红书热门账号推荐-MCP")


@mcp.tool()
def xiaohongshu_search_hot_notes(keyword: Annotated[Optional[str], Field(description="搜索关键词（可选，不传则按互动数降序返回最热门数据），[可选]，示例: AIGC创业")] = None,
                                 page_num: Annotated[int, Field(description="页码，从1开始（可选，默认1，无关键词时生效），[可选]，示例: 1")] = 1, page_size: Annotated[int, Field(description="每页条数（可选，默认10，最大50，无关键词时生效），[可选]，示例: 10")] = 10,
                                 start_date: Annotated[Optional[str], Field(description="时间范围-开始日期，格式：yyyy-MM-dd（可选），[可选]，示例: 2026-07-01")] = None,
                                 end_date: Annotated[Optional[str], Field(description="时间范围-结束日期，格式：yyyy-MM-dd（可选），[可选]，示例: 2026-07-31")] = None) -> Dict[str, Any]:
    """小红书爆款笔记洞察。keyword 可选，不传则按互动数降序返回最热门数据；
    page_num/page_size 在无关键词时生效（page_size 最大 50）；
    start_date/end_date 格式 yyyy-MM-dd。

接口: POST /story/api/xhs/search/search"""
    return call(lambda: get_client().xiaohongshu.search_hot_notes,
                keyword=keyword, page_num=page_num, page_size=page_size,
                start_date=start_date, end_date=end_date, source="小红书爆款笔记洞察-MCP")


@mcp.tool()
def xiaohongshu_get_dark_horse_notes(category: Annotated[str, Field(description="分类：'综合全部','出行代步','医疗保健','休闲爱好','综合杂项','婚庆婚礼','居家装修','影视娱乐','星座情感','拍摄记录','学习教育','旅行度假','亲子育儿','日常生活','科学探索','数码科技','时尚穿搭','化妆美容','个人护理','美味佳肴','职业发展','宠物天地','新闻资讯','体育锻炼','潮流鞋包'，[必填]，示例: 潮流鞋包")], start_date: Annotated[str, Field(description="开始日期，格式：yyyy-MM-dd，最长为最近30天，默认30天前 （当日下午18:00更新昨日榜单数据），[必填]，示例: 2026-09-08")]) -> Dict[str, Any]:
    """小红书黑马爆文榜（低粉账号爆款笔记）。category 为分类（必填），
    取值如 综合全部、出行代步、医疗保健、时尚穿搭、美味佳肴 等中文分类名；
    start_date 为榜单日期 yyyy-MM-dd（最长最近 30 天）。

接口: POST /story/api/cozeSkill/getLowPowderExplosiveArticle"""
    return call(lambda: get_client().xiaohongshu.get_dark_horse_notes,
                category=category, start_date=start_date, source="小红书黑马爆文榜-MCP")


# ─── 评论（异步任务） ──────────────────────────────────────


@mcp.tool()
def xiaohongshu_get_comments(opus_id: Annotated[str, Field(description="（必填，作品id），[必填]，示例: 6a546c340000000007022631")], data_num: Annotated[int, Field(description="（必填，所需条数，必须大于0），[必填]，示例: 20")],
                             timeout_seconds: Optional[int] = None) -> Dict[str, Any]:
    """提交小红书笔记一级评论任务（广域库），立即返回 taskId，不自动查询结果。
    opus_id 为作品 id（笔记链接 explore/ 后的部分）；data_num 为所需条数，-1=全部。
    评论数据约 24 小时后才可见，请稍后用 xiaohongshu_get_comments_result(task_id)
    自行查询结果。timeout_seconds 为可选参数，可传可不传，传与不传都不影响本调用
    （本工具只提交任务、不再自动轮询结果）。

接口: POST /story/api/xhs/commentSubmit"""
    return call(lambda: get_client().xiaohongshu.comment_submit,
                opus_id=opus_id, data_num=data_num, source="获取小红书笔记一级评论-MCP")


@mcp.tool()
def xiaohongshu_get_comments_result(task_id: Annotated[str, Field(description="任务ID，[必填]，示例: xxxxx")]) -> Dict[str, Any]:
    """查询小红书评论任务结果。传 xiaohongshu_get_comments 提交返回的 taskId。

接口: POST /story/api/xhs/commentResult"""
    return call(lambda: get_client().xiaohongshu.comment_result, task_id=task_id, source="查询小红书评论任务结果-MCP")


# ─── 视频提文案（异步任务） ─────────────────────────────────


@mcp.tool()
def xiaohongshu_transcript(url: Annotated[str, Field(description="视频链接，[必填]，示例: https://www.xiaohongshu.com/explore/6a3c7aa6000000001003e071?xsec_token=AB-U4vc8DJUJoY9w-ebP_DvuxgiSNYmx8n35V4zvPo__M=&xsec_source=pc_feed")], timeout_seconds: Optional[int] = None) -> Dict[str, Any]:
    """提交小红书视频提文案任务，立即返回 taskId，不自动查询结果。
    url 为笔记/视频链接。请稍后用 xiaohongshu_transcript_result(task_id)
    自行查询结果。timeout_seconds 为可选参数，可传可不传，传与不传都不影响本调用
    （本工具只提交任务、不自动轮询结果）。

接口: POST /story/api/parseWork/audioTextExtract/submit/xhs"""
    return call(lambda: get_client().xiaohongshu.transcript_submit,
                url=url, source="小红书视频提文案-MCP")


@mcp.tool()
def xiaohongshu_transcript_result(task_id: Annotated[str, Field(description="任务ID（必填），[必填]，示例: 08fbd9bb8b4f41fd80c0a0baf1b26cd1")]) -> Dict[str, Any]:
    """查询小红书视频提文案任务结果。传 xiaohongshu_transcript 提交返回的 taskId。

接口: POST /story/api/parseWork/audioTextExtract/result/xhs"""
    return call(lambda: get_client().xiaohongshu.transcript_result, task_id=task_id, source="查询小红书视频提文案任务结果-MCP")


def main() -> None:
    serve(mcp, prog="redfox-xiaohongshu-mcp", description="RedFox 小红书数据 MCP server")


if __name__ == "__main__":
    main()
