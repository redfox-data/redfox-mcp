"""RedFox B 站数据 MCP Server

将 RedFoxHub（红狐数据平台）的 B 站数据 API 暴露为 MCP 工具。

认证：stdio 模式读环境变量 REDFOX_API_KEY；HTTP 模式从请求头
REDFOX_API_KEY（或 Authorization: Bearer <key>）取 key。
获取地址 https://redfox.hk/settings/api-keys?source=mcp
"""

from typing import Annotated, Any, Dict, Optional
from pydantic import Field

from redfox_mcp_core import call, create_server, get_client, serve

from redfox_bilibili_mcp import __version__

mcp = create_server("redfox-bilibili", __version__)


@mcp.tool()
def bilibili_search_articles(keyword: Annotated[str, Field(description="（必填，搜索关键词），[必填]，示例: 羽绒服")], page: Annotated[int, Field(description="（必填，页码），[可选]，示例: 1")] = 1,
                             page_size: Annotated[Optional[int], Field(description="（非必填，每页条数，默认10，最大50），[可选]，示例: 10")] = None,
                             order: Annotated[Optional[str], Field(description="（非必填，排序：time=发布时间/play=播放数/like=点赞数/comment=评论数/favorite=收藏数，默认time），[可选]，示例: time")] = None) -> Dict[str, Any]:
    """搜索 B 站视频（优质库）。keyword 必填；page 从 1 开始；page_size 默认 10、最大 50；
    order：time=发布时间 / play=播放数 / like=点赞数 / comment=评论数 / favorite=收藏数。

接口: POST /story/api/bili/data/workSearch"""
    return call(lambda: get_client().bilibili.search_articles,
                keyword=keyword, page=page, page_size=page_size, order=order, source="搜索 B 站视频-MCP")


@mcp.tool()
def bilibili_search_users(keyword: Annotated[str, Field(description="（必填，搜索关键词），[必填]，示例: 影视飓风")], page: Annotated[int, Field(description="（必填，页码，从1开始），[可选]，示例: 1")] = 1,
                          page_size: Annotated[Optional[int], Field(description="非必填，每页条数，默认10，最大50），[可选]，示例: 10")] = None,
                          order: Annotated[Optional[str], Field(description="（非必填，排序：follower=粉丝数/like=获赞数，默认相关性），[可选]，示例: follower")] = None) -> Dict[str, Any]:
    """搜索 B 站 UP 主（优质库）。keyword 必填；
    order：follower=粉丝数 / like=获赞数，默认按相关性。

接口: POST /story/api/bili/data/accountSearch"""
    return call(lambda: get_client().bilibili.search_users,
                keyword=keyword, page=page, page_size=page_size, order=order, source="搜索 B 站 UP 主-MCP")


@mcp.tool()
def bilibili_get_account(mid: Annotated[str, Field(description="账号MID（必填），B站用户唯一ID，[必填]，示例: 946974")]) -> Dict[str, Any]:
    """获取 B 站 UP 主信息（优质库）。mid 为 B 站用户唯一 ID。

接口: POST /story/api/bili/data/accountDetail"""
    return call(lambda: get_client().bilibili.get_account, mid=mid, source="获取 B 站 UP 主信息-MCP")


@mcp.tool()
def bilibili_get_user_works(mid: Annotated[Optional[str], Field(description="（非必填，与accountUrl二选一），[可选]，示例: 946974")] = None,
                            account_url: Annotated[Optional[str], Field(description="（非必填，与mid二选一），[可选]，示例: https://space.bilibili.com/946974?spm_id_from=333.788.upinfo.head.click")] = None, page: Annotated[int, Field(description="（非必填，页码，默认1），[可选]，示例: 1")] = 1,
                            page_size: Annotated[Optional[int], Field(description="（非必填，每页条数，默认10，最大50），[可选]，示例: 10")] = None,
                            order: Annotated[Optional[str], Field(description="（非必填，排序：time=发布时间/play=播放数/like=点赞数，默认time），[可选]，示例: time")] = None) -> Dict[str, Any]:
    """获取 B 站 UP 主视频列表（优质库）。mid 与 account_url（主页链接）至少传一个；
    order：time=发布时间 / play=播放数 / like=点赞数。

接口: POST /story/api/bili/data/accountWorkList"""
    return call(lambda: get_client().bilibili.get_user_works,
                mid=mid, account_url=account_url, page=page,
                page_size=page_size, order=order, source="获取 B 站 UP 主视频列表-MCP")


@mcp.tool()
def bilibili_get_work(bvid: Annotated[Optional[str], Field(description="BV号（非必填，与workUrl二选一），[可选]，示例: BV1ghJg6hEWV")] = None,
                      work_url: Annotated[Optional[str], Field(description="作品链接（非必填，与bvId二选一，支持 https://www.bilibili.com/video/BV1xxx 或 https://b23.tv/xxx 格式），[可选]，示例: https://www.bilibili.com/video/BV1ghJg6hEWV/?spm_id_from=333.1007.tianma.1-1-1.click")] = None) -> Dict[str, Any]:
    """获取 B 站视频详情（优质库）。bvid 与 work_url 至少传一个，
    work_url 支持 bilibili.com/video/BVxxx 或 b23.tv 短链。

接口: POST /story/api/bili/data/workDetail"""
    return call(lambda: get_client().bilibili.get_work, bvid=bvid, work_url=work_url, source="获取 B 站视频详情-MCP")


@mcp.tool()
def bilibili_get_audio(url: Annotated[str, Field(description="作品链接，[必填]，示例: https://www.bilibili.com/video/BV1L1bD61Emd")]) -> Dict[str, Any]:
    """获取 B 站视频音频地址。url 为 B 站作品链接（必填）。

接口: POST /story/api/parseWork/audioExtract/bilibili"""
    return call(lambda: get_client().bilibili.get_audio, url=url, source="获取 B 站视频音频地址-MCP")


@mcp.tool()
def bilibili_transcript(url: Annotated[str, Field(description="作品地址，[必填]，示例: https://www.bilibili.com/video/BV1L1bD61Emd")], timeout_seconds: Optional[int] = None) -> Dict[str, Any]:
    """提交 B 站视频字幕/文案提取任务，立即返回 taskId，不自动查询结果。
    url 为作品链接（必填）。请稍后用 bilibili_transcript_result(task_id)
    自行查询结果。timeout_seconds 为可选参数，可传可不传，传与不传都不影响本调用
    （本工具只提交任务、不自动轮询结果）。

接口: POST /story/api/parseWork/bilibiliSubtitle/submit"""
    return call(lambda: get_client().bilibili.transcript_submit,
                url=url, source="B 站视频字幕/文案提取-MCP")


@mcp.tool()
def bilibili_transcript_result(task_id: Annotated[str, Field(description="任务id，[必填]，示例: 9600331947cb41dba77d082e6aa72c64")]) -> Dict[str, Any]:
    """查询 B 站字幕提取任务结果。传 bilibili_transcript 提交返回的 taskId。

接口: POST /story/api/parseWork/bilibiliSubtitle/result"""
    return call(lambda: get_client().bilibili.transcript_result, task_id=task_id, source="查询 B 站字幕提取任务结果-MCP")


def main() -> None:
    serve(mcp, prog="redfox-bilibili-mcp", description="RedFox B 站数据 MCP server")


if __name__ == "__main__":
    main()
