# Sunset Harbor V5 — Agent 2 atmosphere and light integration

Issue: #13 • Branch: `agent/sunset-harbor-v5-light-water` • Target: `integration/sunset-harbor-v4-final` • Baseline commit: `22f9c9f87aed98fb2cbdeaf958f998c3eda32a10`.

## Owned source / intended integration

- `src/scenes/v5/AtmosphereV5.tsx`: export `V5AtmospherePlane` with **`{frame:number, motion:any, plane:'sky'|'clouds'|'water'|'reflections'|'lighting'|'air'}`**.
- `src/scenes/v5/AtmosphereV5Proof.tsx`: isolated 12s moving proof over original approved V4 world/actors/camera.
- `scripts/render-v5-atmosphere.mjs`, `.github/workflows/sunset-harbor-v5-atmosphere.yml`: native Remotion proof, reference render, MP4 and QA artifact.
- No other agents' files, shared Root, final workflow, or music are edited.

Use planes in this order: `sky → clouds → [distant ridge] → air → water → reflections → [boat wake + architecture + quays] → lighting → [boats + promenade + life + foreground]`. A full-size `360 × 640` SVG is returned per plane; the integrator owns camera/parallax and puts *each plane inside a transformed wrapper*, not nested transforms. Each SVG is transparent except sky/water. Draw Agent 1's revised architecture after the reflections, and place Agent 3's characters above the lamps.

## Native pixels and timing

- Stage `360×640`, `30 fps`, 360 indexed frames, 12.0 seconds. Upscale 3x with `scale=1080:1920:flags=neighbor`.
- Sun `(225,252)`, horizon `y=353`, water through `y=535`. Defaults are overridable by `motion.sunX`, `sunY`, `waterTop`, `waterBottom`.
- Optional motion inputs: `cloudDrift` (V4 units), `waterPhase`, `lightIntensity`, `waveStrength`. All have deterministic frame-only fallbacks, safe for out-of-order rendering and parallel Remotion workers.
- Sky/sun is painted by V5; **do not also render V4 world.sky**, or it will cover V5 painterly bands and sunlight.
- No external image libraries, asset extraction, randomness per frame, texture sampling, procedural glitter, blur, or big additive glow overlays.

## Art reconstruction

- Seven independently drifting hand-drawn cloud formations, each with custom silhouette, occluded layered pigment, lavender shadow cavities, salmon midtones and sparse warm rim light.
- Quiet teal sea: gradient depth, 21 coherent crest lanes with decreasing apparent size toward the horizon, sparse shadow troughs. No 400-plus independent sparkles.
- Broken golden sun ribbon widens toward the camera; 25 deliberate ripple clusters and a few graceful longer crescents. Sun reflections are centered on the supplied sun X. Warm building reflections stay directly below actual quays.
- Tiny practical light bounces and bounded mountain mist, never all-frame bloom.
- No V4 birds or boat wakes reproduced; these are owned by Agent 3's story module.

## Proof / QA contract

```bash
npm install --no-audit --no-fund
node scripts/render-v4-final.mjs
node scripts/render-v5-atmosphere.mjs
```

Runs the actual V4 film first (for exact picture comparison and same owner-supplied 12s Day & Night crossfaded soundtrack), then renders all 360 V5 Remotion frames and encodes `out/sunset-harbor-v5-atmosphere-1080p.mp4` in H.264/AAC 1080×1920. Uses FFprobe counted frames and full FFmpeg decode. Extracts nine timestamps 0/45/90/135/180/225/270/315/359, compares each against same V4 frame, generates `out/v5-atmosphere-qa/v4-v5-side-by-side.png` (V4 left, V5 right), V5 contact sheet and JSON report. No claim of success until the workflow run has succeeded and its MP4 artifact exists.

The soundtrack is **the user's existing V4 excerpt**, not a licensed replacement. Owner must separately confirm public use and distribution rights.
