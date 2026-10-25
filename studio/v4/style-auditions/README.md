# Reproducible environment style auditions

Twelve additional animated choices, numbered 05–16 to follow the original four. Each lasts four seconds. All artwork is original native-pixel code artwork, rendered with Pillow and FFmpeg. These are visual auditions, not proof that the V4 PixiJS/Remotion or external editor workflows are implemented.

## Recreate

From the repository root with Python, Pillow and FFmpeg installed:

```bash
python3 -m pip install -r requirements-demo.txt
python3 scripts/render_style_variants.py
```

Produces `out/style-variants/Pixel_Styles_05_to_16.mp4` and native PNGs, plus a comparison sheet. Source recipes and palette metadata are in `recipes.json`; the renderer's `RECIPES` table is authoritative and exports that JSON on rebuild. Edit the Python table, not the exported JSON.

## What makes these practical for general agents

Every scene uses the same small modules: stepped cloud, two ridge planes, one modular tree species, one simple landmark, repeating fence and road, grass tufts and optional weather. Pure integer positions derive from the frame number. There are no external assets, paid services, GPU requirements or image-generation calls. Source artwork uses either 270×480 with exact 4× output or 135×240 with exact 8× output; the coarse variants use coarse drawing primitives before grid quantisation. Preserve the supplied shapes rather than replacing them with smooth illustrations.

**Recommended starting point: 06 Clean Arcade.** Clear silhouettes, outlines, restrained shading and a small modular scene give an agent fewer artistic decisions to get wrong. **07 Classic Grove** adds leaf detail through the same renderer. **10 Dusk Silhouettes** reduces the need for detailed internal shading. These are engineering judgments based on the implementation, not benchmarked claims about other agents.

| Number | Style | First second | Construction |
|---|---|---|---|
| 05 | Pocket Woodland | 0 | Coarse block canopy and four-colour scene artwork |
| 06 | Clean Arcade | 4 | Outline and coherent three-tone leaf masses |
| 07 | Classic Grove | 8 | Structured highlights and animated windmill |
| 08 | Autumn Birch | 12 | Slim pale trunks and golden tall crowns |
| 09 | Alpine Postcard | 16 | Tiered pines and angular peaks |
| 10 | Dusk Silhouettes | 20 | Simplified dark willow masses and sunset bands |
| 11 | Rainy Woodland | 24 | Cool grove, moving rain and road puddles |
| 12 | Coastal Summer | 28 | Segmented palms and moving water tiles |
| 13 | Snow Country | 32 | Capped pines and independently falling snow |
| 14 | Desert Evening | 36 | Jointed cacti and stepped mesa layers |
| 15 | Mosaic Meadow | 40 | Rectangular canopy clusters and soft palette |
| 16 | Ink & Paper | 44 | Limited inks, willow forms and ordered dithering |

All original source and pixel artwork use this repository's MIT licence. Pillow and FFmpeg remain separate tools with their own upstream licences. No music or third-party art is included.
