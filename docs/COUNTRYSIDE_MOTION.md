# Countryside Drive — Agent 3 motion handoff

**Scope:** This branch owns only native frame-based animation; the motion-only proof contains **debug stand-in art**, not real Agent 1 or Agent 2 sprites. Agent 4 owns the finished film.

## Single animation interface

Import `getCountrysideMotion` from `src/scenes/countryside/DrivingMotion.ts`. In the final Remotion composition call it **once** per frame:

```tsx
const frame = useCurrentFrame();
const m = getCountrysideMotion(frame, measuredWheelRadiusInNativePixels);
const layers = ['sky','farTrees','midTrees','nearTrees','verge','road'] as const;
return <>
  {layers.map(layer => (
    <CountrysideWorldLayer
      key={layer}
      frame={frame}
      layer={layer}
      offsetX={layer === 'sky' ? 0 : m.offsets[layer]}
    />
  ))}
  <CarLayer frame={frame} x={m.carX} wheelContactY={495} />
</>;
```

The final car wheel pose should use **`wheelPoseIndex(m.wheelRotationTurns, authoredPoseCount)`** (or interpolate authored hub angles without changing tyre outline). Prefer an optional `wheelRotationTurns` prop on Agent 1's CarLayer; if its API doesn't expose one, have Agent 1 call `getCountrysideMotion(frame,measuredRadius)` inside its wheel layer. **Do not put a second wheel clock in CarLayer.** Apply `bobY` only to the suspension/body artwork if supported, *not* to wheels or tyre contact point. The car holds X=180, wheel contact Y≈495; no global camera transform or zoom.

## Native speeds, looping and tiling

| Layer | Native pixels/frame | Travel/12s | Recommended exact repeat width |
| --- | ---: | ---: | ---: |
| farTrees | 0.5 | 180px | 180px |
| midTrees | 1.0 | 360px | 360px |
| nearTrees | 2.0 | 720px | 360px |
| verge | 2.5 | 900px | 180px |
| road | 3.0 | 1080px | 360px |

Every computed `offsets` value is **negative** and **integer-pixel-snapped**, i.e. leftward scrolling. World renderer must interpret it as authoritative: avoid any additional `frame*speed`, CSS easing, fractional transforms or smoothing. Background sky stays still. Render enough neighbouring sprite tiles that neither seam nor empty space can be seen. `wrapTileOffset(offsetX,tileWidth)` normalises negative offsets to `[-width+1,0]`.

**Coordination requirement for Agent 2:** these widths are a recommended exact 12s loop contract. If actual layer tile widths differ, tell Agent 3 and Agent 4; adjust period/speed coherently before final integration rather than claiming a guaranteed loop. Tree artwork MUST have identical first/last edges at each periodic boundary and meaningful shape variety within each cycle.

### Wheel calibration

- Nominal road travel = **3 native pixels per frame** (90px/s).
- Turns = `roadTravelPx / (2 * PI * measuredWheelRadiusPx)`.
- The provisional radius `1080/(36π) ≈ 9.549px` is a loop-friendly engineering assumption, **not a measurement of Agent 1's wheel sprite**. It produces exactly 18 rotations per 12 seconds while road repeats at the correct tile period.
- If Agent 1's tyre contact radius is 10px or 12px instead, supply that actual measured radius explicitly: no deliberate wheel slip. A different radius may not give an exact wheel-hub pose loop; coordinate a matching hand-authored hub-phase period instead of pretending it is loop-seamless.
- Tyre centre around Y=485 and bottom/contact Y≈495 in initial proof. The **real car artist must confirm actual measured wheel radius**, pose count, and axle coordinates to Agent 4.

## Executable QA

```bash
npm install --no-audit --no-fund
npm run tools:check
npm run typecheck:toolkit
npm run assets:verify
node --experimental-strip-types --test tests/countryside-motion.test.mjs
npx remotion browser ensure
node scripts/render-countryside-motion.mjs
```

Standalone motion proof:
`out/countryside-motion/countryside-motion-proof-1080p.mp4` (12s, 360 frames, 30fps, H.264 yuv420p, 1080×1920).
Contact sheet and 9 stills:
`out/countryside-motion/motion-contact-sheet.png` and `captures/*.png`.
QA report:
`out/countryside-motion/motion-verification.json` (full FFmpeg decode, distinct captures, FFprobe). CI publishes all outputs as `countryside-agent3-motion-native-proof` artifact. **The actual MP4 and checks must exist before any PASS claim.**

Studio toolkit use: pure deterministic Remotion/JS frame math, isolated React proof composition, native pixels/nearest-neighbour FFmpeg, FFprobe full decode and existing toolkit smoke checks. Pixelorama/Krita/LDtk/Godot are authoring tools, *not* needed to implement this motion-only rig; no claim they are installed. No harbour 3D/parallax depth preset reused.

No modification of Agent 1 or Agent 2 art source, final `src/Root.tsx`, final workflow, or main branch.
