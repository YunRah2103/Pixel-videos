import importlib.util, os, pathlib, unittest
import numpy as np

ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = ROOT / "scripts/dream_car_story.py"
spec = importlib.util.spec_from_file_location("story", SRC)
r = importlib.util.module_from_spec(spec); spec.loader.exec_module(r)
HAS_VO = (ROOT / "out/story/vo/timings.json").exists()


class Story(unittest.TestCase):
    def test_palette_and_font(self):
        self.assertLessEqual(len(r.PAL), 64)
        for ch in "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.,'?!-: ":
            self.assertIn(ch, r.F)

    def test_captions_fit_two_lines(self):
        import json
        for seg in json.load(open(r.SCRIPT))["segments"]:
            for chunk in r.caption_chunks(seg["text"], 10.0, []):
                lines = r.wrap(chunk[2])
                self.assertLessEqual(len(lines), 2)
                self.assertTrue(all(r.text_width(l) <= r.W - 8 for l in lines))

    @unittest.skipUnless(HAS_VO, "narration not generated")
    def test_frames_on_grid_every_scene(self):
        tl, total = r.build_timeline()
        self.assertGreater(total, 180)
        for seg in tl:
            a = r.frame_indices(seg["start"] + seg["dur"] / 2)
            self.assertEqual(a.shape, (r.H, r.W))
            self.assertLess(int(a.max()), len(r.PAL))


if __name__ == "__main__":
    unittest.main()
