# Countryside Drive V3 — master integration evidence and release status

**Status: BLOCKED pending actual V3 agent files and execution proof. This branch is intentionally NOT final and MUST NOT merge to main.**

## Source baseline inspected

- Base `integration/countryside-drive-v2-art` at `097a00ee348d2b07ae40019916712c8343efab56`.
- PR #31 and real CI run [40144338121](https://github.com/YunRah2103/Pixel-videos/actions/runs/40144338121) establish a genuine **V2** 1080x1920, 30fps, 12s Remotion/FFmpeg baseline. This is NOT proof of V3 tools.
- V2 hero sprite: 192x80 native source, eight 32x32 wheel poses, measured rolling radius **15.5 native px**. Preserve exact wheel distance formula `roadTravelPx/(2*Math.PI*WHEEL_RADIUS_PX)`, fixed contact Y=495 and body-only spring offsets.
- Original world source: `studio/countryside/world/build-world-v2.mjs`, production layers in `WorldLayers.tsx`. Keep integer/native pixel scale, no blur, vector fake art or camera shake.

## Mandatory V3 specialist intake (not accepted on claims)

| Specialist | Native source/evidence required | Present at branch initialization |
| --- | --- | --- |
| Agent 1: World | Original layered .ora or native .pxo/.kra imported/exported by real Pixelorama and Krita, .ldtk LDtk, execution logs, authored PNGs, motion proof and branch/PR | **NO** |
| Agent 2: Car | Original layered car .ora/.pxo, Pixelorama-generated native PNG and unique wheel frames, actual editor execution log, moving proof and branch/PR | **NO** |
| Agent 3: Motion | Production Remotion graph imports PixiJS and uses it to draw real moving frames, recorded real render/proof and PR | **YES — technically verified**: PR #35, [successful Actions 40145928869](https://github.com/YunRah2103/Pixel-videos/actions/runs/40145928869). Import integrated into this branch. Owner aesthetic approval still false. |

Merely installing Pixelorama, Krita, LDtk or PixiJS is not sufficient. Independently open and inspect native editable files and recorded execution evidence; manually check actual MP4 movement. `scripts/audit-countryside-v3.mjs --strict` blocks absent source and missing run references; **its passing is only machine preflight**, not proof of trustworthy tool usage or artistic approval.

## Production integration rules

1. Port Agent 1 original scene, art, LDtk layout into real `CountrysideDrive` production path. Inspect layer seams, transparency, depth, canopy silhouette and countryside composition at 360x640 native.
2. Port Agent 2 hero sprite and its measured rolling radius/wheel-frame count. Respect wheel centres and contact Y from the real updated art; no independent spin timer.
3. Port Agent 3 actual PixiJS code into the production Remotion render. Trace imports and verify runtime render side effects. No dead/demo Pixi imports credited as implementation.
4. Integrate with Pixel Studio V3 pipelines, single shared road-distance clock, subtle spring physics and integer nearest-neighbour scaling.
5. Run the actual 360-frame Remotion source at 30fps, 1080x1920 H.264, full FFmpeg -xerror decode, FFprobe metadata, 9 distinct decoded frames and contact sheet. Compare opening/middle/ending visually at mobile size.
6. Approve only after original artwork and premium pixel-art appearance meet quality bar; reject average art, missing native tool evidence, clipping, black gaps, wheel sliding, repeated bland trees or irrelevant visual effects.

## Audit/report location

- `out/countryside-v3-qa/tool-audit.json` generated on CI. Failure is intentional until V3 agent evidence lands.
- `evidence/countryside-v3/agent{1,2,3}/tool-execution.json` must identify specific real CI/tool-execution URLs and source-file provenance.
- A separate workflow job can publish a **nonfinal V2-derived moving preview**. Do not label it as the verified V3 film.

## Agent 3 independent integration / actual MP4 examination (25 Oct 2026)

- Real original V3 [PR #35](https://github.com/YunRah2103/Pixel-videos/pull/35) source files imported by their **exact source blob SHA**, not reimplementations.
- [Run #40145928869](https://github.com/YunRah2103/Pixel-videos/actions/runs/40145928869) concluded SUCCESS and produced [artifact #12580342095](https://github.com/YunRah2103/Pixel-videos/actions/runs/40145928869/artifacts/12580342095). Real `PixiCountrysideWorld` connects to active `CountrysideDrive` and performs PixiJS Application, Assets.load, six TilingSprite tile offsets, Graphics shadows and renderer.render at the exact Remotion frame. It throws rather than falling back when WebGL fails.
- Downloaded and independently inspected actual H.264 Pixi-proven MP4 and its 9-frame contact sheet, compared frame 180 to the V2 baseline and executed full FFmpeg -xerror decode PASS; 1080x1920 30fps 360 frames 12s. These checks verify real video production, **not artistic approval**.
- Current trees still appear blocky and too symmetrical, sky occupies excessive screen area; Agent 1 scenery and Agent 2 car must improve before release. Their source/tool proofs remain blocked.

### Editable source format policy

Both Pixelorama and Krita can work with the open layered raster `.ora` format. Requiring `.pxo` or `.kra` **specifically** would wrongly reject genuine exports. The integrator instead requires authentic layered source generated/committed or linked in a verified CI artifact, actual executable tool invocation and logs with resulting exported PNGs, plus LDtk's real level data. A source file or installed package alone is **not** proof those tools were used.
