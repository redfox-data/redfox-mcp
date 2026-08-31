"""RedFox 微信视频号数据 MCP Server

将 RedFoxHub（红狐数据平台）的微信视频号数据 API 暴露为 MCP 工具。

认证：stdio 模式读环境变量 REDFOX_API_KEY；HTTP 模式从请求头
X-API-Key（或 Authorization: Bearer <key>）取 key。
获取地址 https://redfox.hk/settings/api-keys?source=mcp
"""

from typing import Any, Dict, Optional

from redfox_mcp_core import call, create_server, get_client, run_task, serve

from redfox_wechat_channels_mcp import __version__

mcp = create_server("redfox-wechat-channels", __version__)


@mcp.tool()
def wechat_channels_search_works(keyword: str, sort: Optional[str] = None,
                                 page: int = 1, size: int = 20) -> Dict[str, Any]:
    """微信视频号关键词搜索作品。keyword 必填；
    sort：最新/最多点赞/最多收藏/综合；page 从 1 开始。"""
    return call(lambda: get_client().wechat_channels.search_works,
                keyword=keyword, sort=sort, page=page, size=size)


@mcp.tool()
def wechat_channels_get_work(video_id: str) -> Dict[str, Any]:
    """获取微信视频号单个作品详情。video_id 为作品 ID（必填）。"""
    return call(lambda: get_client().wechat_channels.get_work, video_id=video_id)


@mcp.tool()
def wechat_channels_get_user_works(nickname: str, page: int = 1,
                                   size: int = 20) -> Dict[str, Any]:
    """获取微信视频号用户作品列表。nickname 为用户昵称（必填）；page 从 1 开始。"""
    return call(lambda: get_client().wechat_channels.get_user_works,
                nickname=nickname, page=page, size=size)


@mcp.tool()
def wechat_channels_get_work_by_link(url: str) -> Dict[str, Any]:
    """通过链接获取微信视频号作品详情。url 为作品链接（必填）。"""
    return call(lambda: get_client().wechat_channels.get_work_by_link, url=url)


@mcp.tool()
def wechat_channels_search_users(account_name: str, page: int = 1,
                                 page_size: int = 20) -> Dict[str, Any]:
    """微信视频号关键词搜索账号。account_name 为搜索关键词（必填）。"""
    return call(lambda: get_client().wechat_channels.search_users,
                account_name=account_name, page=page, page_size=page_size)


@mcp.tool()
def wechat_channels_transcript(url: str, timeout_seconds: int = 240) -> Dict[str, Any]:
    """微信视频号视频字幕/文案提取，提交后自动等待并返回完整文案。
    url 为作品链接（必填）；超时未完成时返回 taskId，可用 wechat_channels_transcript_result 再查。"""
    return run_task(lambda: get_client().wechat_channels.transcript_submit,
                    lambda: get_client().wechat_channels.transcript_result,
                    timeout_seconds, url=url)


@mcp.tool()
def wechat_channels_transcript_result(task_id: str) -> Dict[str, Any]:
    """查询微信视频号字幕提取任务结果。仅在 wechat_channels_transcript 超时返回 taskId 后使用。"""
    return call(lambda: get_client().wechat_channels.transcript_result, task_id=task_id)


def main() -> None:
    serve(mcp, prog="redfox-wechat-channels-mcp",
          description="RedFox 微信视频号 MCP server")


if __name__ == "__main__":
    main()
