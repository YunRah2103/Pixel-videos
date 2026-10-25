# V5 sky courier art-and-motion pass

**State:** visual enhancement in draft PR #45. Do not merge into `main` or `production/countryside-drive` without owner approval.

## Why this pass

The previous 5-second portrait proof had authentic artist-made architecture and independent street motion, but little upper-sky activity. A first candidate resembled a miniature second tram, so it was rejected after inspecting an actual rendered nine-frame contact sheet.

The revised original sprite is a peach/pink **clockwork delivery blimp** with a segmented canopy, suspended gondola, 8-step revolving rotor, trim and lighting. It is deliberately distinct from the lower-street teal streamlined tram. It is hand-specified pixel artwork in `scripts/v5_sky_courier.py`, not an imported or AI-generated vehicle.

## Source separation and animation

- `scripts/v5_sky_courier.py`: eight independent 66x34 RGBA sprite cels, deterministically generated and saved as `courier-cel-{0..7}.png` for refinement.
- `studio/v5/neon-portrait.tmx`: `sky-courier` object layer with `courier-start` and `courier-finish` placement; exported using the actual free Tiled CLI in GitHub Actions.
- `scripts/render_neon_portrait.py`: composites the blimp after **far** licensed architecture but before nearer buildings, so it is naturally occluded and not pasted over shopfronts. The ship travels from the right side into the mid-foreground of the distant skyline during the middle of the film, with a small native-pixel rotor animation and restrained short trail.
- Original Ansimuz Cyberpunk Street Environment art remains unchanged. Preserve the CC BY 3.0 credit included in `ATTRIBUTION.txt` and `render-qa.json`.

## Evidence / limits

Re-run `.github/workflows/pixel-v5-neon-portrait.yml`. The result must include 8 new original sky sprite cels, eight trolley cels, 5 umbrella pedestrian cels, the editable TMX, exported Tiled JSON, a hero still, nine-frame contact sheet, MP4 and QA. The CI asserts exactly 150 frames, 1080x1920, 30 FPS and performs full FFmpeg decode.

**Actually used:** script-authored independent pixel artwork in Pillow; Tiled CLI map export, FFmpeg, FFprobe. **Not claimed as artwork-authoring tools:** Laigter, LibreSprite, SpookyGhost GUI. No additional paid AI services, credits or subscriptions.

## Artistic judgement

The revised upper-sky subject introduces a distinguishable colour and silhouette, with independent motion between the tram arrival and storefront reveal. The film remains a short technical-and-artistic proof, not a certification that a premium commercial game reference has been matched. Visual approval must be based on the **real output frames**, not successful CI alone.
