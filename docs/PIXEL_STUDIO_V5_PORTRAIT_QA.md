# Pixel Studio V5 — portrait film visual review and free-tool evidence

This branch is an **art-first correction**, not a claim that downloading editors automatically makes good artwork.

## Why this branch exists

The prior V5 landscape neon proof used a much richer Ansimuz pixel-art city than the existing green, repetitive V5 portrait movie. The new 5-second portrait film recomposes the **real licensed, independently separable PNG layers** to favour the original detailed coffee shop, restaurant signage, skyline, wet street and animated transit foreground.

**Source:** Cyberpunk Street Environment by Luis Zuno (Ansimuz), [OpenGameArt](https://opengameart.org/content/cyberpunk-street-environment), licensed **CC BY 3.0**. The upstream archive includes `public-license.txt`. Publish attribution with any redistribution. This is NOT the different itch.io "Synth Cities" release, and no other pack's licence is assumed.

## Reproduce with zero extra AI subscriptions

On Linux x86_64, with free `python3-pil`, `ffmpeg`, `ffprobe`, `tiled` and `xvfb` installed:

```bash
python3 scripts/setup_free_pixel_v5.py --art
mkdir -p out/pixel-v5-portrait
xvfb-run -a tiled --export-map studio/v5/neon-portrait.tmx out/pixel-v5-portrait/tiled-layout.json
python3 scripts/render_neon_portrait.py
```

Map objects in the Tiled-exported JSON control the tram route and neon-sign position; missing or invalid objects fail the render. This is genuine **Tiled CLI export and scene-data use**, not a claim that an artist dragged objects with the GUI. The map is an editable native `.tmx` source.

The Python source authors and exports four independently frame-addressed trolley sprite cels, while the three original city PNG planes are composited and pixel-snapped at different depths. Rain, moving headlights, pavement reflections, signage and original quiet synthetic ambience are separate. The 150 unique native frames are 270×480 and use nearest-neighbour x4 upscale for a 1080×1920 H.264 MP4. No AI API, paid software, credit or paid export.

The GitHub Actions workflow `pixel-v5-neon-portrait.yml` installs the free renderer, downloads the licensed original art, **actually exports through Tiled**, creates MP4/stills/source cels/contact-sheet/provenance and runs FFprobe and full FFmpeg decode. Download the output from the successful workflow run's artifact called `pixel-v5-neon-portrait-five-second-proof`.

## Actual usage versus availability

| Program or resource | Status in this film |
| --- | --- |
| Tiled | **Used via CLI** to export an authored `.tmx` map to JSON; the renderer reads its objects |
| Ansimuz Cyberpunk Street | **Used** as three independent licensed city layers, CC BY 3.0 |
| Pillow, FFmpeg, FFprobe | **Used** for original trolley cels, animation, native render, audiovisual encode and QA |
| SpookyGhost | Available through previous V5 installer; **not used for this film's animation** |
| LibreSprite | Available through previous V5 installer; **not used for this film's sprite editing** |
| Laigter | Available through previous V5 installer; **not used for lighting maps** |
| Kenney Tiny City | Downloadable CC0 kit; **not used in this composition** |
| Lospec | Palette catalogue usable for future work; **not used as a palette override** |
| Pixelorama, Krita, Godot, LDtk, Pixel Snapper, PixiJS, Sharp, Remotion | Preserved from earlier studio versions; **not claimed as used in this render** |

## Artistic review

The film has a coherent night palette and better real hand-made architecture than the old vertical test. The trolley is significantly larger and moves across the frame; the 3.7–5s neon sign/reflection payoff changes the image rather than only adding rain. The city layers and vehicle cels are real independent assets, not a flattened image passed off as full animation.

**Remaining limits:** The trolley is still authored programmatically rather than hand-pixelled in LibreSprite; city architecture uses licensed artwork rather than newly painted original buildings. Overall scene motion is deliberately restrained. A 5-second technical pass is **not** certification of premium indie-game art. Owner visual approval is required before this becomes an artistic release standard.

**Never merge `main` without approval.** This PR targets `production/countryside-drive` for review only.
