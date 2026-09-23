"""RedFox MCP busybox entry — one binary, all servers.

Usage:
    redfox-mcp <server> [server args...]

Examples:
    redfox-mcp douyin
    redfox-mcp xiaohongshu --transport http --port 8000
    redfox-mcp all            # all-in-one aggregate server

HTTP mode requires request header REDFOX_API_KEY (or Authorization: Bearer)
to create a session; /health stays open. Set REDFOX_MCP_REQUIRE_API_KEY=0
to disable the gate while debugging.
"""

import sys

# Static imports so PyInstaller collects every server module.
from redfox_ai_gen_mcp.server import main as _ai_gen
from redfox_ai_search_mcp.server import main as _ai_search
from redfox_auto_mcp.server import main as _auto
from redfox_bilibili_mcp.server import main as _bilibili
from redfox_douyin_mcp.server import main as _douyin
from redfox_instagram_mcp.server import main as _instagram
from redfox_kuaishou_mcp.server import main as _kuaishou
from redfox_mcp.server import main as _all
from redfox_tiktok_mcp.server import main as _tiktok
from redfox_tools_mcp.server import main as _tools
from redfox_toutiao_mcp.server import main as _toutiao
from redfox_twitter_mcp.server import main as _twitter
from redfox_wechat_channels_mcp.server import main as _wechat_channels
from redfox_wechat_mcp.server import main as _wechat
from redfox_xiaohongshu_mcp.server import main as _xiaohongshu
from redfox_youtube_mcp.server import main as _youtube

SERVERS = {
    "ai-gen": _ai_gen,
    "ai-search": _ai_search,
    "auto": _auto,
    "bilibili": _bilibili,
    "douyin": _douyin,
    "instagram": _instagram,
    "kuaishou": _kuaishou,
    "tiktok": _tiktok,
    "tools": _tools,
    "toutiao": _toutiao,
    "twitter": _twitter,
    "wechat": _wechat,
    "wechat-channels": _wechat_channels,
    "xiaohongshu": _xiaohongshu,
    "youtube": _youtube,
    "all": _all,
}


def main():
    args = sys.argv[1:]
    if not args or args[0] not in SERVERS:
        code = 0 if args and args[0] in ("-h", "--help") else 2
        out = sys.stdout if code == 0 else sys.stderr
        out.write("Usage: redfox-mcp <server> [server args...]\n\nAvailable servers:\n")
        for name in sorted(SERVERS):
            out.write(f"  {name}\n")
        sys.exit(code)
    # Drop the server name so the server sees a normal argv.
    del sys.argv[1]
    SERVERS[args[0]]()


if __name__ == "__main__":
    main()
