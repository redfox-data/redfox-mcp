# redfox-tools-mcp

RedFoxHub Tools MCP server — installable via npm, zero Python dependencies.

## Install

```bash
npm install -g redfox-tools-mcp
```

## Usage

```bash
# Set your API key
export REDFOX_API_KEY=ak_your_key

# Run MCP server (stdio mode, for local MCP clients)
redfox-tools-mcp

# Run MCP server (HTTP mode)
redfox-tools-mcp --transport http --host 0.0.0.0 --port 8000
```

## MCP Client Configuration

```json
{
  "mcpServers": {
    "redfox-tools-mcp": {
      "command": "npx",
      "args": ["-y", "redfox-tools-mcp"],
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
