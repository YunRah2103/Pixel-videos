# Sunset Harbor V4 — Agent 1 world and integration contract

**Issue:** #5  
**Branch:** agent/sunset-harbor-v4-world  
**PR base:** integration/sunset-harbor-v3-final

## Art

An original 360 × 640 world reillustration: several atmospheric mountain planes, varied seaside houses with gable/hip/shed roofs, bell tower, shops and arcaded façade, windows and flowerboxes, stone seawalls, hand-planked fishing piers, two small boats, benches, café furniture, wisteria, plants, detailed paving and warm streetlights.

## Stable API and layering

Import renderHarborBaseLayers(frame, motion={}) from src/scenes/v4/HarborWorldV4.mjs.

Returns six **raw SVG strings**: sky, distant, architecture, harbourStructures, promenade, foreground (no nested SVG root).

Suggested order for final integration: sky, [Agent 2 clouds], distant, [Agent 2 water], architecture, harbourStructures, [Agent 3 people and story boat], promenade, foreground.

Sky covers y0–354, water reserved y353–537, village shoreline roughly y240–405, promenade y515–640.

The module deliberately does NOT render clouds or open water: Agent 2 replaces those independently. Existing animation / foreground actors remain Agent 3-owned. CameraX/Y are optional and scaled by depth. Pixel positions are rounded and deterministic. SVG root must use width 360, height 640, viewBox 0 0 360 640, and shape-rendering crispEdges.

## Isolated proof

Run `npm install` then `node scripts/render-v4-world.mjs`.

Own entry point: src/scenes/v4/HarborWorldProofIndex.ts. Composition: HarborWorldV4Proof. Duration: 360 frames at 30 FPS. The proof contains **temporary cloud and water placeholders only**. It does not edit the V3 root or the other V4 agents' modules.

Output: out/v4-world/sunset-harbor-v4-world-1080p.mp4. FFmpeg nearest-neighbour 3× upscale; H.264 video and AAC from the existing user-supplied V3 Day & Night audio. Full decoding and FFprobe checks are required. Screenshots from frames 0, 180, 330 and JSON proof are written to out/v4-world/qa.

## Provenance and boundaries

All vector clusters and pixel structures are newly authored source code. No third-party artworks or additional music assets. No changes to V3, V2, main, Agent 2, or Agent 3 files.
