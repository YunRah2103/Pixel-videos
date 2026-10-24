# Sunset Harbor V5 Agent 1 — original illustrated world
- Issue #12, source branch `agent/sunset-harbor-v5-world-art`, base PR #11.
- Primary contract `src/scenes/v5/WorldV5.tsx`: `V5WorldPlane({frame,motion,plane})` where plane is `far | architecture | harbor | promenade | foreground`.
- Actual original pixel source is `scripts/generate-v5-world.py`, drawing detailed per-material faces, custom Dutch and Normandy gables, clock tower, arcades, fishing docks, cobbles, railings, flowers and lanterns. Requires Pillow **only when changing the drawing**, not while rendering.
- Render asset: native 360x3200 128-colour indexed PNG atlas `public/v5/world/world-v5-atlas.png`. Each independent 360x640 slice occupies 640 pixel rows. Regenerate with `python3 scripts/generate-v5-world.py`.
- Composition: 360x640 @30fps/360 frames, depth mapping far=.28, architecture=.55, harbour=.63, promenade=1.0, foreground=1.28, nearest-neighbour 1080x1920 delivery.
- Never reuse V4 architecture: V5 proof replaces all V4 scenery except the atmospheric sky, water and character/boat/story motion owned by other agents.
- Agent 4: insert each V5 plane in the corresponding V4 layer slot. If you externally apply the camera depth like V4 Final, pass `motion={{...motion,disableWorldParallax:true}}` to prevent double movement. Optional motion falls back to V4 frame-derived motion.
- Native standalone preview: `node scripts/render-v5-world.mjs`. Dedicated proof root and scripts avoid modifying shared `src/Root.tsx`.
- Verify actual Github Actions artifact before marking approved. There is no merge to main in this PR.
