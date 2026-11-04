import importlib.util, pathlib, unittest
import numpy as np

SRC = pathlib.Path(__file__).resolve().parents[1] / "scripts/ramen_hero.py"
spec = importlib.util.spec_from_file_location("ramen_hero", SRC)
r = importlib.util.module_from_spec(spec); spec.loader.exec_module(r)


class RamenHero(unittest.TestCase):
    def test_one_fixed_palette_and_grid(self):
        self.assertLessEqual(len(r.PAL), 32)
        for t in (0, 2, 6, 8.1):
            idx = r.frame_indices(t)
            self.assertEqual(idx.shape, (180, 180))
            self.assertLess(int(idx.max()), len(r.PAL))
            a = np.asarray(r.frame(t))
            self.assertTrue((a[::4, ::4] == a[3::4, 3::4]).all())

    def test_car_is_hero_in_first_second(self):
        a, b = r.frame_indices(0.0), r.frame_indices(0.5)
        car = np.isin(a, [27, 28])                       # car body colours
        self.assertGreater(car.sum(), 400)               # big, clearly visible
        self.assertGreater((a != b).mean(), .05)         # and moving

    def test_continuous_shot_no_hard_cut(self):
        diffs = [(r.frame_indices(i / 30) != r.frame_indices((i + 1) / 30)).mean() for i in range(0, 245, 5)]
        self.assertLess(max(diffs), .5)


if __name__ == "__main__":
    unittest.main()
