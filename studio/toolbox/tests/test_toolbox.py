"""Repeatable tests of toolbox catalog, pixel integrity and atlas metadata."""
import sys
import tempfile
import unittest
import json
from pathlib import Path
from PIL import Image

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/"scripts"))
from pixel_toolbox import catalog
from pixel_art_qa import inspect
from pixel_spritepack import pack
from pixel_demo_assets import make

class PixelToolboxTest(unittest.TestCase):
    def test_catalog(self):
        rows=catalog()
        self.assertGreaterEqual(len(rows), 40)
        self.assertTrue(all(r.get("source","").startswith("https://") for r in rows))
        self.assertGreaterEqual(len({r["stage"] for r in rows}), 6)
    def test_atlas_and_nearest(self):
        with tempfile.TemporaryDirectory() as td:
            d=Path(td)
            files=make(d/"sprites")
            self.assertEqual(len(files),4)
            atlas=d/"atlas.png"; metadata=d/"atlas.json"
            self.assertEqual(pack(files,atlas,metadata,columns=2),4)
            data=json.loads(metadata.read_text())
            self.assertEqual(set(data["frames"]),{p.name for p in files})
            self.assertEqual(tuple(Image.open(atlas).size),(128,64))
            image=Image.open(files[0]).convert("RGBA")
            scaled=d/"scaled.png"
            image.resize((256,128),Image.Resampling.NEAREST).save(scaled)
            self.assertTrue(inspect(scaled,source=files[0],scale=4)["ok"])
            self.assertFalse(inspect(scaled,source=files[0],scale=3)["ok"])
            self.assertFalse(inspect(files[0],max_colors=2)["ok"])
    def test_reject_mismatched_frames(self):
        with tempfile.TemporaryDirectory() as td:
            d=Path(td)
            a=d/"a.png"; b=d/"b.png"
            Image.new("RGBA",(8,8)).save(a)
            Image.new("RGBA",(9,8)).save(b)
            with self.assertRaises(ValueError):
                pack([a,b],d/"out.png",d/"atlas.json")
if __name__=="__main__":
    unittest.main()
