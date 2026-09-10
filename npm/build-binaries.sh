#!/usr/bin/env bash
# Build PyInstaller binaries for all RedFox MCP npm packages.
#
# Usage:
#   ./npm/build-binaries.sh [--platform darwin-arm64] [--packages redfox-douyin-mcp]
#
# Requirements:
#   - Python 3.10+ with pip
#   - PyInstaller (`pip install pyinstaller`)
#   - All redfox-*-mcp packages installed (`pip install -e packages/*`)
#
# Output:
#   npm/<package>/bin/<platform>-<arch>/<binary>
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

# Cross-platform python detection (Windows uses 'python', Unix uses 'python3')
if command -v python3 &>/dev/null; then
  PYTHON=python3
elif command -v python &>/dev/null; then
  PYTHON=python
else
  echo "Error: python3 or python not found"; exit 1
fi

# Detect platform
detect_platform() {
  local os arch
  os=$(uname -s | tr '[:upper:]' '[:lower:]')
  arch=$(uname -m)
  case "$arch" in
    x86_64|amd64) arch="x64" ;;
    aarch64|arm64) arch="arm64" ;;
  esac
  echo "${os}-${arch}"
}

PLATFORM=$(detect_platform)
PACKAGES=""

while [[ $# -gt 0 ]]; do
  case $1 in
    --platform) PLATFORM="$2"; shift 2 ;;
    --packages) PACKAGES="$2"; shift 2 ;;
    *) echo "Unknown option: $1"; exit 1 ;;
  esac
done

echo "=== RedFox MCP Binary Build ==="
echo "Platform: $PLATFORM"
echo ""

# Check PyInstaller
if ! $PYTHON -c "import PyInstaller" 2>/dev/null; then
  echo "Installing PyInstaller..."
  $PYTHON -m pip install pyinstaller
fi

build_one() {
  local pkg_name="$1"
  local npm_dir="$SCRIPT_DIR/$pkg_name"
  local entry="$npm_dir/_entry.py"
  local out_dir="$npm_dir/bin/$PLATFORM"

  if [[ ! -f "$entry" ]]; then
    echo "  SKIP $pkg_name (no _entry.py)"
    return
  fi

  echo "  Building $pkg_name ..."
  mkdir -p "$out_dir"

  # --copy-metadata: fastmcp/redfox 等包在运行时通过 importlib.metadata 读取版本号，
  # PyInstaller 默认不打包 .dist-info，必须显式复制
  $PYTHON -m PyInstaller \
    --onefile \
    --name "$pkg_name" \
    --distpath "$out_dir" \
    --workpath "/tmp/pyinstaller-$pkg_name" \
    --specpath "/tmp" \
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
    "$entry" 2>&1 | tail -3

  # Windows produces .exe, Unix does not
  local bin_file="$out_dir/$pkg_name"
  [[ "$(uname -s)" == MINGW* || "$(uname -s)" == CYGWIN* || "$(uname -s)" == MSYS* ]] && bin_file="$out_dir/$pkg_name.exe"

  if [[ -f "$bin_file" ]]; then
    local size
    size=$(du -h "$bin_file" | cut -f1)
    echo "  ✓ $pkg_name ($size)"
  else
    echo "  ✗ $pkg_name FAILED"
  fi
}

if [[ -n "$PACKAGES" ]]; then
  IFS=',' read -ra PKG_LIST <<< "$PACKAGES"
  for pkg in "${PKG_LIST[@]}"; do
    build_one "$pkg"
  done
else
  for pkg_dir in "$SCRIPT_DIR"/redfox-*-mcp; do
    [[ -d "$pkg_dir" ]] || continue
    build_one "$(basename "$pkg_dir")"
  done
fi

echo ""
echo "=== Build complete ==="
echo "Binaries in: npm/*/bin/$PLATFORM/"
