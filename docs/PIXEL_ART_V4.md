# Pixel Studio V4 — Genuine Artist-First Pixel Art Pipeline

**Read this before creating another Pixel Videos film.** A passing MP4 render is not proof that the art looks good.
The earlier films failed artistically because they relied on generic rectangles, sparse composition, weak silhouettes, and static action. More code effects alone cannot fix this.

## Available software and actual install status

| Tool | Use | How to get it | Fully automated? |
|---|---|---|---|
| Sprite Fusion Pixel Snapper (MIT) | Fix messy grid/quantise palettes | npm run art:install:snapper (native Rust Cargo binary) | YES; CLI, verified through CI proof |
| Pixelorama (open source) | Hand-draw/edit original sprites and cel animations | npm run art:install:editors or existing scripts/install_studio_v2.py --pixelorama | Installer provided; GUI authoring needs an interactive editor |
| Krita (open source) | Detailed layered illustration and original backgrounds | npm run art:install:editors on Linux with apt/sudo | Installer provided; may require system access |
| Godot and LDtk (free) | Parallax animation and original scene/level layouts | npm run art:install:editors | Installers provided, real use needs editor project evidence |
| PixelLab MCP (remote service) | Produce native-style character props and tilesets as editable candidates | https://www.pixellab.ai/mcp; configure own secret token | NO download: remote HTTPS API; account/token/subscription needed; cannot pretend connected |
| Sprite Fusion (web version) | Arrange artist-produced tiles into detailed locations | https://www.spritefusion.com/ | NO local package for the free hosted edition; manually export maps |
| PixelOver (EULA) | Rig/bone/mesh pixel animation, lights | https://deakcor.itch.io/pixelover | NO automated paid download; free demo cannot export |
| Ansimuz Synth Cities (CC0 at itch) | Professional layered night-city art/reference | https://ansimuz.itch.io/cyberpunk-street-environment | On itch: click Download and accept free/name-your-price download; import with provenance script |

**Important licensing distinction:** the older Ansimuz Cyberpunk Street Environment listing on OpenGameArt is CC-BY 3.0 and requires attribution. The itch Synth Cities listing is CC0. Respect the precise archive's actual licence and notices. Do not mix these together. Do not import any music from a pack without verifying that track's licence separately.

## Agent quickstart — reproducible

From a branch that contains V4:

    npm install
    npm run art:install:snapper
    npm run art:verify

The proof runs the real native pixel snapper on an enlarged copy of one of our original palette sprites and produces a new native-resolution sprite (size may change slightly). It saves before/after PNGs and tool evidence to out/artist-v4 and runs a numeric pixel-grid audit at native scale 1. Enlarge the processed sprite separately with integer nearest-neighbour filtering for a video; never compare the before/after PNG dimensions as if the snapper only changed colours. This is **installation/technical evidence**, not a beautiful scene.

For all existing open-source desktop tools on a supported Linux machine:

    npm run art:install:free

This attempts Pixel Snapper, Pixelorama, Godot, LDtk and Krita; it requires internet access, permissions and sufficient disk space. On unsupported systems follow official vendor links, never claim all installed.

Checking locally without installing anything:

    npm run art:check

For PixelLab use its real official MCP configuration, not a fabricated npm package:
- Endpoint: https://api.pixellab.ai/mcp
- Your own private token as an Authorization Bearer header.
- Use the generated setup instructions: https://www.pixellab.ai/mcp
- Never store tokens in commits, workflow YAML, issues or screenshots.
- If the agent cannot actually invoke PixelLab, say so and use Pixelorama/CC0 PNG artwork instead.

For PixelOver demo: download it from https://deakcor.itch.io/pixelover manually. The demo CAN preview/edit/save projects but CANNOT export animation. Paid licence is a separate owner decision.

For Sprite Fusion: open https://www.spritefusion.com/ and export a PNG/JSON/TMX map to studio/imports or another documented location. Do not claim a web URL is a command-line binary.

## Reuse an artist-made pack without silently rewriting its licence

First acquire an actual licensed ZIP from its official publisher. For a free CC0 Synth Cities itch download (follow its download UI, no scraper):

    python3 scripts/import-licensed-art.py --archive /path/to/cyberpunk-street-files.zip \
      --asset-id ansimuz-synth-cities --source-url https://ansimuz.itch.io/cyberpunk-street-environment \
      --author "Luis Zuno (Ansimuz)" --license CC0-1.0

This copies editable PNG/PSD/etc. plus notices into .tools/licensed-art/ansimuz-synth-cities, generates ASSET_PROVENANCE.json, excludes potentially differently licensed audio and never commits unverified files. It DOES NOT download the private archive for you.

## STRICT VISUAL APPROVAL GATE — mandatory for cinematic deliverables

**Gate A — original layered still, before motion:** each scene must feature designed architecture/vehicles/trees, distinctive silhouettes, coherent 16–40 colour scene palette, real pixel clusters, deliberate shadow shapes, usable negative space and a story focus. Create/edit original assets or demonstrate properly licensed artist-made sources. Reject simple rectangles, repeated clones, empty filler sky, image-pixelation filters and one flattened AI picture.

**Gate B — scene animation:** animate real separate assets: foreground, hero character/car, prop, atmosphere, background. Require at least two clear visual beats in 5 seconds; a fixed camera plus identical repeated rain particles isn't sufficient. Use a limited, consistent native pixel size, integer snapping, and nearest-neighbour scale. Make changes to what viewers see, not just numeric counters.

**Gate C — film quality:** native 360x640 (or explicitly documented low-res master), 30 fps, 5 seconds / 150 frames, 1080x1920 final through integer nearest-neighbour. Verify full FFmpeg decode, FFprobe metadata and multiple distinct contact-sheet frames. Provide a playable MP4 **and** an honest subjective review at phone size. Silence is okay but deliberate ambience is better if properly licensed.

**Gate D — real tool evidence:** log which applications were actually invoked, their real source files and how many outputs they produced. Installing Pixelorama is not the same as painting with Pixelorama. A website link is not proof that PixelLab API generated a sprite. Never claim PixelOver exported footage if only its demo is used.

Our automated tools prove that software ran, not that the result looks attractive. Artwork must be visually inspected and rejected if average.

## Hand-off for a specialist test agent

Copy docs/PIXEL_ART_V4_AGENT_TEST.md into a new ChatGPT agent. The agent should create a separate PR against production/countryside-drive, not touch current Countryside V3 or Sunset Harbor final branches and never merge to main without approval.


## Editor installation proof (V4.1)

The `pixel-v4-editors.yml` workflow downloads and installs the *real free editor binaries* on a Linux GitHub Actions runner. It uses the upstream release-specific filenames; Pixelorama publishes `Pixelorama-Linux-64bit.tar.gz`, Godot publishes `Godot_v..._linux.x86_64.zip`, and LDtk publishes `ubuntu-distribution.zip`. Krita is installed from the Ubuntu apt repository.

Commands:

    python3 scripts/setup_pixel_art_v4.py --free-editors
    python3 scripts/verify_open_source_editors.py

The verifier **runs Pixelorama and Godot headlessly**, calls Krita's version command, checks LDtk's executable, and writes `out/editor-toolchain/verification.json`. It does not claim an LDtk GUI render occurred and it does not certify an agent genuinely painted any sprites in the installed programs. Inspect the GitHub Actions job logs and verification artifact for actual evidence. Generated editor binaries are intentionally not uploaded, redistributed, or added to git: agents can reproduce the installation using the same commands.
