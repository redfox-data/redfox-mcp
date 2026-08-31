"""RedFox 汽车垂类数据 MCP Server

将 RedFoxHub（红狐数据平台）的汽车垂类数据 API 暴露为 MCP 工具，
聚合懂车帝、汽车之家、易车三个平台。

认证：stdio 模式读环境变量 REDFOX_API_KEY；HTTP 模式从请求头
X-API-Key（或 Authorization: Bearer <key>）取 key。
获取地址 https://redfox.hk/settings/api-keys?source=mcp
"""

from typing import Any, Dict, Optional

from redfox_mcp_core import call, create_server, get_client, serve

from redfox_auto_mcp import __version__

mcp = create_server("redfox-auto", __version__)


# ─── 懂车帝 ──────────────────────────────────────────────

@mcp.tool()
def dongchedi_search_works(keyword: str, offset: str = "0",
                           source_type: str = "1") -> Dict[str, Any]:
    """懂车帝关键词搜索作品。keyword 必填；
    source_type：1=综合 / 2=视频。"""
    return call(lambda: get_client().dongchedi.search_works,
                keyword=keyword, offset=offset, source_type=source_type)


@mcp.tool()
def dongchedi_get_work(work_id: str, work_type: str) -> Dict[str, Any]:
    """获取懂车帝作品详情。work_id 为作品 ID（必填）；work_type：video/article。"""
    return call(lambda: get_client().dongchedi.get_work,
                work_id=work_id, work_type=work_type)


@mcp.tool()
def dongchedi_get_user_works(user_id: str, cursor: int = 0) -> Dict[str, Any]:
    """获取懂车帝用户作品列表。user_id 为用户 ID（必填）；cursor 翻页游标。"""
    return call(lambda: get_client().dongchedi.get_user_works,
                user_id=user_id, cursor=cursor)


@mcp.tool()
def dongchedi_search_users(keyword: str, offset: int = 0) -> Dict[str, Any]:
    """懂车帝关键词搜索账号。keyword 必填；offset 翻页偏移。"""
    return call(lambda: get_client().dongchedi.search_users,
                keyword=keyword, offset=offset)


# ─── 汽车之家 ────────────────────────────────────────────

@mcp.tool()
def autohome_search_works(keyword: str, offset: str = "0", page: str = "1",
                          source_type: str = "video") -> Dict[str, Any]:
    """汽车之家关键词搜索作品。keyword 必填；
    source_type：club=论坛 / article=文章 / video=视频。"""
    return call(lambda: get_client().autohome.search_works,
                keyword=keyword, offset=offset, page=page, source_type=source_type)


@mcp.tool()
def autohome_get_article(work_id: str, page: int = 0) -> Dict[str, Any]:
    """获取汽车之家文章详情。work_id 为文章 ID（必填）；page 用于长文章分页。"""
    return call(lambda: get_client().autohome.get_article,
                work_id=work_id, page=page)


@mcp.tool()
def autohome_get_video(video_id: str, video_type: str) -> Dict[str, Any]:
    """获取汽车之家视频详情。video_id 为视频 ID（必填）；
    video_type：0=原创 / 4=车家号。"""
    return call(lambda: get_client().autohome.get_video,
                video_id=video_id, video_type=video_type)


@mcp.tool()
def autohome_get_user_works(author_id: str, page: int = 0) -> Dict[str, Any]:
    """获取汽车之家作者作品列表。author_id 为作者 ID（必填）；page 翻页页码。"""
    return call(lambda: get_client().autohome.get_user_works,
                author_id=author_id, page=page)


# ─── 易车 ────────────────────────────────────────────────

@mcp.tool()
def yiche_search_works(keyword: str, page: int = 1,
                       source_type: str = "xinwen") -> Dict[str, Any]:
    """易车关键词搜索作品。keyword 必填；
    source_type：club=社区 / shipin=视频 / xinwen=文章。"""
    return call(lambda: get_client().yiche.search_works,
                keyword=keyword, page=page, source_type=source_type)


@mcp.tool()
def yiche_get_article(url: str) -> Dict[str, Any]:
    """获取易车文章详情。url 为文章 URL（必填）。"""
    return call(lambda: get_client().yiche.get_article, url=url)


@mcp.tool()
def yiche_get_video(work_id: str) -> Dict[str, Any]:
    """获取易车视频详情。work_id 为易车视频作品 ID（必填）。"""
    return call(lambda: get_client().yiche.get_video, work_id=work_id)


@mcp.tool()
def yiche_get_user_works(user_id: str,
                         timestamp: Optional[str] = None) -> Dict[str, Any]:
    """获取易车用户作品列表。user_id 为用户 ID（必填）；
    timestamp 第一页不传，翻页传前一页返回的最后一条的 publishTime。"""
    return call(lambda: get_client().yiche.get_user_works,
                user_id=user_id, timestamp=timestamp)


@mcp.tool()
def yiche_search_users(keyword: str, page: int = 1) -> Dict[str, Any]:
    """易车关键词搜索账号。keyword 必填；page 从 1 开始。"""
    return call(lambda: get_client().yiche.search_users,
                keyword=keyword, page=page)


def main() -> None:
    serve(mcp, prog="redfox-auto-mcp", description="RedFox 汽车垂类 MCP server")


if __name__ == "__main__":
    main()
