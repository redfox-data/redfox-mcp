<div align="center">
<a href="https://pypi.org/project/redfox-mcp/"><img src="https://img.shields.io/pypi/v/redfox-mcp.svg" alt="PyPI version"></a> <a href="https://pypi.org/project/redfox-mcp/"><img src="https://img.shields.io/pypi/pyversions/redfox-mcp.svg" alt="Python"></a> <a href="https://pypi.org/project/redfox-mcp/"><img src="https://img.shields.io/pypi/l/redfox-mcp.svg" alt="License"></a>

<p align="center">
  <a href="https://github.com/redfox-data/redfox-mcp/blob/main/README.zh.md">中文</a>
  English
</p>

</div>

<p align="center">
  <a href="https://redfox.hk/?source=mcp"><img src="https://lyy.redfox.hk/page/logo-redfox-name.png" alt="RedFox Logo" width="200"></a>
</p>

# redfox-mcp

RedFoxHub MCP monorepo — the data APIs of 11 content platforms plus auto vertical (3 brands), AI search / generation and download/upload tools, exposed as 134 MCP tools split into 15 independent per-platform MCP servers, ready for any MCP client such as dsh, Claude Code or Cursor.

Every package supports both **local stdio** (single-user, `REDFOX_API_KEY` env var) and **remote HTTP** (multi-tenant, per-request API key header), and ships its own Dockerfile for independent deployment.

## Packages

| Package | Tools | stdio command | Docker service / port |
|---|---|---|---|
| [`redfox-mcp`](packages/redfox-mcp) (all-in-one) | 134 | `uvx redfox-mcp` | `all` → 8000 |
| [`redfox-douyin-mcp`](packages/redfox-douyin-mcp) | 16 | `uvx redfox-douyin-mcp` | `douyin` → 8001 |
| [`redfox-xiaohongshu-mcp`](packages/redfox-xiaohongshu-mcp) | 15 | `uvx redfox-xiaohongshu-mcp` | `xiaohongshu` → 8002 |
| [`redfox-wechat-mcp`](packages/redfox-wechat-mcp) | 16 | `uvx redfox-wechat-mcp` | `wechat` → 8003 |
| [`redfox-bilibili-mcp`](packages/redfox-bilibili-mcp) | 8 | `uvx redfox-bilibili-mcp` | `bilibili` → 8004 |
| [`redfox-toutiao-mcp`](packages/redfox-toutiao-mcp) | 5 | `uvx redfox-toutiao-mcp` | `toutiao` → 8005 |
| [`redfox-tiktok-mcp`](packages/redfox-tiktok-mcp) | 4 | `uvx redfox-tiktok-mcp` | `tiktok` → 8006 |
| [`redfox-ai-search-mcp`](packages/redfox-ai-search-mcp) | 12 | `uvx redfox-ai-search-mcp` | `ai-search` → 8007 |
| [`redfox-ai-gen-mcp`](packages/redfox-ai-gen-mcp) | 8 | `uvx redfox-ai-gen-mcp` | `ai-gen` → 8008 |
| [`redfox-kuaishou-mcp`](packages/redfox-kuaishou-mcp) | 6 | `uvx redfox-kuaishou-mcp` | `kuaishou` → 8009 |
| [`redfox-instagram-mcp`](packages/redfox-instagram-mcp) | 4 | `uvx redfox-instagram-mcp` | `instagram` → 8010 |
| [`redfox-twitter-mcp`](packages/redfox-twitter-mcp) | 4 | `uvx redfox-twitter-mcp` | `twitter` → 8011 |
| [`redfox-youtube-mcp`](packages/redfox-youtube-mcp) | 4 | `uvx redfox-youtube-mcp` | `youtube` → 8012 |
| [`redfox-wechat-channels-mcp`](packages/redfox-wechat-channels-mcp) | 7 | `uvx redfox-wechat-channels-mcp` | `wechat-channels` → 8013 |
| [`redfox-auto-mcp`](packages/redfox-auto-mcp) | 13 | `uvx redfox-auto-mcp` | `auto` → 8014 |
| [`redfox-tools-mcp`](packages/redfox-tools-mcp) | 12 | `uvx redfox-tools-mcp` | `tools` → 8015 |
| [`redfox-mcp-core`](packages/redfox-mcp-core) | — | shared runtime (not user-facing) | — |

Async tools (AI search / generation) poll internally: submit → wait → return the full result. If the wait exceeds `timeout_seconds` (default 240s, 480s for video), a `taskId` is returned for the matching `*_result` tool.

## Authentication

All APIs require a RedFoxHub API key:

1. Get one at <https://redfox.hk/settings/api-keys/?source=mcp>
2. Set the environment variable:

```bash
export REDFOX_API_KEY="YOUR_API_KEY"
```

Without a key, every tool returns a structured message explaining how to obtain one.

## Quick Start (stdio)

Python ≥ 3.10 required. Pick only the platforms you need — e.g. Douyin only:

```bash
uvx redfox-douyin-mcp
```

or the all-in-one bundle with all 134 tools:

```bash
uvx redfox-mcp
```

Client configuration (Cursor / other MCP clients):

```json
{
  "mcpServers": {
    "redfox-douyin": {
      "command": "uvx",
      "args": ["redfox-douyin-mcp"],
      "env": { "REDFOX_API_KEY": "YOUR_API_KEY" }
    }
  }
}
```

Claude Code:

```bash
claude mcp add redfox-douyin --env REDFOX_API_KEY=YOUR_API_KEY -- uvx redfox-douyin-mcp
```

## Remote HTTP Mode (multi-tenant)

Each server can run as a remote HTTP service where every user brings their own API key:

```bash
redfox-douyin-mcp --transport http --host 0.0.0.0 --port 8000
# or via env vars: REDFOX_MCP_TRANSPORT=http REDFOX_MCP_HOST=0.0.0.0 REDFOX_MCP_PORT=8000
```

- MCP endpoint: `http://<host>:8000/mcp` (Streamable HTTP); health check: `GET /health`
- Each request carries its own key via header `X-API-Key: <key>` (or `Authorization: Bearer <key>`). A dedicated client is created and cached per key — quotas are never shared across users.

Client-side config (remote URL + header):

```json
{
  "mcpServers": {
    "redfox-douyin": {
      "url": "http://<host>:8000/mcp",
      "headers": { "X-API-Key": "ak_your_key" }
    }
  }
}
```

## Docker Deployment

Each package directory is self-contained with its own Dockerfile and can be deployed independently:

```bash
cd packages/redfox-douyin-mcp
docker build -t redfox-douyin-mcp .
docker run -d -p 8001:8000 redfox-douyin-mcp
```

A root-level `docker-compose.yml` is provided for convenience — every service is independent and can be started/stopped on its own:

```bash
docker compose up -d douyin        # one platform only
docker compose up -d               # all 16 services, ports 8000-8015
```

Images never embed API keys; callers pass their own key via request header.

## Development

This repo is a uv workspace. After cloning:

```bash
uv sync                            # installs all packages from source
uv run redfox-douyin-mcp --help    # run any server from source
```

## Publishing

Packages are published to PyPI individually, in dependency order:

```bash
cd packages/redfox-mcp-core && uv build && uv publish        # 1. core first
cd packages/redfox-douyin-mcp && uv build && uv publish      # 2. platform packages
# ... repeat for the other 13 platform packages ...
cd packages/redfox-mcp && uv build && uv publish             # 3. all-in-one last
```

## Under the Hood

Built on the official SDK [redfox-python-sdk](https://github.com/redfox-data/redfox-python-sdk). API docs: <https://redfox.hk/?source=mcp>.

## License

MIT
