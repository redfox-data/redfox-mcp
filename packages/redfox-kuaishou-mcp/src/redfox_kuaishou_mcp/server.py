"""RedFox 快手数据 MCP Server

将 RedFoxHub（红狐数据平台）的快手数据 API 暴露为 MCP 工具。

认证：stdio 模式读环境变量 REDFOX_API_KEY；HTTP 模式从请求头
REDFOX_API_KEY（或 Authorization: Bearer <key>）取 key。
获取地址 https://redfox.hk/settings/api-keys?source=mcp
"""

from typing import Any, Dict, Optional

from redfox_mcp_core import call, create_server, get_client, serve

from redfox_kuaishou_mcp import __version__

mcp = create_server("redfox-kuaishou", __version__)


@mcp.tool()
def kuaishou_search_works(keyword: str, page: int = 1, size: int = 20,
                          sort: str = "综合") -> Dict[str, Any]:
    """快手关键词搜索作品。keyword 必填；page 从 1 开始；
    sort：综合/最新/最热。"""
    return call(lambda: get_client().kuaishou.search_works,
                keyword=keyword, page=page, size=size, sort=sort, source="快手关键词搜索作品-MCP")


@mcp.tool()
def kuaishou_get_work(photo_id: str) -> Dict[str, Any]:
    """获取快手单个作品详情。photo_id 为作品 ID（必填）。"""
    return call(lambda: get_client().kuaishou.get_work, photo_id=photo_id, source="获取快手单个作品详情-MCP")


@mcp.tool()
def kuaishou_get_user_works(kwai_id: Optional[str] = None,
                            three_x_id: Optional[str] = None,
                            page: int = 1, size: int = 20) -> Dict[str, Any]:
    """获取快手用户作品列表。kwai_id 与 three_x_id 至少传一个。"""
    return call(lambda: get_client().kuaishou.get_user_works,
                kwai_id=kwai_id, three_x_id=three_x_id, page=page, size=size, source="获取快手用户作品列表-MCP")


@mcp.tool()
def kuaishou_search_users(account_name: str, page: int = 1,
                          page_size: int = 20) -> Dict[str, Any]:
    """快手关键词搜索账号。account_name 为搜索关键词（必填）。"""
    return call(lambda: get_client().kuaishou.search_users,
                account_name=account_name, page=page, page_size=page_size, source="快手关键词搜索账号-MCP")


@mcp.tool()
def kuaishou_transcript(url: str, timeout_seconds: Optional[int] = None) -> Dict[str, Any]:
    """提交快手视频字幕/文案提取任务，立即返回 taskId，不自动查询结果。
    url 为作品链接（必填）。请稍后用 kuaishou_transcript_result(task_id)
    自行查询结果。timeout_seconds 为可选参数，可传可不传，传与不传都不影响本调用
    （本工具只提交任务、不自动轮询结果）。"""
    return call(lambda: get_client().kuaishou.transcript_submit,
                url=url, source="快手视频字幕/文案提取-MCP")


@mcp.tool()
def kuaishou_transcript_result(task_id: str) -> Dict[str, Any]:
    """查询快手字幕提取任务结果。传 kuaishou_transcript 提交返回的 taskId。"""
    return call(lambda: get_client().kuaishou.transcript_result, task_id=task_id, source="查询快手字幕提取任务结果-MCP")


def main() -> None:
    serve(mcp, prog="redfox-kuaishou-mcp", description="RedFox 快手 MCP server")


if __name__ == "__main__":
    main()
