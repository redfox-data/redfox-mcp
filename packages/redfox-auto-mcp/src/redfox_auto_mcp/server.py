"""RedFox 汽车垂类数据 MCP Server

将 RedFoxHub（红狐数据平台）的汽车垂类数据 API 暴露为 MCP 工具，
聚合懂车帝、汽车之家、易车三个平台。

认证：stdio 模式读环境变量 REDFOX_API_KEY；HTTP 模式从请求头
REDFOX_API_KEY（或 Authorization: Bearer <key>）取 key。
获取地址 https://redfox.hk/settings/api-keys?source=mcp
"""

from typing import Annotated, Any, Dict, Optional
from pydantic import Field

from redfox_mcp_core import call, create_server, get_client, serve

from redfox_auto_mcp import __version__

mcp = create_server("redfox-auto", __version__)


# ─── 懂车帝 ──────────────────────────────────────────────

@mcp.tool()
def dongchedi_search_works(keyword: Annotated[str, Field(description="搜索关键词 不支持采用空格/逗号等方式一次输入多个关键词，[必填]，示例: 智界")], offset: Annotated[str, Field(description="翻页偏移量，从0开始，翻页+20，[可选]，示例: 0")] = "0",
                           source_type: Annotated[str, Field(description="内容类型：1=综合，2=视频，[可选]，示例: 1")] = "1") -> Dict[str, Any]:
    """懂车帝关键词搜索作品。keyword 必填；
    source_type：1=综合 / 2=视频。

接口: POST /story/api/dongchedi/searchWork"""
    return call(lambda: get_client().dongchedi.search_works,
                keyword=keyword, offset=offset, source_type=source_type, source="懂车帝关键词搜索作品-MCP")


@mcp.tool()
def dongchedi_get_work(work_id: Annotated[str, Field(description="懂车帝作品ID，[必填]，示例: 7677400278014149145")], work_type: Annotated[str, Field(description="作品类型：video=视频，article=图文，[必填]，示例: video")]) -> Dict[str, Any]:
    """获取懂车帝作品详情。work_id 为作品 ID（必填）；work_type：video/article。

接口: POST /story/api/dongchedi/workDetail"""
    return call(lambda: get_client().dongchedi.get_work,
                work_id=work_id, work_type=work_type, source="获取懂车帝作品详情-MCP")


@mcp.tool()
def dongchedi_get_user_works(user_id: str, cursor: int = 0) -> Dict[str, Any]:
    """获取懂车帝用户作品列表。user_id 为用户 ID（必填）；cursor 翻页游标。"""
    return call(lambda: get_client().dongchedi.get_user_works,
                user_id=user_id, cursor=cursor, source="获取懂车帝用户作品列表-MCP")


@mcp.tool()
def dongchedi_search_users(keyword: Annotated[str, Field(description="搜索关键词，[必填]，示例: 小米")], offset: Annotated[int, Field(description="偏移量，从0开始，[可选]，示例: 0")] = 0) -> Dict[str, Any]:
    """懂车帝关键词搜索账号。keyword 必填；offset 翻页偏移。

接口: POST /story/api/dongchedi/searchUser"""
    return call(lambda: get_client().dongchedi.search_users,
                keyword=keyword, offset=offset, source="懂车帝关键词搜索账号-MCP")


# ─── 汽车之家 ────────────────────────────────────────────

@mcp.tool()
def autohome_search_works(keyword: Annotated[str, Field(description="搜索关键词，[必填]，示例: 智界")], offset: Annotated[str, Field(description="翻页偏移量，从0开始，翻页+10，[可选]，示例: 0")] = "0", page: Annotated[str, Field(description="页码，从1开始，翻页+1，[可选]，示例: 1")] = "1",
                          source_type: Annotated[str, Field(description="内容类型：club / article / video，[可选]，示例: video")] = "video") -> Dict[str, Any]:
    """汽车之家关键词搜索作品。keyword 必填；
    source_type：club=论坛 / article=文章 / video=视频。

接口: POST /story/api/autohome/searchWork"""
    return call(lambda: get_client().autohome.search_works,
                keyword=keyword, offset=offset, page=page, source_type=source_type, source="汽车之家关键词搜索作品-MCP")


@mcp.tool()
def autohome_get_article(work_id: Annotated[str, Field(description="作品ID，[必填]，示例: 2259992")], page: Annotated[int, Field(description="[可选]，示例: 0")] = 0) -> Dict[str, Any]:
    """获取汽车之家文章详情。work_id 为文章 ID（必填）；page 用于长文章分页。

接口: POST /story/api/autohome/articleDetail"""
    return call(lambda: get_client().autohome.get_article,
                work_id=work_id, page=page, source="获取汽车之家文章详情-MCP")


@mcp.tool()
def autohome_get_video(video_id: Annotated[str, Field(description="视频ID，[必填]，示例: 26280540")], video_type: Annotated[str, Field(description="视频类型：0=原创账号，4=车家号，[必填]，示例: 4")]) -> Dict[str, Any]:
    """获取汽车之家视频详情。video_id 为视频 ID（必填）；
    video_type：0=原创 / 4=车家号。

接口: POST /story/api/autohome/videoDetail"""
    return call(lambda: get_client().autohome.get_video,
                video_id=video_id, video_type=video_type, source="获取汽车之家视频详情-MCP")


@mcp.tool()
def autohome_get_user_works(author_id: Annotated[str, Field(description="作者ID，[必填]，示例: 19996353")], page: Annotated[int, Field(description="[可选]，示例: 0")] = 0) -> Dict[str, Any]:
    """获取汽车之家作者作品列表。author_id 为作者 ID（必填）；page 翻页页码。

接口: POST /story/api/autohome/workList"""
    return call(lambda: get_client().autohome.get_user_works,
                author_id=author_id, page=page, source="获取汽车之家作者作品列表-MCP")


# ─── 易车 ────────────────────────────────────────────────

@mcp.tool()
def yiche_search_works(keyword: Annotated[str, Field(description="搜索关键词，[必填]，示例: 极氪")], page: Annotated[int, Field(description="页码，从1开始，翻页+1，[可选]，示例: 1")] = 1,
                       source_type: Annotated[str, Field(description="内容类型 club：社区；shipin：视频；xinwen：文章，[可选]，示例: xinwen")] = "xinwen") -> Dict[str, Any]:
    """易车关键词搜索作品。keyword 必填；
    source_type：club=社区 / shipin=视频 / xinwen=文章。

接口: POST /story/api/yiche/searchWork"""
    return call(lambda: get_client().yiche.search_works,
                keyword=keyword, page=page, source_type=source_type, source="易车关键词搜索作品-MCP")


@mcp.tool()
def yiche_get_article(url: str) -> Dict[str, Any]:
    """获取易车文章详情。url 为文章 URL（必填）。"""
    return call(lambda: get_client().yiche.get_article, url=url, source="获取易车文章详情-MCP")


@mcp.tool()
def yiche_get_video(work_id: Annotated[str, Field(description="易车视频作品ID，[必填]，示例: 12710581")]) -> Dict[str, Any]:
    """获取易车视频详情。work_id 为易车视频作品 ID（必填）。

接口: POST /story/api/yiche/videoDetail"""
    return call(lambda: get_client().yiche.get_video, work_id=work_id, source="获取易车视频详情-MCP")


@mcp.tool()
def yiche_get_user_works(user_id: Annotated[str, Field(description="用户ID，[必填]，示例: 16670166")],
                         timestamp: Annotated[Optional[str], Field(description="时间戳，第一页不传，翻页传前一页返回的最后一条的publishTime，[可选]")] = None) -> Dict[str, Any]:
    """获取易车用户作品列表。user_id 为用户 ID（必填）；
    timestamp 第一页不传，翻页传前一页返回的最后一条的 publishTime。

接口: POST /story/api/yiche/workList"""
    return call(lambda: get_client().yiche.get_user_works,
                user_id=user_id, timestamp=timestamp, source="获取易车用户作品列表-MCP")


@mcp.tool()
def yiche_search_users(keyword: Annotated[str, Field(description="搜索关键词，[必填]，示例: 极氪")], page: Annotated[int, Field(description="页码，从1开始，[可选]，示例: 1")] = 1) -> Dict[str, Any]:
    """易车关键词搜索账号。keyword 必填；page 从 1 开始。

接口: POST /story/api/yiche/searchAccount"""
    return call(lambda: get_client().yiche.search_users,
                keyword=keyword, page=page, source="易车关键词搜索账号-MCP")


def main() -> None:
    serve(mcp, prog="redfox-auto-mcp", description="RedFox 汽车垂类 MCP server")


if __name__ == "__main__":
    main()
