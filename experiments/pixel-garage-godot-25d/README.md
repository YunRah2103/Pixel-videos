# Pixel Garage — Godot 2.5D Rally (isolated experiment)

**Status:** isolated experimental implementation, unapproved. Never edit an earlier Pixel Garage production.

This is a **true spatial 2.5D** scene: illustrated, seeded, reproducible PNG sprites are mounted on `Sprite3D` world planes; a `Camera3D` moves through a curving mesh road with fixed roadside vegetation at real positions. The video is captured by **Godot Movie Writer**, not by a Python perspective imitation.

- Internal resolution: 360×640; nearest-neighbour upscale to 1080×1920
- Goal: 450 frames, 30fps, 15 seconds with original synthesized stereo WAV audio and AAC mux
- Dedicated experiment folder: `experiments/pixel-garage-godot-25d/`
- All art comes from an editable original illustration generator; the `.png` sprite outputs can also be edited in Pixelorama or Krita. No existing artwork copied.

## Build

Prerequisites: Godot 4.4.1+ standard edition, Python 3 + Pillow, FFmpeg/ffprobe, Linux Xvfb/OpenGL compatibility renderer.

```sh
cd experiments/pixel-garage-godot-25d
python3 art/make_assets.py
python3 tools/make_audio.py
GODOT_BIN=/path/to/Godot_v4.4.1-stable_linux.x86_64 bash tools/render.sh
```

Godot project is in `godot/`; script `Main.gd` contains road spline, deterministic car/camera timeline, true physical parallax, angle-specific car sprites, and spark-flame timing. Assets are generated in `godot/assets/` so the project is editable and self-contained after a build.

## Creative QA / factual copy

Unburned fuel may ignite in hot exhaust gases when there is enough oxygen; rally anti-lag can add conditions for exhaust combustion, but **not every flame is caused by anti-lag**. Stylised illustration is not a mechanical simulation.

Do not publish until you have visually reviewed at least 1s, 4s, 8s, 11s, 14s, checked the actual MP4, and confirmed that the car silhouette is beautiful enough. The runner fails if frames, geometry, fps, duration, sound, or file size are missing. Passing technical QA alone does not certify art quality.

## Architecture limits

Vehicle appearance uses discrete authored sprite perspectives selected at shot cuts, not continuously rotatable 3D geometry. Cars therefore should not spin freely mid-shot. The camera translates with *real depth*; all motion reads one `z_car` and one road spline. No motion blur, no pixelation shader, no procedural low-poly car.

No previous project, output, or renderer is changed. Never merge without approval.