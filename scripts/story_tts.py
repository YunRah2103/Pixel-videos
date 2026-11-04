#!/usr/bin/env python3
"""Generate the narration for a story script with Gemini TTS (one request per segment).

  python3 scripts/story_tts.py stories/dream-car/script.json out/story/vo
Writes <id>.wav (24 kHz mono, leading/trailing silence trimmed) and timings.json with each
segment's duration and its internal pauses (used to time captions sentence by sentence).
Skips segments whose wav already exists, so re-runs never re-bill finished lines.
"""
import base64, json, os, re, subprocess, sys, time, urllib.request

MODEL = "gemini-2.5-flash-preview-tts"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent"


def tts(text, style, voice):
    body = {"contents": [{"parts": [{"text": f"{style}\n\n{text}"}]}],
            "generationConfig": {"responseModalities": ["AUDIO"],
                                 "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}}}}
    req = urllib.request.Request(URL, json.dumps(body).encode(), {"Content-Type": "application/json", "x-goog-api-key": "proxy-injected"})
    with urllib.request.urlopen(req, timeout=180) as r:
        d = json.load(r)
    return base64.b64decode(d["candidates"][0]["content"]["parts"][0]["inlineData"]["data"])


def run(*a):
    return subprocess.run(a, capture_output=True, text=True, check=True)


def pauses(wav):
    out = subprocess.run(["ffmpeg", "-v", "info", "-i", wav, "-af", "silencedetect=n=-38dB:d=0.28", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    st = [float(x) for x in re.findall(r"silence_start: ([0-9.]+)", out)]
    en = [float(x) for x in re.findall(r"silence_end: ([0-9.]+)", out)]
    return [[round(a, 3), round(b, 3)] for a, b in zip(st, en)]


def main(script, outdir):
    s = json.load(open(script))
    os.makedirs(outdir, exist_ok=True)
    timings = {}
    for seg in s["segments"]:
        wav = os.path.join(outdir, seg["id"] + ".wav")
        if not os.path.exists(wav):
            for attempt in (1, 2):
                try:
                    pcm = tts(seg["text"], s["style"], s["voice"]); break
                except Exception as e:
                    if attempt == 2:
                        raise
                    print("retry", seg["id"], e); time.sleep(5)
            raw = wav + ".pcm"; open(raw, "wb").write(pcm)
            trim = "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.05,areverse," \
                   "silenceremove=start_periods=1:start_threshold=-45dB:start_silence=0.15,areverse"
            run("ffmpeg", "-v", "error", "-y", "-f", "s16le", "-ar", "24000", "-ac", "1", "-i", raw, "-af", trim, wav)
            os.remove(raw)
        dur = float(run("ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", wav).stdout)
        timings[seg["id"]] = {"duration": round(dur, 3), "pauses": pauses(wav)}
        print(seg["id"], round(dur, 1), "s", len(timings[seg["id"]]["pauses"]), "pauses")
    json.dump(timings, open(os.path.join(outdir, "timings.json"), "w"), indent=1)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
