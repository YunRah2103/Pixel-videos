# Countryside Drive V2 — Agent 3 moving-pixel polish
Branch: `agent/countryside-motion-v2` from existing integrated Countryside Drive film.
**Only a motion proof.** Agent 4 owns final integration and aesthetic acceptance.

## Sources and decisions

- World and car from the existing actual integrated native pixel assets, not fake rectangles or Sunset Harbor scenery.
- Frame 0–359, native 360x640 @30fps; 3x nearest-neighbour 1080x1920 MP4.
- Five independently wrapped planes: far 0.5px/f (180px repeat), mid 1px/f (360px), near 2px/f (360px), verge 2.5px/f (180px), road 3px/f (360px). All negative native integer offsets.
- Road movement is the only wheel clock: wheel turns = native road travel / (2π·11.5px). Eight authored wheel pose sprites; **no CSS spin**.
- Two individual axles sample road positions 137px and 222px using actual source road pixel marks at 109px and 305px. Compression/rebound is +1/-1 native px for just a few frames; **body sprite moves, tyres do not**. Camera and car location stay locked. No blur, grain, shake or FX.
- Native Pixel Studio V3 `contactShadow` creates a compact quantised alpha shadow. The V3 `carPose` rig is tested/assessed, but its generic wheelAngle and unrelated sinusoidal body pitch are intentionally *not* layered over real tyre rotation; this avoids wheel slide and waving car bodies. V3 `lightPixelScene` was inspected but full-scene ambient grading was intentionally omitted as it would grow a restrained 16-bit palette and flatten sprite accents.
- The 12s environment itself is unchanged; Agent 2 and Agent 4 own overall scenery art and final scene composition.

## Run and handoff

```sh
npm run studio:setup
npm run rigs:test
npm run environment:proof
npm run visual:qa
npx tsc --project tsconfig.countryside-motion.json --noEmit
node --experimental-strip-types --test tests/countryside-motion.test.mjs tests/countryside-motion-v2.test.mjs
node studio/countryside/world/build-world-art.mjs
node scripts/build-countryside-motion-shadow.mjs
npx remotion browser ensure
node scripts/render-countryside-motion.mjs
```

The GitHub Actions workflow `countryside-motion-v2-proof.yml` runs the same checks and uploads the 12s native Remotion `out/countryside-motion/countryside-motion-proof-1080p.mp4`, full FFmpeg decode verification, nine captured real frames and a contact sheet.

**Agent 4 instructions:** merge/cherry-pick `DrivingMotion.ts` and optional quantised `contact-shadow.png` generator. Keep original car art; separate body image from wheel sprites (as this standalone proof demonstrates), using `bobY` on BODY ONLY. Pass the authoritative `wheelRotationTurns` from the same `getCountrysideMotion(frame,11.5)`. Do not adjust layer scroll speeds separately or double-bob via CarLayer defaults. New fields `frontSpringPx`, `rearSpringPx`, `shadowOpacity` are additive; existing offsets and method signature remain compatible.

**Known limitation:** tyre circumference at the measured 11.5px radius does not divide 1080px road travel into an integer number of hub turns; do not fudge tyre rotation to create a mathematically impossible perfectly seamless hub phase. A cut at a nearly identical hand-drawn pose can be chosen by Agent 4 during final QA.
