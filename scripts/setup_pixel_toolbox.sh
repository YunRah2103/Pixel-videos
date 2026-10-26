#!/usr/bin/env bash
# Free, optional tool bootstrap for Ubuntu/Debian. Nothing runs merely by reading this file.
# Installation is per-runtime, not checked-in binaries.
set -euo pipefail
mode="${1:---help}"
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$root"
help_text() {
  cat <<'EOF'
Usage: bash scripts/setup_pixel_toolbox.sh --core|--editors|--node|--show
  --core     Ubuntu/Debian command-line art/render tools + isolated Python venv
  --editors  Additional OPTIONAL GUI pixel artists; can be large and need a desktop
  --node     Optional PixiJS tilemap/camera processing libs in repo npm workspace
  --show     Show proposed installs, with NO changes
This is NOT a promise that every one of the 49 catalog options is pre-installed.
EOF
}
apt_install() {
  if ! command -v apt-get >/dev/null 2>&1; then
    echo "This install profile requires Ubuntu/Debian; consult the official project links." >&2
    exit 2
  fi
  if (( EUID == 0 )); then
    apt-get update
    apt-get install -y "$@"
  elif command -v sudo >/dev/null 2>&1; then
    sudo apt-get update
    sudo apt-get install -y "$@"
  else
    echo "Root/sudo needed for apt packages; run manually or use --show" >&2
    exit 2
  fi
}
case "$mode" in
  --help|-h) help_text ;;
  --show)
    help_text
    echo "CORE APT: ffmpeg imagemagick graphicsmagick gifsicle pngquant tiled xvfb libvips-tools"
    echo "CORE VENV: Pillow pytmx pytiled-parser"
    echo "EDITORS APT: grafx2 krita gimp mtpaint pinta pencil2d"
    echo "NODE NPM: @pixi/tilemap pixi-viewport sharp pixelmatch"
    ;;
  --core)
    apt_install ffmpeg imagemagick graphicsmagick gifsicle pngquant tiled xvfb libvips-tools
    python3 -m venv .tools/venv
    .tools/venv/bin/python -m pip install Pillow pytmx pytiled-parser
    echo "Core ready. Use .tools/venv/bin/python scripts/pixel_toolbox.py doctor"
    ;;
  --editors)
    apt_install grafx2 krita gimp mtpaint pinta pencil2d
    echo "GUI editors installed where packages exist. Desktop display required."
    ;;
  --node)
    if [[ ! -f package.json ]]; then echo "Missing root package.json" >&2; exit 1; fi
    npm install --save @pixi/tilemap@^5 pixi-viewport sharp pixelmatch
    echo "Node libraries installed. Verify npm compatibility and run existing build."
    ;;
  *) help_text; exit 2 ;;
esac
