# Countryside Drive V2 — Agent 4 final integration

**Specialist sources**: PR #33 world art, PR #32 car art, PR #30 native motion, integrated on PR #31. These are the real production sources, not Pixel Studio V3 demos.

- Original 16-bit pixel forest at six independent native layers; two restrained pixel-cloud groupings fill formerly dead upper sky.
- V2 car 192×80 with 256×32 eight-pose rotating wheels, measured native wheel radius **15.5px**.
- The **one** 3px/frame road clock determines wheel turns as travel / (2π × 15.5).
- V2 wheel screen centres **127px rear** and **235px front** are used for axle events; spring displacement moves body only and tyres remain at Y495.
- Native transparent pixel verge now composited *after* the road to add grass without covering asphalt.
- Pixel Studio V3 setup, environment build/proof, atlas, rig test, visual QA remain part of final CI.
- Final render contract: native 360×640, 360 frames, 30fps; nearest-neighbour 3× encoded H.264 yuv420p 1080×1920; full frame decode, no black intervals, 9 real checkpoint frames and contact sheet.
- No merge to main until actual owner approval after watching the film. Technical QA is not artistic approval.
