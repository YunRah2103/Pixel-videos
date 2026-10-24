# Countryside Drive V2 — Agent 2 car art handoff

**Scope:** Original hero vehicle artwork only. The native pixel-art car is a 192x80 side-view red/orange sporting coupe, replacing the original 156x63 sprite. No smooth vector-to-raster conversion, downscaling, blur, AI-derived art, 3D or borrowed sprites. The body is encoded as editable palette-indexed pixel rows in `studio/countryside/car/build-car-v2.mjs`; the generator also creates eight native 32x32 rotating hub designs. Each pixel is authored directly on the native grid.

## Art and assets
- Master sprite source: `studio/countryside/car/build-car-v2.mjs`
- Body: `public/countryside/car/coupe-v2-body.png` — 192x80, transparent
- Wheel strip: `public/countryside/car/coupe-v2-wheels-8.png` — 256x32 (8x 32x32)
- Palette: original 15-entry native RGBA table, primarily warm burnt red/orange and dark teal glass.
- Design cues: tall cabin, long athletic shoulder, separately drawn angular side glazing, tiny mirror, stepped nose, front/rear lamps, layered rocker panels, wheel openings and five-spoke metallic hub details.
- Original art; no third-party sprite assets or attribution dependencies.

## Stable composition interface
`src/scenes/countryside/CarLayer.tsx` still exports `CarLayer({frame,x?,wheelContactY?,wheelRotationTurns?,bobY?})` and `WHEEL_RADIUS_PX`. Native car centre defaults to `x=180`; contact Y defaults to `495`. Body sprite origin = `[x - 96, wheelContactY - 78]`. Wheel centres are native local X `43` and `151`, Y `62`; wheel diameter `32`, measured rolling radius `15.5` px (effective circumference `2π × 15.5 ≈ 97.389` native px).

**Important:** Agent 3/4 should pass `wheelRotationTurns=roadTravelPx/(2*Math.PI*WHEEL_RADIUS_PX)` from the one road motion rig. Do not reuse the old 11.5px radius. Wheel sprites remain grounded when a `bobY` is supplied; only the body moves ±1px. The contact shadow is two pixel-snapped static bands beneath the chassis, not a blurred filtered ellipse.

## Toolkit and proof
This branch includes the actual Pixel Studio V3 scripts ported from `feat/pixel-studio-v3-production` atop the prior finished countryside baseline. Run:

```bash
npm run studio:setup
npm run atlas:build
npm run rigs:test
npm run visual:qa
npm run car:v2:build
npm run car:v2:proof
```

The first command runs dependency install, toolkit scene proof, rig tests, atlas packing and 90-frame numerical visual QA; the last command renders separate 120-frame real Remotion proof, exact nearest-neighbour 3x enlargement to 1080×1920, FFprobe, full FFmpeg decode, nine independently decoded captures, and contact sheet. Main final CountrysideDrive composition remains owned by the master integrator; this PR makes no final film or main-branch merge claim.

**Isolated video source:** `src/countryside-v2-car-proof.tsx` (road/tree shapes are neutral technical staging, not Agent 1's replacement environment). Generated proof: `out/car-v2-proof/coupe-v2-1080x1920.mp4`; QA: `out/car-v2-proof/verification.json`, `out/car-v2-proof/contact-sheet.png`.

The car was independently inspected in a local four-second 30fps 1080x1920 genuine MP4 with 120 distinct native frames, FFprobe PASS, full decode PASS and nine-frame visual contact sheet. GitHub native Remotion and toolkit proof must pass Actions before PR is described as CI-verified. Final art approval remains with owner / Agent 4.
