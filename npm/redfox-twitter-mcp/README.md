# redfox-twitter-mcp

RedFoxHub X(Twitter) MCP server — installable via npm, zero Python dependencies.

## Install

```bash
npm install -g redfox-twitter-mcp
```

## Usage

```bash
# Set your API key
export REDFOX_API_KEY=ak_your_key

# Run MCP server (stdio mode, for local MCP clients)
redfox-twitter-mcp

# Run MCP server (HTTP mode)
redfox-twitter-mcp --transport http --host 0.0.0.0 --port 8000
```

## MCP Client Configuration

```json
{
  "mcpServers": {
    "redfox-twitter-mcp": {
      "command": "npx",
      "args": ["-y", "redfox-twitter-mcp"],
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
