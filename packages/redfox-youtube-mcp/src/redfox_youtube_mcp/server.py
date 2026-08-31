"""RedFox YouTube 数据 MCP Server

将 RedFoxHub（红狐数据平台）的 YouTube 数据 API 暴露为 MCP 工具。

认证：stdio 模式读环境变量 REDFOX_API_KEY；HTTP 模式从请求头
X-API-Key（或 Authorization: Bearer <key>）取 key。
获取地址 https://redfox.hk/settings/api-keys?source=mcp
"""

from typing import Any, Dict, Optional

from redfox_mcp_core import call, create_server, get_client, serve

from redfox_youtube_mcp import __version__

mcp = create_server("redfox-youtube", __version__)


@mcp.tool()
def youtube_search_videos(search_query: str,
                          continuation_token: Optional[str] = None) -> Dict[str, Any]:
    """YouTube 关键词视频搜索。search_query 必填；continuation_token 用于翻页。"""
    return call(lambda: get_client().youtube.search_videos,
                search_query=search_query, continuation_token=continuation_token)


@mcp.tool()
def youtube_get_video(video_id: str) -> Dict[str, Any]:
    """获取 YouTube 单个视频详情。video_id 为视频 ID（必填）。"""
    return call(lambda: get_client().youtube.get_video, video_id=video_id)


@mcp.tool()
def youtube_get_comments(video_id: str, language_code: Optional[str] = None,
                         country_code: Optional[str] = None,
                         sort_by: Optional[str] = None,
                         continuation_token: Optional[str] = None) -> Dict[str, Any]:
    """获取 YouTube 视频评论。video_id 必填；sort_by：top=最热/newest=最新；
    continuation_token 用于翻页。"""
    return call(lambda: get_client().youtube.get_comments,
                video_id=video_id, language_code=language_code,
                country_code=country_code, sort_by=sort_by,
                continuation_token=continuation_token)


@mcp.tool()
def youtube_get_transcript(video_url: str, format: Optional[str] = None,
                           include_timestamp: Optional[bool] = None,
                           send_metadata: Optional[bool] = None,
                           language: Optional[str] = None) -> Dict[str, Any]:
    """提取 YouTube 视频字幕/文案。video_url 为视频链接（必填）；
    format：text/srt/vtt/json3；include_timestamp 是否带时间戳；
    language 指定语言代码（如 zh/en）。"""
    return call(lambda: get_client().youtube.get_transcript,
                video_url=video_url, format=format,
                include_timestamp=include_timestamp,
                send_metadata=send_metadata, language=language)


def main() -> None:
    serve(mcp, prog="redfox-youtube-mcp", description="RedFox YouTube MCP server")


if __name__ == "__main__":
    main()
