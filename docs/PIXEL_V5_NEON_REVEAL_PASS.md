# V5 neon reveal — six independently editable sprite frames

This pass upgrades the **story payoff** in the existing 5-second neon-street film. It does not replace the licensed architecture or pretend that a single attractive still is a complete animated movie.

- `scripts/v5_neon_activation.py` specifies the word **OPEN** with explicit five-by-seven pixel glyphs and creates six actual RGBA sprite cels. The letters illuminate one after the other and briefly flicker before settling.
- The position is taken from `open-sign` in the editable Tiled `studio/v5/neon-portrait.tmx` map exported by the Tiled CLI, not a random after-effects overlay.
- Localized native-pixel light below the fixture and broken street reflections correspond to the switch-on. A first local test placed a cyan bar across original storefront artwork; it was rejected and the architectural overlay shortened to the actual sign fixture instead.
- All six transparent source cels are saved as `open-sign-cel-*.png` and exported by the GitHub Actions ZIP along with the MP4, trolley/umbrella/skyship cels, Tiled map, provenance, contact sheet, stills and FFprobe/FFmpeg QA.
- **Actually used:** Pillow for 2D authoring/compositing, Tiled CLI for object route/fixture export, FFmpeg/FFprobe for verification. No paid AI dependencies, and no untrue claim that LibreSprite / SpookyGhost / Laigter GUI tools authored frames.

These assets and animations can be edited individually. The artistic result still needs owner approval on a phone-sized playback before the PR leaves draft status or merges into the production branch. Source Cyberpunk Street artist remains Luis Zuno (Ansimuz), licensed **CC BY 3.0**, with attribution.
