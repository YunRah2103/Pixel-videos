import importlib.util, pathlib, unittest

SRC = pathlib.Path(__file__).resolve().parents[1] / "scripts/render_neon_detail.py"
spec = importlib.util.spec_from_file_location("neon_detail", SRC)
r = importlib.util.module_from_spec(spec); spec.loader.exec_module(r)


class NeonDetail(unittest.TestCase):
    def test_limited_palette_and_size(self):
        f = r.frame(3.5)
        self.assertEqual(f.size, (720, 720))
        self.assertLessEqual(len(f.getcolors(1 << 20)), r.PAL_SIZE)

    def test_chunky_pixel_grid(self):
        a = r.frame(1.0).load()
        step = 720 // r.NATIVE
        self.assertEqual({a[x, y] for x in range(10 * step, 11 * step) for y in range(10 * step, 11 * step)}.__len__(), 1)

    def test_deterministic_and_animated(self):
        self.assertEqual(r.frame(6.0).tobytes(), r.frame(6.0).tobytes())
        self.assertNotEqual(r.frame(6.0).tobytes(), r.frame(6.2).tobytes())


if __name__ == "__main__":
    unittest.main()
