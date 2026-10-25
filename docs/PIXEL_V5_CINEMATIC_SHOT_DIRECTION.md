# Pixel Studio V5 — 5-second cinematic shot direction (free-only)

## Why this edit exists
The previous successful film kept essentially one composition for 150 frames.
The detailed, properly credited artist-made city backdrop and independent trolley
and pedestrian sprites deserved a more deliberate edit. Passing CI is not an
art-direction pass.

## Verified local proof / render contract
- Native film artwork: 270x480, each original licensed layer remains independent.
- Frame rate and length: 30 FPS, 150 frames, 5.0 seconds.
- Export: 1080x1920 H.264 / AAC with a nearest-neighbour 4x final upscale.
- Frames 0–57 (0.00–1.90s): wide establishing; architecture/airship approach.
- Frames 58–104 (1.93–3.47s): hard cut to tracked 2x native pixel close-up of
  the *actual composited moving* tram and umbrella character. Crop is 135x240
  native pixels, nearest-neighbour x2, never blurred.
- Frames 105–149 (3.50–5.00s): hard cut back to scene wide for the actual six-cel
  OPEN-sign reveal, animated pedestrian and broken water reflections.
- Camera horizontal focus tracks Tiled-staged tram x coordinate; the camera
  is a deliberate editorial crop and does not fake independent animations.

## What is and is not improved
Real shot-scale variation and composition change now occur, without hiding weak
source artwork under rain or global blur. The production pipeline still relies
on CC BY 3.0 licensed Ansimuz architecture and hand-specified code-authored
tram / courier / pedestrian sprite cels. This remains a reviewed visual
candidate, **not** owner-approved or a claim of professional commercial art.
The zoom deliberately doubles display pixel scale during its close-up; it does
not interpolate or violate pixel sharpness. Frame-accurate cuts are intentionally
visible and should be evaluated on an actual phone.

## No false editor claims
Actually used: real Tiled CLI export of `studio/v5/neon-portrait.tmx`,
Pillow source art compositor and cel renderer, FFmpeg and FFprobe.
Not claimed as creative editor use: LibreSprite GUI, Laigter GUI,
SpookyGhost GUI or Pixelorama GUI.

Only free local binaries and licensed artwork are required. The original source
download is available through `scripts/setup_free_pixel_v5.py --art`.
No paid token or AI generation services.

## QA commands
```bash
python3 -m py_compile scripts/v5_cinematic_shots.py scripts/render_neon_portrait.py
npm run art:v5:assets
# From Tiled GUI or headless:
xvfb-run -a tiled --export-map studio/v5/neon-portrait.tmx out/pixel-v5-portrait/tiled-layout.json
/usr/bin/python3 scripts/render_neon_portrait.py
ffprobe -v error -select_streams v:0 -count_frames -show_entries stream=width,height,nb_read_frames,r_frame_rate -of json out/pixel-v5-portrait/pixel-v5-neon-portrait-5s.mp4
ffmpeg -v error -xerror -i out/pixel-v5-portrait/pixel-v5-neon-portrait-5s.mp4 -f null -
```

Inspect the full MP4 and the 9-frame contact sheet before artistic signoff.
The branch and PR remain draft; do not merge into production or main without approval.
