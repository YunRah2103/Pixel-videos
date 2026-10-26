# F82 Director's Cut — significant upgrade

A six-shot 10-second edit of the Austin Yellow F82: tight nose reveal, front hero, accelerating side tracker, wheel-level close-up, rear acceleration and a newly illustrated sunset overlook finale. Original stereo electronic score and subtle road texture are included. No sampled engine audio or third-party music.

## Reproduce
Install Python packages in requirements.txt, FFmpeg and DejaVu Sans fonts. Run `python3 score.py`, then `python3 render.py`. Run `python3 test_wheels.py` for wheel geometry invariants. `python3 render.py --stills` exports native keyframes. Native 360×640, nearest-neighbour 3× to 1080×1920.

## Changes
- Six compositions with much wider shot-size variation, including intentional close-up cropping.
- New original finale illustration: matching yellow F82, sunset reflections, rough asphalt, stonework, orange flowers and alpine overlook.
- More rapid road travel, acceleration, closer tracking camera and moving reflections limited to painted panels.
- Fewer horizontal parallax splits; no split through tree trunks.
- Fixed tyre and rim contours retained. Caliper colours excluded from rotating samples so they do not multiply around the wheel.
- Original 48 kHz stereo music composed in score.py and encoded as AAC.

## Provenance and limits
New finale created with the built-in image generation tool using the current car master as identity reference. Other car/environment assets are retained from the previous rebuilt production. All are AI-generated pixel-style artwork, not represented as human hand-drawn sprites. No third-party game art or music used.

The last 2.2 seconds are an illustrated parked hero with a short camera settle and subtle foliage highlights, not a fully articulated parked-car simulation. Driving remains 2D sprite animation. Reflected panorama features and small sprite sampling changes may remain. The soundtrack is an original synth cue with road texture, not a recorded BMW engine. Intentional close-ups crop the car. Previous productions preserved; no merge to main.
