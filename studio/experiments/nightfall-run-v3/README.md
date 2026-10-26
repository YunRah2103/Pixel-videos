# NIGHTFALL RUN V3 — full visual redraw

**Separate experiment built over draft PR #53. Do not merge without owner approval.**

V2 was too similar to V1. This V3 changes the actual hero-car sprite, forest, cliffs, moonlit palette, road art, and source animation. The car is now a low ivory-and-teal fastback instead of a coral hatchback.

## Original, reproducible artwork

- `src/v3_art.py`: creates native, editable alpha PNG pixel environment layers and the base wheel.
- `src/v3_overhang.py`: top-frame authored pine-frond parallax layers.
- `src/v3_car.py`: **final low-slung sports coupe** replaces the temporary base body sprite.
- `src/v3_render.py`: 30 FPS, 300 frames, actual independently scrolling scenery and road, physically coupled rotating wheel cels, subtly sprung car body, full-car tracking.
- `V3_REPORT.md`: limitations, QA, and honest tool-use record.

Run in this order:
```bash
python -m pip install pillow
python src/v3_art.py
python src/v3_overhang.py
python src/v3_car.py
python src/v3_render.py --output nightfall_run_v3_10s.mp4
ffmpeg -v error -i nightfall_run_v3_10s.mp4 -f null -
ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate,nb_frames -show_entries format=duration -of json nightfall_run_v3_10s.mp4
```

The render script writes native artwork to `src/v3_assets/`. The intentionally isolated GitHub Action `pixel-garage-v3-render.yml` runs the same original-source pipeline and uploads both MP4 and layered PNGs as workflow artifacts.

## Output and review
The entire 1080×1920, 30 FPS, 10s final MP4, before/after frames, native layered OpenRaster document and a zipped editable-source archive were delivered to the owner in ChatGPT on 26 October 2026. They are separate deliverables; **this pull request does not claim the already-produced MP4 is committed into GitHub** until the Actions artifact is confirmed.

No existing V1 or V2 footage, scripts, models, or artifacts were modified. This is original pixel art, not a Katana ZERO game-asset import.
