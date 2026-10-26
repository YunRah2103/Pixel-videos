# Agent instructions — Pixel-videos

This repository makes **original pixel-art films**. Read `docs/PIXEL_TOOLBOX_2026.md` and `docs/AGENT_GUIDE.md` before any creative work.

- The real failure mode is *unconvincing artwork*, not too few dependencies. A tool inventory, pixelating weak geometry, glows, fades or procedural rectangles do NOT count as improved vehicle or environment art.
- Run `python3 scripts/pixel_toolbox.py doctor` and `recommend sprites --headless` before choosing an editor. Clearly distinguish installed tools from catalogued links. If a GUI editor was not opened and used, NEVER say the car was drawn with it.
- Every creative deliverable needs original editable car/environment source layers, still-frame signoff, animation cels, robust render commands, visual contact sheet, license records and playable verified MP4. Never claim subjective art quality passes merely because CI passes.
- Preserve earlier rally-car source/MP4 and Godot experiments. PRs #48–#50 are independent experiments; do not modify them. Make feature branches. Do not merge into `main` without owner permission.
- For vehicles specifically: recognizable hood/roof/rear, hatchback body volume, front/rear overhang, consistent axles/rotating wheels, coherent 3/4 or side perspective. No overly flat pancake cars.
- For pixel art: clusters and contrast at 1× native resolution, controlled ramps, no interpolation/blur. Upscale final frames only by exact integer nearest-neighbour. Rain, dust, light and camera must enhance *already beautiful* static art.
- Use minimum necessary software for a shot: e.g. Pixelorama/LibreSprite + Tiled + Godot/PixiJS + FFmpeg. Don't install 49 tools for a single scene.
- Run `python3 -m unittest discover -s studio/toolbox/tests -v` (Pillow needed). Record actual tool versions and failed/unsupported commands.
