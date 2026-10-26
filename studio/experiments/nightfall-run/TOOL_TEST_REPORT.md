# PIXEL GARAGE — 49-tool studio field test — 26 October 2026

## Production: Nightfall Run (10.000 seconds)

Base: GitHub PR #51 (`feat/pixel-toolbox-free-tools-2026`). Experiment branch: `exp/pixel-garage-49-tool-car-film-20261026` (never merge without approval). This project is entirely original, inspired by but not copying premium pixel-art games. All ten SVG source layers and corresponding transparent RGBA PNG exports are editable/reusable. No existing video, branch, or episode was modified.

## Honest availability and actual tool use

Tool | Actually executed? | Contribution | Exact command / entrypoint | Problems | Reproducible by another AI agent?
--- | --- | --- | --- | --- | ---
Inkscape 1.4 | **Yes** | Rasterized ten pixel-aligned, editable original SVG artwork layers | `./src/export_svg.sh` calls `inkscape FILE.svg --export-type=png --export-filename=assets/FILE.png` | Default antialiasing generated 1,773 RGB/alpha combinations for the 43-fill body source; solved using `src/pixel_lock.py` | Yes, package available in common Linux desktop images
Pillow + NumPy | **Yes** | Restored exact artist-authored palette/alpha cells, composited seven independently scrolling native-resolution layers, created 24 rotating wheel cels and two camera compositions | `python src/pixel_lock.py`; `python src/render.py` | Code-authored art still lacks judgment and finish of manual sprite artists | Yes, requirements widely available
ImageMagick 7.1.2 | **Yes** | Analyzed native palette count, assembled contact sheet of frames *decoded from final MP4* | `magick assets/08_car_body.png -format '%k' info:`; `magick montage ... -tile 4x2 ... contact_sheet.png` | Original unquantized PNG mixed colors. No artifacts after correction | Yes
FFmpeg 7.1.5 | **Yes** | Encoded actual 300 frames, nearest 3× scale to 1080×1920/H.264 30 fps; extracted actual contact frames, full-decode test | See `src/render.py`, `logs/render_final.log`; `ffmpeg -v error -i nightfall_run_10s.mp4 -f null -` | H.264 yuv420p compression may alter colors slightly versus lossless 1× sprite PNG | Yes
FFprobe 7.1.5 | **Yes** | Checked 10s, 300 frames, 1080×1920, H.264, 30fps | `ffprobe -v error -select_streams v:0 -show_entries stream=codec_name,width,height,r_frame_rate,nb_frames,pix_fmt -show_entries format=duration,size -of json nightfall_run_10s.mp4` | None | Yes
OpenCV | **No** | Not needed: Pillow frame comparisons and FFmpeg decode suffice | — | — | —
Pixelorama | **No** | Listed in PR #51 catalog, absent locally | `command -v pixelorama` failed | No network/DNS, cannot download releases | Could be used by future agent with installed editor
LibreSprite | **No** | Listed, absent | `command -v libresprite` failed | Same | Yes, with appropriate environment
Tiled | **No** | Listed, absent | `command -v tiled` failed | Same | Yes, if installed
Godot | **No** | Listed, absent | `command -v godot` / `command -v godot4` failed | Same | Yes, if installed

Other relevant observed tools: `node`, `npm`, `xvfb-run` installed, but not claimed as production art tools. `magick`, `inkscape`, `ffmpeg`, `ffprobe` are available. Cataloged 49 does **not** mean 49 installed or used.

## Creative/art inspection

First review of `stills/frame_050.png` established: recognizable orange/coral two-door road-car silhouette, detailed multi-hue fenders, darker rear/front windows, individual handles, grill and lights, 5-spoke rotating wheels; separate conifer/mountain/autumn maple clusters and visible road markings. A 2× front/side close-up at frame 185 makes the quality of individual pixels easy to assess. No blur or shader pixelation. We deliberately did not cover art with intense flares or lighting effects.

**NOT APPROVED as premium**: car is still slightly too square/sedan-like rather than a top-tier sleek hatch/coupe; trees and canopies repeat and lack premium handcrafted lighting; upper sky composition is too empty; second shot relies on crop rather than separately painted three-quarter car perspective. The still art is clean enough for an internal tool test, but not yet the extraordinary visual standard of Katana ZERO. No false 'artist-approved' claim.

## Comparison with old minimal workflow

- Older Pillow+FFmpeg-only workflow: often flattened art, no real source layers, soft/blended edges, and no transparent tool-use audit. New: **10 editable SVG layers**, Inkscape export, a native palette-lock step and per-layer compositing.
- **Measurable art improvement**: raw exported car body had 1,773 blended colors; strict palette-lock brought it to **44 exact color/alpha values**, with a set of 43 explicitly authored opaque fill colors. More obvious deliberately clustered 1× art.
- Toolbox did not magically improve drawing. Most direct visual benefit here came from the long-form source artwork and correcting pixel consistency, NOT merely installing tooling; Pixelorama/Godot/Tiled/LibreSprite were unavailable and did not help this render.

## Camera/animation

Shot A frames 0–184: full-profile road car tracked on a scrolling twilight forest road. Shot B frames 185–299: integer-exact 2× close-up moving horizontally across the body and rotating wheels. Independent sky/far mountain/mid forest/near trees/road/guardrail/foreground offsets; wheel rotates across 24 real cels, suspension subtly moves with road, road markings move. No motion blur.

## Testing

- Actual `ffprobe` report in `logs/ffprobe.json`: H.264, 1080×1920, 30/1 fps, 300 frames, exactly 10.000000s; size approximately 2.8MB.
- `logs/full_decode.log`: FULL DECODE PASSED, `ffmpeg -v error -i ... -f null -` returns 0.
- 8 frames decoded from real MP4, contact sheet saved in `contact_sheet.png`; sample frames shown in `/stills`.
- Cross-frame sampled-image difference verified distinct adjacent samples; strict native PNG RGB palette restored with zero partial-alpha antialiasing.
- The technical tests passed, not the premium subjective visual sign-off.

## Reproduce in Linux environment

```bash
python3 -m pip install Pillow numpy
python3 src/generate_art.py
bash src/export_svg.sh
python3 src/render.py --stills-only
python3 src/render.py
ffprobe -v error -select_streams v:0 -show_entries stream=width,height,nb_frames,r_frame_rate -of json nightfall_run_10s.mp4
ffmpeg -v error -i nightfall_run_10s.mp4 -f null -
```

No third-party artwork, music or borrowed assets. Source designs are original and available as source SVG + PNG. This run has no soundtrack because the task prioritizes artwork/tool test.