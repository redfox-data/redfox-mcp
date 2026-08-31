<div align="center">
<a href="https://pypi.org/project/redfox-mcp/"><img src="https://img.shields.io/pypi/v/redfox-mcp.svg" alt="PyPI version"></a> <a href="https://pypi.org/project/redfox-mcp/"><img src="https://img.shields.io/pypi/pyversions/redfox-mcp.svg" alt="Python"></a> <a href="https://pypi.org/project/redfox-mcp/"><img src="https://img.shields.io/pypi/l/redfox-mcp.svg" alt="License"></a>

<p align="center">
  中文
  <a href="https://github.com/redfox-data/redfox-mcp/blob/main/README.md">English</a>
</p>

</div>

<p align="center">
  <a href="https://redfox.hk/?source=github"><img src="https://lyy.redfox.hk/page/logo-redfox-name.png" alt="RedFox Logo" width="200"></a>
</p>



# redfox-mcp

RedFoxHub（红狐数据平台）MCP monorepo — 将 11 大内容平台 + 汽车垂类（3 家）+ AI 搜索/生成 + 下载/上传能力拆分为 15 个按平台独立的 MCP server（共 134 个工具），可被 dsh、Claude Code、Cursor 等任意 MCP 客户端直接调用。

每个包都同时支持**本地 stdio**（单用户，环境变量 `REDFOX_API_KEY`）与**远程 HTTP**（多租户，按请求头传递 API Key），并自带 Dockerfile 可独立部署。

## 包索引

| 包 | 工具数 | stdio 命令 | Docker 服务 / 端口 |
|---|---|---|---|
| [`redfox-mcp`](packages/redfox-mcp)（全量聚合版） | 134 | `uvx redfox-mcp` | `all` → 8000 |
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
| [`redfox-mcp-core`](packages/redfox-mcp-core) | — | 共享运行时（不直接面向用户） | — |

异步工具（AI 搜索/生成）内部自动轮询：提交 → 等待 → 返回完整结果。若等待超过 `timeout_seconds`（默认 240 秒、视频 480 秒），返回 `taskId`，可用对应的 `*_result` 工具补查。

## 认证

所有 API 均需 RedFoxHub API Key：

1. 前往 <https://redfox.hk/settings/api-keys/?source=mcp> 获取
2. 设置环境变量：

```bash
export REDFOX_API_KEY="YOUR_API_KEY"
```

未配置 key 时，每个工具都会返回结构化的获取引导。

## 快速开始（本地 stdio）

需要 Python ≥ 3.10。按需只装需要的平台 —— 例如只要抖音：

```bash
uvx redfox-douyin-mcp
```

或使用包含全部 134 个工具的聚合包：

```bash
uvx redfox-mcp
```

客户端配置（Cursor / 其他 MCP 客户端）：

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

Claude Code：

```bash
claude mcp add redfox-douyin --env REDFOX_API_KEY=YOUR_API_KEY -- uvx redfox-douyin-mcp
```

## 远程 HTTP 模式（多租户）

每个 server 都可作为远程 HTTP 服务运行，每个用户携带自己的 API Key：

```bash
redfox-douyin-mcp --transport http --host 0.0.0.0 --port 8000
# 或环境变量：REDFOX_MCP_TRANSPORT=http REDFOX_MCP_HOST=0.0.0.0 REDFOX_MCP_PORT=8000
```

- MCP 端点：`http://<host>:8000/mcp`（Streamable HTTP）；健康检查：`GET /health`
- 每个请求通过请求头 `X-API-Key: <key>`（或 `Authorization: Bearer <key>`）携带自己的 key，按 key 建独立客户端缓存，额度互不共享

客户端配置（远程 URL + 请求头）：

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

## Docker 部署

每个包目录自包含独立 Dockerfile，可按目录独立构建部署（以抖音为例）：

```bash
cd packages/redfox-douyin-mcp
docker build -t redfox-douyin-mcp .
docker run -d -p 8001:8000 redfox-douyin-mcp
```

根目录附带 `docker-compose.yml` 作为便利编排，各服务完全独立、可单独起停：

```bash
docker compose up -d douyin        # 只起一个平台
docker compose up -d               # 起全部 16 个服务（端口 8000-8015）
```

镜像均不内置 API Key，调用方通过请求头携带自己的 key。

## 本地开发

本仓库为 uv workspace，clone 后：

```bash
uv sync                            # 以源码安装全部包
uv run redfox-douyin-mcp --help    # 以源码运行任意 server
```

## 发布

各包按依赖顺序独立发布到 PyPI：

```bash
cd packages/redfox-mcp-core && uv build && uv publish        # 1. 先发 core
cd packages/redfox-douyin-mcp && uv build && uv publish      # 2. 再发 14 个平台包
# ... 其余平台包同理 ...
cd packages/redfox-mcp && uv build && uv publish             # 3. 最后发聚合包
```

## 底层实现

基于官方 SDK [redfox-python-sdk](https://github.com/redfox-data/redfox-python-sdk)。API 文档：<https://redfox.hk/?source=mcp>。

## License

MIT
