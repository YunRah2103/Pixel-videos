import importlib.util, pathlib, unittest
import numpy as np

SRC = pathlib.Path(__file__).resolve().parents[1] / "scripts/pixel_neon.py"
spec = importlib.util.spec_from_file_location("pixel_neon", SRC)
r = importlib.util.module_from_spec(spec); spec.loader.exec_module(r)


class PixelNeon(unittest.TestCase):
    def test_every_pixel_is_a_palette_colour(self):
        for t in (1.0, 3.5, 6.5):
            idx, pal = r.frame_indices(t)
            rgb = np.asarray(r.frame(t)).reshape(-1, 3)
            self.assertTrue(set(map(tuple, np.unique(rgb, axis=0))) <= set(map(tuple, pal)))

    def test_hard_4x4_pixels(self):
        a = np.asarray(r.frame(2.0))
        self.assertTrue((a[::4, ::4] == a[3::4, 3::4]).all())

    def test_animated_and_deterministic(self):
        self.assertTrue((np.asarray(r.frame(6.0)) == np.asarray(r.frame(6.0))).all())
        self.assertFalse((np.asarray(r.frame(6.0)) == np.asarray(r.frame(6.1))).all())


if __name__ == "__main__":
    unittest.main()
