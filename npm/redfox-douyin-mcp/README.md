# redfox-douyin-mcp

RedFoxHub Douyin MCP server — installable via npm, zero Python dependencies.

## Install

```bash
npm install -g redfox-douyin-mcp
```

## Usage

```bash
# Set your API key
export REDFOX_API_KEY=ak_your_key

# Run MCP server (stdio mode, for local MCP clients)
redfox-douyin-mcp

# Run MCP server (HTTP mode)
redfox-douyin-mcp --transport http --host 0.0.0.0 --port 8000
```

HTTP 模式建连时必须在请求头携带 API Key（`REDFOX_API_KEY` 或
`Authorization: Bearer ak_xxx`），否则返回 401、不创建 session。
`/health` 探活无需 Key。紧急排查可设 `REDFOX_MCP_REQUIRE_API_KEY=0`
关闭拦截（仍会打建连日志）。

## MCP Client Configuration

### stdio（本地）

```json
{
  "mcpServers": {
    "redfox-douyin-mcp": {
      "command": "npx",
      "args": ["-y", "redfox-douyin-mcp"],
      "env": {
        "REDFOX_API_KEY": "ak_your_key"
      }
    }
  }
}
```

### HTTP（远程 / 自建）

```json
{
  "mcpServers": {
    "redfox-douyin-mcp": {
      "url": "http://127.0.0.1:8000/mcp",
      "headers": {
        "REDFOX_API_KEY": "ak_your_key"
      }
    }
  }
}
```

## Platforms

macOS (Apple Silicon) and Windows (x64). The matching native binary is
pulled in automatically via optionalDependencies.

Intel Mac (darwin-x64) has no npm binary — the macos-13 CI runner is too
scarce to build it reliably. Install from PyPI instead:
`uvx redfox-douyin-mcp` or `pipx install redfox-douyin-mcp` (pure Python, any platform).

## API Key

Get your API key at: https://redfox.hk/settings/api-keys?source=mcp

## License

MIT
