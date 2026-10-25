# PIXEL GARAGE — Authentic 3D Pixel-Art Rally TikTok

**Separate experimental Godot 4 project. No production V3/V4/V5 assets are modified.**

The scene uses **real 3D geometry** built procedurally in GDScript: a modern five-door WRC-inspired rally hatchback, bevelled section body geometry, roof and windows, 3D wheels, rear wing, head/tail lighting, gravel road geometry, volumetric trees and distant 3D mountains. A real perspective camera follows the moving car.

The art direction is pixel art, not standard low-poly 3D: native 360×640 internal Godot rendering, nearest-filtered materials, a game-palette quantisation shader, ordered 4×4 Bayer dithering, 3D raised pixel-livery clusters and nearest-neighbour integer upscale to 1080×1920. No temporal or motion blur. Minimal TikTok-safe captions stay at top.

## Video
14 seconds, 420 frames, 30fps, 1080×1920, H.264/AAC original synthesised audio. Hook with rear exhaust flames, side profile, low front angle, exhaust close-up and anti-lag explanation, driving finale. This is a stylised educational interpretation, not a simulation of chemical combustion.

## Reproducible hosted render
Run the GitHub Actions workflow `Pixel Garage real-3D isolated rendering experiment` on branch `experiment/pixel-garage-godot-3d-oct25`. It installs Godot 4.4.1, Blender, Mesa, FFmpeg and Python audio dependencies; executes `bash experiments/pixel-garage-godot-3d/render/render.sh`; and uploads MP4, five proof PNGs and verification.json.

**Approval gate**: do not merge into main until user approves actual rendered frames. Binary output in Actions artifacts, not in Git LFS.
