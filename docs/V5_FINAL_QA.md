# Sunset Harbor V5 — Final Director's Production Plan / QA Gate

**Status: PREPRODUCTION ONLY — NOT A FINISHED V5 FILM.**
**Issue:** #15. **Base:** `integration/sunset-harbor-v4-final` at `22f9c9f87aed98fb2cbdeaf958f998c3eda32a10`.
**Delivering branch:** `integration/sunset-harbor-v5-final`; PR target must remain V4, never main.

## V4 baseline actually inspected (24 October 2026)
- Source: successful native V4 run [40110703217](https://github.com/YunRah2103/Pixel-videos/actions/runs/40110703217), artifact [12566107531](https://github.com/YunRah2103/Pixel-videos/actions/runs/40110703217/artifacts/12566107531). Extracted the real MP4 and 9-image contact sheet, reviewed full-resolution frame 180.
- Independent ffprobe/full ffmpeg decode: H.264 1080x1920 30/1 fps, **360 decoded frames**, AAC 48kHz mono, **12.000s**, complete decode successful. V4 is sound as a technical reference, *not* an artistic target.
- Visible strengths: pleasant teal/rose palette, recognisable harbour scale, warm windows, moving boat, active promenade, real native-pixel edges.
- Concrete weaknesses: clouds are still broad stepped geometric wedges; repeated rectilinear facades/window matrices create prefab feeling; water has too many small equal-value shimmer strokes; the foreground railing/ground takes substantial picture space; subjects are tiny and their acting is difficult to read at phone scale. The opening/middle/closing contact sheet changes but the entire piece retains nearly the same shot composition.
- V5 must demonstrably fix each failure: **drawing changes, not extra procedural noise**, stronger atmosphere and visible narrative staging. Compare V4 and V5 at frames 0/45/90/135/180/225/270/315/359.

## Hard blocker (checked 24 October 2026)
At preproduction start, all three specialist branches and this integration branch compare IDENTICAL to V4 (0 commits ahead), and no V5 proof PRs exist. **Do not compose a pretend film from old V4 art or claim V5 rendered.** Wait for actual PRs, source files and verified moving proof artifacts *before final integration*.

## Handoffs / acceptance gates
| Agent | Must deliver in source | Actual proof to review |
| --- | --- | --- |
| #12 world illustrator | `WorldV5.tsx` / `V5WorldPlane` plus any original PNG plane sources in `public/v5/world/` | Native 12s MP4, 9+ frame captures, FFprobe, compare to V4 architecture |
| #13 atmosphere | `AtmosphereV5.tsx` / `V5AtmospherePlane` | Native 12s MP4; review clouds, wave flow, broken gold reflection; seek-order stability |
| #14 motion & story | `MotionV5.mjs` / `getV5Motion`, `StoryV5.tsx` / `V5StoryPlane` | Native 12s MP4, legible step/turn/cat/boat beats, no ground penetration |

Inspect exact PR heads and code before importing. Validate separately that no imported assets are non-original, links at render time, or moving objects duplicated between planes. Do not override agents' branches.

## Director's shot score (360 native frames)
- **0–89 / wonder:** harbour-wide sunset and open sky; visible distant bird and entering boat, unhurried establishing move. Negative space around sun (225,252).
- **90–239 / discovery:** shift attention toward living promenade and coast; figures approach and recognise each other; natural gestures and cat crossing; parallax feels like camera, not sheet sliding.
- **240–359 / connection:** characters settle, boat moves through aligned sea, cat reacts, gentle final warm reflection, hold a composed emotional final image without overlay/outro/abrupt audio cut.

Stage constants unless jointly updated: **360x640**, sun about **(225,252)**, horizon **y353**, water ends about **y535**, promenade lower **510–640**. Final **1080x1920 30fps** / 360 frames.

## V5 integration ownership
Final composition `src/scenes/v5/SunsetHarborV5Final.tsx` uses actual new V5 planes, deterministic `getV5Motion(frame)` and **only one camera transform per depth plane**. World: far / architecture / harbor / promenade / foreground. Atmosphere: sky / clouds / water / reflections / lighting / air. Story: birds / waterInteraction / boat / characters / cat / foregroundLife. Stage sorting to check against live source:

1. Atmosphere sky, drifting clouds; birds; world far; air/haze behind nearest facades
2. Atmosphere water, reflections; story waterInteraction; world architecture + harbour
3. Story moving boat (after water and before docks/foreground where appropriate)
4. Atmosphere selective practical lights (only where correctly occluded); world promenade
5. Story people + cat at compatible ground contact; world foreground; story foregroundLife

Actual z-order must be tested against the resulting artwork. Keep only one sky, one sun, one boat system, one animated bird set, one reflected wake, one lantern-light logic. Do not use V4 fallback for missing required art; failing visibly is better.

## Audio (source provenance)
Preserve `assets/v3-chill-part01.b64`, the **short original user-supplied Day & Night excerpt** (~4 seconds); V4 joins it with ~420ms overlap crossfades to reach 12s. Do not imply the full original exists. Examine seam RMS and listen across transition points. For public distribution, owner must confirm soundtrack rights.

## Release acceptance / no false positives
- Agents #12/#13/#14 PR links, source commit SHAs, moving-proof run URLs, downloadable artifacts documented.
- Shared V5 scene imports source modules from V5, Root maps correct ID, no V4 imports used for replacement visual planes.
- `node scripts/render-v5-final.mjs` renders actual Remotion at 360x640, FFmpeg scales **neighbor** x3, H.264 yuv420p + AAC 48kHz, duration 12s, decoded frames 360.
- Entire final video decodes; no black gaps; strong frame differences but no flicker; no cropped silhouettes, floating feet, duplicate craft or duplicate character; soundtrack every full second.
- Nine real V5 PNG frames and 3x3 sheet; **V4 vs V5 paired** 9-frame sheet at identical timestamps; human watches full film, including audio, at native and phone size.
- Fix weak visuals, re-render and inspect *again* before setting approved=true. Artifact exists + CI green is not artistic signoff.
- PR into V4 only, not main. Delivery must include final MP4, PR URL, successful run URL, artifact link, comparison sheet, ffprobe JSON and remaining limitations.

## Current signoff
**REJECT / WAIT FOR DEPENDENCIES** — as of this audit, V5 assets and isolated proof renders have not been delivered. This document records verified V4 observations only; final aesthetic assessment remains pending.
