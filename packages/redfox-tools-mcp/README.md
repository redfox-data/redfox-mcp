# redfox-tools-mcp

RedFoxHub 工具类 MCP Server — 多平台作品下载与素材上传共 12 个 MCP 工具，适用于 dsh、Claude Code、Cursor 等任意 MCP 客户端。

## 工具（12）

| 工具 | 分类 | 说明 |
|---|---|---|
| `tools_download` | 下载 | 通用解析下载（任意平台作品链接） |
| `tools_download_douyin` | 下载 | 抖音作品下载 |
| `tools_download_kuaishou` | 下载 | 快手作品下载 |
| `tools_download_xiaohongshu` | 下载 | 小红书作品下载 |
| `tools_download_bilibili` | 下载 | B 站作品下载 |
| `tools_download_wechat_channels` | 下载 | 微信视频号作品下载 |
| `tools_download_tiktok` | 下载 | TikTok 作品下载 |
| `tools_download_youtube` | 下载 | YouTube 视频下载 |
| `tools_download_instagram` | 下载 | Instagram 作品下载 |
| `tools_download_twitter` | 下载 | X(Twitter) 作品下载 |
| `tools_upload_image` | 上传 | 上传图片（png/jpeg/webp），返回 URL |
| `tools_upload_file` | 上传 | 上传文件（视频≤50MB / 音频≤20MB / 图像≤10MB） |

上传类工具接收**本地文件路径**，由 server 打开文件后交给 SDK 上传。

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
uvx redfox-tools-mcp
```

或：

```bash
pip install redfox-tools-mcp
redfox-tools-mcp
```

## 客户端配置

Claude Code：

```bash
claude mcp add redfox-tools --env REDFOX_API_KEY=YOUR_API_KEY -- uvx redfox-tools-mcp
```

Cursor / 其他 MCP 客户端：

```json
{
  "mcpServers": {
    "redfox-tools": {
      "command": "uvx",
      "args": ["redfox-tools-mcp"],
      "env": { "REDFOX_API_KEY": "YOUR_API_KEY" }
    }
  }
}
```

## 远程 HTTP 模式（多租户）

适用于 MCP 市场与托管场景，每个用户携带自己的 API Key：

```bash
redfox-tools-mcp --transport http --host 0.0.0.0 --port 8000
# 或环境变量：REDFOX_MCP_TRANSPORT=http REDFOX_MCP_HOST=0.0.0.0 REDFOX_MCP_PORT=8000
```

- MCP 端点：`http://<host>:8000/mcp`（Streamable HTTP）；健康检查：`GET /health`
- 每个请求通过请求头 `X-API-Key: <key>`（或 `Authorization: Bearer <key>`）携带自己的 key，按 key 建独立客户端缓存，额度互不共享
- 注意：上传类工具读取的是 **server 所在机器**的本地文件路径，远程模式下请先将文件放到服务端可访问的路径

客户端配置（远程 URL + 请求头）：

```json
{
  "mcpServers": {
    "redfox-tools": {
      "url": "http://<host>:8000/mcp",
      "headers": { "X-API-Key": "ak_your_key" }
    }
  }
}
```

## Docker 部署

本包目录自带 Dockerfile，可独立构建部署：

```bash
cd packages/redfox-tools-mcp
docker build -t redfox-tools-mcp .
docker run -d -p 8000:8000 redfox-tools-mcp
```

镜像不内置任何 API Key，调用方通过请求头携带自己的 key。

## 底层实现

基于官方 SDK [redfox-python-sdk](https://github.com/redfox-data/redfox-python-sdk)。API 文档：<https://redfox.hk/?source=mcp>。

## License

MIT
