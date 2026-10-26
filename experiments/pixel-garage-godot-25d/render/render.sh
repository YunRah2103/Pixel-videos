#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
mkdir -p render/output
python3 scripts/generate_art.py
GODOT_BIN="${GODOT_BIN:-$(command -v godot || command -v godot4 || true)}"
test -n "$GODOT_BIN" || { echo 'Godot 4.x is unavailable'; exit 4; }
"$GODOT_BIN" --headless --editor --path "$ROOT" --import --quit
if command -v xvfb-run >/dev/null;then
 xvfb-run -a -s '-screen 0 900x1000x24' "$GODOT_BIN" --path "$ROOT" --rendering-driver opengl3 --resolution 360x640 --write-movie "$ROOT/render/output/godot-25d.avi" --fixed-fps 30 --quit-after 420
else
 "$GODOT_BIN" --path "$ROOT" --rendering-driver opengl3 --resolution 360x640 --write-movie "$ROOT/render/output/godot-25d.avi" --fixed-fps 30 --quit-after 420
fi
test -s render/output/godot-25d.avi
python3 render/make_audio.py
ffmpeg -hide_banner -loglevel error -y -i render/output/godot-25d.avi -i render/output/audio.wav -map 0:v:0 -map 1:a:0 -vf scale=1080:1920:flags=neighbor,setsar=1 -c:v libx264 -crf 17 -preset veryfast -pix_fmt yuv420p -r 30 -c:a aac -b:a 192k -t 14 render/output/pixel-garage-25d-tiktok.mp4
for item in '1.2 hook' '4.4 side' '7.4 close' '11.2 anti-lag' '13.5 finale'; do
 read -r second name <<< "$item"
 ffmpeg -hide_banner -loglevel error -y -ss "$second" -i render/output/pixel-garage-25d-tiktok.mp4 -frames:v 1 "render/output/proof-$name.png"
done
python3 render/verify.py render/output/pixel-garage-25d-tiktok.mp4
