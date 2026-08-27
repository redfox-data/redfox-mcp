"""RedFox 小红书数据 MCP Server

将 RedFoxHub（红狐数据平台）的小红书数据 API 暴露为 MCP 工具。

认证：stdio 模式读环境变量 REDFOX_API_KEY；HTTP 模式从请求头
X-API-Key（或 Authorization: Bearer <key>）取 key。
获取地址 https://redfox.hk/settings/api-keys?source=mcp
"""

from typing import Any, Dict, Optional

from redfox_mcp_core import call, create_server, get_client, serve

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


def main() -> None:
    serve(mcp, prog="redfox-xiaohongshu-mcp", description="RedFox 小红书数据 MCP server")


if __name__ == "__main__":
    main()
