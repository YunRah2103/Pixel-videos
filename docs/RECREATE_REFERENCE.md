# Recreate a reference video (structure 1:1, art original)

Use when a user supplies a clip and says "make this". Copy its **format, timing, palette, motion and mood**;
draw every scene, sign and character yourself (no tracing, no reusing the artist's sprites or watermark).
Credit the inspiration in the commit message if the artist is named.

## Workflow
1. `npm run analyze -- REF.mp4 references/<name>` -> `spec.json` (size, fps, cut times, per-scene palette,
   motion per second) and `sheet.png` (one frame per scene). View the sheet once.
2. Pick native size with integer scaling (reference 720x720 -> 180x180 x4; vertical -> 360x640 x3).
3. One scene function per shot: gradient sky, silhouettes, 2-3 neon accents, lit windows, ground.
   Draw on a canvas wider than the view so the camera can drift (~6 px/s).
4. Layers of motion (3+ per shot): rain, flickering neon, cloud/steam drift, water ripples, camera drift.
   Wet ground = flipped copy above the waterline, sine-wobbled, darkened. Bloom = blur bright pixels, add back.
5. Hard cuts at `cuts_s`. Audio: synthesized pads + pluck + rain noise, 0.4 s fade in, 0.6 s fade out.
6. Preview stills at mid-scene times, then full render, then `ffprobe` (size, fps, duration, audio) and
   `ffmpeg -af volumedetect`. Do not call it checked until frames were actually viewed.

## Reference implementation
`scripts/render_neon_offline.py` (Pillow + NumPy + FFmpeg, deterministic, no network):
```bash
python3 scripts/render_neon_offline.py still out/neon 1.0 3.5 6.5
npm run demo:neon          # out/neon-street.mp4, 8.2 s, 720x720, 30 fps, AAC
npm test
```
Spec of the supplied reference: `references/neon-street/spec.json` (cuts at 2.50 s and 5.53 s).

## Porting to the other tools
- Remotion: port each `scene_*` to a React component keyed on `useCurrentFrame()/fps`; keep the seeded
  RNG; render at native size then `scale=...:flags=neighbor` like `scripts/render.mjs`.
- PixiJS: sprites for signs/windows, `Filter` for bloom, a ticker driven by frame number (not Date.now).
- Pixelorama: hand-draw sprites (truck, car, signs) as PNGs under `public/sprites/<name>/` with provenance.
- Godot: only for true 3D/parallax shots; render frames, then assemble with FFmpeg.
