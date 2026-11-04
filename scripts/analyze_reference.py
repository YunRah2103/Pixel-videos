#!/usr/bin/env python3
"""Turn a reference clip into a recreation spec: size/fps, scene cuts, motion, palette, contact sheet.

  python3 scripts/analyze_reference.py REF.mp4 OUT_DIR
Writes OUT_DIR/spec.json and OUT_DIR/sheet.png (one frame from the middle of each scene).
Statistics only: use the spec to build ORIGINAL scenes, never to trace the reference's art.
Needs ffmpeg, ffprobe, Pillow, NumPy.
"""
import json, re, subprocess, sys
from pathlib import Path
import numpy as np
from PIL import Image

SAMPLE_FPS = 10


def run(cmd, **kw):
    return subprocess.run(cmd, capture_output=True, check=True, **kw)


def probe(path):
    d = json.loads(run(["ffprobe", "-v", "error", "-show_entries", "format=duration:stream=codec_type,width,height,r_frame_rate",
                        "-of", "json", path], text=True).stdout)
    v = next(s for s in d["streams"] if s["codec_type"] == "video")
    n, m = v["r_frame_rate"].split("/")
    return float(d["format"]["duration"]), int(v["width"]), int(v["height"]), float(n) / float(m), any(s["codec_type"] == "audio" for s in d["streams"])


def cuts(path, thr=0.2):
    r = subprocess.run(["ffmpeg", "-v", "info", "-i", path, "-vf", f"select='gt(scene,{thr})',showinfo", "-f", "null", "-"],
                       capture_output=True, text=True)
    return [round(float(x), 2) for x in re.findall(r"pts_time:([0-9.]+)", r.stderr)]


def frames(path, w=180, h=180):
    raw = run(["ffmpeg", "-v", "error", "-i", path, "-vf", f"fps={SAMPLE_FPS},scale={w}:{h}:flags=neighbor",
               "-f", "rawvideo", "-pix_fmt", "rgb24", "-"]).stdout
    n = len(raw) // (w * h * 3)
    return np.frombuffer(raw, np.uint8)[: n * w * h * 3].reshape(n, h, w, 3).astype(np.float32)


def main(src, out):
    out = Path(out); out.mkdir(parents=True, exist_ok=True)
    dur, W, H, fps, audio = probe(src)
    cut = cuts(src)
    arr = frames(src)
    motion = np.abs(np.diff(arr, axis=0)).mean(axis=(1, 2, 3)) / 255
    bounds = [0.0, *cut, dur]
    scenes = []
    for i in range(len(bounds) - 1):
        a, b = bounds[i], bounds[i + 1]
        seg = arr[int(a * SAMPLE_FPS): max(int(b * SAMPLE_FPS), int(a * SAMPLE_FPS) + 1)]
        q = Image.fromarray(seg.astype(np.uint8).reshape(-1, seg.shape[2], 3)).quantize(8, method=Image.Quantize.MEDIANCUT)
        pal = q.getpalette()[:24]
        scenes.append({"start_s": a, "end_s": round(b, 2),
                       "mean_brightness": round(float(seg.mean()), 1),
                       "palette_8": ["#%02x%02x%02x" % tuple(pal[j:j + 3]) for j in range(0, 24, 3)]})
        mid = (a + b) / 2
        run(["ffmpeg", "-v", "error", "-y", "-ss", f"{mid:.2f}", "-i", src, "-frames:v", "1", str(out / f"scene{i + 1}.png")])
    sheet = [Image.open(out / f"scene{i + 1}.png").resize((360, int(360 * H / W))) for i in range(len(scenes))]
    s = Image.new("RGB", (360 * len(sheet), sheet[0].height))
    for i, im in enumerate(sheet):
        s.paste(im, (360 * i, 0))
    s.save(out / "sheet.png")
    spec = {"duration_s": round(dur, 2), "size": [W, H], "fps": round(fps, 2), "has_audio": audio,
            "cuts_s": cut, "scenes": scenes,
            "motion_per_second": [round(float(motion[k * SAMPLE_FPS:(k + 1) * SAMPLE_FPS].mean()), 4)
                                  for k in range(int(dur)) if len(motion[k * SAMPLE_FPS:(k + 1) * SAMPLE_FPS])]}
    (out / "spec.json").write_text(json.dumps(spec, indent=2))
    print(json.dumps({k: spec[k] for k in ("duration_s", "size", "fps", "cuts_s")}))


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2])
