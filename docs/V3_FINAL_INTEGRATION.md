# Sunset Harbor V3 — integrated master

This branch joins PR #3's fully redrawn procedural coastal world with PR #2's frame-exact camera motion and handmade character/life layers.

- **Native scene**: `SunsetHarborV3Final` @ 360×640, 30fps, 360 frames, twelve seconds.
- **Render**: `node scripts/render-v3-final.mjs`; outputs 1080×1920 H.264 + AAC with nearest-neighbour pixels.
- **Score**: user-supplied Day & Night upload excerpt from Agent 2's proof, compact encoded source `assets/v3-chill-part01.b64` (4s repeated with fade). This replaces the old V2 jazz recording in the final V3 cut.
- **Art**: imported `renderHarborWorld` from Agent 1; augmented `harborLifeSvg` from Agent 2.
- **QA**: GitHub Actions confirms all 360 decoded frames, music, dimensions and audio codec, plus 3 frame captures. No success may be claimed before the workflow passes.
- **Provenance**: handmade code art; the provided audio is not guaranteed public-distribution cleared.

Agent PRs are unmerged. The integration branch does not modify main.
