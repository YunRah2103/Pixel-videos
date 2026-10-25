"""Car-first, pixel-native three-shot edit for the V5 neon GT film.

A 135x240 native crop is enlarged 2x using ONLY nearest-neighbour;
the original 270x480 scene then gets its existing exact 4x film upscale.
No blended camera scales, digital blur or pseudo-motion.
"""
from PIL import Image

NATIVE_WIDTH = 270
NATIVE_HEIGHT = 480
CLOSE_START = 36  # 1.20 seconds at 30 FPS
CLOSE_END = 114   # 3.80 seconds at 30 FPS
CLOSE_CROP_TOP = 240
HERO_CENTRE_OFFSET_X = 82  # midpoint of genuine 164px sports coupe

SHOT_LIST = (
    {'start_frame': 0, 'end_frame_exclusive': CLOSE_START,
     'shot': 'car visible at first frame: low wide entrance, background subdued',
     'integer_camera_scale': 1},
    {'start_frame': CLOSE_START, 'end_frame_exclusive': CLOSE_END,
     'shot': 'extended 2x native-pixel coupe side tracking: wheels, paint and canopy',
     'integer_camera_scale': 2},
    {'start_frame': CLOSE_END, 'end_frame_exclusive': 150,
     'shot': 'whole-car neon storefront payoff with gradual braking and body highlights',
     'integer_camera_scale': 1},
)

def apply_cinematic_camera(scene, frame, car_x):
    """Only integer-resolution framing of a fully moving, composited car scene."""
    if scene.size != (NATIVE_WIDTH, NATIVE_HEIGHT):
        raise ValueError('Expected original 270x480 native artwork')
    if not CLOSE_START <= frame < CLOSE_END:
        return scene
    crop_w, crop_h = NATIVE_WIDTH // 2, NATIVE_HEIGHT // 2
    left = max(0, min(NATIVE_WIDTH-crop_w,
                      round(car_x + HERO_CENTRE_OFFSET_X - crop_w / 2)))
    return scene.crop((left, CLOSE_CROP_TOP, left+crop_w,
                       CLOSE_CROP_TOP+crop_h)).resize(
        (NATIVE_WIDTH, NATIVE_HEIGHT), Image.Resampling.NEAREST)
