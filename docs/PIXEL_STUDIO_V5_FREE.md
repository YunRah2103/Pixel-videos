# Pixel Studio V5 — COMPLETE-FREE ART PRODUCTION

**No PixelLab, paid AI generation, PixelOver purchase, subscriptions, trials or credit limitations.** You may use ChatGPT/GPT agents with the following free native programs, authentic artist-made CC0 assets and existing repo video tools.

## Downloads available through one command (Linux x64)

    npm run art:v5:install
    npm run art:v5:check

The installer downloads into gitignored .tools/pixel-v5 rather than adding program binaries to Git. A fresh GitHub Actions runner needs to run the installer each time.

| Tool or pack | What it does | Installed how |
|---|---|---|
| LibreSprite | Edit real native pixel sprites/frames/layers, frame-by-frame animation | official v1.3 Linux x64 AppImage |
| Tiled | Build detailed layered 2D tilemaps and world layouts | official v1.12.2 Linux x64 AppImage |
| SpookyGhost | Animate layers and export real frame sequences | real upstream SpookyGhost-artifacts binary; SHA256 checked against vendor manifest |
| Laigter | Generate normal/specular/ambient occlusion maps for attractive sprite lighting | official v1.14.0 tagged source cloned; builds into native executable when Qt5 qmake and libs installed |
| Kenney Tiny City | 130 original CC0 pixel-art buildings and objects | official Kenney free ZIP downloaded, licence and provenance preserved |
| Luis Zuno / Ansimuz Industrial | Four actual individually hand-illustrated CC0 pixel-art backgrounds | exact 2015 original OpenGameArt ZIP with bundled CC0 licence |
| Lospec Greyt-bit | Original artist's freely listed pixel palette for colour consistency | download via the official Lospec free palette API; retain creator attribution |

Existing V4 free programs still available:

    npm run art:install:free

This installs Pixelorama, Krita, Godot, LDtk and Pixel Snapper. The old expensive services are not part of this system.

The installer supports Linux x64 automatically. Windows/macOS can use corresponding official software downloads without buying anything. It will never automatically acquire a paid asset.

## Actual genuine 5-second animation test

Run:

    npm run art:v5:assets
    npm run art:v5:film

Requires Python Pillow, NumPy and FFmpeg. Github Actions installs those for you, then renders a full 150-frame 5.000-second, 30fps H.264, 1080x1920 vertical MP4.

The film has **four separate human-made pixel source layers** from the bundled 2015 CC0 Ansimuz archive, EACH with its own deterministic pixel-snapped parallax speed. Extra motion consists of a separately authored frame-indexed transit sprite, illuminated shop lights, rain/petals and original synthesised audio. No image generation. Not a camera pan on a flattened image.

Outputs:
- out/pixel-v5/artist-led-city-5s-1080x1920.mp4
- out/pixel-v5/approved-artwork-candidate.png
- out/pixel-v5/contact-sheet.png (9 actual rendered movie frames)
- out/pixel-v5/render-qa.json (source art, 150 frames, FFprobe specs, full FFmpeg decode)
- out/pixel-v5/tool-readiness.json

All downloadable from the V5 GitHub Actions artifact when a test succeeds.

## Essential quality rule

The test establishes that the artist-first pipeline can use real authored art. It is NOT an artistic certification and is NOT proof that LibreSprite, Tiled, SpookyGhost or Laigter authored the art. The test reuses licensed existing art. The moving original sprite/FX are authored inside scripts. Agent-created commercial-quality work still needs actual sprite editing, visual review and real original layered source files.

For every future film: approve attractive still FIRST, then animate meaningful visible events, then visually inspect 9 frames and full MP4. Reject repeated uninteresting scenery and simplified geometric cars. No extra paid services.

## Source, licences and links

- LibreSprite: https://github.com/LibreSprite/LibreSprite (GPL-2.0)
- Tiled: https://github.com/mapeditor/tiled (open source)
- SpookyGhost: https://github.com/SpookyGhost2D/SpookyGhost (MIT). Official binaries: https://github.com/SpookyGhost2D/SpookyGhost-artifacts/tree/SpookyGhost-master-linux-gcc
- Laigter: https://github.com/azagaya/laigter (GPL-3.0)
- Kenney: https://kenney.nl/assets/tiny-city (CC0)
- Original Ansimuz pack: https://opengameart.org/content/industrial-parallax-background (CC0 on this specific OpenGameArt release). Not all other Ansimuz archives necessarily have the same licence.
- Lospec: https://lospec.com/palettes/api (respect palette author's use/credit conditions)
- Additional $0 CC0 Synth Cities: https://ansimuz.itch.io/cyberpunk-street-environment ; itch requires user to click free download UI. Do not bypass checkout or claim it was auto-installed.

Never sell or relicense upstream software, distribute unrelated artwork without verified permission, or invent use of art editors because they were merely installed.

## Additional free neon reference artwork (attribution required)

Ansimuz's original 2017 Cyberpunk Street Environment is freely downloadable from OpenGameArt under CC BY 3.0. Its source ZIP is downloaded automatically as ansimuz_cyberpunk by art:v5:install or art:v5:assets. Attribution is mandatory: Art by ansimuz.com — https://opengameart.org/content/cyberpunk-street-environment — CC BY 3.0 (https://creativecommons.org/licenses/by/3.0/). Edited for Pixel Videos if adapted. This pack is a separate, explicitly attributed asset from the 2015 CC0 industrial background.
