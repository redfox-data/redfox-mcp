#!/usr/bin/env bash
# Build the single RedFox MCP busybox binary for one platform.
# Output: npm/redfox-mcp-bin-<platform>/bin/redfox-mcp[.exe]
#
# Usage:
#   bash npm/build-binaries.sh [--platform darwin-arm64]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# ── Cross-platform python detection ──
if command -v python3 &>/dev/null; then
  PY=python3
elif command -v python &>/dev/null; then
  PY=python
else
  echo "Error: python3/python not found"; exit 1
fi

# ── Detect platform ──
detect_platform() {
  local os arch
  os=$(uname -s | tr '[:upper:]' '[:lower:]')
  arch=$(uname -m)
  case "$arch" in x86_64|amd64) arch="x64" ;; aarch64|arm64) arch="arm64" ;; esac
  # MSYS/MINGW/CYGWIN → win32
  case "$os" in msys*|mingw*|cygwin*) os="win32" ;; esac
  echo "${os}-${arch}"
}

PLATFORM=$(detect_platform)

while [[ $# -gt 0 ]]; do
  case $1 in
    --platform) PLATFORM="$2"; shift 2 ;;
    *) echo "Unknown: $1"; exit 1 ;;
  esac
done

IS_WINDOWS=false
[[ "$PLATFORM" == win32-* ]] && IS_WINDOWS=true

BIN_NAME="redfox-mcp"
$IS_WINDOWS && BIN_NAME="redfox-mcp.exe"

OUT_DIR="$SCRIPT_DIR/redfox-mcp-bin-$PLATFORM/bin"
WORK_DIR="${TMPDIR:-${TEMP:-/tmp}}/pyi-redfox-mcp"
mkdir -p "$OUT_DIR"

echo "=== RedFox MCP busybox binary build ==="
echo "Platform: $PLATFORM | Python: $PY"

# ── Check PyInstaller ──
if ! $PY -c "import PyInstaller" 2>/dev/null; then
  echo "Installing PyInstaller..."
  $PY -m pip install pyinstaller
fi

$PY -m PyInstaller \
  --onefile \
  --name redfox-mcp \
  --distpath "$OUT_DIR" \
  --workpath "$WORK_DIR" \
  --specpath "$WORK_DIR" \
  --noconfirm \
  --clean \
  --copy-metadata fastmcp \
  --copy-metadata fastmcp-slim \
  --copy-metadata redfox-python-sdk \
  --copy-metadata redfox-mcp-core \
  --copy-metadata mcp \
  --copy-metadata starlette \
  --copy-metadata httpx \
  --copy-metadata pydantic \
  --copy-metadata pydantic-core \
  --copy-metadata anyio \
  --copy-metadata httpcore \
  --exclude-module tkinter \
  --exclude-module unittest \
  --exclude-module pytest \
  "$SCRIPT_DIR/_entry.py"

if [[ -f "$OUT_DIR/$BIN_NAME" ]]; then
  size=$(du -h "$OUT_DIR/$BIN_NAME" | cut -f1)
  echo ""
  echo "=== Done: npm/redfox-mcp-bin-$PLATFORM/bin/$BIN_NAME ($size) ==="
else
  echo "=== FAILED: binary not produced ==="
  exit 1
fi
