# Pixel Studio V5 Neon Proof — complementary no-fee artistic test

Existing V5 tools and CI: docs/PIXEL_STUDIO_V5_FREE.md
This deliberately runs beside the original 9:16 Industrial V5 proof, not over it. Nothing here requires subscriptions, paid export or generation credits.

## Commands
On Linux x64:

    npm run v5:neon:install
    sudo apt-get install -y python3-pil ffmpeg
    /usr/bin/python3 scripts/render_pixel_studio_v5.py

## Quality demonstration
This is a **1920x1080, 5.000-second, 30fps**, native **320x180 nearest-neighbour ×6**, artist-source-based animation using separately editable licensed Ansimuz original pixel graphics:
- Cyberpunk Street Environment by Luis Zuno, OpenGameArt **CC BY 3.0**, attribution required: https://opengameart.org/content/cyberpunk-street-environment
- Warped City 2 by Luis Zuno, OpenGameArt **CC0**: https://opengameart.org/content/warped-city-2

Unlike procedural rectangles, this scene uses hand-illustrated environment PNG layers from an existing art pack and independently frame-animated human actor and neon-sign sprite cels; new motion, atmosphere and original audio are scripted with Pillow/FFmpeg. This is **licensed reused pixel art, NOT hand-drawn from scratch by Pixel Videos**. 16:9 protects the original artist's scene composition. The film is not a polished bespoke new-city asset library.

The installer additionally downloads for £0: official SpookyGhost Linux developer build (MIT), Laigter 1.13.1 Linux binary (GPL), LibreSprite v1.3 (GPL), Tiled v1.12.2 (GPL), Kenney Tiny City CC0, and Lospec palette. This test does not claim those desktop editors individually made the movie. They must be independently applied to real edited sprites in later productions and shown with actual source/export evidence.

## GitHub Actions
Run .github/workflows/pixel-v5-neon-proof.yml to install these sources, render and decode the MP4, inspect contact sheet and upload actual movie artifact. Art/attribution/provenance are included in the artifact; executables & third-party archives remain only on the ephemeral runner under gitignored .tools/v5-free.

The earlier reference video cannot be fully replicated by installing software. Human art direction and meaningful composition, sprite editing, visual inspection and asset quality gates remain essential.
