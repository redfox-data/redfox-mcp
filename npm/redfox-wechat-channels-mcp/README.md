# redfox-wechat-channels-mcp

RedFoxHub WeChat Channels MCP server — installable via npm, zero Python dependencies.

## Install

```bash
npm install -g redfox-wechat-channels-mcp
```

## Usage

```bash
# Set your API key
export REDFOX_API_KEY=ak_your_key

# Run MCP server (stdio mode, for local MCP clients)
redfox-wechat-channels-mcp

# Run MCP server (HTTP mode)
redfox-wechat-channels-mcp --transport http --host 0.0.0.0 --port 8000
```

## MCP Client Configuration

```json
{
  "mcpServers": {
    "redfox-wechat-channels-mcp": {
      "command": "npx",
      "args": ["-y", "redfox-wechat-channels-mcp"],
      "env": {
        "REDFOX_API_KEY": "ak_your_key"
      }
    }
  }
}
```

## Platforms

macOS (Apple Silicon) and Windows (x64). The matching native binary
is pulled in automatically via optionalDependencies.

## API Key

Get your API key at: https://redfox.hk/settings/api-keys?source=mcp

## License

MIT
