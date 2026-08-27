"""RedFox MCP Server（全量聚合版）

将 RedFoxHub（红狐数据平台）的 40 个 API 能力暴露为 MCP 工具：
- 6 大内容平台数据查询（抖音/小红书/公众号/B站/头条/TikTok，26 个同步工具）
- AI 搜索（Kimi/豆包/Deepseek，3 个自动轮询工具 + 3 个结果查询工具）
- AI 生成（GPT 图片/豆包图片 Pro/Lite/豆包视频，4 个自动轮询工具 + 4 个结果查询工具）

本包为聚合包：工具实现位于各平台独立包（redfox-douyin-mcp 等），
此处通过 fastmcp mount 无前缀合并，工具名与历史版本完全一致。

认证：环境变量 REDFOX_API_KEY（获取地址 https://redfox.hk/settings/api-keys?source=mcp）
"""

from redfox_mcp_core import create_server, serve

from redfox_ai_gen_mcp.server import mcp as ai_gen_mcp
from redfox_ai_search_mcp.server import mcp as ai_search_mcp
from redfox_bilibili_mcp.server import mcp as bilibili_mcp
from redfox_douyin_mcp.server import mcp as douyin_mcp
from redfox_tiktok_mcp.server import mcp as tiktok_mcp
from redfox_toutiao_mcp.server import mcp as toutiao_mcp
from redfox_wechat_mcp.server import mcp as wechat_mcp
from redfox_xiaohongshu_mcp.server import mcp as xiaohongshu_mcp

from redfox_mcp import __version__

mcp = create_server("redfox", __version__)

# 无前缀合并 8 个平台 server，工具名保持 douyin_xxx / xiaohongshu_xxx 等不变
for _sub in (douyin_mcp, xiaohongshu_mcp, wechat_mcp, bilibili_mcp,
             toutiao_mcp, tiktok_mcp, ai_search_mcp, ai_gen_mcp):
    mcp.mount(_sub)


def main() -> None:
    """启动 MCP server：默认 stdio（本地客户端），--transport http 切换为远程多租户模式"""
    serve(mcp, prog="redfox-mcp", description="RedFoxHub MCP server")


if __name__ == "__main__":
    main()
