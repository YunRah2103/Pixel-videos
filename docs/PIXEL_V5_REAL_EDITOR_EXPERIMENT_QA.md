# PIXEL VIDEOS V5 — genuine Krita + LibreSprite editor experiment

25 October 2026 · [PR #45](https://github.com/YunRah2103/Pixel-videos/pull/45) · draft / not merged

## Why

The original neon street was an attractive composition because of licensed Ansimuz background art, but the hero car remained code-authored. This experiment checks whether actual free pixel-art editor exports can improve the production pipeline, with **real source assets entering the exported film** rather than tool installation being treated as art creation.

## What runs and feeds the film

1. **Pixel-native layered input**: `scripts/v5_editor_art_pass.py prepare` constructs an editable 164×66 OpenRaster (.ora) document with two independent hand-specified, transparent pixel cluster layers for differentiated neon reflection ramps and small paint/wet surface details. This drawing originated in the project script (Pillow); it was not mouse/stylus-drawn in Krita.
2. **Krita actually runs** under Xvfb and opens that .ora, exporting `car-detail-krita.png` at full native 164×66. CI validates non-empty artwork and an exact RGBA pixel match to the original flattened reference (no blur or smoothing).
3. **LibreSprite actually runs**, opening the Krita output and exporting its own `car-detail-libresprite.png`, which is composited into all 24 animated GT car cels; it then processes all 24 frames into a **real exported PNG animation atlas and metadata JSON**.
4. `v5_editor_art_pass.py adopt` scans the actual LibreSprite atlas to match the 24 true exported cells by their image hashes, extracts all 24 into film-ready `car-cel-*.png` files and records coordinates and SHA256 hashes. The media renderer **requires** these processed sprite cels and the evidence manifest. It has no Pillow-only car fallback.
5. Actual Tiled CLI map export, independent licensed artist art planes, pixel-native character/environment animations, Pillow compositing and FFmpeg encoding retain the 5-second, three-shot 1080×1920 / 30fps / 150-frame production contract.

## Verified evidence

- Exact successful source commit: `00832c7a07c8e5b12b0b2fb63279381929224ea9`
- [GitHub Actions **SUCCESS** run 40203779025](https://github.com/YunRah2103/Pixel-videos/actions/runs/40203779025)
- [Download complete updated MP4, source .ora, Krita export, LibreSprite export/atlas, 24 final car cels, contact sheet and stills — artifact 12602144875](https://github.com/YunRah2103/Pixel-videos/actions/runs/40203779025/artifacts/12602144875)
- Reviewed exact exported 9-frame contact sheet and source sprite before-and-after.
- Independent FFprobe confirmation: H.264, 1080×1920, 30/1 fps, **150 decoded frames**.
- Independent full FFmpeg audio/video decode: **PASS**.
- Independent frame extraction and comparison: frames 36, 72 and 90 are different from the baseline video.
- Native 164×66 car comparison: **240 of 10,824 pixels changed**, mostly small paint, canopy and trim highlights. **Not** a scene-wide artistic revolution. Enhancements are more legible at the pixel-native 2× close-up than in the wider establishing scene.
- `real-editor-evidence.json` documents 24 exported, 24 unique car cels; exact Krita and LibreSprite export hashes and atlas cell positions.

## Honest QA / limitations

**Actual free tools run in this experiment:** Krita CLI (two-layer ORA import/export), LibreSprite CLI (PNG roundtrip and 24-frame sprite atlas), Tiled CLI, Pillow, FFmpeg/FFprobe and GitHub Actions.

**Not used:** Pixelorama, Laigter, SpookyGhost, Blender, generative AI image creation, or paid rendering platforms. No fake claim of painting by hand in Krita/LibreSprite's GUI. The editor operations are substantive source-to-export stages because their output is directly rendered, but authoring of those editor-input pixel clusters is **script-specified**.

**Art verdict:** Actual observable additional specular/material paint detail on the sports coupe; original scene composition, pedestrian, weather and cameras deliberately preserved. High-end hand-painted indie-game sprite polish still has room for improvement. The result demonstrates a reliable **Krita → LibreSprite → animated video** pipeline, not that more tools automatically improve art significantly.

**Branch policy:** Draft PR #45, base `production/countryside-drive`; do not merge to base or `main` without explicit user approval.
