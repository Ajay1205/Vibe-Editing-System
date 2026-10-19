"""Build the rough-cut edit list for the Nikita 3 reel (Actually / Instead / Finally).

Cuts only inside measured silence, so no word is ever clipped:
  - silence longer than MIN_GAP is shrunk to KEEP_BEFORE + KEEP_AFTER around the speech,
  - the user-requested removals (EXCLUDE) are dropped,
  - each clip is trimmed to its first and last speech.

Writes edl.json (segments in output order) and words.json (transcript words on the output timeline).
"""

import json
import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[2]
FOOT = ROOT / "footage" / "nikita5"
OUT = pathlib.Path(__file__).resolve().parent

CLIPS = ["n51", "n52", "n53", "n54", "n55", "n56"]
FPS = 30
SILENCE_DB = -38
MIN_GAP = 0.30      # shorter pauses are left alone
KEEP_BEFORE = 0.10  # kept after the last word before a pause
KEEP_AFTER = 0.08   # kept before the next word
HEAD = 0.06
TAIL = 0.18

# Requested removals, in source seconds: (clip, start, end)
EXCLUDE = [
    ("n51", 0.0, 0.42),     # room tone before "Add these three English words"
    ("n52", 24.10, 99),     # silence and a sideways glance after the Probably tip
    ("n53", 23.85, 99),     # silence after the Almost tip
    ("n54", 0.0, 1.70),     # silence before "Teesra word hai"
]


def duration(clip):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                          str(FOOT / "audio" / f"{clip}.wav")], capture_output=True, text=True, check=True)
    return float(out.stdout)


def silences(clip):
    log = subprocess.run(["ffmpeg", "-i", str(FOOT / "audio" / f"{clip}.wav"), "-af",
                          f"silencedetect=n={SILENCE_DB}dB:d=0.12", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    starts = [float(v) for v in re.findall(r"silence_start: ([\d.]+)", log)]
    ends = [float(v) for v in re.findall(r"silence_end: ([\d.]+)", log)]
    return list(zip(starts, ends + [duration(clip)] * (len(starts) - len(ends))))


def subtract(ranges, a, b):
    out = []
    for s, e in ranges:
        if s < a:
            out.append([s, min(e, a)])
        if e > b:
            out.append([max(s, b), e])
    return [r for r in out if r[1] - r[0] > 0.06]


def keep_ranges(clip):
    dur = duration(clip)
    sil = silences(clip)
    # speech spans = complement of silences
    speech, t = [], 0.0
    for s, e in sil:
        if s > t:
            speech.append([t, s])
        t = max(t, e)
    if t < dur:
        speech.append([t, dur])
    speech = [r for r in speech if r[1] - r[0] > 0.06]  # drop clicks
    if speech and speech[0][1] - speech[0][0] < 0.25 and speech[0][0] < 0.3:
        speech = speech[1:]  # mic handling noise before the first word
    for c, a, b in EXCLUDE:
        if c == clip:
            speech = subtract(speech, a, b)
    # pad and merge
    ranges = []
    for i, (s, e) in enumerate(speech):
        s = s - (HEAD if i == 0 else KEEP_AFTER)
        e = e + (TAIL if i == len(speech) - 1 else KEEP_BEFORE)
        s, e = max(0.0, s), min(dur, e)
        if ranges and s - ranges[-1][1] < MIN_GAP - KEEP_BEFORE - KEEP_AFTER:
            ranges[-1][1] = e
        else:
            ranges.append([s, e])
    for c, a, b in EXCLUDE:  # padding must never reach back into an excluded span
        if c == clip:
            ranges = subtract(ranges, a, b)
    return [(round(s, 3), round(e, 3)) for s, e in ranges if e - s > 0.05]


def main():
    segments, words_out, t, frame = [], [], 0.0, 0
    for clip in CLIPS:
        words = json.load(open(FOOT / "transcripts" / f"{clip}.words.json"))["words"]
        for s, e in keep_ranges(clip):
            n = round((e - s) * FPS)  # whole frames, so picture and sound stay in sync
            e = round(s + n / FPS, 4)
            t = frame / FPS
            segments.append({"clip": clip, "in": s, "out": e, "start": round(t, 4), "frames": n})
            frame += n
            for w in words:
                mid = (w["start"] + w["end"]) / 2
                if s <= mid < e:
                    words_out.append({"clip": clip, "text": w["text"],
                                      "start": round(t + max(w["start"], s) - s, 3),
                                      "end": round(t + min(w["end"], e) - s, 3)})
    t = frame / FPS
    json.dump({"fps": FPS, "frames": frame, "duration": round(t, 4), "segments": segments}, open(OUT / "edl.json", "w"), indent=1)
    json.dump(words_out, open(OUT / "words.json", "w"), ensure_ascii=False, indent=1)
    raw = sum(duration(c) for c in CLIPS)
    print(f"{len(segments)} segments, {raw:.1f}s raw -> {t:.1f}s cut")


if __name__ == "__main__":
    main()
