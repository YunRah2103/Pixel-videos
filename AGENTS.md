# Pixel Videos — AGENTS.md (persistent agent art contract)

## Project goal
Make genuinely excellent, coherent, authored 2D pixel-art movies.
A technically valid MP4, green CI or successful git PR does not qualify as beautiful artwork.

## Before ANY new shot
1. Read docs/PIXEL_ART_V4.md and docs/PIXEL_STUDIO_V3.md.
2. Check tool availability with npm run art:check. For the native Pixel Snapper use npm run art:install:snapper and npm run art:verify. Never claim tool usage without actual invocation evidence.
3. Use real original edited sprite layers or licensed external artist assets with source/provenance; no placeholder trees, rectangular cars, generic programmer cityscapes or flattened image-with-moving-camera substitute.
4. Produce a richly detailed 360x640 native-pixel STILL, audit palette and layout, then look at it at 1080x1920 nearest-neighbour on a phone-size preview. Reject an unconvincing still and redo artwork BEFORE animating.
5. Only after art approval: animate independently authored objects with meaningful changes over time. 5s, 30fps, 150 frames. Native pixel camera coords are integer snapped; integer nearest-neighbour 1080x1920 output.
6. Inspect the actual complete MP4, nine keyframes, full FFmpeg decode, FFprobe, and give an HONEST artistic critique. Sound must have clear licence.
7. Do not overwrite another agent's branch, do not merge completed movies into main without owner instruction.

## Services versus executable installations
PixelLab is remote, requires user-authorised token/subscription: https://www.pixellab.ai/mcp
Sprite Fusion free is browser-hosted: https://www.spritefusion.com/
PixelOver demo has no export; paid copy requires owner licence: https://deakcor.itch.io/pixelover
Ansimuz official asset pack can be free/downloadable from itch UI and must be imported with provenance:
https://ansimuz.itch.io/cyberpunk-street-environment
Do not falsely present any website as a downloaded executable.

## Starter assignment
For a specialist first quality test, follow docs/PIXEL_ART_V4_AGENT_TEST.md in a separate branch and PR.

## V5 free-only rule

Read [docs/PIXEL_STUDIO_V5_FREE.md](docs/PIXEL_STUDIO_V5_FREE.md) before adding new pixel-art tooling. Do not require or suggest paid PixelLab API, PixelOver export purchase, proprietary image generators, paid asset packs or credits. Use real freely licensed artist sprites with accurate source/licence and test frame-by-frame. Never claim a GUI tool was used merely because its executable was installed.
