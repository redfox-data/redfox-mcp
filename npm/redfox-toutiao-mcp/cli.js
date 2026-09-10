#!/usr/bin/env node
"use strict";

const { spawn } = require("child_process");
const path = require("path");
const fs = require("fs");

const SERVER = "toutiao";
const binPkg = `redfox-mcp-bin-${process.platform}-${process.arch}`;
const binName = process.platform === "win32" ? "redfox-mcp.exe" : "redfox-mcp";

function findBin() {
  // 1) npm-installed platform package (hoisted or nested)
  try {
    const pkgJson = require.resolve(`${binPkg}/package.json`);
    return path.join(path.dirname(pkgJson), "bin", binName);
  } catch (e) { /* not resolvable, fall through */ }
  // 2) monorepo sibling directory (local development)
  const sibling = path.join(__dirname, "..", binPkg, "bin", binName);
  if (fs.existsSync(sibling)) return sibling;
  return null;
}

const binPath = findBin();
if (!binPath || !fs.existsSync(binPath)) {
  process.stderr.write(
    `Error: no RedFox MCP binary for ${process.platform}-${process.arch}.\n` +
    `Supported platforms: darwin-arm64, win32-x64\n`
  );
  process.exit(1);
}

try { fs.chmodSync(binPath, 0o755); } catch (e) { /* windows: no-op */ }

const child = spawn(binPath, [SERVER, ...process.argv.slice(2)], { stdio: "inherit" });
child.on("exit", (code, sig) => process.exit(code ?? (sig ? 1 : 0)));
child.on("error", (err) => {
  process.stderr.write(`Failed to start redfox-mcp: ${err.message}\n`);
  process.exit(1);
});
