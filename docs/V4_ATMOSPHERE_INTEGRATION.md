# Sunset Harbor V4 — Agent 2 lighting & atmosphere

Owner: GitHub Issue #6. Branch: agent/sunset-harbor-v4-atmosphere. Baseline: integration/sunset-harbor-v3-final, PR #4.

## Integrator contract

Import the art-only function from src/scenes/v4/HarborAtmosphereV4.mjs:

    import {renderHarborFxLayers} from './HarborAtmosphereV4.mjs';
    const fx=renderHarborFxLayers(frame, motion);

Five raw SVG fragment strings: clouds, water, waterHighlights, illumination, nearAir. Each is independently compositable inside a 360 × 640 SVG stage. Do not inject nested SVG roots. The function is seek-safe, pure and deterministic; no image references, clocks or mutable state.

Painting order for the eventual V4 integrated scene:
1. Sky and fx.clouds, then sun and distant coastline. Clouds includes a carefully tuned upper-sky repaint, so draw its opaque sky section behind visible sun/landmark architecture.
2. fx.water, then fx.waterHighlights; the latter carries solar, pier lamp and optional boat wake reflections.
3. Docks, boat, buildings, trees, people, promenade, railed foreground.
4. fx.nearAir as a distant mountain/horizon pass where appropriate, and fx.illumination as restrained lamp/window light accents. The proof places nearAir over a V3 backdrop; the integrated scene can split by depth.

Motion contract:
- cloudDrift in V3 units (defaults to frame/30). Independent parallax speeds and no random per-frame jitter.
- waterPhase (defaults to frame*.087) drives coherent crest, trough, reflection and boat wake motion.
- lightIntensity roughly 0.7–1.2; controls windows, lanterns and reflections.
- Optional geometry sunX, sunY (defaults 227/273), waterTop, waterBottom (353/535). Agent 1 should supply final scene geometry if it changes. Sun X controls the entire vertical reflected path.
- Optional boatX, boatY, boatBob track the wake; defaults match V3 boat animation.

## Proof render

Run node scripts/render-v4-atmosphere.mjs with Node 22, FFmpeg and npm dependencies installed. It dynamically writes an ephemeral isolated Remotion composition entry under out/, so no edits to src/Root.tsx or another agent's scene are required. It draws new sky/sea over V3 as a temporary proof and restores the V3 buildings/piers/near-field details with a separate clip. This temporary mask is not intended for the V4 integrated scene, where source FX layers can be placed in true depth order.

Outputs:
- out/sunset-harbor-v4-atmosphere-1080p.mp4: 12 seconds, 30fps, 360 native rendered frames, nearest-neighbour 3x 1080x1920 H.264/AAC.
- out/qa-v4-atmosphere/opening.png, middle.png, ending.png at frames 0/180/359.
- out/qa-v4-atmosphere/verification.json: ffprobe codec/frame count/duration validation plus whole-video ffmpeg decode and frame hashes.

Music uses exactly the V3 user-uploaded Day & Night score source, not replacement music. The audio's redistribution rights are not represented as cleared. The dedicated GitHub Action archives MP4, QA stills and report.

No changes to the main branch, source Root, Agent 1's world or Agent 3's story/camera modules. PR targets integration/sunset-harbor-v3-final.
