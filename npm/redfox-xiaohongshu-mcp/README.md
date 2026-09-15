# redfox-xiaohongshu-mcp

RedFoxHub Xiaohongshu MCP server — installable via npm, zero Python dependencies.

## Install

```bash
npm install -g redfox-xiaohongshu-mcp
```

## Usage

```bash
# Set your API key
export REDFOX_API_KEY=ak_your_key

# Run MCP server (stdio mode, for local MCP clients)
redfox-xiaohongshu-mcp

# Run MCP server (HTTP mode)
redfox-xiaohongshu-mcp --transport http --host 0.0.0.0 --port 8000
```

## MCP Client Configuration

```json
{
  "mcpServers": {
    "redfox-xiaohongshu-mcp": {
      "command": "npx",
      "args": ["-y", "redfox-xiaohongshu-mcp"],
      "env": {
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
`uvx redfox-xiaohongshu-mcp` or `pipx install redfox-xiaohongshu-mcp` (pure Python, any platform).

## API Key

Get your API key at: https://redfox.hk/settings/api-keys?source=mcp

## License

MIT
