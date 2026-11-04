"""RedFox YouTube 数据 MCP Server

将 RedFoxHub（红狐数据平台）的 YouTube 数据 API 暴露为 MCP 工具。

认证：stdio 模式读环境变量 REDFOX_API_KEY；HTTP 模式从请求头
REDFOX_API_KEY（或 Authorization: Bearer <key>）取 key。
获取地址 https://redfox.hk/settings/api-keys?source=mcp
"""

from typing import Annotated, Any, Dict, Optional
from pydantic import Field

from redfox_mcp_core import call, create_server, get_client, serve

from redfox_youtube_mcp import __version__

mcp = create_server("redfox-youtube", __version__)


@mcp.tool()
def youtube_search_videos(search_query: Annotated[str, Field(description="搜索关键词，[必填]，示例: 南浔")],
                          continuation_token: Annotated[Optional[str], Field(description="翻页游标（传入上次响应的continuationToken获取下一页），[可选]，示例: null")] = None) -> Dict[str, Any]:
    """YouTube 关键词视频搜索。search_query 必填；continuation_token 用于翻页。

接口: POST /story/api/youtube/searchVideo"""
    return call(lambda: get_client().youtube.search_videos,
                search_query=search_query, continuation_token=continuation_token, source="YouTube 关键词视频搜索-MCP")


@mcp.tool()
def youtube_get_video(video_id: Annotated[str, Field(description="视频ID（如 sa8AzBK4dao），[必填]，示例: sa8AzBK4dao")]) -> Dict[str, Any]:
    """获取 YouTube 单个视频详情。video_id 为视频 ID（必填）。

接口: POST /story/api/youtube/videoDetail"""
    return call(lambda: get_client().youtube.get_video, video_id=video_id, source="获取 YouTube 单个视频详情-MCP")


@mcp.tool()
def youtube_get_comments(video_id: Annotated[str, Field(description="视频ID（如 sa8AzBK4dao），[必填]，示例: sa8AzBK4dao")], language_code: Annotated[Optional[str], Field(description="评论显示语言偏好，默认 \"zh-CN\"，可选 \"en-US\"、\"ja-JP\"、\"ko-KR\" 等，[可选]，示例: zh-CN")] = None,
                         country_code: Annotated[Optional[str], Field(description="地区代码，默认 \"US\"，可选 \"JP\"、\"GB\" 等，[可选]，示例: US")] = None,
                         sort_by: Annotated[Optional[str], Field(description="评论排序方式，默认 \"top\"：热门评论，\"newest\"：最新评论，[可选]，示例: top")] = None,
                         continuation_token: Annotated[Optional[str], Field(description="翻页令牌，从上一次响应中获取，首次请求传null或不传，[可选]")] = None) -> Dict[str, Any]:
    """获取 YouTube 视频评论。video_id 必填；sort_by：top=最热/newest=最新；
    continuation_token 用于翻页。

接口: POST /story/api/youtube/videoComments"""
    return call(lambda: get_client().youtube.get_comments,
                video_id=video_id, language_code=language_code,
                country_code=country_code, sort_by=sort_by,
                continuation_token=continuation_token, source="获取 YouTube 视频评论-MCP")


@mcp.tool()
def youtube_get_transcript(video_url: Annotated[str, Field(description="视频链接，[必填]，示例: https://www.youtube.com/watch?v=jNQXAC9IVRw")]) -> Dict[str, Any]:
    """提取 YouTube 视频字幕轨道。video_url 为视频链接（必填）。
    返回视频信息（标题、时长、发布时间、封面、描述）及各语言、各格式
    （srt/vtt/ttml/json3）的字幕下载地址，含人工字幕与自动生成字幕。

接口: POST /story/api/parseWork/videoSubtitle/youtube"""
    return call(lambda: get_client().youtube.get_transcript,
                video_url=video_url, source="提取 YouTube 视频字幕/文案-MCP")


def main() -> None:
    serve(mcp, prog="redfox-youtube-mcp", description="RedFox YouTube MCP server")


if __name__ == "__main__":
    main()
