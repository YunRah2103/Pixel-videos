#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$ROOT/render/output"
mkdir -p "$OUT"
cd "$ROOT"
GODOT_BIN="${GODOT_BIN:-$(command -v godot || command -v godot4 || true)}"
if [[ -z "$GODOT_BIN" ]]; then echo "ERROR: Godot 4 is not available"; exit 3; fi
"$GODOT_BIN" --version
command -v blender >/dev/null || { echo 'Blender not found: no premium car mesh possible'; exit 6; }
blender -b -t 2 --python tools/build_rally_car.py
test -s assets/rally_car_body.glb || { echo 'Blender model generation failed'; exit 7; }
"$GODOT_BIN" --headless --path "$ROOT" --editor --import --quit
ARGS=("$GODOT_BIN" --path "$ROOT" --rendering-driver opengl3 --resolution 270x480 --write-movie "$OUT/godot-actual-3d.avi" --fixed-fps 30 --quit-after 420)
if command -v xvfb-run >/dev/null && [[ -z "${DISPLAY:-}" ]]; then
   xvfb-run -a -s '-screen 0 900x980x24' "${ARGS[@]}"
else
   "${ARGS[@]}"
fi
test -s "$OUT/godot-actual-3d.avi"
RAW_SIZE="$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 "$OUT/godot-actual-3d.avi")"
test "$RAW_SIZE" = "270x480" || (echo "Unexpected Godot dimensions $RAW_SIZE"; exit 4)
python3 render/make_audio.py
ffmpeg -hide_banner -loglevel warning -y -i "$OUT/godot-actual-3d.avi" -i "$OUT/original-engine-audio.wav" -map 0:v:0 -map 1:a:0 -vf 'scale=1080:1920:flags=neighbor,setsar=1' -c:v libx264 -preset medium -crf 17 -pix_fmt yuv420p -r 30 -c:a aac -b:a 192k -ar 48000 -t 14.000 -shortest "$OUT/pixel-garage-godot-3d-tiktok.mp4"
for marker in '1.25 rear' '3.15 side' '6.05 front' '8.10 exhaust' '13.10 finale'; do
  read -r seconds name <<< "$marker"
  ffmpeg -hide_banner -loglevel error -y -ss "$seconds" -i "$OUT/pixel-garage-godot-3d-tiktok.mp4" -frames:v 1 "$OUT/proof-$name.png"
done
python3 render/verify.py "$OUT/pixel-garage-godot-3d-tiktok.mp4"
