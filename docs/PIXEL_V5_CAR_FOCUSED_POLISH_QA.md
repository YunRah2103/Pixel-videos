# V5 car-focused neon GT polish pass — verification contract

Branch: `feat/v5-car-focused-hero-polish`, built from the exact latest V5 neon-portrait head. The existing portrait film and free-tool source workflow are preserved. **No merge to production or main.**

## Visual direction

The sports coupe must win the eye over the city. Native composition stays **270x480** with **nearest-neighbour x4 output, 1080x1920, 30 fps, 150 frames, exactly five seconds**. No AI stills, Gaussian bloom, interpolated sprite pixels or paid art tools.

| Frames | Time | Story | Pixel camera |
| --- | --- | --- | --- |
| 0–35 | 0.0–1.2 s | Moving coupe visible already at frame zero; low wide entrance | 1x |
| 36–113 | 1.2–3.8 s | Continuous follow-crop through alloys, roof and full paint shoulder | Cropped 135x240, pixel-perfect integer 2x |
| 114–149 | 3.8–5.0 s | Complete coupe remains visible in front of cyan OPEN shop light, slow finish and stronger body reflections | 1x |

Storyboard car travel changes from **Tiled** x=-25 to x=97, retaining the original checked Tiled object names for workflow compatibility. The final x=97 still fits the full **164px** wide car within a 270px screen; the shop sign at x=221 is over its front half. Camera is genuinely applied to each animated original frame, never to a frozen hero photograph.

## Concrete car sprite changes

- More legible black tyres, deep-dish alloy lips, split 5-spoke animated rims and readable centre caps.
- A more defined sill and front splitter, low-profile roof edge and several broken enamel highlights.
- Extra author-specified reflection clusters inserted in the **actual editable OpenRaster -> Krita CLI -> LibreSprite sprite atlas** chain, subject to CI verification.
- The last 36 frames add narrow cyan/pink highlights to the *moving actual car cel*, before its matching puddle reflection.

## Distraction control

- 14 dim glints rather than 115, and 14 subdued streaks of rain rather than 55.
- Background is dimmed before the opaque, bright car is composited; do **not** dim or blur the final car.
- The courier and pedestrian are limited to the short entrance; micro-life is confined to the first 18 frames.
- Original architecture, properly licensed Ansimuz art, source cels and native Tiled map remain available.

## Mandatory checks / honesty

1. GitHub Actions run must compile the actual scripts; export the editable Tiled .tmx through Tiled; verify real Krita and LibreSprite CLI exports; generate 24 car cels from the LibreSprite atlas; run the full render.
2. The film must fully decode through FFmpeg; FFprobe must report H.264, **1080x1920, 30/1, 150 frames**.
3. Open and inspect the **actual MP4**, nine-panel contact sheet, close-up `hero-still.png` and final `final-car-hero-still.png`. Confirm wheel proportions, no clipped hero in final, no interpolation and genuinely visible neon car emphasis.
4. CI passing confirms technical operation, **not** artistic approval. Do not claim actual GUI brush painting or that Laigter, SpookyGhost, Pixelorama or other unrelated tools authored this video.
5. Preserve attribution for **Luis Zuno / Ansimuz Cyberpunk Street (CC BY 3.0)**.

**Owner acceptance test:** the viewer notices the GT coupe, moving alloys and neon body reflections first; if the city steals the eye, this cut fails. Pending viewing and acceptance; **do not merge**.
