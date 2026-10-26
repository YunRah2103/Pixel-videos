# Pixel Garage: handcrafted 2D sprites with parallax depth

This experiment is **not full 3D** and does **not put a pixelation effect over low-poly geometry**. One consistent five-door rally hatchback crosses a gravel road in side view, with sky, mountains, far forest, near forest, track and grass moving at separate speeds.

Run from this folder after installing Godot 4.5+ and Python Pillow:

```bash
python3 -m pip install Pillow numpy
python3 build_art.py
python3 build_audio.py
godot --headless --path . --editor --import --quit
godot --headless --path . --write-movie godot_movie.avi --fixed-fps 30 --quit-after 450
ffmpeg -y -i godot_movie.avi -i original_audio.wav -vf "scale=1080:1920:flags=neighbor" -c:v libx264 -crf 18 -pix_fmt yuv420p -c:a aac -b:a 192k -shortest pixel-garage-godot.mp4
```

Or use the isolated workflow `.github/workflows/pixel-garage-godot-25d.yml` to build and retrieve a Godot-generated MP4 artifact.

All artwork in `build_art.py` is original, and each sprite is saved as a separately editable PNG. No previous Pixel Videos project is changed. This branch is experimental; **do not merge into main without approval**.

**Quality gate:** Open exported stills, verify the wheels stay in their arches and that car shape stays consistent, and listen to the produced video. PNG sprites should be crisp at native internal resolution (360×640). The original preview rendered offline is not to be mistaken for Godot output.
