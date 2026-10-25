# V5 — vehicle silhouette redesign: tram to sports coupe

**Date:** 25 October 2026  
**Repository:** YunRah2103/Pixel-videos  
**PR:** #45; remains draft. **Do not merge to production or main.**

## Why the old car was rejected

The previous “streamlined tram” used five repeated square windows, a flat passenger-transit side and a tall elongated body. It reads as a minibus or railcar, not an attractive sports car. Increasing wheel animation from 8 to 24 frames did not solve the flawed silhouette. The old module `scripts/v5_streamline_tram.py` is no longer used by the production renderer.

## Changes actually made

- New `scripts/v5_sports_car.py`: **164x66 native RGBA, two-door neo-retro GT coupe**, drawn from individually placed pixel polygons, highlights and rim clusters, **not** GUI sprite painting.
- Proportion redesign: wedge bonnet, low cockpit, shorter greenhouse with only **two glass sections**, rear deck/ducktail, deep lower sill and distinct front/rear wheel arches.
- Palette now coordinates cool turquoise car surfaces with neon-pink edge reflections and warm headlamps from the original city colour language.
- **24 independently rendered animated car cels**, all 24 distinct under SHA/image comparison in the exact rendered artifact. Wheel spokes and brake-valve markers rotate; subtly modified driver highlight animates.
- `scripts/render_neon_portrait.py` uses `save_car_cels` for the actual moving, puddle-reflected vehicle. The stage objects in the editable Tiled map retain their old names `tram-start`/`tram-finish` solely to preserve the validated positional contract. They no longer control a tram-like sprite.
- The GitHub workflow checks that all 24 `car-cel-*.png` exist, that at least twelve cels are distinguishable, and that the QA manifest explicitly states the new vehicle type. Previous camera/edit and environmental animation remain intact.

## Exact completed render

- Source commit: `f557682d19ad3d1ba908148e93370a806b82653e`
- **GitHub Actions success:** https://github.com/YunRah2103/Pixel-videos/actions/runs/40202788614
- **Playable film, contact sheet, stills, 24 car cels, original storyboard and manifest:** https://github.com/YunRah2103/Pixel-videos/actions/runs/40202788614/artifacts/12602780692
- Independently inspected actual **nine-shot contact sheet**: vehicle visibly reads as a compact sports coupe rather than an oversized tram. New roof line and wheel spacing look coherent in the wide frames and in the integer-2x middle close-up.
- Independently ran FFprobe: **H.264, 1080x1920, 30 FPS, exactly 150 decoded frames**; independently ran full FFmpeg decode with no errors.
- Source remains native 270x480, nearest-neighbour 4x, with integer cropped hero close-up. Movie stays exactly five seconds.

## Honest remaining limitations

The car is a significantly better *recognizable silhouette*, but its paint and wheelwork are still script-authored pixel clusters, **not hand-painted by a professional pixel artist in Pixelorama/LibreSprite or another GUI**. The drawn wheel fender arcs and reflections could still be polished by an artist. The animation/film's three-shot structure and busy original architecture are unchanged. This is a meaningful visual replacement, **not** a statement that premium indie-game quality has been conclusively achieved. Owner visual approval is still pending.

**Tools used:** source-authored Pillow, free Tiled CLI, FFmpeg/FFprobe, GitHub Actions. No paid software or fabricated GUI interaction.

**Merge status:** not merged. `main` stays unchanged.
