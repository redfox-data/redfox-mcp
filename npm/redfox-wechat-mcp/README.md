# redfox-wechat-mcp

RedFoxHub WeChat MCP server — installable via npm, zero Python dependencies.

## Install

```bash
npm install -g redfox-wechat-mcp
```

## Usage

```bash
# Set your API key
export REDFOX_API_KEY=ak_your_key

# Run MCP server (stdio mode, for local MCP clients)
redfox-wechat-mcp

# Run MCP server (HTTP mode)
redfox-wechat-mcp --transport http --host 0.0.0.0 --port 8000
```

## MCP Client Configuration

```json
{
  "mcpServers": {
    "redfox-wechat-mcp": {
      "command": "npx",
      "args": ["-y", "redfox-wechat-mcp"],
      "env": {
        "REDFOX_API_KEY": "ak_your_key"
      }
    }
  }
}
```

## API Key

Get your API key at: https://redfox.hk/settings/api-keys?source=mcp

## License

MIT
