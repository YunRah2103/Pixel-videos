# Countryside Drive — Agent 4 final assembly and QA

**Stage:** Integration scaffold only; **not** a delivered final film. Issue #25.
Base `production/countryside-drive`; final integration branch `integration/countryside-drive-final`.
Do not merge into `main` without owner signoff.

## Specialist source requirements

1. Agent 1 (#21) must deliver real `src/scenes/countryside/CarLayer.tsx`,
   original editable car sprites under `studio/countryside/car/`,
   output assets under `public/countryside/car/`, four wheel poses and MP4 proof.
2. Agent 2 (#22) must deliver real `src/scenes/countryside/WorldLayers.tsx`,
   authored countryside PNG sprites/tiles in `studio/countryside/world/` and
   `public/countryside/world/`, tile seam checks and moving MP4 proof.
3. Agent 3 (#23) must deliver real `src/scenes/countryside/DrivingMotion.ts`,
   deterministic parallax, wheel-distance tests and moving MP4 proof.
4. The integration branch must incorporate each actual original authored source,
   including PNGs; inspect signatures and test `CarLayer` wheel cadence against
   `getCountrysideMotion(frame).wheelRotationTurns` before signoff.
5. Check the linked PRs, successful proof workflows and nine-frame sheets.
   A present source file is not proof of artistic or technical completion.

## Composition choreography

Native frame canvas 360×640, 360 frames, 30 FPS, one side-on car, road, sky and trees.
One scrolling controller: Agent 3's exported `offsets`, passed once to
Agent 2's `offsetX`. Do **not** duplicate camera motion inside layers.
Layer order: sky → farTrees → midTrees → nearTrees → verge → road → car.
Verify near foliage is behind the car or intentionally masked, road starts at
native Y480, wheel contact near Y495, and vertical bob never introduces floating.
Pixel snap before placement. No 3D/post-pixelation, no full-image blur.

## Reproduce

```bash
npm install --no-audit --no-fund
npm run tools:check
npm run typecheck:toolkit
npm run assets:verify
node scripts/check-countryside-ready.mjs
node scripts/render-countryside.mjs
```

The readiness step is **supposed to fail** if any specialist source does not exist.
The render is never allowed to substitute toolkit demo art or Sunset Harbor footage.
Actual Remotion native render is converted with FFmpeg nearest-neighbour 3×,
yuv420p H.264 1080×1920, 30 fps and 12 seconds; it is silent, without unlicensed music.

## Automated QA

- FFprobe: exact 360 decoded frames, 30/1 FPS, H.264, 1080×1920, yuv420p,
  approximately 12.000 seconds.
- FFmpeg full decode with `-xerror` and automated black-gap detection.
- Nine captures at native source frames 0,45,90,135,180,225,270,315,359
  from **decoded final MP4**, 3×3 contact sheet and hash diversity check.
- Measure approximate deviation from exact 3× raster grid. YUV420 encoding
  can soften chroma edges, so this is a *reported measurement*, not automatic
  proof that the authored sprite work is pixel-perfect.
- `verification.json` marks technical verification only; owner/artistic
  signoff requires manual movie and contact-sheet inspection.

## Human review and release gates

- Inspect frames **and play real MP4** on phone-size display. Confirm recognisable
  hand-authored red car silhouette, distinct original tree crowns, limited colour
  palette, hard 1-native-pixel edges, believable wheels and ground contact.
- Review at least 0s, 1.5s, 3s, 4.5s, 6s, 7.5s, 9s, 10.5s, 11.97s for seam
  jumps, duplicate trees, wobble, blur, dark frames or wrong direction of travel.
- Compare travel speed and axle rotation empirically with Agent 3 wheel radius
  and Agent 1 artwork. No slipping or surreal suspension bounce.
- Film must show only car, countryside trees, one road and basic verges/sky.
- Confirm source-art ownership/licenses before publication.
- Link the **actual successful** Actions run and its final **MP4 artifact** in
  the draft PR. Do not mark delivered based on workflow definition alone.
- Merge is forbidden until the owner explicitly approves after watching.

## 24 October integration source audit / scenery recovery

- Agent 1 PR #28: `CarLayer.tsx`, original body PNG and 8-pose wheel PNG
  imported by blob SHA (no rewritten placeholder). 11.5 native-pixel radius.
- Agent 3 PR #27: `DrivingMotion.ts` original exported rig imported by SHA.
  The final composition calls `getCountrysideMotion(frame,WHEEL_RADIUS_PX)`;
  road moves three native pixels/frame and both wheel sprites use its turns.
- Agent 2 branch `agent/countryside-world`, commit `2b5b0d1`, did deliver
  `WorldLayers.tsx`, but **did not commit any of the six PNG sprite images
  referenced by that component**, nor a successful moving scenery proof/PR
  at integration time. It would render missing images uncorrected.
- As Agent 4 recovery, `studio/countryside/world/build-world-art.mjs` now
  generates *new original native pixel art* rather than pretending missing
  PNGs were supplied by Agent 2. Code uses hand-authored stepped oak,
  beech, chestnut and poplar silhouettes with authored leaf clusters and
  limited hard pixel palette. All sources are editable, owned by this PR.
  **This is NOT attributed to Agent 2.** Its original world renderer
  and style contract are retained with updated width constants.
- World tile widths now far 180, mid 360, near 360, verge 180, road 360
  native pixels. Each exact width divides its 12-second motion travel
  (180,360,720,900,1080). Agent 3 is still the only scrolling source.
- Tyre-contact alignment is fixed: `wheelContactY={495}`,
  `bobY={0}`, `wheelRotationTurns={m.wheelRotationTurns}`.
  Applying bobY to the car's entire layer would make *both wheels float*,
  so body suspension animation is withheld rather than faking contact.
- The final verification output is still subject to **actual workflow
  completion and visual review**; build/run success by itself does not
  certify artistry or user approval.
