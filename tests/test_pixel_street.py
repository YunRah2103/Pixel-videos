import importlib.util, pathlib, unittest
import numpy as np

SRC = pathlib.Path(__file__).resolve().parents[1] / "scripts/pixel_street.py"
spec = importlib.util.spec_from_file_location("pixel_street", SRC)
r = importlib.util.module_from_spec(spec); spec.loader.exec_module(r)


class PixelStreet(unittest.TestCase):
    def test_palette_only_and_hard_3x3_pixels(self):
        for t in (1.2, 3.9, 6.6):
            idx, pal = r.frame_indices(t)
            self.assertLess(int(idx.max()), len(pal))
            a = np.asarray(r.frame(t))
            self.assertTrue((a[::3, ::3] == a[2::3, 2::3]).all())

    def test_life_moves_between_frames(self):
        for t in (1.0, 4.0, 7.0):
            changed = (r.frame_indices(t)[0] != r.frame_indices(t + .2)[0]).mean()
            self.assertGreater(changed, .01)

    def test_deterministic(self):
        self.assertTrue((r.frame_indices(5.0)[0] == r.frame_indices(5.0)[0]).all())


if __name__ == "__main__":
    unittest.main()
