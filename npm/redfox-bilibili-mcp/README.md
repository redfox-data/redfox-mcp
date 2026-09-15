# redfox-bilibili-mcp

RedFoxHub Bilibili MCP server — installable via npm, zero Python dependencies.

## Install

```bash
npm install -g redfox-bilibili-mcp
```

## Usage

```bash
# Set your API key
export REDFOX_API_KEY=ak_your_key

# Run MCP server (stdio mode, for local MCP clients)
redfox-bilibili-mcp

# Run MCP server (HTTP mode)
redfox-bilibili-mcp --transport http --host 0.0.0.0 --port 8000
```

## MCP Client Configuration

```json
{
  "mcpServers": {
    "redfox-bilibili-mcp": {
      "command": "npx",
      "args": ["-y", "redfox-bilibili-mcp"],
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
`uvx redfox-bilibili-mcp` or `pipx install redfox-bilibili-mcp` (pure Python, any platform).

## API Key

Get your API key at: https://redfox.hk/settings/api-keys?source=mcp

## License

MIT
