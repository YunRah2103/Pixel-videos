#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
GODOT_BIN="${GODOT_BIN:-godot}"
mkdir -p "$ROOT/output/frames"
rm -f "$ROOT/output/frames/"*.png
python3 "$ROOT/art/make_assets.py"
python3 "$ROOT/tools/make_audio.py"
# Godot 4 movie writer, not a Python perspective renderer or a viewport screen recording.
"$GODOT_BIN" --headless --path "$ROOT/godot" --editor --import --quit
# Xvfb gives OpenGL a real display on GitHub-hosted Ubuntu CI.
xvfb-run -a "$GODOT_BIN" --path "$ROOT/godot" --rendering-method gl_compatibility --write-movie "$ROOT/output/frames/movie.png" --fixed-fps 30 --quit-after 450
FRAME_COUNT=$(find "$ROOT/output/frames" -name '*.png' | wc -l)
echo "Godot-generated frames: $FRAME_COUNT"
test "$FRAME_COUNT" -ge 449
audio="$ROOT/output/soundtrack.wav"
ffmpeg -hide_banner -loglevel error -y -framerate 30 -pattern_type glob -i "$ROOT/output/frames/*.png" -i "$audio" -vf 'scale=1080:1920:flags=neighbor,format=yuv420p' -r 30 -frames:v 450 -c:v libx264 -preset medium -crf 18 -c:a aac -b:a 192k -shortest -movflags +faststart "$ROOT/output/pixel-garage-rally-25d.mp4"
python3 "$ROOT/tools/verify.py" "$ROOT/output/pixel-garage-rally-25d.mp4"