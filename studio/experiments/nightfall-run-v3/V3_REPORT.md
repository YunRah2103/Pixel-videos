# Pixel Garage — Nightfall Run V3 / Full Art Redesign
**26 October 2026 · Independent improvement to V2 PR #53 · Unmerged / pending owner approval**

## Artistic changes
- **Car silhouette entirely replaced:** the old coral hatchback is replaced by an ivory/teal low-slung two-door GT with sloped fastback glass, sculpted bonnet, carved wheel arches, wing, diffuser, specific light assemblies, motorsport rocker, door seams and 5-spoke rotatable wheels. This is a new multi-part sprite, not a recolor or particle overlay.
- **Visuals redrawn at native pixel resolution:** warm moonlit indigo palette, new angular alpine mountains and snowy faceted peaks, detailed lakeshore/village, individually keyed spruce branches, polygonal deciduous crowns with interior shade and pixel highlights, wind clouds, hanging pine branches, roadside barriers and lane/road texture.
- **Static-art QA before animation:** reviewed original V2 and static V3 frames, rejected first V3 car as too sedan-like, rebuilt as the current low white sports coupe. Compare exact MP4 output in `before_after.png`.
- **Movement:** all eight scenery strata have independently advancing time offsets; road and foreground posts move far faster than cliffs and sky. Car advances visibly ~20 native pixels across the scene instead of static anchoring. Independent sprung body motion and actual 60-cel rotating wheel images tied to distance.
- **Camera:** one readable uninterrupted full-car tracking shot, no cropped wheel/door closeup, abrupt cut or aggressive zoom.

## Actual tool execution
| Tool | Used? | Work performed |
|---|---|---|
| Pillow / Python | YES | Original transparent RGBA PNG scene/vehicle/wheel layers, native pixel art, parallax + compositing, 300 frame generation, OpenRaster package |
| FFmpeg | YES | 300-frame lossless-native pipeline nearest 3× upscale, H.264 encode, frame grabs, complete decode test |
| FFprobe | YES | H.264 1080×1920/30fps/300 frames/10.000s metadata verification |
| ImageMagick | YES | Validates final contact still colors/dimensions independently |
| Krita / Pixelorama / LibreSprite / Tiled | NO | None of these GUI editors are installed; editable PNG layers and OpenRaster supplied for user editing. No invented tool claims. |
| Inkscape | NO | Installed, but PNG pixel-master pipeline was used instead of SVG export. |

## Format and honesty
H.264, 1080 × 1920, 30 FPS, 300 frames, 10.000s, yuv420p, faststart and full FFmpeg decode PASS. No soundtrack included. Source artwork remains pixel-addressable and editable; no blur, bloom or interpolation. Original V1/V2 files and PRs remain unchanged; V3 is a wholly separate folder and GitHub branch.

**Visual assessment:** The V3 art, car type, palette and framing are substantively redesigned and more legible, but these are digitally hand-keyed pixel polygons authored through Python, not verified by a professional human pixel artist. Not a claim of Katana ZERO-level illustration. Unlike adding particles to the former scene, all key scene and vehicle art was regenerated.

## Reproducibility
```
python3 src/v3_art.py
python3 src/v3_overhang.py
python3 src/v3_car.py
python3 src/v3_render.py --stills-only
python3 src/v3_render.py --output nightfall_run_v3_10s.mp4
ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate,nb_frames -show_entries format=duration -of json nightfall_run_v3_10s.mp4
ffmpeg -v error -i nightfall_run_v3_10s.mp4 -f null -
```
**Important:** Source scripts and their `v3_assets` directory are colocated in the archive under `src/`, so the build commands can run directly after extracting and entering `src/`. These scripts are included verbatim.