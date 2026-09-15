# redfox-toutiao-mcp

RedFoxHub Toutiao MCP server — installable via npm, zero Python dependencies.

## Install

```bash
npm install -g redfox-toutiao-mcp
```

## Usage

```bash
# Set your API key
export REDFOX_API_KEY=ak_your_key

# Run MCP server (stdio mode, for local MCP clients)
redfox-toutiao-mcp

# Run MCP server (HTTP mode)
redfox-toutiao-mcp --transport http --host 0.0.0.0 --port 8000
```

## MCP Client Configuration

```json
{
  "mcpServers": {
    "redfox-toutiao-mcp": {
      "command": "npx",
      "args": ["-y", "redfox-toutiao-mcp"],
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
`uvx redfox-toutiao-mcp` or `pipx install redfox-toutiao-mcp` (pure Python, any platform).

## API Key

Get your API key at: https://redfox.hk/settings/api-keys?source=mcp

## License

MIT
