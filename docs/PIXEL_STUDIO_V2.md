# Pixel Videos — Studio V2 Toolkit

A reusable art-to-film production pipeline for this repository, added separately from the Sunset Harbor V5 film work.

## What's genuinely available

| Tool | How it's used | Status |
| --- | --- | --- |
| Remotion | Frame-perfect film editing and H.264 delivery | Existing |
| PixiJS v8 | Layer-only water/lantern effects and deterministic motes | Existing dependency, new src/toolkit/pixiFx.ts code |
| Sharp | Native pixel sprite creation, nearest-neighbour processing and compositing | Added npm dependency |
| Pixelorama | Export original .pxo spritesheets through CLI | Existing downloader, new CLI adapter |
| Godot | 2.5D Movie Maker PNG sequences via adapter | Existing downloader, new CLI adapter |
| Krita | Convert original .kra painting to transparent PNGs | New optional Linux apt installer + CLI adapter |
| LDtk | Author multi-layer towns and coastal levels | New optional Linux x64 official-release installer + .ldtk inspector |
| FFmpeg | Motion proof generation and integrity checks | Existing |

Editors are standalone native binaries. They are deliberately **not** committed to Git (large downloads, upstream licensing). npm setup makes the scripted asset-generation and animation helpers usable right away. For real art editors, install on the host or include the corresponding setup script in an agent's Action.

## Quick start in any agent branch that contains this commit

    npm install --no-audit --no-fund
    npm run tools:check
    npm run typecheck:toolkit
    npm run assets:build
    npm run assets:proof
    npm run assets:qa

Output:
- public/toolkit/sprites/*.png — crisp indexed-palette hand-authored sprites
- out/toolkit/assets-report.json — asset report
- out/toolkit/pixel-toolkit-proof-1080p.mp4 — moving 3-second test (not V5 final)
- out/toolkit/proof-still.png — toolchain preview
- out/toolkit/verification.json — validation and full MP4 decode

The demo is a **plumbing test**. It is not intended to prove world-class environmental art by itself. That requires original authored assets and evaluation of a real film.

## Optional external editors (run only for tools needed)

    python3 scripts/install_studio_v2.py --pixelorama
    python3 scripts/install_studio_v2.py --godot
    python3 scripts/install_studio_v2.py --ldtk
    python3 scripts/install_studio_v2.py --krita
    python3 scripts/install_studio_v2.py --all

Installers use upstream official GitHub releases or apt package managers. LDtk automatic install supports Linux x64; Krita uses apt on Linux. Other systems use official releases/downloads. Check output to confirm presence; no tool is claimed installed just because the downloader exists.

### Export the artwork, not placeholder rectangles

    python3 scripts/export-studio-art.py pixelorama studio/original/characters.pxo studio/imports/characters.png
    python3 scripts/export-studio-art.py krita studio/original/clouds.kra studio/imports/clouds.png
    python3 scripts/export-studio-art.py inspect-ldtk studio/original/seaside.ldtk
    python3 scripts/export-studio-art.py godot studio/godot/coast out/godot-scene.png --frames 90 --fps 30

For LDtk, export PNG layers in the editor, add them as imports to studio/pixel-assets.json and rebuild. The .ldtk inspector reads and displays level structure but **does not** claim to headlessly render LDtk. Godot Movie Maker exports PNG frame sequences to be edited in Remotion/FFmpeg; an actual Godot project must exist at the indicated location. Krita CLI export may require xvfb-run on headless Linux.

## Adding art directly to film

- Hand-authored ASCII/palette sprites can be added under studio/pixel-assets.json with 1 character per pixel. This is for editable original clusters, small sprites, and deterministic QA; don't replace thoughtful illustration with repeated procedural blocks.
- Real Pixelorama or Krita artwork goes into studio/imports/*.png (retain original .pxo/.kra outside generated folder as well). Add to the imports array with id, source filename and optional scale, then run npm run assets:build.
- In a Remotion composition, use staticFile('toolkit/sprites/lantern.png') or staticFile('toolkit/imports/characters.png') via <Img>. For PixiJS, use Assets.load() and Sprite.
- src/toolkit/camera.ts exports cinematicCamera, parallaxTransform, spriteFrame and waveSurface, all pure deterministic frame-index functions.
- src/toolkit/pixiFx.ts exports createPixelWaterFilter, createWarmWindowFilter and pixelMotes. Construct the filter **once**, attach to water/window layer only, then call setFrame(frame) from useCurrentFrame. Pixi filters are WebGL-only; do not claim WebGPU shader support. Avoid blur/shimmer on character silhouettes or whole scene.
- Prefer **authored PNG foreground / architecture / cloud planes** plus motion and small shader accents. This prevents the V4 trap of uniformly repeated SVG rectangles.

## Non-destructive V5 hand-off

Toolkit branch: feat/pixel-studio-v2-toolkit
Baseline: integration/sunset-harbor-v4-final

Agents 1–3 and V5 integrator have their **own already-created branches**. Their branches do not magically receive new commits. After the toolkit is checked and merged into baseline, each agent may merge/rebase baseline or cherry-pick the toolkit commit; coordinate with the integrator to avoid collisions. Only integrator changes shared Root and final film workflow. Toolkit itself must not alter V4/V5 story, cameras, soundtrack or other agent-owned files.

## QA and provenance

- Audio/music and externally sourced sprite licenses must be verified before publication. The toolkit generates only newly authored demo sprites; external editor downloads keep upstream licenses.
- Native 360x640 -> exact 3x nearest-neighbour output for authentic pixel art, H.264 yuv420p 1080x1920 30fps; no full-frame blur/upscale hallucination.
- Film QA remains obligatory: compare 9+ checkpoints with previous MP4, check contact sheets at phone size, validate black gaps/audio, and visually watch video; metadata alone does not prove cinematic quality.
- Studio V2 CI workflow checks generated assets, moving 90-frame proof, MP4 full decode and frame diversity. It does not replace full V5 film QA.

Upstream tools: https://pixelorama.org/user_manual/cli/ ; https://docs.krita.org/en/reference_manual/linux_command_line.html ; https://ldtk.io ; https://docs.godotengine.org/en/stable/tutorials/animation/creating_movies.html ; https://pixijs.com/8.x/guides/components/filters ; https://sharp.pixelplumbing.com/

### Baseline TypeScript warning

The V4 integration branch currently reports missing TypeScript declarations for several legacy V3/V4 .mjs imports under a full-project tsc --noEmit. The isolated toolkit quality gate uses tsconfig.toolkit.json so new toolkit modules are strictly checked without modifying another agent's existing source. The legacy declaration backlog is separate from this tooling PR.
