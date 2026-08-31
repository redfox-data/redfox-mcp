"""RedFox 工具类 MCP Server

将 RedFoxHub（红狐数据平台）的多平台作品下载与素材上传能力暴露为 MCP 工具。

认证：stdio 模式读环境变量 REDFOX_API_KEY；HTTP 模式从请求头
X-API-Key（或 Authorization: Bearer <key>）取 key。
获取地址 https://redfox.hk/settings/api-keys?source=mcp
"""

from typing import Any, Dict

from redfox_mcp_core import call, create_server, get_client, serve

from redfox_tools_mcp import __version__

mcp = create_server("redfox-tools", __version__)


def _upload(method: str, file: str, format: str) -> Dict[str, Any]:
    """打开本地文件并把文件句柄交给 SDK 上传方法，异常统一转结构化结果"""
    try:
        handle = open(file, "rb")
    except OSError as e:
        return {"error": "file_error",
                "message": f"无法读取本地文件 {file}：{e}"}
    with handle:
        return call(lambda: getattr(get_client().tools, method),
                    file=handle, format=format)


# ─── 下载 ────────────────────────────────────────────────

@mcp.tool()
def tools_download(url: str) -> Dict[str, Any]:
    """通用作品下载：传入任意平台作品链接，自动解析返回下载信息。"""
    return call(lambda: get_client().tools.download, url=url)


@mcp.tool()
def tools_download_douyin(url: str) -> Dict[str, Any]:
    """抖音作品下载。url 为抖音作品链接（必填）。"""
    return call(lambda: get_client().tools.download_douyin, url=url)


@mcp.tool()
def tools_download_kuaishou(url: str) -> Dict[str, Any]:
    """快手作品下载。url 为快手作品链接（必填）。"""
    return call(lambda: get_client().tools.download_kuaishou, url=url)


@mcp.tool()
def tools_download_xiaohongshu(url: str) -> Dict[str, Any]:
    """小红书作品下载。url 为小红书作品链接（必填）。"""
    return call(lambda: get_client().tools.download_xiaohongshu, url=url)


@mcp.tool()
def tools_download_bilibili(url: str) -> Dict[str, Any]:
    """B 站作品下载。url 为 B 站作品链接（必填）。"""
    return call(lambda: get_client().tools.download_bilibili, url=url)


@mcp.tool()
def tools_download_wechat_channels(url: str) -> Dict[str, Any]:
    """微信视频号作品下载。url 为视频号作品链接（必填）。"""
    return call(lambda: get_client().tools.download_wechat_channels, url=url)


@mcp.tool()
def tools_download_tiktok(url: str) -> Dict[str, Any]:
    """TikTok 作品下载。url 为 TikTok 作品链接（必填）。"""
    return call(lambda: get_client().tools.download_tiktok, url=url)


@mcp.tool()
def tools_download_youtube(url: str) -> Dict[str, Any]:
    """YouTube 视频下载。url 为 YouTube 视频链接（必填）。"""
    return call(lambda: get_client().tools.download_youtube, url=url)


@mcp.tool()
def tools_download_instagram(url: str) -> Dict[str, Any]:
    """Instagram 作品下载。url 为 Instagram 帖子/Reel 链接（必填）。"""
    return call(lambda: get_client().tools.download_instagram, url=url)


@mcp.tool()
def tools_download_twitter(url: str) -> Dict[str, Any]:
    """X(Twitter) 作品下载。url 为推文链接（必填）。"""
    return call(lambda: get_client().tools.download_twitter, url=url)


# ─── 上传 ────────────────────────────────────────────────

@mcp.tool()
def tools_upload_image(file: str, format: str = "png") -> Dict[str, Any]:
    """上传图片到红狐素材库。file 为本地图片文件路径（必填）；
    format：png/jpeg/webp。返回上传后的 URL。"""
    return _upload("upload_image", file, format)


@mcp.tool()
def tools_upload_file(file: str, format: str = "mp4") -> Dict[str, Any]:
    """上传文件到红狐素材库（视频≤50MB / 音频≤20MB / 图像≤10MB）。
    file 为本地文件路径（必填）；format 为文件扩展名（如 mp4/mp3/png）。
    返回上传后的 URL。"""
    return _upload("upload_file", file, format)


def main() -> None:
    serve(mcp, prog="redfox-tools-mcp", description="RedFox 工具类 MCP server")


if __name__ == "__main__":
    main()
