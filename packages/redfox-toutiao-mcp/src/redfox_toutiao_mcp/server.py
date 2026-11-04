"""RedFox 今日头条数据 MCP Server

将 RedFoxHub（红狐数据平台）的今日头条数据 API 暴露为 MCP 工具。

认证：stdio 模式读环境变量 REDFOX_API_KEY；HTTP 模式从请求头
REDFOX_API_KEY（或 Authorization: Bearer <key>）取 key。
获取地址 https://redfox.hk/settings/api-keys?source=mcp
"""

from typing import Annotated, Any, Dict, Optional
from pydantic import Field

from redfox_mcp_core import call, create_server, get_client, serve

from redfox_toutiao_mcp import __version__

mcp = create_server("redfox-toutiao", __version__)


@mcp.tool()
def toutiao_search_works(keyword: Annotated[str, Field(description="（必填，搜索关键词），[必填]，示例: 羽绒服")], offset: Annotated[int, Field(description="（必填，翻页偏移量，从0开始，每页+1），[可选]，示例: 0")] = 0) -> Dict[str, Any]:
    """搜索今日头条内容（实时）。keyword 必填；offset 翻页偏移从 0 开始、每页 +1。

接口: POST /story/api/toutiao/searchWork"""
    return call(lambda: get_client().toutiao.search_works, keyword=keyword, offset=offset, source="搜索今日头条内容-MCP")


@mcp.tool()
def toutiao_get_work(opus_id: Annotated[str, Field(description="（必填，作品ID），[必填]，示例: 7657068025711051306")]) -> Dict[str, Any]:
    """获取今日头条作品详情（实时）。opus_id 为作品 ID。

接口: POST /story/api/toutiao/workDetail"""
    return call(lambda: get_client().toutiao.get_work, opus_id=opus_id, source="获取今日头条作品详情-MCP")


@mcp.tool()
def toutiao_get_comments(opus_id: Annotated[str, Field(description="作品ID，[必填]，示例: 7667285947545731584")], offset: Annotated[Optional[str], Field(description="翻页偏移量，[可选]，示例: 0")] = None) -> Dict[str, Any]:
    """获取今日头条作品评论（实时）。opus_id 为作品 ID（必填）；offset 为翻页偏移量。

接口: POST /story/api/toutiao/workComment"""
    return call(lambda: get_client().toutiao.get_comments, opus_id=opus_id, offset=offset, source="获取今日头条作品评论-MCP")


@mcp.tool()
def toutiao_search_users(name: Annotated[str, Field(description="搜索关键词，[必填]，示例: 南浔")], offset: Annotated[Optional[str], Field(description="翻页偏移量，hasMore为1时使用返回的offset，[可选]，示例: 0")] = None,
                         search_id: Annotated[Optional[str], Field(description="搜索ID，hasMore为1时使用返回的searchId，[可选]")] = None) -> Dict[str, Any]:
    """今日头条关键词搜索账号（实时）。name 为搜索关键词（必填）；
    hasMore 为 1 时使用返回的 offset 与 searchId 翻页。

接口: POST /story/api/toutiao/searchAccount"""
    return call(lambda: get_client().toutiao.search_users,
                name=name, offset=offset, search_id=search_id, source="今日头条关键词搜索账号-MCP")


@mcp.tool()
def toutiao_get_user_works(category: Annotated[str, Field(description="内容分类（必填） profile_all 全部；pc_profile_article 文章；pc_profile_video 视频； pc_profile_ugc 微头条；profile_wenda 问答；pc_profile_short_video 小视频，[必填]，示例: profile_all")], token: Annotated[str, Field(description="web端uid（必填） 从账号主页 https://www.toutiao.com/c/user/token/MS4wLjABAAAAiAce5qhH31TeuB3UdpFMV8u-uwy2LnoiqI10uZHqAt8/ 中获取，[必填]，示例: MS4wLjABAAAA3KU9ifwN12G41E6PJRpZgIfzVrXWQ4WPF66ns54c0uw")]) -> Dict[str, Any]:
    """获取今日头条账号作品列表（实时）。
    category：profile_all=全部 / pc_profile_article=文章 / pc_profile_video=视频
    / pc_profile_ugc=微头条 / profile_wenda=问答 / pc_profile_short_video=小视频；
    token 为 web 端 uid（必填）。

接口: POST /story/api/toutiao/userWorkList"""
    return call(lambda: get_client().toutiao.get_user_works,
                category=category, token=token, source="获取今日头条账号作品列表-MCP")


def main() -> None:
    serve(mcp, prog="redfox-toutiao-mcp", description="RedFox 今日头条数据 MCP server")


if __name__ == "__main__":
    main()
