"""Directed three-beat shot framing for the V5 neon-street film.

Source art and independent sprites are composed first at 270x480, THEN a
strict integer 2x native-pixel crop makes the centre shot. This is an editorial
camera cut, not an AI-generated still, Gaussian blur or fake pixel detail.
"""
from PIL import Image

NATIVE_WIDTH = 270
NATIVE_HEIGHT = 480
CLOSE_START = 58           # establish real environment, then inspect the hero
CLOSE_END = 105            # return for the animated neon storefront reveal
CLOSE_CROP_TOP = 230       # storefront, pedestrian, tram, wheels and wet road
HERO_CENTRE_OFFSET_X = 82 # centre of genuine independent tram sprite

SHOT_LIST = (
    {'start_frame': 0, 'end_frame_exclusive': CLOSE_START,
     'shot': 'wide establishing scene', 'integer_camera_scale': 1},
    {'start_frame': CLOSE_START, 'end_frame_exclusive': CLOSE_END,
     'shot': '2x pixel-native hero vehicle tracking close-up', 'integer_camera_scale': 2},
    {'start_frame': CLOSE_END, 'end_frame_exclusive': 150,
     'shot': 'wide neon activation and puddle-reflection payoff', 'integer_camera_scale': 1},
)

def apply_cinematic_camera(scene, frame, tram_x):
    """Apply only pixel-exact native camera edits to a fully composited frame."""
    if scene.size != (NATIVE_WIDTH, NATIVE_HEIGHT):
        raise ValueError('Expected original 270x480 native artwork')
    if not CLOSE_START <= frame < CLOSE_END:
        return scene
    crop_w, crop_h = NATIVE_WIDTH // 2, NATIVE_HEIGHT // 2
    left = max(0, min(NATIVE_WIDTH-crop_w, round(tram_x+HERO_CENTRE_OFFSET_X-crop_w/2)))
    return scene.crop((left, CLOSE_CROP_TOP, left+crop_w, CLOSE_CROP_TOP+crop_h)).resize(
        (NATIVE_WIDTH,NATIVE_HEIGHT), Image.Resampling.NEAREST)
