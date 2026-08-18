"""RedFox MCP Server

将 RedFoxHub（红狐数据平台）的 40 个 API 能力暴露为 MCP 工具：
- 6 大内容平台数据查询（抖音/小红书/公众号/B站/头条/TikTok，26 个同步工具）
- AI 搜索（Kimi/豆包/Deepseek，3 个自动轮询工具 + 3 个结果查询工具）
- AI 生成（GPT 图片/豆包图片 Pro/Lite/豆包视频，4 个自动轮询工具 + 4 个结果查询工具）

认证：环境变量 REDFOX_API_KEY（获取地址 https://redfox.hk/settings/api-keys?source=mcp）
"""

import time
from typing import Any, Dict, List, Optional

from fastmcp import FastMCP
from redfox import RedFoxClient
from redfox.exceptions import RedFoxAPIError, RedFoxAuthError, RedFoxRateLimitError

mcp = FastMCP("redfox")

API_KEY_GUIDE = (
    "REDFOX_API_KEY 未配置或无效。请前往 "
    "https://redfox.hk/settings/api-keys?source=mcp 注册并获取 API Key，"
    "然后设置环境变量 REDFOX_API_KEY 后重启本服务。"
)

TASK_PENDING_MSG = (
    "任务仍在进行中，已超过本次等待时间。"
    "请稍后使用对应的 result 工具并传入此 taskId 查询结果。"
)

TERMINAL_STATUSES = {
    "succeeded", "success", "completed", "complete", "done",
    "failed", "error", "cancelled", "canceled",
}

_client: Optional[RedFoxClient] = None


def _get_client() -> RedFoxClient:
    global _client
    if _client is None:
        _client = RedFoxClient()  # 零配置：自动读环境变量 REDFOX_API_KEY
    return _client


def _call(fn_factory, **kwargs) -> Dict[str, Any]:
    """统一调用 SDK 方法并把异常转为结构化结果，agent 可直接读取出错引导"""
    try:
        return fn_factory()(**{k: v for k, v in kwargs.items() if v is not None})
    except (RedFoxAuthError, ValueError):
        return {"error": "auth_failed", "message": API_KEY_GUIDE}
    except RedFoxRateLimitError:
        return {"error": "rate_limited", "message": "请求频率超限，请稍后重试"}
    except RedFoxAPIError as e:
        return {"error": "api_error", "code": e.code, "message": e.message}


def _is_done(res: Any) -> bool:
    """判断异步任务是否到达终态（兼容各品类不同的响应结构）"""
    if not isinstance(res, dict):
        return True
    if res.get("error"):
        return True
    if res.get("completed") is True:
        return True
    status = res.get("status")
    if isinstance(status, str) and status.lower() in TERMINAL_STATUSES:
        return True
    for field in ("content", "imagePaths", "images", "videoUrl", "videoUrls", "video"):
        if res.get(field):
            return True
    return False


def _poll(result_fn, task_id: str, timeout_seconds: int, interval: float = 3.0) -> Dict[str, Any]:
    deadline = time.monotonic() + timeout_seconds
    while True:
        res = _call(result_fn, task_id=task_id)
        if _is_done(res):
            return res
        if time.monotonic() >= deadline:
            return {"completed": False, "taskId": task_id, "message": TASK_PENDING_MSG}
        time.sleep(interval)


def _run_task(submit_fn, result_fn, timeout_seconds: int, **kwargs) -> Dict[str, Any]:
    """提交异步任务并自动轮询至完成；超时则返回 taskId 供 result 工具后续查询"""
    submitted = _call(submit_fn, **kwargs)
    if not isinstance(submitted, dict) or submitted.get("error"):
        return submitted
    task_id = submitted.get("taskId") or submitted.get("task_id")
    if not task_id:
        return submitted
    return _poll(result_fn, task_id, timeout_seconds)


# ─── 抖音 ────────────────────────────────────────────────


@mcp.tool()
def douyin_search_articles(keyword: str, offset: int = 0,
                           sort_type: Optional[str] = None) -> Dict[str, Any]:
    """搜索抖音作品（优质库）。keyword 必填；offset 分页偏移从 0 开始、每次 +20；
    sort_type 排序方式，如 "default"。返回含 total/hasMore/list。"""
    return _call(lambda: _get_client().douyin.search_articles,
                 keyword=keyword, offset=offset, sort_type=sort_type)


@mcp.tool()
def douyin_search_users(keyword: str, offset: int = 0,
                        sort_type: Optional[str] = None) -> Dict[str, Any]:
    """搜索抖音账号（优质库）。keyword 必填；offset 分页偏移从 0 开始。"""
    return _call(lambda: _get_client().douyin.search_users,
                 keyword=keyword, offset=offset, sort_type=sort_type)


@mcp.tool()
def douyin_get_user(account_id: str) -> Dict[str, Any]:
    """获取抖音账号信息（优质库）。account_id 为抖音账号 ID，
    支持 unique_id、short_id、uid 任一匹配。"""
    return _call(lambda: _get_client().douyin.get_user, account_id=account_id)


@mcp.tool()
def douyin_get_user_works(account_id: Optional[str] = None,
                          author_url: Optional[str] = None,
                          sec_user_id: Optional[str] = None,
                          offset: int = 0,
                          sort_type: Optional[str] = None) -> Dict[str, Any]:
    """获取抖音账号作品列表（优质库）。account_id（抖音号）/ author_url（主页链接）/
    sec_user_id 至少传一个；offset 每页 +20；sort_type：0=默认，2=最新，4=最热。"""
    return _call(lambda: _get_client().douyin.get_user_works,
                 account_id=account_id, author_url=author_url,
                 sec_user_id=sec_user_id, offset=offset, sort_type=sort_type)


@mcp.tool()
def douyin_get_work(work_id: Optional[str] = None,
                    work_url: Optional[str] = None) -> Dict[str, Any]:
    """获取抖音作品详情（优质库）。work_id 与 work_url（作品链接）至少传一个，
    返回互动数据、作者信息等。"""
    return _call(lambda: _get_client().douyin.get_work, work_id=work_id, work_url=work_url)


@mcp.tool()
def douyin_search_ai_articles(keyword: str, page_num: int = 1, page_size: int = 20,
                              start_time: Optional[str] = None,
                              end_time: Optional[str] = None) -> Dict[str, Any]:
    """搜索抖音 AI 相关作品（优质库）。keyword 必填；
    start_time/end_time 格式如 "2026-06-01 00:00:00"。"""
    return _call(lambda: _get_client().douyin.search_ai_articles,
                 keyword=keyword, page_num=page_num, page_size=page_size,
                 start_time=start_time, end_time=end_time)


# ─── 小红书 ──────────────────────────────────────────────


@mcp.tool()
def xiaohongshu_search_articles(keyword: str, offset: int = 0,
                                sort_type: Optional[str] = None) -> Dict[str, Any]:
    """搜索小红书笔记（优质库）。keyword 必填；offset 分页偏移。"""
    return _call(lambda: _get_client().xiaohongshu.search_articles,
                 keyword=keyword, offset=offset, sort_type=sort_type)


@mcp.tool()
def xiaohongshu_search_users(keyword: str, offset: int = 0,
                             sort_type: Optional[str] = None) -> Dict[str, Any]:
    """搜索小红书博主账号（优质库）。keyword 必填；offset 分页偏移。"""
    return _call(lambda: _get_client().xiaohongshu.search_users,
                 keyword=keyword, offset=offset, sort_type=sort_type)


@mcp.tool()
def xiaohongshu_get_account(account_id: str,
                            user_id: Optional[str] = None) -> Dict[str, Any]:
    """获取小红书账号信息（优质库）。account_id 为小红书号（必填），user_id 可选。"""
    return _call(lambda: _get_client().xiaohongshu.get_account,
                 account_id=account_id, user_id=user_id)


@mcp.tool()
def xiaohongshu_get_work(work_id: Optional[str] = None,
                         work_link: Optional[str] = None) -> Dict[str, Any]:
    """获取小红书笔记详情（优质库）。work_id 与 work_link（笔记链接）至少传一个。"""
    return _call(lambda: _get_client().xiaohongshu.get_work,
                 work_id=work_id, work_link=work_link)


@mcp.tool()
def xiaohongshu_search_ai_articles(keyword: str, page_num: int = 1,
                                   page_size: int = 20,
                                   start_time: Optional[str] = None,
                                   end_time: Optional[str] = None,
                                   source: Optional[str] = None) -> Dict[str, Any]:
    """搜索小红书 AI 创作相关笔记（优质库）。keyword 必填；
    start_time/end_time 格式如 "2026-06-01 00:00:00"；source 为来源平台（可选）。"""
    return _call(lambda: _get_client().xiaohongshu.search_ai_articles,
                 keyword=keyword, page_num=page_num, page_size=page_size,
                 start_time=start_time, end_time=end_time, source=source)


# ─── 公众号 ──────────────────────────────────────────────


@mcp.tool()
def wechat_search_articles(keyword: str, offset: int = 0,
                           sort_type: Optional[str] = None) -> Dict[str, Any]:
    """搜索公众号文章（优质库）。keyword 必填；offset 从 0 开始、每页 +20。"""
    return _call(lambda: _get_client().wechat.search_articles,
                 keyword=keyword, offset=offset, sort_type=sort_type)


@mcp.tool()
def wechat_search_users(keyword: str, offset: int = 0,
                        sort_type: Optional[str] = None) -> Dict[str, Any]:
    """搜索公众号账号（优质库）。keyword 必填；sort_type：_0=默认，_2=最新，_4=最热。"""
    return _call(lambda: _get_client().wechat.search_users,
                 keyword=keyword, offset=offset, sort_type=sort_type)


@mcp.tool()
def wechat_get_account(account: str,
                       account_name: Optional[str] = None) -> Dict[str, Any]:
    """获取公众号账号信息（优质库）。account 为公众号微信号（必填），
    account_name 为公众号名称（可选）。"""
    return _call(lambda: _get_client().wechat.get_account,
                 account=account, account_name=account_name)


@mcp.tool()
def wechat_get_user_works(account: str, account_name: Optional[str] = None,
                          offset: int = 0, sort_type: Optional[str] = None,
                          publish_time_start: Optional[str] = None,
                          publish_time_end: Optional[str] = None) -> Dict[str, Any]:
    """获取公众号文章列表（优质库）。account 为公众号微信号（必填）；
    sort_type：_0=默认，_2=最新，_4=最热；publish_time_start/end 格式如 "2026-07-01"。"""
    return _call(lambda: _get_client().wechat.get_user_works,
                 account=account, account_name=account_name, offset=offset,
                 sort_type=sort_type, publish_time_start=publish_time_start,
                 publish_time_end=publish_time_end)


@mcp.tool()
def wechat_get_work(work_uuid: str) -> Dict[str, Any]:
    """根据作品 UUID 获取公众号文章元数据（优质库）。"""
    return _call(lambda: _get_client().wechat.get_work, work_uuid=work_uuid)


@mcp.tool()
def wechat_get_article_detail(url: str) -> Dict[str, Any]:
    """根据文章链接获取公众号文章详情，支持全文内容（优质库）。
    url 形如 https://mp.weixin.qq.com/s/..."""
    return _call(lambda: _get_client().wechat.get_article_detail, url=url)


@mcp.tool()
def wechat_search_ai_articles(keyword: str, page_num: int = 1, page_size: int = 20,
                              start_time: Optional[str] = None,
                              end_time: Optional[str] = None) -> Dict[str, Any]:
    """搜索公众号 AI 创作相关文章（优质库）。keyword 必填；
    start_time/end_time 格式如 "2026-06-01 00:00:00"。"""
    return _call(lambda: _get_client().wechat.search_ai_articles,
                 keyword=keyword, page_num=page_num, page_size=page_size,
                 start_time=start_time, end_time=end_time)


# ─── B 站 ────────────────────────────────────────────────


@mcp.tool()
def bilibili_search_articles(keyword: str, page: int = 1,
                             page_size: Optional[int] = None,
                             order: Optional[str] = None) -> Dict[str, Any]:
    """搜索 B 站视频（优质库）。keyword 必填；page 从 1 开始；page_size 默认 10、最大 50；
    order：time=发布时间 / play=播放数 / like=点赞数 / comment=评论数 / favorite=收藏数。"""
    return _call(lambda: _get_client().bilibili.search_articles,
                 keyword=keyword, page=page, page_size=page_size, order=order)


@mcp.tool()
def bilibili_search_users(keyword: str, page: int = 1,
                          page_size: Optional[int] = None,
                          order: Optional[str] = None) -> Dict[str, Any]:
    """搜索 B 站 UP 主（优质库）。keyword 必填；
    order：follower=粉丝数 / like=获赞数，默认按相关性。"""
    return _call(lambda: _get_client().bilibili.search_users,
                 keyword=keyword, page=page, page_size=page_size, order=order)


@mcp.tool()
def bilibili_get_account(mid: str) -> Dict[str, Any]:
    """获取 B 站 UP 主信息（优质库）。mid 为 B 站用户唯一 ID。"""
    return _call(lambda: _get_client().bilibili.get_account, mid=mid)


@mcp.tool()
def bilibili_get_user_works(mid: Optional[str] = None,
                            account_url: Optional[str] = None, page: int = 1,
                            page_size: Optional[int] = None,
                            order: Optional[str] = None) -> Dict[str, Any]:
    """获取 B 站 UP 主视频列表（优质库）。mid 与 account_url（主页链接）至少传一个；
    order：time=发布时间 / play=播放数 / like=点赞数。"""
    return _call(lambda: _get_client().bilibili.get_user_works,
                 mid=mid, account_url=account_url, page=page,
                 page_size=page_size, order=order)


@mcp.tool()
def bilibili_get_work(bvid: Optional[str] = None,
                      work_url: Optional[str] = None) -> Dict[str, Any]:
    """获取 B 站视频详情（优质库）。bvid 与 work_url 至少传一个，
    work_url 支持 bilibili.com/video/BVxxx 或 b23.tv 短链。"""
    return _call(lambda: _get_client().bilibili.get_work, bvid=bvid, work_url=work_url)


# ─── 今日头条 ────────────────────────────────────────────


@mcp.tool()
def toutiao_search_works(keyword: str, offset: int = 0) -> Dict[str, Any]:
    """搜索今日头条内容（实时）。keyword 必填；offset 翻页偏移从 0 开始、每页 +1。"""
    return _call(lambda: _get_client().toutiao.search_works, keyword=keyword, offset=offset)


@mcp.tool()
def toutiao_get_work(opus_id: str) -> Dict[str, Any]:
    """获取今日头条作品详情（实时）。opus_id 为作品 ID。"""
    return _call(lambda: _get_client().toutiao.get_work, opus_id=opus_id)


# ─── TikTok ──────────────────────────────────────────────


@mcp.tool()
def tiktok_search_users(keyword: str, cursor: int = 0,
                        rid: Optional[str] = None) -> Dict[str, Any]:
    """搜索 TikTok 账号。keyword 必填；cursor 翻页游标第一页为 0、每页 +10；
    rid 为上一页数据返回的 rid，翻页时传入。返回含 cursor/hasMore/userList。"""
    return _call(lambda: _get_client().tiktok.search_users,
                 keyword=keyword, cursor=cursor, rid=rid)


# ─── AI 搜索（自动轮询）──────────────────────────────────


@mcp.tool()
def ai_search_kimi(inquiry_text: str, timeout_seconds: int = 240) -> Dict[str, Any]:
    """Kimi 联网 AI 搜索，提交后自动等待并返回完整结果（含 content/webPages）。
    inquiry_text 为搜索提问文本；超时未完成时返回 taskId，可用 ai_search_kimi_result 再查。"""
    return _run_task(lambda: _get_client().ai_search.kimi_submit,
                     lambda: _get_client().ai_search.kimi_result,
                     timeout_seconds, inquiry_text=inquiry_text)


@mcp.tool()
def ai_search_doubao(inquiry_text: str, timeout_seconds: int = 240) -> Dict[str, Any]:
    """豆包联网 AI 搜索，提交后自动等待并返回完整结果。
    inquiry_text 为搜索提问文本；超时未完成时返回 taskId，可用 ai_search_doubao_result 再查。"""
    return _run_task(lambda: _get_client().ai_search.doubao_submit,
                     lambda: _get_client().ai_search.doubao_result,
                     timeout_seconds, inquiry_text=inquiry_text)


@mcp.tool()
def ai_search_deepseek(inquiry_text: str, timeout_seconds: int = 240) -> Dict[str, Any]:
    """Deepseek 联网 AI 搜索，提交后自动等待并返回完整结果。
    inquiry_text 为搜索提问文本；超时未完成时返回 taskId，可用 ai_search_deepseek_result 再查。"""
    return _run_task(lambda: _get_client().ai_search.deepseek_submit,
                     lambda: _get_client().ai_search.deepseek_result,
                     timeout_seconds, inquiry_text=inquiry_text)


@mcp.tool()
def ai_search_kimi_result(task_id: str) -> Dict[str, Any]:
    """查询 Kimi 搜索任务结果。仅在 ai_search_kimi 超时返回 taskId 后使用。"""
    return _call(lambda: _get_client().ai_search.kimi_result, task_id=task_id)


@mcp.tool()
def ai_search_doubao_result(task_id: str) -> Dict[str, Any]:
    """查询豆包搜索任务结果。仅在 ai_search_doubao 超时返回 taskId 后使用。"""
    return _call(lambda: _get_client().ai_search.doubao_result, task_id=task_id)


@mcp.tool()
def ai_search_deepseek_result(task_id: str) -> Dict[str, Any]:
    """查询 Deepseek 搜索任务结果。仅在 ai_search_deepseek 超时返回 taskId 后使用。"""
    return _call(lambda: _get_client().ai_search.deepseek_result, task_id=task_id)


# ─── AI 生成（自动轮询）──────────────────────────────────


@mcp.tool()
def gpt_image_generate(prompt: str, n: int = 1, size: str = "1024x1024",
                       quality: str = "medium", background: str = "auto",
                       output_format: str = "png",
                       output_compression: Optional[int] = None,
                       model_name: str = "gpt-image-2",
                       operation: str = "generate",
                       input_fidelity: Optional[str] = None,
                       images: Optional[List[Dict[str, str]]] = None,
                       timeout_seconds: int = 240) -> Dict[str, Any]:
    """GPT 图片生成（gpt-image-2），提交后自动等待并返回 imagePaths。
    operation：generate=文生图 / edit=图生图（edit 时 images 必填，
    形如 [{"url": "https://..."}]，input_fidelity 支持 high/low）；
    quality：low/medium/high/auto；background：transparent/opaque/auto；
    output_format：png/jpeg/webp。超时返回 taskId，可用 gpt_image_result 再查。"""
    return _run_task(lambda: _get_client().gpt_image.submit,
                     lambda: _get_client().gpt_image.result,
                     timeout_seconds, prompt=prompt, n=n, size=size, quality=quality,
                     background=background, output_format=output_format,
                     output_compression=output_compression, model_name=model_name,
                     operation=operation, input_fidelity=input_fidelity, images=images)


@mcp.tool()
def gpt_image_result(task_id: str) -> Dict[str, Any]:
    """查询 GPT 图片生成任务结果（含 status/imagePaths/failReason）。
    仅在 gpt_image_generate 超时返回 taskId 后使用。"""
    return _call(lambda: _get_client().gpt_image.result, task_id=task_id)


@mcp.tool()
def doubao_image_pro_generate(prompt: str, size: str = "2048x2048",
                              image: Optional[Any] = None,
                              output_format: str = "jpeg",
                              response_format: str = "url",
                              watermark: bool = True,
                              optimize_prompt: bool = False,
                              optimize_mode: str = "standard",
                              timeout_seconds: int = 240) -> Dict[str, Any]:
    """豆包 Seedream 5.0 Pro 图片生成，提交后自动等待结果。
    size 支持 "1K"/"2K" 或像素值如 "2048x2048"；image 为图生图输入（URL 或 Base64，
    可传单个字符串或字符串列表）；optimize_prompt 开启提示词优化（standard/fast）。
    超时返回 taskId，可用 doubao_image_pro_result 再查。"""
    return _run_task(lambda: _get_client().doubao_image.pro_submit,
                     lambda: _get_client().doubao_image.pro_result,
                     timeout_seconds, prompt=prompt, size=size, image=image,
                     output_format=output_format, response_format=response_format,
                     watermark=watermark, optimize_prompt=optimize_prompt,
                     optimize_mode=optimize_mode)


@mcp.tool()
def doubao_image_pro_result(task_id: str) -> Dict[str, Any]:
    """查询 Seedream 5.0 Pro 任务结果。仅在 doubao_image_pro_generate 超时返回 taskId 后使用。"""
    return _call(lambda: _get_client().doubao_image.pro_result, task_id=task_id)


@mcp.tool()
def doubao_image_lite_generate(prompt: str, size: str = "2048x2048",
                               image: Optional[Any] = None,
                               output_format: str = "jpeg",
                               response_format: str = "url",
                               watermark: bool = True,
                               sequential: str = "disabled",
                               max_images: int = 4,
                               optimize_prompt: bool = False,
                               optimize_mode: str = "standard",
                               timeout_seconds: int = 240) -> Dict[str, Any]:
    """豆包 Seedream 5.0 Lite 图片生成，支持组图，提交后自动等待结果。
    size 支持 "2K"/"3K"/"4K" 或像素值；sequential 设为 "auto" 时生成组图，
    max_images 控制组图数量（1~10）。超时返回 taskId，可用 doubao_image_lite_result 再查。"""
    return _run_task(lambda: _get_client().doubao_image.lite_submit,
                     lambda: _get_client().doubao_image.lite_result,
                     timeout_seconds, prompt=prompt, size=size, image=image,
                     output_format=output_format, response_format=response_format,
                     watermark=watermark, sequential=sequential, max_images=max_images,
                     optimize_prompt=optimize_prompt, optimize_mode=optimize_mode)


@mcp.tool()
def doubao_image_lite_result(task_id: str) -> Dict[str, Any]:
    """查询 Seedream 5.0 Lite 任务结果。仅在 doubao_image_lite_generate 超时返回 taskId 后使用。"""
    return _call(lambda: _get_client().doubao_image.lite_result, task_id=task_id)


@mcp.tool()
def doubao_video_generate(content: List[Dict[str, Any]],
                          model: Optional[str] = None,
                          resolution: str = "720p",
                          ratio: str = "adaptive",
                          duration: int = 5,
                          seed: int = -1,
                          watermark: bool = False,
                          generate_audio: bool = True,
                          return_last_frame: bool = False,
                          timeout_seconds: int = 480) -> Dict[str, Any]:
    """豆包 Seedance 2.0 视频生成，提交后自动等待结果。
    content 为输入内容列表（必填），每项形如：
    {"type": "text", "text": "描述文字"}；
    {"type": "image_url", "imageUrl": "图片URL", "imageRole": "first_frame/reference_image"}；
    {"type": "video_url", "videoUrl": "视频URL", "videoRole": "reference_video"}；
    {"type": "audio_url", "audioUrl": "音频URL", "audioRole": "reference_audio"}。
    resolution：480p/720p/1080p；ratio：adaptive/16:9/4:3/1:1/3:4/9:16/21:9；
    duration 秒数 [4,15] 或 -1 智能。超时返回 taskId，可用 doubao_video_result 再查。"""
    return _run_task(lambda: _get_client().doubao_video.submit,
                     lambda: _get_client().doubao_video.result,
                     timeout_seconds, content=content, model=model,
                     resolution=resolution, ratio=ratio, duration=duration,
                     seed=seed, watermark=watermark, generate_audio=generate_audio,
                     return_last_frame=return_last_frame)


@mcp.tool()
def doubao_video_result(task_id: str) -> Dict[str, Any]:
    """查询豆包视频生成任务结果。仅在 doubao_video_generate 超时返回 taskId 后使用。"""
    return _call(lambda: _get_client().doubao_video.result, task_id=task_id)


def main() -> None:
    """以 stdio transport 启动 MCP server"""
    mcp.run()


if __name__ == "__main__":
    main()
