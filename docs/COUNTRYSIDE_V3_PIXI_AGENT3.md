# Countryside Drive V3 — Agent 3 PixiJS Motion & Visual Polish

Branch: `agent/countryside-v3-motion-pixi`, based on `integration/countryside-drive-v2-art`. **DO NOT MERGE TO MAIN.** The integrated film/art remain subject to owner and Agent 4 approval.

## Exactly where PixiJS is used (runtime, NOT only installed)

**Entrypoint:** `src/scenes/countryside/CountrysideDrive.tsx` renders `<PixiCountrysideWorld frame={frame} motion={m} />` before the original V2 `<CarLayer />`.

**Actual Pixi renderer:** `src/scenes/countryside/PixiCountrysideWorld.tsx`:
1. Instantiates `new pixi.Application()`, initializes a **real 360×640 WebGL canvas** with `antialias:false`, `resolution:1`, `autoStart:false` and transparent background.
2. `pixi.Assets.load(staticFile('countryside/world/...'))` loads six **actual hand-authored Agent 1 V2 world PNGs**, not demo geometry. The image textures explicitly set `texture.source.scaleMode='nearest'`.
3. Constructs six real `new pixi.TilingSprite({texture,width:360,height:...})` objects, in artist-approved order: sky, farTrees, midTrees, nearTrees, road, verge.
4. On each Remotion frame, `tile.tilePosition.x=layer.tileX` changes ALL five scrolling Pixi planes using the shared authoritative `getCountrysideMotion` state; all positions are native integers.
5. Constructs real `new pixi.Graphics()` objects to draw two restrained, quantized contact-shadow bars and at most seven 1×2 native-pixel moving foliage highlight flecks. Never use blur/soft lights/full-scene effects.
6. Explicitly calls `app.renderer.render({container:app.stage})` to write the new pixels to the **actual on-screen Pixi canvas** for that exact frame. The Pixi ticker remains stopped; no wall-clock animation is involved.
7. Remotion's `delayRender` blocks capture until PixiJS and all PNGs have initialized. If Pixi startup fails, `cancelRender` fails the MP4 render. **No CSS, DOM fallback, or static toolkit screenshot is used as a substitute.**

**Motion contract:** `src/scenes/countryside/DrivingMotion.ts` owns all world offsets, wheel rotations, and the 1-pixel axle-aware suspension. `PixiWorldPlan.ts` only converts that same exact frame/motion into safe Pixi sprite and Graphics instructions. Wheels still use original eight authored V2 hub frames with **15.5 px rolling radius**; `wheelRotationTurns = roadTravelPx / (2π × 15.5)`. Car chassis may spring ±1 native px, wheels stay grounded at native Y=495, zero camera shake.

The kit itself is exercised with `npm run studio:setup`, building PNG/atlas/environment, testing rigs, rendering a separate moving example and running visual QA. **That toolkit example is NOT this film's PixiJS proof.**

## Reproduce and inspect REAL evidence

Run in a Node 22 environment with Chromium and FFmpeg/FFprobe:

```bash
npm install --no-audit --no-fund
npm run studio:setup
npx tsc --project tsconfig.countryside-pixi.json --noEmit
node --experimental-strip-types --test tests/countryside-motion.test.mjs tests/countryside-motion-v2.test.mjs tests/countryside-v2-geometry.test.mjs tests/countryside-pixi-v3.test.mjs
node scripts/render-countryside.mjs
ffprobe -v error -count_frames -show_entries stream=codec_name,pix_fmt,width,height,nb_read_frames:format=duration -of json out/countryside-drive-final-1080p.mp4
ffmpeg -v error -xerror -i out/countryside-drive-final-1080p.mp4 -f null -
```

The branch-push workflow `.github/workflows/countryside-v3-pixi-motion.yml` runs this in GitHub Actions and publishes a **genuine 12-second, 360-frame, 30fps Remotion H.264 1080×1920 file** plus FFprobe/FFmpeg JSON, nine decoded frames, nine-frame contact sheet, Pixel Studio V3 diagnostics. Every captured frame is rendered from the actual Pixi canvas plus V2 coupe via Remotion then nearest-neighbour upscaled exactly 3×. Check video at mobile scale for smooth parallax, grounded wheels, foliage, no gaps, silhouette size, consistent native pixels. Tests and metadata do **not** equal subjective artistic approval.

## Integration ownership & future asset swap

* **World Agent:** Replace PNG files or their authored source in `studio/countryside/world/build-world-v2.mjs`. Keep the six stable layer names or update `PIXI_WORLD_LAYERS` concurrently. Agent 3's motion takes no dependency on world tree geometry.
* **Car Agent:** Keep exporting `CarLayer({frame,x,wheelContactY,wheelRotationTurns,bobY})`, `WHEEL_RADIUS_PX`. If sprite radius or road Y changes, communicate and use the new **actual** radius once in `getCountrysideMotion(frame,WHEEL_RADIUS_PX)`.
* **Final editor/Agent 4:** Cherrypick the V3 Pixi source, motion-plan file and this scene edit. Preserve the real scene and the 12s frame clock. No second scroll/wheel animation. This is a visual-motion proof until human artistic review, not a forced main merge.

Known boundary: the V2 world PNG widths (720/840/960/384/384) differ from the older motion rig's conceptual 180/360/360/180/360 cycle repeat values. PixiJS wraps at each **actual PNG** tile width; all scrolling is continuous at internal tile seams. The last frame is **not guaranteed** to be perfectly match-cut loopable to frame 0 without a future art/motion loop contract. Do not falsely label it seamless across the 12-second cut.
