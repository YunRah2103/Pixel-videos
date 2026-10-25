# V5 rainy-neon street: independent sprite-story upgrade

## What is new

The artist-made **Cyberpunk Street Environment** (Luis Zuno / Ansimuz, **CC BY 3.0**) is preserved unchanged, retaining its three individual transparent image planes. Pixel Videos now adds one original, independent, four-cel umbrella pedestrian (and one final reveal cel) and positions the character on a genuinely editable Tiled scene map.

- `studio/v5/neon-portrait.tmx`: editable native Tiled source with separate `pedestrian-start` and `pedestrian-stop` objects, the trolley route and the `open-sign` reveal object.
- `scripts/v5_pedestrian.py`: editable source of hand-specified native-pixel RGBA character sprites. Each walking frame changes the feet and bob; these are **not paid generative assets**, nor a flat animated backdrop.
- `scripts/render_neon_portrait.py`: composites licensed architecture and original sprites on independent layers, performs native-pixel lighting, and animates real 150-frame action.
- `.github/workflows/pixel-v5-neon-portrait.yml`: exports the Tiled map with its **actual command-line exporter**, renders all frames, executes a full FFmpeg decode, runs FFprobe and uploads the MP4, sprite cels, still, and contact sheet.

## Timeline and actual tool evidence

0.0–0.3s: Rainy neon storefront and traffic stage.  
0.3–2.8s: Original umbrella pedestrian walks in four visibly distinct cels, while a separate trolley crosses and wheels animate.  
2.8–3.7s: Person stops beneath the shop, tram continues; distinct street reflections follow both independent actors.  
3.7–5.0s: Tiled-authored **OPEN** sign activates and cyan light catches the umbrella.

**Used to produce the film**: original PNG licensed art, Python Pillow pixel composition, Tiled **CLI map export** on Linux, FFmpeg encoding/complete decode, FFprobe metadata validation. **Not used to draw this actor**: SpookyGhost, Laigter, LibreSprite GUI, Pixelorama, Krita, paid AI APIs.

### Local reproducibility

On Linux with free `tiled`, `xvfb-run`, FFmpeg/FFprobe, Pillow and the repository:

```sh
python3 scripts/setup_free_pixel_v5.py --art
mkdir -p out/pixel-v5-portrait
xvfb-run -a tiled --export-map studio/v5/neon-portrait.tmx out/pixel-v5-portrait/tiled-layout.json
/usr/bin/python3 scripts/render_neon_portrait.py
ffprobe -v error -select_streams v:0 -count_frames -show_entries stream=width,height,nb_read_frames,r_frame_rate -of json out/pixel-v5-portrait/pixel-v5-neon-portrait-5s.mp4
ffmpeg -v error -xerror -i out/pixel-v5-portrait/pixel-v5-neon-portrait-5s.mp4 -f null -
```

Result: `out/pixel-v5-portrait/pixel-v5-neon-portrait-5s.mp4` (5s, H.264, 1080×1920, 30fps, native 270×480 / exact integer ×4 upscale). The workflow packages the actual video and cels in its Actions artifact.

## Quality gate (important)

The licensed city architecture is detailed. The actor adds genuine separate storytelling beyond rain, trolley translation and light flickers. However, this remains a **short, source-licensed, script-authored sprite test**; it is **not evidence of GUI-authored sprite work**, nor automatic certification that the output matches the user's premium indie-game reference. Review the 9-frame contact sheet and watch the full MP4 at phone size before accepting this as final.

Do not merge into `main` without approval.

## Provenance

- Luis Zuno (Ansimuz), Cyberpunk Street Environment, CC BY 3.0: https://opengameart.org/content/cyberpunk-street-environment
- New four walking cels and one reveal cel, original Pixel Videos pixel drawing code in `scripts/v5_pedestrian.py`.
- Generated quiet audio original to the renderer (no external music).
