# Agent 1 — Countryside pixel car, integration handoff

Original asset: one red side-view coupe; no outside sprite license. Hand-edited 156x63 grid in `studio/countryside/car/build-car-art.mjs`, 13-colour indexed palette, plus original eight-pose 192x24 wheel strip. Generated PNGs in `public/countryside/car/`.

`import {CarLayer,WHEEL_RADIUS_PX,carRollAtFrame} from './CarLayer'`

`<CarLayer frame={frame} x={motion.carX} wheelContactY={495} wheelRotationTurns={motion.wheelRotationTurns} bobY={motion.bobY}/>`

Defaults: x=180 and wheelContactY=495; local top-left x-78 / wheelContactY+bobY-59. Wheel centres local x=35 and 120, y=47, 24x24 frame crops, visible radius **11.5 native pixels**. Distance-per-revolution = **2π × 11.5 = 72.2566 native pixels**. Positive turns roll right; Agent 3 should supply `roadTravelPx / (2*Math.PI*11.5)`. Without supplied turns, standalone proof uses 2.8 native px/frame. Suspension is deterministic and pixel-snapped, with optional external bobY.

Proof-only isolated entry `src/countryside-car-proof.tsx` does NOT modify `src/Root.tsx` or road/world/final film files. Native 360x640 at 30fps, 120 proof frames; exact 3x nearest upscaling, H.264 1080x1920, 9-frame contact sheet, FFprobe, full decode and eight distinct wheel poses. The proof's single horizontal line is a contact-position ruler, not the final road.

Reproduction: `npm install --no-audit --no-fund && npm run tools:check && npm run typecheck:toolkit && npm run assets:build && npm run assets:proof && npm run assets:qa && node scripts/render-countryside-car.mjs`.

Pixelorama optional editor is not preinstalled; editable palette source + Sharp used. Only report GitHub Actions MP4 verified once the workflow succeeds. No claim that this proof is the final film.
