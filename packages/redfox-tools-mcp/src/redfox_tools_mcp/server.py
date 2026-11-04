"""RedFox 工具类 MCP Server

将 RedFoxHub（红狐数据平台）的多平台作品下载与素材上传能力暴露为 MCP 工具。

认证：stdio 模式读环境变量 REDFOX_API_KEY；HTTP 模式从请求头
REDFOX_API_KEY（或 Authorization: Bearer <key>）取 key。
获取地址 https://redfox.hk/settings/api-keys?source=mcp
"""

from typing import Annotated, Any, Dict
from pydantic import Field

from redfox_mcp_core import call, create_server, get_client, serve

from redfox_tools_mcp import __version__

mcp = create_server("redfox-tools", __version__)


def _upload(method: str, file: str, format: str, source: str) -> Dict[str, Any]:
    """打开本地文件并把文件句柄交给 SDK 上传方法，异常统一转结构化结果"""
    try:
        handle = open(file, "rb")
    except OSError as e:
        return {"error": "file_error",
                "message": f"无法读取本地文件 {file}：{e}"}
    with handle:
        return call(lambda: getattr(get_client().tools, method),
                    file=handle, format=format, source=source)


# ─── 下载 ────────────────────────────────────────────────

@mcp.tool()
def tools_download(url: str) -> Dict[str, Any]:
    """通用作品下载：传入任意平台作品链接，自动解析返回下载信息。"""
    return call(lambda: get_client().tools.download, url=url, source="通用作品下载-MCP")


@mcp.tool()
def tools_download_douyin(url: Annotated[str, Field(description="视频链接，[必填]，示例: 4.38 Oxs:/ e@O.xS 06/01 :2pm 如果你听懂了程艾影，那么即便是前奏也能够让你热泪盈眶了🩵 # 赵雷 # 程艾影 # 永远都像初次见你那样 # 署前街少年 # 音乐节现场 https://v.douyin.com/pjE9uqFMK68/ 复制此链接，打开Dou音搜索，直接观看视频！")]) -> Dict[str, Any]:
    """抖音作品下载。url 为抖音作品链接（必填）。

接口: POST /story/api/parseWork/videoDownload/douyin"""
    return call(lambda: get_client().tools.download_douyin, url=url, source="抖音作品下载-MCP")


@mcp.tool()
def tools_download_kuaishou(url: Annotated[str, Field(description="视频链接，[必填]，示例: https://www.kuaishou.com/short-video/3xabin6qa7k2jn9?authorId=3x5d76fipfzyygu&streamSource=find&area=homexxbrilliant")]) -> Dict[str, Any]:
    """快手作品下载。url 为快手作品链接（必填）。

接口: POST /story/api/parseWork/videoDownload/kuaishou"""
    return call(lambda: get_client().tools.download_kuaishou, url=url, source="快手作品下载-MCP")


@mcp.tool()
def tools_download_xiaohongshu(url: Annotated[str, Field(description="视频链接，[必填]，示例: https://www.xiaohongshu.com/explore/6a3c7aa6000000001003e071?xsec_token=AB-U4vc8DJUJoY9w-ebP_DvuxgiSNYmx8n35V4zvPo__M=&xsec_source=pc_feed")]) -> Dict[str, Any]:
    """小红书作品下载。url 为小红书作品链接（必填）。

接口: POST /story/api/parseWork/videoDownload/xhs"""
    return call(lambda: get_client().tools.download_xiaohongshu, url=url, source="小红书作品下载-MCP")


@mcp.tool()
def tools_download_bilibili(url: Annotated[str, Field(description="视频链接，[必填]，示例: https://www.bilibili.com/video/BV1AmSSBMEqo/")]) -> Dict[str, Any]:
    """B 站作品下载。url 为 B 站作品链接（必填）。

接口: POST /story/api/parseWork/videoDownload/bilibili"""
    return call(lambda: get_client().tools.download_bilibili, url=url, source="B 站作品下载-MCP")


@mcp.tool()
def tools_download_wechat_channels(url: Annotated[str, Field(description="视频链接，[必填]，示例: https://weixin.qq.com/sph/As0liHeOg6")]) -> Dict[str, Any]:
    """微信视频号作品下载。url 为视频号作品链接（必填）。

接口: POST /story/api/parseWork/videoDownload/sph"""
    return call(lambda: get_client().tools.download_wechat_channels, url=url, source="微信视频号作品下载-MCP")


@mcp.tool()
def tools_download_tiktok(url: Annotated[str, Field(description="视频链接，[必填]，示例: https://www.tiktok.com/@koji_japanese_food/video/7636776450875591957?is_from_webapp=1&sender_device=pc")]) -> Dict[str, Any]:
    """TikTok 作品下载。url 为 TikTok 作品链接（必填）。

接口: POST /story/api/parseWork/videoDownload/tiktok"""
    return call(lambda: get_client().tools.download_tiktok, url=url, source="TikTok 作品下载-MCP")


@mcp.tool()
def tools_download_youtube(url: Annotated[str, Field(description="视频链接，[必填]，示例: https://www.youtube.com/watch?v=dQw4w9WgXcQ")]) -> Dict[str, Any]:
    """YouTube 视频下载。url 为 YouTube 视频链接（必填）。

接口: POST /story/api/parseWork/videoDownload/youtube"""
    return call(lambda: get_client().tools.download_youtube, url=url, source="YouTube 视频下载-MCP")


@mcp.tool()
def tools_download_instagram(url: Annotated[str, Field(description="视频链接，[必填]，示例: https://www.instagram.com/reel/Dasg6uZuD5B/?utm_source=ig_web_button_share_sheet")]) -> Dict[str, Any]:
    """Instagram 作品下载。url 为 Instagram 帖子/Reel 链接（必填）。

接口: POST /story/api/parseWork/videoDownload/instagram"""
    return call(lambda: get_client().tools.download_instagram, url=url, source="Instagram 作品下载-MCP")


@mcp.tool()
def tools_download_twitter(url: Annotated[str, Field(description="视频链接，[必填]，示例: https://x.com/chiikawa_movie/status/2076962843841470561")]) -> Dict[str, Any]:
    """X(Twitter) 作品下载。url 为推文链接（必填）。

接口: POST /story/api/parseWork/videoDownload/x"""
    return call(lambda: get_client().tools.download_twitter, url=url, source="X(Twitter) 作品下载-MCP")


# ─── 上传 ────────────────────────────────────────────────

@mcp.tool()
def tools_upload_image(file: str, format: Annotated[str, Field(description="上传图片格式，支持png、jpeg、webp，[可选]，示例: png")] = "png") -> Dict[str, Any]:
    """上传图片到红狐素材库。file 为本地图片文件路径（必填）；
    format：png/jpeg/webp。返回上传后的 URL。

接口: POST /story/api/parseWork/imageGen/uploadImage"""
    return _upload("upload_image", file, format, "上传图片到红狐素材库-MCP")


@mcp.tool()
def tools_upload_file(file: str, format: Annotated[str, Field(description="素材格式，用于判断文件大小限制和存储路径（视频:mp4/avi/mov/mkv/webm限50MB，音频:mp3/wav/aac/ogg/flac限20MB，图片:png/jpg/jpeg/webp/gif/bmp限10MB），[可选]，示例: mp4")] = "mp4") -> Dict[str, Any]:
    """上传文件到红狐素材库（视频≤50MB / 音频≤20MB / 图像≤10MB）。
    file 为本地文件路径（必填）；format 为文件扩展名（如 mp4/mp3/png）。
    返回上传后的 URL。

接口: POST /story/api/parseWork/videoGen/uploadFile"""
    return _upload("upload_file", file, format, "上传文件到红狐素材库-MCP")


def main() -> None:
    serve(mcp, prog="redfox-tools-mcp", description="RedFox 工具类 MCP server")


if __name__ == "__main__":
    main()
