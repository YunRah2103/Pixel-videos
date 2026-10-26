# BMW F82 cinematic rebuild — QA

## Achieved
- New Austin Yellow car artwork: front three-quarter, side profile and rear three-quarter; no previous BMW sprite reused.
- Recognisable F82 coupe silhouette, kidney grilles, carbon roof, side vents, wheel arches, rear diffuser and four exhaust tips.
- Newly illustrated alpine sunset panorama with detailed trees, valley, stone barrier, textured asphalt and foreground foliage.
- 360×640 logical canvas; exact 3× nearest-neighbour upscale.
- Four timed moments: front introduction, 71%-width tracking drive, lower rear performance view, sunset arrival and settle. Three proper illustrated angles; no skewing a flat sprite for perspective.
- Road travel accelerates, wheel rotation derives from travel divided by rim radius, pixel-snapped suspension motion, independent landscape/road/foreground scrolling.
- Only opening title and final question. No explanatory HUDs.
- Extracted opening, middle, consecutive driving frames and ending from the actual MP4. Full decode checked for errors.

## Technical verification
H.264; 1080×1920; 30/1 fps; 10.000 seconds; exactly 300 decoded video frames. FFmpeg full-file decode completed without errors.

## Honest limits
- Silent: no music or verified engine recording was added.
- Car and scenery masters are AI-generated pixel-style artwork, then prepared as editable PNG sprites; they are not claimed to be hand-drawn by a human. OpenRaster layers and original masters are supplied.
- This remains 2D sprite animation. The performance sequence suggests acceleration and rear-wheel-drive character, rather than mechanically simulating or explaining the twin-turbo engine.
- Parallax layers are derived from one panorama; repeated/mirrored landscape features and some horizontal layer joins may remain visible. Wheel rotation uses masked rim patches and can show small sampling changes.
- The ending uses the front sprite again with different scenery and arrival motion. There are three unique car angles, not four independently painted vehicles.
- The new environment is substantially richer and the shot structure more varied than the rejected video. Artistic quality remains a viewer judgement; no claim of a professional-quality score is made.

## References inspected
197987.mp4 and 197981.mp4 were both accessible and frames inspected. Repository main at 091049c7630efabbea20fbcae91302c83ba3713a was inspected. Original productions were preserved. Work is isolated under experiments/f82-cinematic-rebuild and experiment/f82-cinematic-rebuild; main was not merged.

## Wheel correction
Replaced rectangular crop rotation with wheel-plane spoke sampling. Tyre silhouettes, outer rims and surrounding body pixels remain stationary relative to the sprite. Corrected hub coordinates and used one physical rolling radius per car rather than perspective ellipse width. Regression checks pass for zero-angle identity, unchanged alpha and unchanged pixels outside wheel interiors. Five consecutive decoded rear-shot frames were inspected. Corrected MP4 verified as 300 frames, 10.000 seconds, 1080×1920, 30 fps, H.264; full decode passed.
