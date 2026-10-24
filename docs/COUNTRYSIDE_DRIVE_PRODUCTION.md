# Countryside Drive — Shared Production Contract (Pixel Videos)

**Status:** locked preproduction specification; artwork and final MP4 not yet delivered.
**Repository:** `YunRah2103/Pixel-videos`
**Shared production baseline:** `production/countryside-drive` (created from toolkit-equipped `integration/sunset-harbor-v4-final`).
**Separate from Sunset Harbor:** do not copy harbour scenes, sky/water styles, V4/V5 footage, character art, soundtrack, or pastel painterly direction into this film.

## The picture — one clear idea

A charming **authentic 2D side-view pixel-art car** driving RIGHT along a horizontal countryside road, while **layered original pixel trees** move LEFT. Clean, bright, playful 16-bit-era game-sprite sensibility. Only one car, a road, roadside ground, a restrained flat sky and trees. No second vehicle, shops, people, signs, buildings, ornate clouds, HUD, subtitles, fire, sparks, 3D camera, lens bloom or procedural filler.

**This is NOT pastel/anime scenery:** colour clusters must be visibly pixel-authored. Do not simulate pixel art by drawing smooth SVG/vector forms, blurring, applying pixelation filters or scaling tiny low-poly renderings.

## Shared canvas / staging (locked before agents start)

- Native canvas: **360 × 640**, 30 FPS, **360 frames (12 seconds)**, portrait. Nearest-neighbour exact **3×** enlargement to **1080 × 1920**, H.264 yuv420p final MP4. Film should loop visually without abrupt jumps; a mild fade only if deliberate.
- Horizontal side-on stage; screen X increases right, Y increases down. No perspective road vanishing point. Car approximately X=100..260, native width ~145px (allow 130–155), wheels should visibly roll, bottom wheel/contact point around **Y=495**.
- **Ground/road upper boundary Y=480**; road occupies approximately Y=480..575, and lower verge extends to bottom. Both wheels' ground contacts at Y≈495; the wheel artwork may overlap top of road. No floating or clipping.
- Tree canopy and trunks occupy approximately Y=265..480. Open sky above; distant tree line darker/desaturated. All layers must share this horizon and native pixel grid.
- **Four-agent team:** Agent 1 creates the car sprite and wheel animation; Agent 2 creates original pixel trees, sky, road and repeating scenery tiles; Agent 3 creates the deterministic driving motion/parallax controller and tests speed/wheel sync; **Agent 4 owns full integration, final Remotion composition, rendering and film QA**. Agent 3 must not claim final delivery.
- Each source pixel is one **native screen pixel**; hard edges, consistent integer-pixel grid at every scale. PNG import uses nearest-neighbour. Pixel-snap all layer positions to integer coordinates each frame. No CSS `image-rendering` smoothing, resampling, filters or subpixel raster placement.

## Palette (shared; small, saturated and deliberate)

Use this core palette; tasteful nearby shades allowed, with **~12–16 working colours TOTAL** across the final scene, plus transparent:
- sky blue `#6DB6E5`
- distant tree `#6A9774`
- mid leaf `#4B8B56`
- near leaf `#2B7047`
- leaf highlight `#85AD65`
- trunk `#705542`
- deep outline `#263E39`
- grass verge `#739D53`
- road `#575E65`
- road shade `#444C55`
- stripe/dust highlight `#E4D49B`
- car red `#D84E3F`
- car light `#F17853`
- car deep shadow `#823B38`
- window `#9ACBDD`
- tyre `#26323B`

Treat this as **crisp retro-pixel artwork**, not washed-out pastel. Prefer distinctive large car silhouette, authored shadow clusters, 1px native highlights, sparing dithering, carefully drawn distinct trees. NO gradients except clustered pixel-palette ramps.

## Motion choreography

- One continuous 12s scenic driving shot; car stays in roughly the same screen region while scenery passes. Optional ±1 native px vertical suspension bob and alternating body tilt, locked to the wheel rhythm; no dancing.
- Hand-drawn wheel animation (minimum four authored poses or manually authored hub-angle frames) at speed matching road drift. Do not use smooth CSS spinning circular vectors or wobbly tyre geometry.
- Agent 3 picks consistent velocities: far trees ~0.3–0.5 native px/frame, mid trees ~0.7–1.2 px/frame, near trees ~1.6–2.2 px/frame, road ~2.4–3.2 px/frame; integer pixel snapping and seamless tiled edges. Reconcile with believable wheel roll (rim spokes/hub progression) and no tyre sliding. No big camera zooms.
- Frame-derived deterministic animation only. Use `useCurrentFrame()`, `spriteFrame()` or direct frame math; no `Date.now()`, nonseeded random, wall-clock animations or random per-frame textures.
- Real source sprite sheets, original PNG planes and editable source. No whole-scene vectors, generic curves or CSS boxes posing as genuine sprite drawings.

## Use the repository's **full relevant toolkit**

Read `docs/PIXEL_STUDIO_V2.md` and `docs/AGENT_GUIDE.md` before editing. Every agent must audit the available tools **and use the relevant ones**, not falsely claim optional editors are preinstalled and not force unrelated shader/3D tools into a flat 2D project.

Run on the toolkit branch before proof:
```bash
npm install --no-audit --no-fund
npm run tools:check
npm run typecheck:toolkit
npm run assets:build
npm run assets:proof
npm run assets:qa
```
Tools to consider:
- **Sharp + `studio/pixel-assets.json` / `scripts/build-pixel-assets.mjs`:** native indexed palette assets and nearest-neighbour sprites.
- **Pixelorama:** strongly preferred for editing genuine car/tree PNG sprite sheets; install on demand: `python3 scripts/install_studio_v2.py --pixelorama`. Preserve editable original `.pxo` where supported.
- **Krita:** optional for original pixel-grid painted background, with crisp PNG export; install with `--krita` when needed.
- **LDtk:** optional for authoring and testing repeatable roadside tile maps, `--ldtk`; import exported native PNG layers.
- **Remotion:** actual deterministic film and proof render.
- **PixiJS v8:** optional for performant sprite planes, **not** mandatory for no-effects 2D scene. Avoid whole-frame FX / filters.
- **`src/toolkit/camera.ts`:** frame-based `spriteFrame` helper may be reused; custom simple layer offsets for this side-on shot should be preferred to its Sunset Harbor depth presets.
- **Godot:** optional only if needed for authentic 2D sprite authoring/animation; **do not render a 3D scene and pixelate it**.
- **FFmpeg/FFprobe, toolkit QA scripts, GitHub Actions:** mandatory film checking and artifact delivery.

External desktop editors are downloaded on demand, not bundled or implied to exist. Record actual commands/availability in PR; use Sharp/palette source directly when unavailable. Avoid copying Sunset Harbor toolkit example cloud, boat, lantern or bush as final Countryside art. No unlicensed imported sprites or music.

## Agent branches, ownership and contracts

All branches originate from **`production/countryside-drive`**:
1. **Agent 1:** `agent/countryside-car`. Own `src/scenes/countryside/CarLayer.tsx`, `studio/countryside/car/**`, `public/countryside/car/**`, local proof and docs. Export `CarLayer({frame, x?, wheelContactY?})` with defaults x=180, wheelContactY=495; one complete side-on car, no external camera transform and no scenery.
2. **Agent 2:** `agent/countryside-world`. Own `src/scenes/countryside/WorldLayers.tsx`, `studio/countryside/world/**`, `public/countryside/world/**`, local proof and docs. Export `CountrysideWorldLayer({frame, layer, offsetX?})` for `layer: 'sky'|'farTrees'|'midTrees'|'nearTrees'|'verge'|'road'`. Art tiles must be truly seamless; offsetX is the **only** externally applied scrolling offset. No car sprite or camera transform.
3. **Agent 3:** `agent/countryside-motion`. Own `src/scenes/countryside/DrivingMotion.ts`, optional isolated motion proof files and motion test/documentation. Export `getCountrysideMotion(frame:number)` returning integer-snapped `offsets` for `'farTrees'|'midTrees'|'nearTrees'|'verge'|'road'` plus `roadTravelPx`, `wheelRotationTurns`, `carX` and `bobY` in native pixel coordinates. Verify smooth scrolling, repeat seams, wheel-distance relation and deterministic frame seeking. Do not edit final `Root.tsx`, car/environment art, or final render workflows. Coordinate wheel radius/pose cadence with Agent 1 and layer tile widths with Agent 2. Native motion proof is an isolated test, **not** a finished film.
4. **Agent 4:** `integration/countryside-drive-final`. Own `src/scenes/countryside/CountrysideDrive.tsx`, final `src/Root.tsx` composition wiring, `scripts/render-countryside.mjs`, `.github/workflows/countryside-drive-final.yml`, `docs/COUNTRYSIDE_DRIVE_QA.md`. Integrate real Agents 1–3 commits/PRs (do NOT invent results), inspect original PNG sprites and the actual motion rig, then render and manually inspect the final MP4. Reject weak artwork and misaligned wheels; do not claim delivery before proof exists.

Agents 1–3 can work in parallel with isolated ownership, without editing shared `Root.tsx`, root `package.json`, or this contract. For isolated Remotion proofs, use an isolated composition entry point/workflow; don't edit each other's source or shared baseline. Agent 3 resolves **motion interfaces**, while Agent 4 resolves **final film integration** exclusively on its own branch. Agents must sync to the latest `production/countryside-drive` contract and report actual evidence. None merges to `main` or Sunset Harbor branches without owner approval.

## Deliverables / quality gates

- **Agent 1:** authored original sprites + editable source, car animation in a moving **MP4** (not only a still), contact-sheet proof from ≥9 frames, code and PR.
- **Agent 2:** native sprite/tiles/parallax planes + editable source, continuously moving **MP4**, explicit seamless repeat tests, 9+ frame samples, code and PR.
- **Agent 3:** frame-exact pixel-snapped parallax and driving motion module with callable export, wheel-speed calculation and meaningful seam/scrubbing tests, real moving proof MP4 and contact sheet, code and PR; no final scene ownership.
- **Agent 4:** integrate actual contributions from Agents 1–3 into a composited 12s native Remotion movie, nearest-neighbour 1080x1920 MP4 **`out/countryside-drive-final-1080p.mp4`**, GitHub Actions artifact with actual MP4 and full FFprobe report (width/height/fps/codec/duration/frame count), 100% FFmpeg decode, blackgap detection, 9-frame contact sheet, manual visual review at mobile screen size, check crisp pixel grid and continuous motion.

Reject and request corrections if any scene looks pastel-painterly or smoothly illustrated; trees are copy-pasted shapes, car silhouette looks like a rectangle, wheel rolls at wrong speed, road-tree layers visibly jerk or seam, sprite resampling blurs pixels, car floats, over-detail distracts from the simple concept, or final MP4 is absent. No invented metrics, success claims or download links.

**Music/audio:** no default Sunset Harbor soundtrack. A silent video is acceptable; agent may include restrained, self-produced/licensed SFX only when provenance is documented. Maintain the simple serene concept. Final publish/delivery requires owner's QA approval.
