import importlib.util, pathlib, unittest

SRC = pathlib.Path(__file__).resolve().parents[1] / "scripts/render_neon_offline.py"
spec = importlib.util.spec_from_file_location("neon", SRC)
r = importlib.util.module_from_spec(spec); spec.loader.exec_module(r)


class Neon(unittest.TestCase):
    def test_scenes_differ_and_size(self):
        a, b, c = r.frame(1.0), r.frame(3.5), r.frame(6.5)
        self.assertEqual(a.size, (720, 720))
        self.assertEqual(len({a.tobytes(), b.tobytes(), c.tobytes()}), 3)

    def test_deterministic(self):
        self.assertEqual(r.frame(4.2).tobytes(), r.frame(4.2).tobytes())


if __name__ == "__main__":
    unittest.main()
