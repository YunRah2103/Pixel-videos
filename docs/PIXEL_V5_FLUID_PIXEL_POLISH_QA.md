# PIXEL VIDEOS V5 — FLUID PIXEL POLISH PASS

Date: 25 October 2026  
Working PR: [#45](https://github.com/YunRah2103/Pixel-videos/pull/45)  
Working branch: `feat/pixel-studio-v5-neon-portrait-art-pass`  
Base: `production/countryside-drive`. **No merge to base or `main`.**

## Delivered changes

- **Tram:** 8 -> **24 individually generated native RGBA cels**; a genuinely phase-moving wheel valve, stepped material clusters and added passenger shading. Frame-sampled at 30 FPS. Two-frequency 1-pixel suspension bounce and continuous easing avoid the original prolonged slow creep.
- **Pedestrian:** 4 -> **12 articulated walking poses** plus the existing reveal pose. Independently phased umbrella sway, foot placements, body bob and hem/coat colour clusters. Smoothstep travel from Tiled start to stop.
- **Water:** current moving actor sprite is reflected into irregularly discontinuous, persistent 7-pixel clusters and slowly drifting ripples; road is not blurred, flattened or passed through a smooth shader.
- **Environment:** original micro-life layer adds three staggered gutter drips, subtle steam from a street vent, occasional window glints, and short puddle rings. Intended to support the hero, not fill the whole frame with particles.
- **Camera:** retains the established three-shot structure (0–57 establishing, 58–104 integer-2x tracking shot, 105–149 wide neon payoff). No global camera blur or fractional resampling. Native 270x480 art is enlarged exactly 4x to 1080x1920.
- **Sources:** source modules `scripts/v5_streamline_tram.py`, `scripts/v5_pedestrian.py`, `scripts/v5_reflections.py`, new `scripts/v5_micro_life.py` and `scripts/render_neon_portrait.py`. Native `studio/v5/neon-portrait.tmx` remains editable; existing Ansimuz CC BY 3.0 credit retained.

## Real render and proof

- [SUCCESS run 40201845303](https://github.com/YunRah2103/Pixel-videos/actions/runs/40201845303)
- [Download exact updated artifact ZIP 12602520646](https://github.com/YunRah2103/Pixel-videos/actions/runs/40201845303/artifacts/12602520646)
- Content includes playable `pixel-v5-neon-portrait-5s.mp4`, `contact-sheet.png`, `hero-still.png`, `preview-still.png`, 24 tram PNGs, 12 walk PNGs and the reveal PNG, sky and sign cels, source TMX, exported Tiled JSON, provenance and QA JSON.
- FFprobe independently checked final H.264 1080x1920 / 30 FPS / 150 decoded frames. Full independent FFmpeg decode: PASS.
- Workflow checks that the 24 tram cels contain >=12 distinct images and 12 pedestrian walking cels contain >=8 unique images, alongside the Tiled export and pixel-native shot-direction assertions.
- Manual side-by-side contact-sheet inspection: the most visible change is in moving/tightly framed **middle section**, which is now better supported by character motion and a differently paced tram. The opening and final shot preserve approved composition.
- Comparing the decoded MP4s at ten-frame intervals shows movement-related differences, particularly around frames 60–90; pixel differences measure *change*, not artistic superiority.

## Honest tool and artistic QA

**Actually used in this pass:** source-authored Pillow RGBA native-pixel rendering, free Tiled CLI map export, FFmpeg and FFprobe, GitHub Actions. **Not claimed:** LibreSprite, Pixelorama, Krita, Laigter or SpookyGhost GUI manual illustration, or premium/paid cloud tools. The hero sprites are hand-specified in code and remain editable, **not hand-painted in a sprite GUI**.

**Improved:** more unique in-between poses, wheel detailing, independently moving canopy/body and small street details, less grid-regular reflections, no interpolation.

**Still needs work:** the tram and pedestrian silhouettes are still compact code-authored artwork and may not match the craft of a skilled pixel artist's individual sprite painting. The integer-2x cut into the middle is intentionally assertive and may feel sudden to some viewers. Steam/rain effects are deliberately restrained. Native pixel animation still moves in discrete one-pixel steps, which is authentic but cannot resemble vector-smoothed motion without abandoning the brief. Review actual MP4 at phone size before awarding artistic PASS; **technical PASS is not artistic approval**.

## Acceptance status

- 5-second 1080x1920 / 30 FPS / 150-frame moving MP4: **PASS**.
- PNG contact sheet, hero still, authentic source cels, credits and QA manifest: **PASS**.
- 3-shot story, nearest-neighbour native pixel constraint: **PASS**.
- Local/free-only pipeline and honest authoring credits: **PASS**.
- Handcrafted premium indie-game visual quality: **PENDING OWNER REVIEW**. Do not misrepresent a render or unique-pose assertion as proof of elite craftsmanship.
- Merge: **NOT PERFORMED**.
