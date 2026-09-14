#!/usr/bin/env python3
"""Generate npm package scaffolding for all RedFox MCP servers (busybox mode).

Usage:
    python npm/generate.py [--version 0.4.1]

Architecture:
  - 16 lightweight main packages (redfox-douyin-mcp, ...): ~5KB each,
    cli.js spawns the shared platform binary with the server name as argv[1].
  - 2 platform binary packages (redfox-mcp-bin-<platform>): one busybox
    binary containing ALL servers, installed via optionalDependencies
    (npm picks the one matching the current os/cpu automatically).

Binaries themselves are compiled by CI into redfox-mcp-bin-*/bin/ (gitignored).
"""

import json
import os
import shutil
import sys
import textwrap

ROOT = os.path.dirname(os.path.abspath(__file__))
VERSION = "0.4.2"

# (os, cpu, npm name suffix) — win32 uses "windows" in the package name:
# the literal token "win32" triggers npm registry spam detection on PUT.
# darwin-arm64 / windows-x64 are compiled by CI; darwin-x64 has no CI runner
# (macos-13 x64 images are scarce) — its binary is built on an Intel Mac and
# published manually before tagging; CI skips it via the idempotency check.
BIN_PLATFORMS = [
    ("darwin", "arm64", "darwin-arm64"),
    ("darwin", "x64", "darwin-x64"),
    ("win32", "x64", "windows-x64"),
]

# (npm_name, server_name, description)
PACKAGES = [
    ("redfox-douyin-mcp", "douyin", "RedFoxHub Douyin MCP server"),
    ("redfox-xiaohongshu-mcp", "xiaohongshu", "RedFoxHub Xiaohongshu MCP server"),
    ("redfox-wechat-mcp", "wechat", "RedFoxHub WeChat MCP server"),
    ("redfox-bilibili-mcp", "bilibili", "RedFoxHub Bilibili MCP server"),
    ("redfox-toutiao-mcp", "toutiao", "RedFoxHub Toutiao MCP server"),
    ("redfox-tiktok-mcp", "tiktok", "RedFoxHub TikTok MCP server"),
    ("redfox-ai-search-mcp", "ai-search", "RedFoxHub AI Search MCP server"),
    ("redfox-ai-gen-mcp", "ai-gen", "RedFoxHub AI Generation MCP server"),
    ("redfox-twitter-mcp", "twitter", "RedFoxHub X(Twitter) MCP server"),
    ("redfox-youtube-mcp", "youtube", "RedFoxHub YouTube MCP server"),
    ("redfox-instagram-mcp", "instagram", "RedFoxHub Instagram MCP server"),
    ("redfox-kuaishou-mcp", "kuaishou", "RedFoxHub Kuaishou MCP server"),
    ("redfox-auto-mcp", "auto", "RedFoxHub Auto MCP server"),
    ("redfox-wechat-channels-mcp", "wechat-channels", "RedFoxHub WeChat Channels MCP server"),
    ("redfox-tools-mcp", "tools", "RedFoxHub Tools MCP server"),
    ("redfox-mcp", "all", "RedFoxHub MCP server (all-in-one, 13 platforms)"),
]

CLI_TEMPLATE = '''#!/usr/bin/env node
"use strict";

const {{ spawn }} = require("child_process");
const path = require("path");
const fs = require("fs");

const SERVER = "{server_name}";
// Package name suffix maps win32 -> windows (npm spam filter avoids "win32").
const platSeg = process.platform === "win32" ? "windows" : process.platform;
const binPkg = `redfox-mcp-bin-${{platSeg}}-${{process.arch}}`;
const binName = process.platform === "win32" ? "redfox-mcp.exe" : "redfox-mcp";

function findBin() {{
  // 1) npm-installed platform package (hoisted or nested)
  try {{
    const pkgJson = require.resolve(`${{binPkg}}/package.json`);
    return path.join(path.dirname(pkgJson), "bin", binName);
  }} catch (e) {{ /* not resolvable, fall through */ }}
  // 2) monorepo sibling directory (local development)
  const sibling = path.join(__dirname, "..", binPkg, "bin", binName);
  if (fs.existsSync(sibling)) return sibling;
  return null;
}}

const binPath = findBin();
if (!binPath || !fs.existsSync(binPath)) {{
  process.stderr.write(
    `Error: no RedFox MCP binary for ${{process.platform}}-${{process.arch}}.\\n` +
    `Supported platforms: darwin-arm64, darwin-x64, win32-x64 (package: windows-x64)\\n`
  );
  process.exit(1);
}}

try {{ fs.chmodSync(binPath, 0o755); }} catch (e) {{ /* windows: no-op */ }}

const child = spawn(binPath, [SERVER, ...process.argv.slice(2)], {{ stdio: "inherit" }});
child.on("exit", (code, sig) => process.exit(code ?? (sig ? 1 : 0)));
child.on("error", (err) => {{
  process.stderr.write(`Failed to start redfox-mcp: ${{err.message}}\\n`);
  process.exit(1);
}});
'''


def bin_pkg_name(platform, arch, suffix=None):
    if suffix is None:
        suffix = "windows-x64" if platform == "win32" else f"{platform}-{arch}"
    return f"redfox-mcp-bin-{suffix}"


def generate_main_package(npm_name, server_name, description, version):
    pkg_dir = os.path.join(ROOT, npm_name)
    os.makedirs(pkg_dir, exist_ok=True)

    # Legacy per-package build entry is obsolete in busybox mode.
    old_entry = os.path.join(pkg_dir, "_entry.py")
    if os.path.exists(old_entry):
        os.remove(old_entry)

    pkg_json = {
        "name": npm_name,
        "version": version,
        "description": description,
        "bin": {npm_name: "./cli.js"},
        "files": ["cli.js", "README.md"],
        "keywords": ["mcp", "redfox", "ai", "model-context-protocol"],
        "license": "MIT",
        "repository": {
            "type": "git",
            "url": "https://github.com/redfox-data/redfox-mcp",
            "directory": f"npm/{npm_name}",
        },
        "homepage": "https://redfox.hk",
        "engines": {"node": ">=14"},
        "optionalDependencies": {
            bin_pkg_name(p, a, s): version for p, a, s in BIN_PLATFORMS
        },
    }
    with open(os.path.join(pkg_dir, "package.json"), "w") as f:
        json.dump(pkg_json, f, indent=2)
        f.write("\n")

    with open(os.path.join(pkg_dir, "cli.js"), "w") as f:
        f.write(CLI_TEMPLATE.format(server_name=server_name))

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
        {npm_name}

        # Run MCP server (HTTP mode)
        {npm_name} --transport http --host 0.0.0.0 --port 8000
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

        ## Platforms

        macOS (Apple Silicon and Intel) and Windows (x64). The matching native
        binary is pulled in automatically via optionalDependencies.

        ## API Key

        Get your API key at: https://redfox.hk/settings/api-keys?source=mcp

        ## License

        MIT
    """)
    with open(os.path.join(pkg_dir, "README.md"), "w") as f:
        f.write(readme)

    with open(os.path.join(pkg_dir, ".gitignore"), "w") as f:
        f.write("node_modules/\n")

    print(f"  ✓ {npm_name} v{version} (server: {server_name})")


def generate_bin_package(platform, arch, suffix, version):
    name = bin_pkg_name(platform, arch, suffix)
    pkg_dir = os.path.join(ROOT, name)
    os.makedirs(pkg_dir, exist_ok=True)

    pkg_json = {
        "name": name,
        "version": version,
        "description": f"RedFox MCP native binary for {platform}-{arch} (busybox, all servers)",
        "files": ["bin/", "README.md"],
        "license": "MIT",
        "repository": {
            "type": "git",
            "url": "https://github.com/redfox-data/redfox-mcp",
            "directory": f"npm/{name}",
        },
        "os": [platform],
        "cpu": [arch],
    }
    with open(os.path.join(pkg_dir, "package.json"), "w") as f:
        json.dump(pkg_json, f, indent=2)
        f.write("\n")

    readme = (
        f"# {name}\n\n"
        f"Platform binary package for RedFox MCP servers ({platform}-{arch}).\n"
        "Do not install directly — install `redfox-douyin-mcp` or any other\n"
        "RedFox MCP package and npm will pull this in automatically.\n"
    )
    with open(os.path.join(pkg_dir, "README.md"), "w") as f:
        f.write(readme)

    # NOTE: no .gitignore here — npm pack would honour it and exclude bin/.
    # Binaries stay out of git via the repo-root .gitignore (npm/*/bin/).
    old_ignore = os.path.join(pkg_dir, ".gitignore")
    if os.path.exists(old_ignore):
        os.remove(old_ignore)

    print(f"  ✓ {name} v{version}")


def main():
    version = VERSION
    if "--version" in sys.argv:
        version = sys.argv[sys.argv.index("--version") + 1]

    print(f"Generating npm packages in {ROOT} (version {version})\n")
    print("Main packages:")
    for npm_name, server_name, description in PACKAGES:
        generate_main_package(npm_name, server_name, description, version)
    print("Platform binary packages:")
    for platform, arch, suffix in BIN_PLATFORMS:
        generate_bin_package(platform, arch, suffix, version)

    total = len(PACKAGES) + len(BIN_PLATFORMS)
    print(f"\nDone! {total} npm packages generated (busybox mode).")
    print("Next: bash npm/build-binaries.sh  (compiles the shared binary)")


if __name__ == "__main__":
    main()
