# Pixel Studio V5 — totally free pixel-art film workflow

**No additional paid software, AI APIs, commercial downloads, subscriptions or generation credits.** All 8 items are available at £0: SpookyGhost, Laigter, Tiled, LibreSprite, Kenney Tiny City, Ansimuz Cyberpunk Street, Ansimuz Warped City 2, and a Lospec palette.

## Install (Linux x86_64 or GitHub Actions runner)

    npm run v5:install:free
    npm run v5:check

Downloads are stored in gitignored .tools/v5-free/. Rerunning on an ephemeral agent downloads them again; GitHub source control contains the installer, not executable archives. Provenance and downloaded file inventory is written to out/studio-v5/free-tools.json.

The official versions/links are pinned in scripts/install_pixel_studio_v5.py. All source links and licence labels are there. SpookyGhost uses its own developers' GCC binary artifact repository, not a paid itch download. Laigter uses v1.13.1 Linux AppImage because the newer 1.14.0 GitHub release has no Linux binary.

## Actual five-second cinematic test

    sudo apt-get install -y python3-pil ffmpeg
    npm run v5:install:free
    /usr/bin/python3 scripts/render_pixel_studio_v5.py

Outputs under out/studio-v5-test:
- pixel-studio-v5-artist-led-5s.mp4 (1920x1080 H.264, 30fps, 150 frames, AAC original ambience)
- first-frame.png
- contact-sheet.png (9 native frames)
- render-qa.json and ATTRIBUTION.txt

**Actual art source**: three separately layered PNG images from Ansimuz Cyberpunk Street and a real multi-frame runner/idle character plus animated sign PNGs from Ansimuz Warped City 2. The film has independent layer parallax, an actor's real cels, rain, reflection shimmer, visual ending beat and self-synthesised ambient sound. Render is native 320x180, integer x6 nearest-neighbour upscale, NOT video pixelation filters.

**This is a 16:9 test to preserve the artist's native composition.** Don't force a horizontal environment into a vertical 9:16 composition if the scene ceases to look good.

The footage is created using Pillow/FFmpeg. **We are not claiming Tiled, LibreSprite, Laigter or SpookyGhost were used to AUTHOR this footage merely because the tools were downloaded.** A later specialist agent can use the tools to create new original editable sprites and supply tool export evidence.

## Clear licence credits

- Cyberpunk Street Environment by Luis Zuno (Ansimuz), from OpenGameArt, CC BY 3.0: https://opengameart.org/content/cyberpunk-street-environment . Credit required. Do not mistakenly call the OGA archive CC0 merely because the newer itch listing carries CC0.
- Warped City 2 by Luis Zuno (Ansimuz), from OpenGameArt, CC0: https://opengameart.org/content/warped-city-2 .
- Kenney Tiny City by Kenney, CC0: https://kenney.nl/assets/tiny-city . Downloaded and available for future asset creation; not forced into the mismatched side-on scene.
- Lospec ENDESGA-32 colour palette: https://lospec.com/palette-list/endesga-32 . Author credit and reuse restrictions need verification when exporting a derived palette file. Not a replacement for artistic palette judgment.
- Official SpookyGhost MIT, LibreSprite GPL-2, Tiled GPL-2+, Laigter GPL-3+ — app source licences belong to their publishers; downloading them does not relicense them into our repo.

The film is partly an adaptation of CC BY artwork, rather than a claim that the studio drew every pixel from scratch. That is intentional: our previous procedural-only attempts looked dreadful. This tests licensed professional sprite sources, visually first, with our own animation and direction.

## Limitations and gate

An animated image built with only subtle background scroll could still be boring. The moving character and animated signage are deliberately separate sprite cels, not a frozen still effect. A numeric QA pass is NOT a substitute for artist review. Inspect the actual MP4 on mobile and reject it if composition, pacing or original animation is below standard.

Do not merge this test branch into main. Agent-owned experimental branches remain separate from finished films.
