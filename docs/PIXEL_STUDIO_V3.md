# Pixel Studio V3 — Production Tools for All Agents

This version extends Studio V2 without changing current Sunset Harbor V5 agent-owned film files.

## One-command agent setup

From a branch containing the toolkit commit, run:

```bash
npm run studio:setup
```

The command runs `npm install`, generates original sprite assets, packs a deterministic PNG atlas, builds the countryside environment's parallax planes, tests frame-exact animation rigs and pixel lighting, renders a **genuine 90-frame 1080×1920 MP4**, computes numerical visual QA and runs toolkit TypeScript checks.

External heavyweight editors (Krita, Pixelorama, Godot, LDtk) are optional downloads. On supported Linux hosts, run:

```bash
npm run studio:setup -- --editors
```

Their upstream executables cannot be preinstalled inside a Git repository; scripts use official releases or OS packages, and machine access may be necessary.

## 1 — Sprite Atlas

`npm run assets:build && npm run atlas:build` generates:
- `public/toolkit/atlas/atlas.png`
- `public/toolkit/atlas/atlas.json` (named frame rectangles and normalised UVs)
- source PNGs in `public/toolkit/sprites/`

Edit `studio/atlas.config.json` for atlas width, padding and columns/rows if importing sprite sheets. All assets are packed at native resolution, with a transparent gap to avoid texture bleeding. Don't use filtering when rendering.

Example consumer:

```js
import data from '../public/toolkit/atlas/atlas.json';
const car = data.frames['country-car'];
// Use atlas.png with pixelated/nearest texture sampling.
// Crop x/y/w/h in a sprite renderer or use car.uv in Pixi.
```

## 2 — Layer-isolated native pixel lighting

`src/toolkit/pixelLighting.mjs` exports `lightPixelScene` and `contactShadow`, using real native-pixel buffers and stepped light attenuation. Existing PixiJS effects remain in `src/toolkit/pixiFx.ts` for a WebGL pipeline.

Do not blur whole images or apply post-upscale filtering. Keep glow and atmospheric mixing local, layered, and low strength.

## 3 — Rigging and repeatable animation

`src/toolkit/rigs.mjs` exports `walkPose`, `carPose`, `boatPose`, `animalPose`, `clothPose`, `frameSlot`, and `rigPose`. Each is a pure function of the frame index; compatible with Remotion or PNG sequence renderers.

```js
import {carPose, frameSlot} from './src/toolkit/rigs.mjs';
const motion=carPose(frame,{roadRoughness:1});
const spriteIndex=frameSlot(frame,{count:6,hold:3});
```

Rigs provide pose signals. Agents still need proper hand-authored pivoted sprite art, not rectangular figures. Test with `npm run rigs:test`.

## 4 — Declarative original environment builder

`studio/countryside.scene.json` contains a 5-plane road-and-trees example based on editable authored sprite assets. Run `npm run environment:build`. Layer exports include PNGs + scene metadata. Each layer has independently adjustable `depth`, palette bands, sprite placements, and pixel-exact integer scales.

To build another environment, create `studio/your-scene.json` using the same schema, set a unique `slug`, and run:

```bash
node scripts/build-environment.mjs studio/your-scene.json
```

Change trees, buildings, hills, foliage and decor through original sprites. Don't confuse the example with a professionally finished illustration.

## 5 — Render-based visual diagnostics

`npm run environment:proof && npm run visual:qa` validates actual H.264 1080×1920 output, decodes every frame, detects identical/frozen frame runs, black captures, and reports brightness and palette bins at nine frames. It writes `out/studio-v3/contact-sheet.png` and `out/studio-v3/visual-qa.json`. To compare numeric pixel differences to a reference PNG:

```bash
node scripts/qa-visual.mjs --reference studio/reference.png
```

These checks provide **objective diagnostics**, not an AI or human subjective quality judgement. Watch the MP4 and inspect the sheet at phone size before accepting film quality.

## Boundaries and agent handoff

The V3 toolkit is shared infrastructure. Existing V5 branches do **not** automatically receive updates when the baseline changes. Integrators must merge/cherry-pick the toolkit carefully into their own branches after checking for conflicts. Do not change agent-owned V5 world, atmosphere, story or audio during toolkit updates. The countryside proof is **not** a finished Sunset Harbor episode. This project keeps original authored art and required license/provenance verification for imported assets.

Get tools: `npm run studio:check`, `npm run tools:install` (all optional editors), or `npm run studio:setup -- --editors` on supported platforms.
