"""RedFox MCP Server（全量聚合版）

将 RedFoxHub（红狐数据平台）的多平台数据能力暴露为 MCP 工具：
- 11 大内容平台数据查询（抖音/小红书/公众号/B站/头条/TikTok/快手/Instagram/X(Twitter)/YouTube/视频号）
- 汽车垂类 3 家（懂车帝/汽车之家/易车）
- AI 搜索（Kimi/豆包/Deepseek/元宝/千问/百度，6 个引擎）
- AI 生成（GPT 图片/豆包图片 Pro/Lite/豆包视频）
- 工具（10 个平台下载器 + 2 个上传器）

本包为聚合包：工具实现位于各平台独立包（redfox-douyin-mcp 等），
此处通过 fastmcp mount 无前缀合并，工具名与各独立包完全一致。

认证：环境变量 REDFOX_API_KEY（获取地址 https://redfox.hk/settings/api-keys?source=mcp）
"""

from redfox_mcp_core import create_server, serve

from redfox_ai_gen_mcp.server import mcp as ai_gen_mcp
from redfox_ai_search_mcp.server import mcp as ai_search_mcp
from redfox_auto_mcp.server import mcp as auto_mcp
from redfox_bilibili_mcp.server import mcp as bilibili_mcp
from redfox_douyin_mcp.server import mcp as douyin_mcp
from redfox_instagram_mcp.server import mcp as instagram_mcp
from redfox_kuaishou_mcp.server import mcp as kuaishou_mcp
from redfox_tiktok_mcp.server import mcp as tiktok_mcp
from redfox_tools_mcp.server import mcp as tools_mcp
from redfox_toutiao_mcp.server import mcp as toutiao_mcp
from redfox_twitter_mcp.server import mcp as twitter_mcp
from redfox_wechat_channels_mcp.server import mcp as wechat_channels_mcp
from redfox_wechat_mcp.server import mcp as wechat_mcp
from redfox_xiaohongshu_mcp.server import mcp as xiaohongshu_mcp
from redfox_youtube_mcp.server import mcp as youtube_mcp

from redfox_mcp import __version__

mcp = create_server("redfox", __version__)

# 无前缀合并 15 个平台 server，工具名保持 douyin_xxx / xiaohongshu_xxx 等不变
for _sub in (douyin_mcp, xiaohongshu_mcp, wechat_mcp, wechat_channels_mcp,
             bilibili_mcp, toutiao_mcp, tiktok_mcp, kuaishou_mcp,
             instagram_mcp, twitter_mcp, youtube_mcp,
             auto_mcp, ai_search_mcp, ai_gen_mcp, tools_mcp):
    mcp.mount(_sub)


def main() -> None:
    """启动 MCP server：默认 stdio（本地客户端），--transport http 切换为远程多租户模式"""
    serve(mcp, prog="redfox-mcp", description="RedFoxHub MCP server")


if __name__ == "__main__":
    main()
