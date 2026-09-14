# redfox-mcp

RedFoxHub MCP server (all-in-one, 13 platforms) — installable via npm, zero Python dependencies.

## Install

```bash
npm install -g redfox-mcp
```

## Usage

```bash
# Set your API key
export REDFOX_API_KEY=ak_your_key

# Run MCP server (stdio mode, for local MCP clients)
redfox-mcp

# Run MCP server (HTTP mode)
redfox-mcp --transport http --host 0.0.0.0 --port 8000
```

## MCP Client Configuration

```json
{
  "mcpServers": {
    "redfox-mcp": {
      "command": "npx",
      "args": ["-y", "redfox-mcp"],
      "env": {
        "REDFOX_API_KEY": "ak_your_key"
      }
    }
  }
}
```

## Platforms

macOS (Apple Silicon and Intel) and Windows (x64). The matching native
binary is pulled in automatically via optionalDependencies.

## API Key

Get your API key at: https://redfox.hk/settings/api-keys?source=mcp

## License

MIT
