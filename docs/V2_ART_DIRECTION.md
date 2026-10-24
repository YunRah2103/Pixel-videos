# Sunset Harbor V2 — cinematic art and soundtrack notes

- **Mood:** nostalgic jazz, last golden light on an imagined seaside town, gentle human connection.
- **Canvas:** 360×640 native pixel composition, 12 seconds / 360 exact frames at 30fps; FFmpeg nearest-neighbour ×3 upscale.
- **Authored artwork:** `src/scenes/sunsetHarborSvg.mjs` creates entirely original frame-specific SVG elements. No sprite library, screenshots, external photographs or pixelation filters.
- **Scene design:** teal-to-lavender-to-salmon twilight, layered stepped pixel clouds, distant hills, sunlit faceted water, varied seaside roof silhouettes, warm windows, balcony railing, lantern-lit promenade, flowering shrubs, fishing boats, a cat and two people.
- **Motion:** cloud and distant-boat drift, independent foreground foliage sways, water highlights and their gold reflection move frame-by-frame, tiny character idle animation and birds.
- **Jazz:** user-provided 12-second excerpt; a converted, lower-bitrate audio copy is stored as base64 solely to be reproducible in GitHub Actions. This is **user-provided music, not MIT-licensed project artwork**. Ensure you have distribution rights before publishing or sharing the video publicly.
- **Render:** `npm run render` from Remotion; output `out/sunset-harbor-1080p.mp4`; validates H.264 / 1080×1920 / 30fps / 360 video frames / 12s. For local SVG-based independent QA, `python scripts/render_local.py --music /path/to/recording.m4a` (requires CairoSVG/Pillow/Node/FFmpeg).