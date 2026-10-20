# redfox-data-mcp

红狐数据的单一 MCP 服务。模型只看到 4 个工具，背后是现有各平台接口的同一批 SDK 调用。

| 工具 | 作用 |
| --- | --- |
| `find` | 用一句话找能力，最多 10 条。按词匹配，没有匹配不换平台 |
| `describe` | 读 1 到 10 个能力的参数和示例 |
| `call` | 按能力编号调用一次。参数不合法时不请求上游 |
| `result` | 用 `call` 超时返回的 `taskId` 查询异步任务 |

HTTP 模式在进入会话前检查 API Key（`REDFOX_API_KEY` 或 `Authorization: Bearer`）。`/health` 除外。打到 SDK 的调用走 `redfox-mcp-core` 的 `call()`，因此 `REDFOX_MCP_LOG=1` 时仍写 `mcp_call`。

远程地址：`https://mcp.redfox.hk/data/mcp`

```json
{
  "mcpServers": {
    "redfox-data": {
      "url": "https://mcp.redfox.hk/data/mcp",
      "headers": { "REDFOX_API_KEY": "YOUR_API_KEY" }
    }
  }
}
```

本地：

```bash
export REDFOX_API_KEY="YOUR_API_KEY"
python -m redfox_data_mcp --transport http --host 0.0.0.0 --port 8080
```

目录由 `scripts/extract_catalog.py` 从现有 `redfox-*-mcp` 的 `server.py` 生成。那些包本身没有改动。
