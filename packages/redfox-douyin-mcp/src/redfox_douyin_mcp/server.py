"""RedFox 抖音数据 MCP Server

将 RedFoxHub（红狐数据平台）的抖音数据 API 暴露为 MCP 工具。

认证：stdio 模式读环境变量 REDFOX_API_KEY；HTTP 模式从请求头
REDFOX_API_KEY（或 Authorization: Bearer <key>）取 key。
获取地址 https://redfox.hk/settings/api-keys?source=mcp
"""

from typing import Annotated, Any, Dict, Optional
from pydantic import Field

from redfox_mcp_core import call, create_server, get_client, serve

from redfox_douyin_mcp import __version__

mcp = create_server("redfox-douyin", __version__)


@mcp.tool()
def douyin_search_articles(keyword: Annotated[str, Field(description="关键词，[必填]，示例: 示例关键词")], offset: Annotated[int, Field(description="offset:偏移量，从0开 始，每页+20，[可选]，示例: 0")] = 0,
                           sort_type: Annotated[Optional[str], Field(description="排序方式 _0: 默认（相关性排序） _2: 最新（按发布时间倒序） _4: 最热（按阅读数倒序），[可选]，示例: default")] = None) -> Dict[str, Any]:
    """搜索抖音作品（优质库）。keyword 必填；offset 分页偏移从 0 开始、每次 +20；
    sort_type 排序方式，如 "default"。返回含 total/hasMore/list。

接口: POST /story/api/dyData/searchArticle"""
    return call(lambda: get_client().douyin.search_articles,
                keyword=keyword, offset=offset, sort_type=sort_type, source="搜索抖音作品（优质库）-MCP")


@mcp.tool()
def douyin_search_users(keyword: Annotated[str, Field(description="关键词，[必填]，示例: 示例关键词")], offset: Annotated[int, Field(description="offset:偏移量，从0开 始，每页+20，[可选]，示例: 0")] = 0,
                        sort_type: Annotated[Optional[str], Field(description="排序方式 _0: 默认（相关性排序） _2: 最新（按发布时间倒序） _4: 最热（按阅读数倒序），[可选]，示例: _0")] = None) -> Dict[str, Any]:
    """搜索抖音账号（优质库）。keyword 必填；offset 分页偏移从 0 开始。

接口: POST /story/api/dyData/searchUser"""
    return call(lambda: get_client().douyin.search_users,
                keyword=keyword, offset=offset, sort_type=sort_type, source="搜索抖音账号（优质库）-MCP")


@mcp.tool()
def douyin_get_user(account_id: Annotated[str, Field(description="抖音账号id（支持unique_id、short_id、uid任一匹配查询），[必填]，示例: dy_user123")]) -> Dict[str, Any]:
    """获取抖音账号信息（优质库）。account_id 为抖音账号 ID，
    支持 unique_id、short_id、uid 任一匹配。

接口: POST /story/api/dyData/queryUser"""
    return call(lambda: get_client().douyin.get_user, account_id=account_id, source="获取抖音账号信息-MCP")


@mcp.tool()
def douyin_get_user_works(account_id: Annotated[Optional[str], Field(description="抖音号，[可选]，示例: nxpt260212")] = None,
                          author_url: Annotated[Optional[str], Field(description="authorUrl，[可选]，示例: https://www.douyin.com/user/MS4wLjABAAAAt31q5fSMDcrB41MMNuisAIymY61Avrq0zJb1wOKVukq7TQKRfz9Jn7Kxw04a0vPh?from_tab_name=main&vid=7649243955624004965")] = None,
                          sec_user_id: Annotated[Optional[str], Field(description="作者sec_user_id，[可选]，示例: MS4wLjABAAAAt31q5fSMDcrB41MMNuisAIymY61Avrq0zJb1wOKVukq7TQKRfz9Jn7Kxw04a0vPh")] = None,
                          offset: Annotated[int, Field(description="offset:偏移量，从0开始，每页+20，[可选]，示例: 0")] = 0,
                          sort_type: Annotated[Optional[str], Field(description="排序方式 _0: 默认（相关性排序） _2: 最新（按发布时间倒序） _4: 最热（按阅读数倒序），[可选]，示例: default")] = None) -> Dict[str, Any]:
    """获取抖音账号作品列表（优质库）。account_id（抖音号）/ author_url（主页链接）/
    sec_user_id 至少传一个；offset 每页 +20；sort_type：0=默认，2=最新，4=最热。

接口: POST /story/api/dyData/queryWorkList"""
    return call(lambda: get_client().douyin.get_user_works,
                account_id=account_id, author_url=author_url,
                sec_user_id=sec_user_id, offset=offset, sort_type=sort_type, source="获取抖音账号作品列表（优质库）-MCP")


@mcp.tool()
def douyin_get_work(work_id: Annotated[Optional[str], Field(description="作品ID（二选一），[可选]，示例: 10000123456789")] = None,
                    work_url: Annotated[Optional[str], Field(description="作品链接（二选一），[可选]，示例: https://example.com/example")] = None) -> Dict[str, Any]:
    """获取抖音作品详情（优质库）。work_id 与 work_url（作品链接）至少传一个，
    返回互动数据、作者信息等。

接口: POST /story/api/dyData/queryWork"""
    return call(lambda: get_client().douyin.get_work, work_id=work_id, work_url=work_url, source="获取抖音作品详情（优质库）-MCP")


@mcp.tool()
def douyin_search_ai_articles(keyword: Annotated[str, Field(description="关键词，[必填]，示例: AI")], page_num: Annotated[int, Field(description="页码，[可选]，示例: 1")] = 1, page_size: Annotated[int, Field(description="每页条数，[可选]，示例: 20")] = 20,
                              start_time: Annotated[Optional[str], Field(description="start时间，[可选]，示例: 2026-06-01 00:00:00")] = None,
                              end_time: Annotated[Optional[str], Field(description="结束时间，[可选]，示例: 2026-06-02 00:00:00")] = None) -> Dict[str, Any]:
    """搜索抖音 AI 相关作品（优质库）。keyword 必填；
    start_time/end_time 格式如 "2026-06-01 00:00:00"。

接口: POST /story/api/parseWork/queryDyAiMsgs"""
    return call(lambda: get_client().douyin.search_ai_articles,
                keyword=keyword, page_num=page_num, page_size=page_size,
                start_time=start_time, end_time=end_time, source="搜索抖音 AI 相关作品-MCP")


# ─── 广域库 ──────────────────────────────────────────────


@mcp.tool()
def douyin_search_works_wide(keyword: Annotated[str, Field(description="搜索关键词（必填，匹配作品正文），[必填]，示例: 美食")], start_date: Annotated[Optional[str], Field(description="开始日期（可选，格式：yyyy-MM-dd），[可选]，示例: 2026-01-01")] = None,
                             end_date: Annotated[Optional[str], Field(description="结束日期（可选，格式：yyyy-MM-dd），[可选]，示例: 2026-07-21")] = None,
                             page_num: Annotated[int, Field(description="页码（从1开始，默认1），[可选]，示例: 1")] = 1, page_size: Annotated[int, Field(description="每页大小（默认10，最大50），[可选]，示例: 10")] = 10) -> Dict[str, Any]:
    """搜索抖音作品（广域库，覆盖范围大于优质库）。keyword 必填（匹配作品正文）；
    start_date/end_date 格式 yyyy-MM-dd；page_num 从 1 开始，page_size 最大 50。

接口: POST /story/api/dy/data/searchWork"""
    return call(lambda: get_client().douyin.search_works_wide,
                keyword=keyword, start_date=start_date, end_date=end_date,
                page_num=page_num, page_size=page_size, source="搜索抖音作品（广域库）-MCP")


@mcp.tool()
def douyin_search_accounts_wide(keyword: Annotated[str, Field(description="搜索关键词（必填，匹配账号名），[必填]，示例: 罗志祥")], page_num: Annotated[int, Field(description="页码（从1开始，默认1），[可选]，示例: 1")] = 1,
                                page_size: Annotated[int, Field(description="每页大小（默认10，最大50），[可选]，示例: 10")] = 10) -> Dict[str, Any]:
    """搜索抖音账号（广域库）。keyword 必填（匹配账号名）；
    page_num 从 1 开始，page_size 最大 50。

接口: POST /story/api/dy/data/searchAccount"""
    return call(lambda: get_client().douyin.search_accounts_wide,
                keyword=keyword, page_num=page_num, page_size=page_size, source="搜索抖音账号（广域库）-MCP")


@mcp.tool()
def douyin_get_work_wide(video_id: Annotated[str, Field(description="作品ID（必填，对应aweme_id），[必填]，示例: 7663047997038644499")]) -> Dict[str, Any]:
    """获取抖音作品详情（广域库）。video_id 为作品 ID（对应 aweme_id，必填）。

接口: POST /story/api/dy/data/workDetail"""
    return call(lambda: get_client().douyin.get_work_wide, video_id=video_id, source="获取抖音作品详情（广域库）-MCP")


@mcp.tool()
def douyin_get_user_works_wide(user_id: Annotated[Optional[str], Field(description="账号主键id / uid（userId / uniqueName / shortId 三选一必填），[可选]，示例: 3822358551859599")] = None,
                               unique_name: Annotated[Optional[str], Field(description="账号平台展示id（三选一必填），[可选]，示例: luoyonghao")] = None,
                               short_id: Annotated[Optional[str], Field(description="账号平台展示id-short（三选一必填），[可选]")] = None,
                               page_num: Annotated[int, Field(description="页码（从1开始，默认1），[可选]，示例: 1")] = 1, page_size: Annotated[int, Field(description="每页大小（默认10，最大50），[可选]，示例: 10")] = 10,
                               start_date: Annotated[Optional[str], Field(description="开始时间，[可选]，示例: 2026-07-01")] = None,
                               end_date: Annotated[Optional[str], Field(description="结束时间，[可选]，示例: 2026-07-20")] = None) -> Dict[str, Any]:
    """获取抖音账号作品列表（广域库）。user_id（uid）/ unique_name（抖音号）/
    short_id 三选一必填；page_num 从 1 开始，page_size 最大 50；
    start_date/end_date 格式 yyyy-MM-dd。

接口: POST /story/api/dy/data/listWorkByAccount"""
    return call(lambda: get_client().douyin.get_user_works_wide,
                user_id=user_id, unique_name=unique_name, short_id=short_id,
                page_num=page_num, page_size=page_size,
                start_date=start_date, end_date=end_date, source="获取抖音账号作品列表（广域库）-MCP")


# ─── 榜单 ────────────────────────────────────────────────


@mcp.tool()
def douyin_get_daily_hot_rank(type: Annotated[Optional[str], Field(description="类别（不传则查询全部）：小剧场、财富理财、二次元、身体锻炼、居家装修、数码科技、科学普及、旅行、美食、动物、明星娱乐、汽车、亲子、人文、三农、潮流风尚、游戏、生活记录、体育、舞蹈才艺、学习教育、休闲玩乐、影视、音乐、颜值造型、健康医学、综艺、个人成长，[可选]，示例: 二次元")] = None,
                              start_time: Annotated[Optional[str], Field(description="开始时间，格式：yyyy-MM-dd（可选，不传则默认前日）每日10点后更新昨日数据，[可选]，示例: 2026-08-11")] = None,
                              end_time: Annotated[Optional[str], Field(description="结束时间，格式：yyyy-MM-dd（可选，不传则默认前日）每日10点后更新昨日数据，[可选]，示例: 2026-08-12")] = None) -> Dict[str, Any]:
    """抖音每日热门作品榜（按点赞排名，日度收录）。type 为类别（如 二次元、美食，
    不传查全部）；start_time/end_time 格式 yyyy-MM-dd，不传默认昨日（每日 10 点后更新）。

接口: POST /story/api/dy/search/likesRank"""
    return call(lambda: get_client().douyin.get_daily_hot_rank,
                type=type, start_time=start_time, end_time=end_time, source="抖音每日热门作品榜-MCP")


@mcp.tool()
def douyin_get_daily_surge_rank(type: Annotated[Optional[str], Field(description="分类展示名称：小剧场 财富理财 二次元 身体锻炼 居家装修 数码科技 科学普及 旅行 美食 动物 明星娱乐 汽车 亲子 人文 三农 潮流风尚 游戏 生活记录 体育 舞蹈才艺 学习教育 休闲玩乐 影视 音乐 颜值造型 健康医学 综艺 个人成长 为空或\"全部\"时查询全部分类，[可选]，示例: 全部")] = None,
                                start_time: Annotated[Optional[str], Field(description="榜单日期，格式：yyyy-MM-dd（可选，不传则默认前日 每日20:00更新昨日数据），[可选]，示例: 2026-08-20")] = None) -> Dict[str, Any]:
    """抖音每日点赞飙升榜（单日新增点赞排名）。type 为分类（如 小剧场、财富理财，
    不传或"全部"查全部分类）；start_time 为榜单日期 yyyy-MM-dd，不传默认昨日（每日 16 点更新）。

接口: POST /story/api/dy/search/getDailyRank"""
    return call(lambda: get_client().douyin.get_daily_surge_rank,
                type=type, start_time=start_time, source="抖音每日点赞飙升榜-MCP")


@mcp.tool()
def douyin_get_weekly_surge_rank(type: Annotated[Optional[str], Field(description="分类展示名称：小剧场 财富理财 二次元 身体锻炼 居家装修 数码科技 科学普及 旅行 美食 动物 明星娱乐 汽车 亲子 人文 三农 潮流风尚 游戏 生活记录 体育 舞蹈才艺 学习教育 休闲玩乐 影视 音乐 颜值造型 健康医学 综艺 个人成长 为空或\"全部\"时查询全部分类，[可选]，示例: 全部")] = None,
                                 start_time: Annotated[Optional[str], Field(description="榜单日期，格式：yyyy-MM-dd（可选，不传则默认前日 每日20:00更新昨日数据），[可选]，示例: 2026-08-17")] = None) -> Dict[str, Any]:
    """抖音七日点赞飙升榜（七日新增点赞排名）。type 为分类，不传或"全部"查全部分类；
    start_time 为榜单日期 yyyy-MM-dd，不传默认昨日（每日 16:30 更新）。

接口: POST /story/api/dy/search/getWeeklyRank"""
    return call(lambda: get_client().douyin.get_weekly_surge_rank,
                type=type, start_time=start_time, source="抖音七日点赞飙升榜-MCP")


@mcp.tool()
def douyin_get_hot_accounts(date_type: Annotated[str, Field(description="日期类型: days-日 weeks-周 months-月，[必填]，示例: days")], rank_date: Annotated[str, Field(description="日期格式：yyyy-MM-dd 当日期类型选择days时，输入所需日的起始时间（每晚8点更新昨日数据） 当日期类型选择weeks时，输入所需周的周一时间（每周一更新上周数据） 当日期类型选择months时，输入所需月的一号时间（每月一号更新上月数据），[必填]，示例: 2026-08-16")],
                            type: Annotated[str, Field(description="类别：全部、个人才艺、生活vlog、财富理财、二次元、居家装修、学习教育、小剧场、数码科技、旅行、美食、化妆美容、动物、亲子、汽车、情感、三农、健康医学、潮流风尚、舞蹈才艺、颜值造型、人文、音乐、影视、身体锻炼、体育、明星娱乐、游戏，[必填]，示例: 个人才艺")]) -> Dict[str, Any]:
    """抖音热门账号推荐（日/周/月榜）。date_type：days=日、weeks=周、months=月；
    rank_date 格式 yyyy-MM-dd（日榜传当日日期、周榜传周一日期、月榜传一号）；
    type 为类别（如 全部、个人才艺、美食）。

接口: POST /story/api/dyData/query"""
    return call(lambda: get_client().douyin.get_hot_accounts,
                date_type=date_type, rank_date=rank_date, type=type, source="抖音热门账号推荐-MCP")


# ─── 视频提文案 ───────────────────────────────────────────


@mcp.tool()
def douyin_transcript(url: Annotated[str, Field(description="视频链接，[必填]，示例: 4.38 Oxs:/ e@O.xS 06/01 :2pm 如果你听懂了程艾影，那么即便是前奏也能够让你热泪盈眶了🩵 # 赵雷 # 程艾影 # 永远都像初次见你那样 # 署前街少年 # 音乐节现场 https://v.douyin.com/pjE9uqFMK68/ 复制此链接，打开Dou音搜索，直接观看视频！")], timeout_seconds: Optional[int] = None) -> Dict[str, Any]:
    """提交抖音视频提文案任务（含带时间戳分句），立即返回 taskId，不自动查询结果。
    url 为视频链接（支持口令分享文本）。请稍后用 douyin_transcript_result(task_id)
    自行查询结果。timeout_seconds 为可选参数，可传可不传，传与不传都不影响本调用
    （本工具只提交任务、不自动轮询结果）。

接口: POST /story/api/parseWork/audioTextExtract/submit/douyin"""
    return call(lambda: get_client().douyin.transcript_submit,
                url=url, source="抖音视频提文案-MCP")


@mcp.tool()
def douyin_transcript_result(task_id: Annotated[str, Field(description="任务ID（必填），[必填]，示例: 08fbd9bb8b4f41fd80c0a0baf1b26cd1")]) -> Dict[str, Any]:
    """查询抖音视频提文案任务结果。传 douyin_transcript 提交返回的 taskId。

接口: POST /story/api/parseWork/audioTextExtract/result/douyin"""
    return call(lambda: get_client().douyin.transcript_result, task_id=task_id, source="查询抖音视频提文案任务结果-MCP")


def main() -> None:
    serve(mcp, prog="redfox-douyin-mcp", description="RedFox 抖音数据 MCP server")


if __name__ == "__main__":
    main()
