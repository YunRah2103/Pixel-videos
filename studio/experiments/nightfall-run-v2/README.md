# Nightfall Run V2: artwork and real-motion upgrade

Render: `nightfall_run_v2_10s.mp4` (delivered to the owner in this ChatGPT conversation; local artifact; not in this commit).

Sources: [`pixel_garage_v2_editable_sources.zip`](pixel_garage_v2_editable_sources.zip) — unpack for 12 editable SVG masters, transparent native sprite PNGs, `src/build_v2_art.py`, `src/render_v2.py`, `src/pixel_lock.py`, `src/verify_v2.py`, and a thorough `V2_REPORT.md` with tool commands and honest limitations.

Changes from V1: redraw coral hatch, wheel rims and arch contours; deepen autumn and pine forest artwork and mid-distance village; richer road/guardrail. Decoupled parallax, coupled wheel rotation to road distance, accelerated road motion, full-car composition in BOTH shots (old close-up cropped vehicle). Preserve V1 project and MP4 in parent branch.

Technical QA: **PASS** 1080x1920 H.264 yuv420p, 30fps, 300 frames, 10.000s, full decode, 12 edited SVG+PNG layer pairs hard-alpha, motion in all 9/9 one-second road+background comparisons. Actual stills and before/after/contact sheets delivered with the video in conversation. See source ZIP for reproduce commands and detailed tests.

Tools actually executed: Inkscape; Pillow/NumPy; ImageMagick; FFmpeg/FFprobe; OpenCV. Pixelorama, LibreSprite, Tiled and Godot were **not** available in this container; do not claim they helped. No borrowed/copyrighted game sprites or music.

Artistic review: meaningfully richer still and readable moving scenery. Still stylised procedure-authored pixel work, **not yet Katana ZERO craft**. Human review requested, especially silhouette/trees. Do not merge without approval.