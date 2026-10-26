# BMW F82 cinematic rebuild

Run `python3 prepare.py`, then `python3 render.py`. Requires Python 3.10+, Pillow, FFmpeg and DejaVu Sans fonts. For static art review use `python3 render.py --stills`.

Files: `assets/car-original.png` and `environment-original.png` are the new image-generation masters. `front.png`, `side.png`, `rear.png` are editable transparent native sprites. `F82_Artwork.ora` contains independently editable car and environment layers. `wheels.json` defines editable wheel patch anchors. `render.py` owns the full deterministic 300-frame timeline.

Art direction: Austin Yellow F82, deep charcoal wheels, warm alpine sunset, dark teal foliage, deliberate pixel clusters. The new master artwork was generated with the built-in image-generation tool for this project; no external game sprites, footage or music were used. Preserve all masters when editing. See QA.md for achievements and limitations.

Shot timing: 0–2 front icon; 2–5 side acceleration; 5–8 low rear performance; 8–10 sunset arrival. Export is a silent H.264 MP4.
