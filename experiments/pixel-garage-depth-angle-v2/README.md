# Pixel Garage V2 — Angled 2.5D pixel-art test

The **previous side-scroller is not used**. This is an isolated eight-second proof-of-concept built from newly authored 2D rear-three-quarter car images, separate pine/bush/rock sprites and textured gravel in a real Godot perspective scene.

The engine provides physical Z-depth and a moving Camera3D. All objects visible as vehicles/foliage are drawn as **2D pixel sprites** (Sprite3D). The plane provides accurate road perspective, but **no vehicle 3D mesh, low-poly prop meshes or pixelation filters** are used. Car wheel frames and exhaust flames derive from the same world-travel timeline as the camera.

Rendered at 360x640 internal resolution, integer nearest-neighbour upscale to 1080x1920. The short test prioritises coherent perspective, road foreshortening and passing forest depth instead of captions, voiceover and flourishes.

To render: install Python Pillow and NumPy, Godot 4.5.2, FFmpeg, and on Linux Xvfb. Run `python3 build_art.py`, `python3 build_audio.py`, `godot --headless --path . --editor --import --quit`, followed by `xvfb-run -a godot --rendering-method gl_compatibility --path . --write-movie original_godot.avi --resolution 360x640 --fixed-fps 30 --quit-after 240`. Encode AVI and original sound WAV to MP4 with FFmpeg using nearest-neighbour 3x scale.

Run CI workflow **Pixel Garage — Angled 2.5D true perspective test** and inspect actual frames before approval. **Never merge without approval.** Earlier experiments remain untouched.
