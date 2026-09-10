#!/usr/bin/env python3
"""Generate npm package scaffolding for all RedFox MCP servers.

Usage:
    python npm/generate.py

Creates one npm package per MCP server under npm/, each containing:
  - package.json  (npm metadata + bin entry)
  - cli.js        (platform-detecting binary launcher)
  - _entry.py     (PyInstaller build entry point)

Binary artifacts go into each package's bin/<platform>-<arch>/ directory,
populated by the CI build pipeline (not checked into git).
"""

import json
import os
import textwrap

ROOT = os.path.dirname(os.path.abspath(__file__))

# (pypi_name, npm_name, binary_name, python_module, description)
PACKAGES = [
    ("redfox-douyin-mcp", "redfox-douyin-mcp", "redfox-douyin-mcp",
     "redfox_douyin_mcp", "RedFoxHub Douyin MCP server"),
    ("redfox-xiaohongshu-mcp", "redfox-xiaohongshu-mcp", "redfox-xiaohongshu-mcp",
     "redfox_xiaohongshu_mcp", "RedFoxHub Xiaohongshu MCP server"),
    ("redfox-wechat-mcp", "redfox-wechat-mcp", "redfox-wechat-mcp",
     "redfox_wechat_mcp", "RedFoxHub WeChat MCP server"),
    ("redfox-bilibili-mcp", "redfox-bilibili-mcp", "redfox-bilibili-mcp",
     "redfox_bilibili_mcp", "RedFoxHub Bilibili MCP server"),
    ("redfox-toutiao-mcp", "redfox-toutiao-mcp", "redfox-toutiao-mcp",
     "redfox_toutiao_mcp", "RedFoxHub Toutiao MCP server"),
    ("redfox-tiktok-mcp", "redfox-tiktok-mcp", "redfox-tiktok-mcp",
     "redfox_tiktok_mcp", "RedFoxHub TikTok MCP server"),
    ("redfox-ai-search-mcp", "redfox-ai-search-mcp", "redfox-ai-search-mcp",
     "redfox_ai_search_mcp", "RedFoxHub AI Search MCP server"),
    ("redfox-ai-gen-mcp", "redfox-ai-gen-mcp", "redfox-ai-gen-mcp",
     "redfox_ai_gen_mcp", "RedFoxHub AI Generation MCP server"),
    ("redfox-twitter-mcp", "redfox-twitter-mcp", "redfox-twitter-mcp",
     "redfox_twitter_mcp", "RedFoxHub X(Twitter) MCP server"),
    ("redfox-youtube-mcp", "redfox-youtube-mcp", "redfox-youtube-mcp",
     "redfox_youtube_mcp", "RedFoxHub YouTube MCP server"),
    ("redfox-instagram-mcp", "redfox-instagram-mcp", "redfox-instagram-mcp",
     "redfox_instagram_mcp", "RedFoxHub Instagram MCP server"),
    ("redfox-kuaishou-mcp", "redfox-kuaishou-mcp", "redfox-kuaishou-mcp",
     "redfox_kuaishou_mcp", "RedFoxHub Kuaishou MCP server"),
    ("redfox-auto-mcp", "redfox-auto-mcp", "redfox-auto-mcp",
     "redfox_auto_mcp", "RedFoxHub Auto MCP server"),
    ("redfox-wechat-channels-mcp", "redfox-wechat-channels-mcp", "redfox-wechat-channels-mcp",
     "redfox_wechat_channels_mcp", "RedFoxHub WeChat Channels MCP server"),
    ("redfox-tools-mcp", "redfox-tools-mcp", "redfox-tools-mcp",
     "redfox_tools_mcp", "RedFoxHub Tools MCP server"),
    ("redfox-mcp", "redfox-mcp", "redfox-mcp",
     "redfox_mcp", "RedFoxHub MCP server (all-in-one, 13 platforms)"),
]

CLI_TEMPLATE = '''#!/usr/bin/env node
"use strict";

const {{ spawn }} = require("child_process");
const path = require("path");
const os = require("os");
const fs = require("fs");

const platform = os.platform();
const arch = os.arch();
const dirName = `${{platform}}-${{arch}}`;
const binName = platform === "win32" ? "{binary_name}.exe" : "{binary_name}";
const binPath = path.join(__dirname, "bin", dirName, binName);

if (!fs.existsSync(binPath)) {{
  process.stderr.write(
    `Error: No binary found for ${{dirName}}.\\n` +
    `Expected: ${{binPath}}\\n` +
    `Supported: darwin-arm64, darwin-x64, linux-x64, win32-x64\\n`
  );
  process.exit(1);
}}

fs.chmodSync(binPath, 0o755);

const child = spawn(binPath, process.argv.slice(2), {{ stdio: "inherit" }});
child.on("exit", (code) => process.exit(code ?? 1));
child.on("error", (err) => {{
  process.stderr.write(`Failed to start {binary_name}: ${{err.message}}\\n`);
  process.exit(1);
}});
'''

ENTRY_TEMPLATE = '''"""PyInstaller entry point for {pypi_name}."""
from {module}.server import main

if __name__ == "__main__":
    main()
'''


def read_version(pypi_name):
    """Read current version from the Python package's pyproject.toml."""
    toml_path = os.path.join(ROOT, "..", "packages", pypi_name, "pyproject.toml")
    toml_path = os.path.normpath(toml_path)
    if not os.path.exists(toml_path):
        return "0.1.0"
    with open(toml_path) as f:
        for line in f:
            line = line.strip()
            if line.startswith("version"):
                return line.split('"')[1]
    return "0.1.0"


def generate_package(pypi_name, npm_name, binary_name, module, description):
    pkg_dir = os.path.join(ROOT, npm_name)
    os.makedirs(pkg_dir, exist_ok=True)

    version = read_version(pypi_name)

    # ── package.json ──
    pkg_json = {
        "name": npm_name,
        "version": version,
        "description": description,
        "bin": {binary_name: "./cli.js"},
        "files": ["cli.js", "bin/", "README.md"],
        "keywords": ["mcp", "redfox", "ai", "model-context-protocol"],
        "license": "MIT",
        "repository": {
            "type": "git",
            "url": "https://github.com/redfox-data/redfox-mcp",
            "directory": f"npm/{npm_name}",
        },
        "homepage": "https://redfox.hk",
        "engines": {"node": ">=14"},
        "os": ["darwin", "linux", "win32"],
        "cpu": ["arm64", "x64"],
    }
    with open(os.path.join(pkg_dir, "package.json"), "w") as f:
        json.dump(pkg_json, f, indent=2)
        f.write("\n")

    # ── cli.js ──
    cli_content = CLI_TEMPLATE.format(binary_name=binary_name)
    with open(os.path.join(pkg_dir, "cli.js"), "w") as f:
        f.write(cli_content)

    # ── _entry.py (PyInstaller build target) ──
    entry_content = ENTRY_TEMPLATE.format(pypi_name=pypi_name, module=module)
    with open(os.path.join(pkg_dir, "_entry.py"), "w") as f:
        f.write(entry_content)

    # ── README.md ──
    readme = textwrap.dedent(f"""\
        # {npm_name}

        {description} — installable via npm, zero Python dependencies.

        ## Install

        ```bash
        npm install -g {npm_name}
        ```

        ## Usage

        ```bash
        # Set your API key
        export REDFOX_API_KEY=ak_your_key

        # Run MCP server (stdio mode, for local MCP clients)
        {binary_name}

        # Run MCP server (HTTP mode)
        {binary_name} --transport http --host 0.0.0.0 --port 8000
        ```

        ## MCP Client Configuration

        ```json
        {{
          "mcpServers": {{
            "{npm_name}": {{
              "command": "npx",
              "args": ["-y", "{npm_name}"],
              "env": {{
                "REDFOX_API_KEY": "ak_your_key"
              }}
            }}
          }}
        }}
        ```

        ## API Key

        Get your API key at: https://redfox.hk/settings/api-keys?source=mcp

        ## License

        MIT
    """)
    with open(os.path.join(pkg_dir, "README.md"), "w") as f:
        f.write(readme)

    # ── .gitignore (ignore compiled binaries) ──
    with open(os.path.join(pkg_dir, ".gitignore"), "w") as f:
        f.write("bin/\nnode_modules/\n")

    print(f"  ✓ {npm_name} v{version}")


def main():
    print(f"Generating npm packages in {ROOT}\n")
    for pkg in PACKAGES:
        generate_package(*pkg)
    print(f"\nDone! {len(PACKAGES)} npm packages generated.")
    print("\nNext steps:")
    print("  1. cd npm/<package-name>")
    print("  2. npm publish  (after CI builds binaries into bin/)")


if __name__ == "__main__":
    main()
