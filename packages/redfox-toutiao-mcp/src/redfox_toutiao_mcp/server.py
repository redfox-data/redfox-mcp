"""RedFox 今日头条数据 MCP Server

将 RedFoxHub（红狐数据平台）的今日头条数据 API 暴露为 MCP 工具。

认证：stdio 模式读环境变量 REDFOX_API_KEY；HTTP 模式从请求头
X-API-Key（或 Authorization: Bearer <key>）取 key。
获取地址 https://redfox.hk/settings/api-keys?source=mcp
"""

from typing import Any, Dict

from redfox_mcp_core import call, create_server, get_client, serve

from redfox_toutiao_mcp import __version__

mcp = create_server("redfox-toutiao", __version__)


@mcp.tool()
def toutiao_search_works(keyword: str, offset: int = 0) -> Dict[str, Any]:
    """搜索今日头条内容（实时）。keyword 必填；offset 翻页偏移从 0 开始、每页 +1。"""
    return call(lambda: get_client().toutiao.search_works, keyword=keyword, offset=offset)


@mcp.tool()
def toutiao_get_work(opus_id: str) -> Dict[str, Any]:
    """获取今日头条作品详情（实时）。opus_id 为作品 ID。"""
    return call(lambda: get_client().toutiao.get_work, opus_id=opus_id)


def main() -> None:
    serve(mcp, prog="redfox-toutiao-mcp", description="RedFox 今日头条数据 MCP server")


if __name__ == "__main__":
    main()
