#!/usr/bin/env node
"use strict";

const { spawn } = require("child_process");
const path = require("path");
const os = require("os");
const fs = require("fs");

const platform = os.platform();
const arch = os.arch();
const dirName = `${platform}-${arch}`;
const binName = platform === "win32" ? "redfox-douyin-mcp.exe" : "redfox-douyin-mcp";
const binPath = path.join(__dirname, "bin", dirName, binName);

if (!fs.existsSync(binPath)) {
  process.stderr.write(
    `Error: No binary found for ${dirName}.\n` +
    `Expected: ${binPath}\n` +
    `Supported: darwin-arm64, darwin-x64, linux-x64, win32-x64\n`
  );
  process.exit(1);
}

fs.chmodSync(binPath, 0o755);

const child = spawn(binPath, process.argv.slice(2), { stdio: "inherit" });
child.on("exit", (code) => process.exit(code ?? 1));
child.on("error", (err) => {
  process.stderr.write(`Failed to start redfox-douyin-mcp: ${err.message}\n`);
  process.exit(1);
});
