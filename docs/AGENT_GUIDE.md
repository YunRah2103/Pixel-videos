# Pixel Videos — agent production contract

## Goal
Produce visually stunning, emotionally evocative short pixel-art films, typically 6–30 seconds at 30fps, vertical 1080×1920. Aim for carefully drawn/palette-limited scenes with parallax, subtle environmental motion, authentic silhouettes, warm/cool contrast, atmospheric perspective, reflective light and hand-animated details. Avoid bland giant pixels, low-poly filters, default game assets or static backgrounds.

## Production pipeline
1. **Scene director** defines shot list, primary palette, emotional beat, subject and animation plan.
2. **Art agent** creates licensed/original pixel assets (e.g. via Pixelorama). Every image is source-controlled with provenance.
3. **Motion agent** animates scenes in React/Remotion or PixiJS; 3D projects may use Godot; all time-dependent values must use the requested frame/seconds, *not* Date.now or non-seeded randomness.
4. **Editor** assembles 2D and 3D outputs with Remotion and FFmpeg. Use nearest-neighbour upscaling for authentic crisp pixels; avoid accidentally smoothing sprites.
5. **QA** validates resolution, frame count, fps, file decoding, no black gaps, legibility on phone screens, actual animation and visual quality. Inspect frame captures from first, middle and last sections.

## Technical requirements
- Use 360×640 native resolution when a 3× upscale to 1080×1920 is appropriate; alternate native sizes are allowed with justified integer scaling.
- Render frame-exact MP4; default 30fps H.264 yuv420p, 1080×1920 final.
- No unlicensed third-party game sprites, copyrighted anime frames, logos or music.
- Do not claim "rendered" or "visually checked" until actual output was produced and inspected.
- This is an independent repository. Do not change YUNEX or its car modelling kit.

## Checklist before merging
- [ ] The scene has distinctive original art direction and multiple independent motion layers.
- [ ] The camera movement is smooth and deliberate, no unnecessary shaky zooms.
- [ ] The palette and pixel density stay consistent between shots.
- [ ] A playable MP4 artifact exists and FFprobe confirms frames, codec, fps and dimensions.
- [ ] Inspect a contact sheet or keyframe captures, plus meaningful playback.
- [ ] Scripts and dependencies are reproducible; commit source files, not node_modules or tool binaries.
- [ ] Explain license / source of any new assets.
