# redfox-auto-mcp

RedFoxHub 汽车垂类数据 MCP Server — 聚合懂车帝、汽车之家、易车三个平台共 13 个 MCP 工具，适用于 dsh、Claude Code、Cursor 等任意 MCP 客户端。

## 工具（13）

| 工具 | 平台 | 说明 |
|---|---|---|
| `dongchedi_search_works` | 懂车帝 | 关键词搜索作品（综合/视频） |
| `dongchedi_get_work` | 懂车帝 | 获取作品详情（video/article） |
| `dongchedi_get_user_works` | 懂车帝 | 获取用户作品列表 |
| `dongchedi_search_users` | 懂车帝 | 关键词搜索账号 |
| `autohome_search_works` | 汽车之家 | 关键词搜索作品（论坛/文章/视频） |
| `autohome_get_article` | 汽车之家 | 获取文章详情（支持长文分页） |
| `autohome_get_video` | 汽车之家 | 获取视频详情（原创/车家号） |
| `autohome_get_user_works` | 汽车之家 | 获取作者作品列表 |
| `yiche_search_works` | 易车 | 关键词搜索作品（社区/视频/文章） |
| `yiche_get_article` | 易车 | 获取文章详情 |
| `yiche_get_video` | 易车 | 获取视频详情 |
| `yiche_get_user_works` | 易车 | 获取用户作品列表 |
| `yiche_search_users` | 易车 | 关键词搜索账号 |

## 认证

1. 前往 <https://redfox.hk/settings/api-keys?source=mcp> 获取 API Key
2. 设置环境变量：

```bash
export REDFOX_API_KEY="YOUR_API_KEY"
```

未配置 key 时，每个工具都会返回结构化的获取引导。

## 安装与运行（本地 stdio）

需要 Python ≥ 3.10，推荐使用 [uv](https://docs.astral.sh/uv/)：

```bash
uvx redfox-auto-mcp
```

或：

```bash
pip install redfox-auto-mcp
redfox-auto-mcp
```

## 客户端配置

Claude Code：

```bash
claude mcp add redfox-auto --env REDFOX_API_KEY=YOUR_API_KEY -- uvx redfox-auto-mcp
```

Cursor / 其他 MCP 客户端：

```json
{
  "mcpServers": {
    "redfox-auto": {
      "command": "uvx",
      "args": ["redfox-auto-mcp"],
      "env": { "REDFOX_API_KEY": "YOUR_API_KEY" }
    }
  }
}
```

## 远程 HTTP 模式（多租户）

适用于 MCP 市场与托管场景，每个用户携带自己的 API Key：

```bash
redfox-auto-mcp --transport http --host 0.0.0.0 --port 8000
# 或环境变量：REDFOX_MCP_TRANSPORT=http REDFOX_MCP_HOST=0.0.0.0 REDFOX_MCP_PORT=8000
```

- MCP 端点：`http://<host>:8000/mcp`（Streamable HTTP）；健康检查：`GET /health`
- 每个请求通过请求头 `X-API-Key: <key>`（或 `Authorization: Bearer <key>`）携带自己的 key，按 key 建独立客户端缓存，额度互不共享

客户端配置（远程 URL + 请求头）：

```json
{
  "mcpServers": {
    "redfox-auto": {
      "url": "http://<host>:8000/mcp",
      "headers": { "X-API-Key": "ak_your_key" }
    }
  }
}
```

## Docker 部署

本包目录自带 Dockerfile，可独立构建部署：

```bash
cd packages/redfox-auto-mcp
docker build -t redfox-auto-mcp .
docker run -d -p 8000:8000 redfox-auto-mcp
```

镜像不内置任何 API Key，调用方通过请求头携带自己的 key。

## 底层实现

基于官方 SDK [redfox-python-sdk](https://github.com/redfox-data/redfox-python-sdk)。API 文档：<https://redfox.hk/?source=mcp>。

## License

MIT
