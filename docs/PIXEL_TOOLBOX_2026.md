# Pixel Videos — Free Pixel Toolbox (49 options, October 2026)

This is a **working selection, installation, agent-discovery and technical QA layer**, not an assertion that 49 apps have been installed or used. The list is in `studio/toolbox/catalog.json` (49 source links, roles, setup routes and local probes).

## One-minute start — AI agent

```bash
python3 scripts/pixel_toolbox.py list
python3 scripts/pixel_toolbox.py doctor
python3 scripts/pixel_toolbox.py recommend sprites --headless
python3 scripts/pixel_toolbox.py recommend motion --headless
python3 scripts/pixel_toolbox.py how pixelorama
bash scripts/setup_pixel_toolbox.sh --show
```

On Ubuntu / Debian if allowed to install packages:

```bash
bash scripts/setup_pixel_toolbox.sh --core
# optional large desktop applications:
bash scripts/setup_pixel_toolbox.sh --editors
# optional Node 2D tools (modifies package.json / npm lock):
bash scripts/setup_pixel_toolbox.sh --node
```

Core setup: FFmpeg, ImageMagick, GraphicsMagick, Gifsicle, pngquant, Tiled, Xvfb and libvips tools, plus an isolated Pillow/PyTMX/pytiled-parser Python environment under gitignored `.tools/venv`. A desktop/X server is still required for many GUI editors. The installer intentionally does not automatically clone, download, compile or execute 49 unrelated upstream projects. No third-party binaries are committed.

### Pick from the catalog (49 free or free-to-use choices)

| Stage | What is cataloged | Agent decision |
| --- | --- | --- |
| **Draw sprites (12)** | Pixelorama, LibreSprite, Besprited, Piskel, GrafX2, PixiEditor, Krita, GIMP, mtPaint, Pinta, Pixa.Pics, PixelCraft | **First** actually create/edit cels and layered original art; never relabel an algorithmically drawn flat rectangle as hand-painted |
| **Level tools (5)** | Tiled, LDtk, Ogmo Editor CE, PyTMX, pytiled-parser | Build reusable editable roads, roadside vegetation and object paths; use Tiled CLI where headless |
| **Motion/render (11)** | Godot 4, Blender, Pencil2D, OpenToonz, Synfig, LÖVE, Pyxel, PixiJS, @pixi/tilemap, pixi-viewport, Phaser | Choose ONE main scene engine. Prefer Godot/PixiJS for depth/parallax; do not mix all engines |
| **Lighting/materials (2)** | Laigter, Material Maker | Only after original pixel artwork looks great without effects |
| **Image/export (12)** | Pillow, Sharp, ImageMagick, GraphicsMagick, libvips, pngquant, Oxipng, Gifsicle, FFmpeg, FFprobe, Free Texture Packer CLI, APNG Assembler | Reproducible atlas exports, nearest-neighbour resizing, MP4 and PNG verification |
| **Audio (4)** | Audacity, LMMS, Bosca Ceoil, sfxr | Original sound/music; licensed independent assets only |
| **Palette and references (3)** | Lospec palettes, Kenney asset packs, OpenGameArt | Track individual palette and asset licenses; references are not unlicensed production assets |

**Existing:** Remotion is part of the root project. It is not counted as an unconditional zero-cost tool: check its usage-based licensing terms for the relevant production situation. PixiJS also already appears in the root package dependencies; cataloging it does not mean it was newly installed. Existing `scripts/install_tools.py` and all historic experiments remain untouched.

## Verified reproducible mini-pipeline (not claimed to be finished film art)

```bash
python3 -m pip install Pillow
python3 scripts/pixel_demo_assets.py --out out/toolbox-fixtures
python3 scripts/pixel_spritepack.py out/toolbox-fixtures/*.png --sheet out/atlas.png --data out/atlas.json --columns 2
python3 scripts/pixel_art_qa.py out/toolbox-fixtures/*.png --size 64x32 --max-colors 8
python3 -m unittest discover -s studio/toolbox/tests -v
```

The `pixel_demo_assets.py` output is **synthetic, tiny, non-production QA fixtures**, not proof of a premium car sprite. The GitHub Actions job generates four transparent sprite cels, a spritesheet+JSON, tests pixel-accurate integer resizing, actually encodes a small video, probes and fully decodes it, and uploads results. The test does not claim any GUI software drew the sprites.

## Agent rules (do not ignore)

1. **Artwork first:** Design a vehicle with a recognizable hatchback greenhouse, roofline, hood, wheels and fenders. Work natively at 1× with a deliberately controlled palette. A car must look like a car in a *still frame*, not just in motion.
2. **Select tools by task and runtime:** Run `doctor`, then `recommend <stage> --headless`. If an editor is missing or GUI-only, do not claim to have used it. Choose a supported CLI/Python alternative or provide an editable importable project for a person.
3. **Original source:** Commit cels and editable source files as well as the rendering code. Separate vehicle, road, horizon, foreground, dust and lighting layers. A flattened still is not enough.
4. **Native pixel rules:** No blur, fractional upscaling, anti-aliasing, resampling between art stages or heavy faux-pixel shader. Export at the chosen 1× resolution, then **only integer nearest-neighbour** upscale.
5. **Proof:** Save the tool commands actually run, native art/atlas, final MP4, FFprobe metadata, full-decode result and a contact sheet. Flag visual quality as **review pending** until a human inspects the actual render.
6. **Project safety:** Work on a fresh branch with a PR. Don't touch old V3 rally MP4, Godot test scenes, PRs #48–#50 or existing production branches. Don't merge to main without the owner's approval.

## Known CLI automation examples

- Pixelorama: supports `--export`, `--spritesheet`, `--output`, `--json` and `--split-layers`; call its bundled binary with the actual project file and verify version syntax first. Source: https://github.com/Orama-Interactive/Pixelorama
- LibreSprite: its Aseprite-derived batch CLI can export a spritesheet/data; verify against the actual installed release and use `--batch`. Source: https://github.com/LibreSprite/LibreSprite
- Tiled: `xvfb-run -a tiled --export-map source.tmx out/map.json` (Linux headless export needs Xvfb). Source: https://github.com/mapeditor/tiled
- Laigter: supports `--no-gui` profile-driven maps; add lighting only after the base sprite passes a visual review. Source: https://github.com/azagaya/laigter
- Oxipng: `oxipng -o 4 --strip safe sprite.png` after the art is finalized. Source: https://github.com/oxipng/oxipng
- Free Texture Packer CLI: `free-tex-packer-cli --project source.ftpp --output out/atlas` once configured. Source: https://github.com/odrick/free-tex-packer-cli
- FFmpeg: `ffmpeg -i native.png -vf 'scale=iw*4:ih*4:flags=neighbor' upscaled.png` (not a replacement for actually animating the car).

**Licensing:** Every option has a separate upstream license. Free software tools do not make imported sprites, soundtracks, fonts or model packs automatically free for publishing. Preserve source/creator/license information per asset. `Kenney` and `OpenGameArt` are **reference/asset services**, not installed CLI tools.

## Actual acceptance bar for the next car film

- First inspect a clean static native-resolution still; visible pixel clusters, great car silhouette, credible setting.
- Then inspect a 4-frame motion test with wheels, parallax, bounce and separate road movement.
- Only then render 5–15 seconds. Require the car to dominate the first frame, clear continuous travel, at least two readable camera compositions, and zero black gaps.
- Export native source files, precise atlas metadata and reproducible render commands. Compare the final contact sheet with the original native art before approving.
