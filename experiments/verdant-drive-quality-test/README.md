# Verdant Drive — independent pixel-art animation experiment

A ten-second, 30fps, 1080x1920 original pixel-art countryside driving loop. This experiment lives in its own directory and does not modify the original Pixel-videos productions.

## Artwork
- Deliberately authored, irregular oak leaf-cluster silhouettes and reflected colour patches; separate fir, cloud, hedge and grass designs.
- Original golden hatchback with hatchback greenhouse, faceted glass, lights, handles, panel seams, wing mirror, bumper, wheel arch and individually rotating rim spokes.
- Cohesive 360x640 logical canvas, no antialiasing or pixelation filter. Precise 3x nearest-neighbour upscale.
- Layer-specific speeds: clouds 0.2, distant mountains 0.25, fields 0.6, far trees 0.72-0.98, near trees 1.57, road and wheels 2.86 logical pixels per frame. Subtle suspension oscillation.

## Run

```bash
python3 -m pip install Pillow
python3 render.py --still
python3 render.py --render
python3 export_assets.py
```

`ffmpeg` must be available on PATH. `render.py` writes `output/Verdant_Drive_10s_1080x1920.mp4`, plus extracted first, midpoint and last source-resolution frames. `export_assets.py` writes reusable unscaled transparent sprite PNGs into `assets/`.

## Output checks

```bash
ffprobe -v error -select_streams v:0 -show_entries stream=codec_name,width,height,r_frame_rate,nb_frames -show_entries format=duration -of default=nw=1 output/Verdant_Drive_10s_1080x1920.mp4
ffmpeg -v error -i output/Verdant_Drive_10s_1080x1920.mp4 -f null -
```

Original sprite shapes are built into `render.py` and separated by functions for reuse and modification. This is code-drawn pixel art, not a manually produced Aseprite painting. No external footage, imported artwork or music are used. Output is silent.
