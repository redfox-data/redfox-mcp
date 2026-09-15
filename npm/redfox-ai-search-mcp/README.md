# redfox-ai-search-mcp

RedFoxHub AI Search MCP server — installable via npm, zero Python dependencies.

## Install

```bash
npm install -g redfox-ai-search-mcp
```

## Usage

```bash
# Set your API key
export REDFOX_API_KEY=ak_your_key

# Run MCP server (stdio mode, for local MCP clients)
redfox-ai-search-mcp

# Run MCP server (HTTP mode)
redfox-ai-search-mcp --transport http --host 0.0.0.0 --port 8000
```

## MCP Client Configuration

```json
{
  "mcpServers": {
    "redfox-ai-search-mcp": {
      "command": "npx",
      "args": ["-y", "redfox-ai-search-mcp"],
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
`uvx redfox-ai-search-mcp` or `pipx install redfox-ai-search-mcp` (pure Python, any platform).

## API Key

Get your API key at: https://redfox.hk/settings/api-keys?source=mcp

## License

MIT
