<div align="center">
<a href="https://pypi.org/project/redfox-python-sdk/"><img src="https://img.shields.io/pypi/v/redfox-mcp.svg" alt="PyPI version"></a> <a href="https://pypi.org/project/redfox-mcp/"><img src="https://img.shields.io/pypi/pyversions/redfox-mcp.svg" alt="Python"></a> <a href="https://pypi.org/project/redfox-mcp/"><img src="https://img.shields.io/pypi/l/redfox-mcp.svg" alt="License"></a>

<p align="center">
  <a href="https://github.com/redfox-data/redfox-mcp/blob/main/README.zh.md">中文</a>
  English
</p>

</div>

<p align="center">
  <a href="https://redfox.hk/?source=mcp"><img src="https://lyy.redfox.hk/page/logo-redfox-name.png" alt="RedFox Logo" width="200"></a>
</p>

# redfox-mcp

RedFoxHub MCP Server — turns the data APIs of 6 major content platforms plus AI search / generation capabilities into 40 MCP tools, ready for any MCP client such as dsh, Claude Code or Cursor.

## Tools (40)

| Category | Tools | Notes |
|---|---|---|
| Douyin | `douyin_search_articles` / `douyin_search_users` / `douyin_get_user` / `douyin_get_user_works` / `douyin_get_work` / `douyin_search_ai_articles` | work search, account search, account info, work lists, work detail, AI-work feed |
| Xiaohongshu | `xiaohongshu_search_articles` / `xiaohongshu_search_users` / `xiaohongshu_get_account` / `xiaohongshu_get_work` / `xiaohongshu_search_ai_articles` | note search, creator search, account info, note detail, AI-note feed |
| WeChat Official Accounts | `wechat_search_articles` / `wechat_search_users` / `wechat_get_account` / `wechat_get_user_works` / `wechat_get_work` / `wechat_get_article_detail` / `wechat_search_ai_articles` | article search (incl. full-text detail), account search, article lists, AI-article feed |
| Bilibili | `bilibili_search_articles` / `bilibili_search_users` / `bilibili_get_account` / `bilibili_get_user_works` / `bilibili_get_work` | video search, UP-master search / info / videos, video detail |
| Toutiao | `toutiao_search_works` / `toutiao_get_work` | content search, work detail (realtime) |
| TikTok | `tiktok_search_users` | account search |
| AI search | `ai_search_kimi` / `ai_search_doubao` / `ai_search_deepseek` | one call submits the query and waits for the full answer |
| AI generation | `gpt_image_generate` / `doubao_image_pro_generate` / `doubao_image_lite_generate` / `doubao_video_generate` | text-to-image / image-to-image / image sets / text-to-video, one call submits and waits |
| Task follow-up | `ai_search_*_result` / `gpt_image_result` / `doubao_image_*_result` / `doubao_video_result` (7 in total) | when an async tool times out it returns a `taskId`; use the matching result tool to fetch the outcome |

Async tools (AI search / generation) poll internally: submit → wait → return the full result, with no manual `taskId` handling. If the wait exceeds `timeout_seconds` (default 240s, 480s for video), a `taskId` is returned for the matching result tool.

## Authentication

All APIs require a RedFoxHub API key:

1. Get one at <https://redfox.hk/settings/api-keys/?source=mcp>
2. Set the environment variable:

```bash
export REDFOX_API_KEY="YOUR_API_KEY"
```

Without a key, every tool returns a structured message explaining how to obtain one.

## Install & Run

Python ≥ 3.10 required. Recommended via [uv](https://docs.astral.sh/uv/):

```bash
uvx redfox-mcp
```

or:

```bash
pip install redfox-mcp
redfox-mcp
```

The server runs on stdio transport.

## Client Configuration

### dsh (DeepSeek Harness)

Install the official bundle plugin [redfox-community-dsh](https://github.com/redfox-data/redfox-community-dsh) — it registers this MCP server out of the box, exposing tools as `mcp__redfox__*`:

```bash
dsh plugin --profile web add -w github:redfox-data/redfox-community-dsh
```

### Claude Code

```bash
claude mcp add redfox --env REDFOX_API_KEY=YOUR_API_KEY -- uvx redfox-mcp
```

### Cursor / other MCP clients

Add to your MCP configuration:

```json
{
  "mcpServers": {
    "redfox": {
      "command": "uvx",
      "args": ["redfox-mcp"],
      "env": { "REDFOX_API_KEY": "YOUR_API_KEY" }
    }
  }
}
```

## Under the Hood

Built on the official SDK [redfox-python-sdk](https://github.com/redfox-data/redfox-python-sdk). API docs: <https://redfox.hk/?source=mcp>.

## License

MIT
