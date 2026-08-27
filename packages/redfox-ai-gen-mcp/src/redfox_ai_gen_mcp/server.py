"""RedFox AI 生成 MCP Server

将 RedFoxHub（红狐数据平台）的 AI 生成能力暴露为 MCP 工具：
- GPT 图片生成（gpt-image-2）
- 豆包 Seedream 5.0 Pro / Lite 图片生成
- 豆包 Seedance 2.0 视频生成
提交后自动轮询等待结果，超时返回 taskId 供 result 工具补查。

认证：stdio 模式读环境变量 REDFOX_API_KEY；HTTP 模式从请求头
X-API-Key（或 Authorization: Bearer <key>）取 key。
获取地址 https://redfox.hk/settings/api-keys?source=mcp
"""

from typing import Any, Dict, List, Optional

from redfox_mcp_core import call, create_server, get_client, run_task, serve

from redfox_ai_gen_mcp import __version__

mcp = create_server("redfox-ai-gen", __version__)


@mcp.tool()
def gpt_image_generate(prompt: str, n: int = 1, size: str = "1024x1024",
                       quality: str = "medium", background: str = "auto",
                       output_format: str = "png",
                       output_compression: Optional[int] = None,
                       model_name: str = "gpt-image-2",
                       operation: str = "generate",
                       input_fidelity: Optional[str] = None,
                       images: Optional[List[Dict[str, str]]] = None,
                       timeout_seconds: int = 240) -> Dict[str, Any]:
    """GPT 图片生成（gpt-image-2），提交后自动等待并返回 imagePaths。
    operation：generate=文生图 / edit=图生图（edit 时 images 必填，
    形如 [{"url": "https://..."}]，input_fidelity 支持 high/low）；
    quality：low/medium/high/auto；background：transparent/opaque/auto；
    output_format：png/jpeg/webp。超时返回 taskId，可用 gpt_image_result 再查。"""
    return run_task(lambda: get_client().gpt_image.submit,
                    lambda: get_client().gpt_image.result,
                    timeout_seconds, prompt=prompt, n=n, size=size, quality=quality,
                    background=background, output_format=output_format,
                    output_compression=output_compression, model_name=model_name,
                    operation=operation, input_fidelity=input_fidelity, images=images)


@mcp.tool()
def gpt_image_result(task_id: str) -> Dict[str, Any]:
    """查询 GPT 图片生成任务结果（含 status/imagePaths/failReason）。
    仅在 gpt_image_generate 超时返回 taskId 后使用。"""
    return call(lambda: get_client().gpt_image.result, task_id=task_id)


@mcp.tool()
def doubao_image_pro_generate(prompt: str, size: str = "2048x2048",
                              image: Optional[Any] = None,
                              output_format: str = "jpeg",
                              response_format: str = "url",
                              watermark: bool = True,
                              optimize_prompt: bool = False,
                              optimize_mode: str = "standard",
                              timeout_seconds: int = 240) -> Dict[str, Any]:
    """豆包 Seedream 5.0 Pro 图片生成，提交后自动等待结果。
    size 支持 "1K"/"2K" 或像素值如 "2048x2048"；image 为图生图输入（URL 或 Base64，
    可传单个字符串或字符串列表）；optimize_prompt 开启提示词优化（standard/fast）。
    超时返回 taskId，可用 doubao_image_pro_result 再查。"""
    return run_task(lambda: get_client().doubao_image.pro_submit,
                    lambda: get_client().doubao_image.pro_result,
                    timeout_seconds, prompt=prompt, size=size, image=image,
                    output_format=output_format, response_format=response_format,
                    watermark=watermark, optimize_prompt=optimize_prompt,
                    optimize_mode=optimize_mode)


@mcp.tool()
def doubao_image_pro_result(task_id: str) -> Dict[str, Any]:
    """查询 Seedream 5.0 Pro 任务结果。仅在 doubao_image_pro_generate 超时返回 taskId 后使用。"""
    return call(lambda: get_client().doubao_image.pro_result, task_id=task_id)


@mcp.tool()
def doubao_image_lite_generate(prompt: str, size: str = "2048x2048",
                               image: Optional[Any] = None,
                               output_format: str = "jpeg",
                               response_format: str = "url",
                               watermark: bool = True,
                               sequential: str = "disabled",
                               max_images: int = 4,
                               optimize_prompt: bool = False,
                               optimize_mode: str = "standard",
                               timeout_seconds: int = 240) -> Dict[str, Any]:
    """豆包 Seedream 5.0 Lite 图片生成，支持组图，提交后自动等待结果。
    size 支持 "2K"/"3K"/"4K" 或像素值；sequential 设为 "auto" 时生成组图，
    max_images 控制组图数量（1~10）。超时返回 taskId，可用 doubao_image_lite_result 再查。"""
    return run_task(lambda: get_client().doubao_image.lite_submit,
                    lambda: get_client().doubao_image.lite_result,
                    timeout_seconds, prompt=prompt, size=size, image=image,
                    output_format=output_format, response_format=response_format,
                    watermark=watermark, sequential=sequential, max_images=max_images,
                    optimize_prompt=optimize_prompt, optimize_mode=optimize_mode)


@mcp.tool()
def doubao_image_lite_result(task_id: str) -> Dict[str, Any]:
    """查询 Seedream 5.0 Lite 任务结果。仅在 doubao_image_lite_generate 超时返回 taskId 后使用。"""
    return call(lambda: get_client().doubao_image.lite_result, task_id=task_id)


@mcp.tool()
def doubao_video_generate(content: List[Dict[str, Any]],
                          model: Optional[str] = None,
                          resolution: str = "720p",
                          ratio: str = "adaptive",
                          duration: int = 5,
                          seed: int = -1,
                          watermark: bool = False,
                          generate_audio: bool = True,
                          return_last_frame: bool = False,
                          timeout_seconds: int = 480) -> Dict[str, Any]:
    """豆包 Seedance 2.0 视频生成，提交后自动等待结果。
    content 为输入内容列表（必填），每项形如：
    {"type": "text", "text": "描述文字"}；
    {"type": "image_url", "imageUrl": "图片URL", "imageRole": "first_frame/reference_image"}；
    {"type": "video_url", "videoUrl": "视频URL", "videoRole": "reference_video"}；
    {"type": "audio_url", "audioUrl": "音频URL", "audioRole": "reference_audio"}。
    resolution：480p/720p/1080p；ratio：adaptive/16:9/4:3/1:1/3:4/9:16/21:9；
    duration 秒数 [4,15] 或 -1 智能。超时返回 taskId，可用 doubao_video_result 再查。"""
    return run_task(lambda: get_client().doubao_video.submit,
                    lambda: get_client().doubao_video.result,
                    timeout_seconds, content=content, model=model,
                    resolution=resolution, ratio=ratio, duration=duration,
                    seed=seed, watermark=watermark, generate_audio=generate_audio,
                    return_last_frame=return_last_frame)


@mcp.tool()
def doubao_video_result(task_id: str) -> Dict[str, Any]:
    """查询豆包视频生成任务结果。仅在 doubao_video_generate 超时返回 taskId 后使用。"""
    return call(lambda: get_client().doubao_video.result, task_id=task_id)


def main() -> None:
    serve(mcp, prog="redfox-ai-gen-mcp", description="RedFox AI 生成 MCP server")


if __name__ == "__main__":
    main()
