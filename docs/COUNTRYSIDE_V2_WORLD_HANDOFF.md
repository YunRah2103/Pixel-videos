# Countryside Drive V2 — World Art / Agent 1 handoff

## Original native pixel artwork
Source: `studio/countryside/world/build-world-v2.mjs`; generated PNGs are
`public/countryside/world/{sky,farTrees,midTrees,nearTrees,verge,road}.png`.
Build with `node studio/countryside/world/build-world-v2.mjs`.

Five distinct native-pixel silhouettes (oak, maple, beech, poplar, pine),
original outline clusters, deliberately placed leaf highlights, layered
depth and varied spacing. No SVG, vector curves, pixelated 3D, noise,
post-filter pixelation, or external art. Every pixel is authored in JS.

| Layer | Tile width | Height | Native Y | Motion |
|---|---:|---:|---:|---|
| sky | 360 | 480 | 0 | Static |
| farTrees | 720 | 300 | 180 | Agent 3 offset |
| midTrees | 840 | 265 | 215 | Agent 3 offset |
| nearTrees | 960 | 235 | 245 | Agent 3 offset |
| verge | 384 | 160 | 480 | Agent 3 offset |
| road | 384 | 160 | 480 | Agent 3 offset |

Layer order: sky, farTrees, midTrees, nearTrees, verge, road, then car.
Road upper edge is Y=480, paved surface ends near Y=575.
Do not apply extra camera offsets in WorldLayers: Agent 3 passes `offsetX`.
Negative offset scrolls left. Positions snap to integer native pixels.

API: `CountrysideWorldLayer({frame,layer,offsetX?})`,
`COUNTRYSIDE_WORLD_TILES`, `wrapWorldOffset`.

## Pixel Studio V3
Based on `feat/pixel-studio-v3-production` because the active film
integration branch predates V3 tooling. This agent did not modify the
integrator/car/motion branches. Integrator should cherry-pick the three
world files or reconcile the V3 toolkit before merging this work.

The CI pipeline exercises the actual V3 commands:
`npm run studio:setup`, `npm run atlas:build`,
`npm run environment:build`, `npm run environment:proof`,
`npm run visual:qa`. These verify the toolkit example. Then our own
V2 builder generates the authored world and a **separate** real MP4.
No claim that the V3 starter environment itself contains V2 artwork.

## Actual moving artwork proof
Run `node scripts/render-world-v2-proof.mjs` after building the art.
It renders 120 native 360x640 frames at 30fps, nearest-neighbour upscales
to H.264 1080x1920, verifies FFprobe codec/frames and full FFmpeg decode,
generates 9-frame contact sheet, checks tile alpha seam continuity,
and writes `out/countryside-v2-world/verification.json`.
The output is world only; not the final 12s film.

Isolated proof scroll speeds: far .42, mid .93, near 1.76,
verge 2.42, road 2.86 native pixels/frame, integer snapped.
Agent 3 owns actual production motion and Agent 4 owns final assembly.
Keep car tyre contact around native Y=495 per original film contract.
