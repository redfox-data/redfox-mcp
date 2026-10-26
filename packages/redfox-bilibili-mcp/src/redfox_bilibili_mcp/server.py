"""RedFox B 站数据 MCP Server

将 RedFoxHub（红狐数据平台）的 B 站数据 API 暴露为 MCP 工具。

认证：stdio 模式读环境变量 REDFOX_API_KEY；HTTP 模式从请求头
REDFOX_API_KEY（或 Authorization: Bearer <key>）取 key。
获取地址 https://redfox.hk/settings/api-keys?source=mcp
"""

from typing import Any, Dict, Optional

from redfox_mcp_core import call, create_server, get_client, serve

from redfox_bilibili_mcp import __version__

mcp = create_server("redfox-bilibili", __version__)


@mcp.tool()
def bilibili_search_articles(keyword: str, page: int = 1,
                             page_size: Optional[int] = None,
                             order: Optional[str] = None) -> Dict[str, Any]:
    """搜索 B 站视频（优质库）。keyword 必填；page 从 1 开始；page_size 默认 10、最大 50；
    order：time=发布时间 / play=播放数 / like=点赞数 / comment=评论数 / favorite=收藏数。"""
    return call(lambda: get_client().bilibili.search_articles,
                keyword=keyword, page=page, page_size=page_size, order=order, source="搜索 B 站视频-MCP")


@mcp.tool()
def bilibili_search_users(keyword: str, page: int = 1,
                          page_size: Optional[int] = None,
                          order: Optional[str] = None) -> Dict[str, Any]:
    """搜索 B 站 UP 主（优质库）。keyword 必填；
    order：follower=粉丝数 / like=获赞数，默认按相关性。"""
    return call(lambda: get_client().bilibili.search_users,
                keyword=keyword, page=page, page_size=page_size, order=order, source="搜索 B 站 UP 主-MCP")


@mcp.tool()
def bilibili_get_account(mid: str) -> Dict[str, Any]:
    """获取 B 站 UP 主信息（优质库）。mid 为 B 站用户唯一 ID。"""
    return call(lambda: get_client().bilibili.get_account, mid=mid, source="获取 B 站 UP 主信息-MCP")


@mcp.tool()
def bilibili_get_user_works(mid: Optional[str] = None,
                            account_url: Optional[str] = None, page: int = 1,
                            page_size: Optional[int] = None,
                            order: Optional[str] = None) -> Dict[str, Any]:
    """获取 B 站 UP 主视频列表（优质库）。mid 与 account_url（主页链接）至少传一个；
    order：time=发布时间 / play=播放数 / like=点赞数。"""
    return call(lambda: get_client().bilibili.get_user_works,
                mid=mid, account_url=account_url, page=page,
                page_size=page_size, order=order, source="获取 B 站 UP 主视频列表-MCP")


@mcp.tool()
def bilibili_get_work(bvid: Optional[str] = None,
                      work_url: Optional[str] = None) -> Dict[str, Any]:
    """获取 B 站视频详情（优质库）。bvid 与 work_url 至少传一个，
    work_url 支持 bilibili.com/video/BVxxx 或 b23.tv 短链。"""
    return call(lambda: get_client().bilibili.get_work, bvid=bvid, work_url=work_url, source="获取 B 站视频详情-MCP")


@mcp.tool()
def bilibili_get_audio(url: str) -> Dict[str, Any]:
    """获取 B 站视频音频地址。url 为 B 站作品链接（必填）。"""
    return call(lambda: get_client().bilibili.get_audio, url=url, source="获取 B 站视频音频地址-MCP")


@mcp.tool()
def bilibili_transcript(url: str, timeout_seconds: Optional[int] = None) -> Dict[str, Any]:
    """提交 B 站视频字幕/文案提取任务，立即返回 taskId，不自动查询结果。
    url 为作品链接（必填）。请稍后用 bilibili_transcript_result(task_id)
    自行查询结果。timeout_seconds 为可选参数，可传可不传，传与不传都不影响本调用
    （本工具只提交任务、不自动轮询结果）。"""
    return call(lambda: get_client().bilibili.transcript_submit,
                url=url, source="B 站视频字幕/文案提取-MCP")


@mcp.tool()
def bilibili_transcript_result(task_id: str) -> Dict[str, Any]:
    """查询 B 站字幕提取任务结果。传 bilibili_transcript 提交返回的 taskId。"""
    return call(lambda: get_client().bilibili.transcript_result, task_id=task_id, source="查询 B 站字幕提取任务结果-MCP")


def main() -> None:
    serve(mcp, prog="redfox-bilibili-mcp", description="RedFox B 站数据 MCP server")


if __name__ == "__main__":
    main()
