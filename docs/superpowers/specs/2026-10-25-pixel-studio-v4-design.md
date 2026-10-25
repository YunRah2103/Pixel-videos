# Pixel Studio V4 design

Status: proposed; implementation and visual acceptance remain pending.

Pinned audit inputs: V3 toolkit `2a366edc3e39b152705443dc6236b0b5e65f1f04`; car `ba429fbe7f8400a4014e43430bd712fa4db66d6d`; world `a8fb67fe0afc5b150e6a3ce0bfab74f06b324dd0`; motion `b4ea75bb16c253970d314f5767f9194ec857fa44`. Later branch changes require a fresh diff before integration.

Builder review clarifications: keep editable masters in `studio/v4/sources/`, committed production exports in `public/studio-v4/`, manifest/configuration in `studio/v4/`, runtime in `src/toolkit/v4/`, and disposable evidence renders in `out/studio-v4/`. Generators write staging files and never overwrite masters. Pixelorama/Krita evidence must show substantive artwork edits and LDtk evidence must show an edited layout affecting output; opening/exporting generated files alone does not prove refinement. A documented unavailable tool and demonstrated compatible alternative satisfies the user's exception; missing or failed evidence without an alternative blocks completion.

Beyond the initial three vehicles, completion requires at least one distinct editable rig-compatible foundation per remaining requested vehicle class and one independently renderable modular preset per listed environment group. Each foundation is visibly labelled as such. The reusable library must also demonstrate a person with idle/walk frames, water/reflection, rain, dust, exhaust, smoke, sparks and lamp effects, alongside flora, terrain, buildings and sky props. Finished status requires inspected exports and moving showcases; catalogue quantity alone is insufficient.

## Purpose

Make Pixel Videos a reusable production studio whose agents can select authored vehicles and environments and render beautiful, consistent pixel animation without rebuilding a pipeline. Preserve existing scenes and commands. Do not merge to main.

## Repository findings

The audited remote contains a minimal main branch and separate V3 toolkit, car, world, motion and integration branches. V3 provides Sharp atlas/environment builders, pure frame rigs, native pixel lighting, TypeScript checks and FFmpeg diagnostics. The car branch contains layered OpenRaster authoring and Pixelorama CLI export scripts. The world branch contains an LDtk layout and editor export workflow. These scripts and handoffs are not proof that every editor invocation succeeded. Existing V4 art-direction work includes small generated vehicle templates and fractional shot zoom; neither is an appropriate foundation for the requested premium vehicle library or strict integer scaling.

## Approaches

1. Extend and consolidate V3 behind a V4 manifest and shared renderer (recommended engineering choice): preserve contracts, selectively integrate compatible artwork, replace weak assets only after comparison, and add evidence-backed editor/export stages.
2. Start an independent studio: cleaner initial layout but duplicates working rigs and risks incompatibility with existing productions.
3. Expand generated template counts: fast breadth but fails the requirement for excellent individually designed vehicle silhouettes.

The proposed design uses approach 1. This is a recommendation awaiting design approval, not a recorded user choice.

## Style contract

Use 360×640 logical portrait frames and exact 3× output at 1080×1920. Author sprites at that same world pixel density; integer placements and nearest sampling throughout. Use curated per-material palette ramps, intentional clusters and sparse controlled dithering. No smooth artwork plus pixelation, fractional sprite zoom, antialiased rotation, or whole-image blur. Wheel motion uses discrete authored frames. Diagnostic renders include native PNGs and mobile-size previews.

## Asset and source architecture

Each manifest entry records ID, category, native dimensions, pivot, contact points, layer ordering, source and export paths, palette, frame rectangles, animation holds, licence and provenance. Vehicle entries additionally record axle centres, wheel radius, paint masks, lamps and supported configurations. Validate geometry and source/export correspondence. Reject missing IDs, duplicate IDs, invalid rectangles and non-integer scales.

Keep editable originals beside versioned exports: Pixelorama native projects where supported plus layered ORA interchange, Krita KRA background masters, and LDtk level sources. Record real editor commands, versions, logs and export hashes. Generated ORA files are labelled generated; they are not evidence of manual editor refinement. A tool blocked by the host is recorded unavailable with its actual error and a clearly named alternative.

## Initial finished collection and expansion

Finish three distinct vehicles first: sports coupe, everyday hatchback and rally vehicle. Each has independently editable paint, glass, wheels and lamps; at least eight discrete wheel poses; paint variations; driving, acceleration, braking and bounded suspension. Validate believable wheelbase, roof, overhangs and road contact visually. Add documented rig-compatible foundations for saloons, SUVs, supercars, racing cars, trucks, vans and motorcycles; label unfinished foundations honestly and exclude them from the finished catalogue.

First environment is a polished countryside with separately authored sky/clouds, distant hills, varied tree silhouettes, undergrowth, grass, road/shoulder and foreground decoration. LDtk positions must directly determine placement. Shared tile/layer contracts support forest/mountain, city/suburb, coastal/harbour, highway/bridge, circuit, desert, rain and night presets. Only promote a preset as finished after inspecting its render; catalogue entries distinguish finished from foundations.

Build reusable flora, rocks, signs, road furniture, buildings, sky objects, people, water and effects in this same style. Prioritise curated assets visible in the demonstrations over quantity.

## Rendering and animation

Remotion owns frame time and capture readiness. A persistent PixiJS scene loads atlas textures once with nearest sampling, disables autonomous ticker progression and explicitly renders deterministic frame updates. Remotion waits for asset loading and each requested frame; propagate renderer failures. Avoid asynchronous screenshots of stale canvases.

Provide pure functions for integrated road distance, wheel frame selection, axle suspension, camera tracking, wrapping parallax, foliage sway, sprite playback, seeded particles, palette-stepped lighting, transitions and loops. Ground wheel centres independently of body bob. Drive wheels and road from one distance signal. Test out-of-order frame evaluation and render concurrency. Loop closure accounts for tile periods, wheel phase and particle state, not just modulo time.

Expose vehicle/environment presets and one small scene configuration API. A starter requires only IDs, duration, speed and lighting; no asset-path plumbing. Preserve all legacy entry points and add isolated V4 composition IDs and scripts.

## Agent workflow

Provide one setup command, manifest validation, deterministic import/export and atlas generation, starter rendering and full verification. Pin dependencies and preserve a lockfile. Produce a visual contact catalogue from actual exports. Document a minimal copyable scene, API options, adding art, editing sources, tool availability, failure recovery and exact proof locations. Setup must not silently regenerate or overwrite edited source art.

## Tool investigation

Audit and meaningfully exercise Pixel Studio V3, Pixelorama, Krita, LDtk, Sharp, PixiJS, Remotion, FFmpeg and FFprobe. Investigate compatible open-source palette/atlas/animation helpers only when they fill an identified gap; prefer the existing atlas and deterministic rigs over dependency accumulation. Record upstream licences separately from original art. No downloaded art enters the finished library without a provenance entry.

## Delivery and acceptance

Commit in reviewable stages: consolidation/contracts; art; runtime/templates; demonstrations/evidence. Open a dedicated PR, unmerged. Deliver a 14-second 1080×1920 30fps countryside film and genuine moving vehicle, environment and component showcases. Render with the production PixiJS/Remotion path. FFprobe validates exact dimensions, rate and duration; full FFmpeg decoding must succeed. Inspect real decoded frames, native pixels and phone-size views for proportions, road contact, palette consistency, clipping, seams, blur and gaps. Numerical frame differences do not substitute for artistic review.

Run TypeScript and production bundling, source/export validation, rig/manifest tests, independent component smoke compositions and repeatability tests. Compare legacy baseline and V4 command results before claiming compatibility. Store evidence reports with commit IDs, exact commands, exit codes, screenshots where available, hashes and failures. Do not call the studio complete while required tools or visual demonstrations lack successful evidence.

## Constraints and builder decisions

Network and GUI availability must be tested, not assumed. Current local audit finds Node and FFmpeg, but no Pixelorama, Krita or LDtk executable on PATH. CI may provide editor execution; CI evidence must be retrieved and inspected before claims. Three finished vehicles and the countryside are the first artistic acceptance milestone; broader categories remain required subsequent work, not an excuse to mark the complete request finished early. Engineer chooses asset IDs, palettes and module internals consistent with this contract.
