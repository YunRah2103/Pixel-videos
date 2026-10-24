# Sunset Harbor V3 — Master Environment Artist handoff

Agent 1 owns `src/scenes/v3/HarborWorld.mjs`, an original 360×640 SVG painter rendering deterministically for any supplied frame. Agent 2 owns camera/story/movement/jazz synchronization and can import `renderHarborWorld(frame, motion = {})`. The original `SunsetHarbor` composition and soundtrack are preserved; environment proof has a different composition ID, `HarborEnvironmentProof`.

## Artwork
- Multi-band sunset atmosphere, new pastel cloud masses, layered atmospheric veils, birds and golden solar focal point.
- Stronger coherent water reflection corridor with hundreds of depth-scaled turquoise/coral/golden facets and reflected architecture.
- Varied seaside houses, dormers, roof tile clusters, lit interiors, flower boxes, terraces, signs, waterfront bell tower, jetties and moving boats.
- Detailed foreground pixel plants, planters, lamps, cobbled terrace, bench and hand-painted foliage.
- New work is procedural in the sense of frame-exact deterministic pixel primitives, but silhouettes, palette groups, skyline, facades and reflection composition are deliberately authored. No external sprites or pixelation filters.

## API
```js
import {renderHarborWorld} from './v3/HarborWorld.mjs';
const svg=renderHarborWorld(frame,{
 cameraX:0,cameraY:0,cameraZoom:1,
 cloudDrift:frame/30,
 waterMotion:Math.sin(frame/40),
 foliage:Math.sin(frame/25),
 lightIntensity:1,
});
```

Return value is complete 360×640 SVG with no wall-clock/random inputs. Motion fields are optional and safe for a separate animation director to drive. The isolated Remotion proof is 360 frames / 12s @ 30fps, nearest-neighbour ×3 to 1080×1920, H.264. GitHub Actions renders via `node scripts/render-v3-environment.mjs`, ffprobes, decodes and uploads the MP4 and frame captures (0/180/359).

Existing jazz is user-supplied and remains in `assets/sunset-jazz-excerpt.m4a.b64`. It is not royalty-free or MIT-licensed; verify rights before public distribution.
