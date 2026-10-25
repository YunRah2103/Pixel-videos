# Pixel Studio V5 — cinematic wet-road and trolley art pass

This is a continuation of PR #45, **not** a new disconnected toolkit. Keep the production branch and main untouched pending owner approval.

## Visual problem addressed

The earlier five-second film had excellent licensed storefront artwork but its trolley entered too late, the road reflections were mostly fixed glints, and there was little interaction between the moving hero and the rainy environment. This change **restages the trolley in the editable Tiled source**, so it is partially visible within the first second, crosses the foreground throughout the middle and clears the storefront reveal toward the ending.

## Real independent changes

- `studio/v5/neon-portrait.tmx`: trolley-start and trolley-finish stage coordinates. The CI scene layout is still exported by the actual free Tiled CLI.
- `scripts/v5_reflections.py`: samples each current transparent trolley sprite cel, mirrors and dims it into broken puddle rows without blur or prerendered images. Distinct rim highlights follow the source cel.
- Same module: actual moving trolley headlight tracks its location; wheel-contact spray responds to the wheel positions; the cyan shop-sign reflection is enabled only during the final timed reveal.
- `scripts/render_neon_portrait.py`: keeps separate licensed sky, architecture, shopfront, actor, and trolley sprites at **270×480 native pixel scale**; composites the wet-road animation at native scale before nearest-neighbour `×4` 1080×1920 export.
- Original umbrella character retains its independent walk/stop/reveal cels and follows Tiled-authored coordinates.

## How to reproduce without paid services

On Linux after checking out this branch:

```sh
sudo apt-get install ffmpeg python3-pil tiled xvfb
python3 scripts/setup_free_pixel_v5.py --art
mkdir -p out/pixel-v5-portrait
xvfb-run -a tiled --export-map studio/v5/neon-portrait.tmx out/pixel-v5-portrait/tiled-layout.json
/usr/bin/python3 scripts/render_neon_portrait.py
ffprobe -v error -select_streams v:0 -count_frames -show_entries stream=width,height,nb_read_frames,r_frame_rate -of json out/pixel-v5-portrait/pixel-v5-neon-portrait-5s.mp4
ffmpeg -v error -xerror -i out/pixel-v5-portrait/pixel-v5-neon-portrait-5s.mp4 -f null -
```

CI automatically performs these steps and publishes **the playable MP4**, hero still, starting still, nine-frame contact sheet, original trolley/character cels, editable Tiled map in Git, licences and QA metadata. It rejects missing Tiled objects, absent asset archives, malformed MP4 format, non-dynamic frames and full-decode errors.

## Licence and evidence boundaries

Architecture and original background layers: **Luis Zuno (Ansimuz), Cyberpunk Street Environment**, [OpenGameArt source](https://opengameart.org/content/cyberpunk-street-environment), **CC BY 3.0**. The original open-source license and output attribution remain mandatory.

Trolley and umbrella cels are original script-authored native pixel art, separately exported as editable PNGs; their reflections operate on these actual cels. **Tiled CLI, Pillow, FFmpeg and FFprobe** are used in the film. SpookyGhost, Laigter, Pixelorama, Krita and LibreSprite are free tools available through other studio setup workflows, but **were not used to hand-draw this film** and must not be claimed as such.

**Visual gate remains open:** the licensed buildings are strong, and native moving lighting improves rain-film coherence. The trolley is still pixel-drawn in Python rather than hand-refined in an editor; professional-indie-game equivalence is not proven by a passing render. User should inspect the actual five-second video at phone size. No merge into `main` without explicit approval.
