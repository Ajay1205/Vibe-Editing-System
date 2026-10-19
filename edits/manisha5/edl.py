"""Build the rough-cut edit list for the Manisha 5 reel (pep-talk English).

Cuts only inside measured silence, so no word is ever clipped:
  - pauses under MIN_GAP stay whole; longer ones shrink to KEEP_SHARE of their length (learner-friendly),
  - the user-requested removals (EXCLUDE) are dropped,
  - each clip is trimmed to its first and last speech.

Writes edl.json (segments in output order) and words.json (transcript words on the output timeline).
"""

import json
import pathlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[2]
FOOT = ROOT / "footage" / "manisha5"
OUT = pathlib.Path(__file__).resolve().parent

CLIPS = ["m51", "m52", "m53", "m54", "m55"]
FPS = 30
SILENCE_DB = -38
# Learner-friendly pacing (user note: viewers must have time to read): natural pauses under MIN_GAP are kept
# whole; longer ones are only shortened to 60% of their length, never below KEEP_MIN or above KEEP_MAX.
MIN_GAP = 0.45
KEEP_SHARE, KEEP_MIN, KEEP_MAX = 0.6, 0.42, 0.85
HEAD = 0.06
TAIL = 0.35
# Pauses right after each taught English line are cut short (user note: the pause after every translation felt
# awkward). Reading time comes from the card staying up into the next situation instead (cues.READ_HOLD).
# (clip, end of the English line)
HOLD_AFTER = []
HOLD_KEEP = 0.32

# Requested removals, in source seconds: (clip, start, end)
EXCLUDE = []


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
    # keep natural pauses, shorten only the long ones
    ranges = []
    for i, (st, en) in enumerate(speech):
        if not ranges:
            ranges.append([max(0.0, st - HEAD), en])
            continue
        gap = st - ranges[-1][1]
        if gap < MIN_GAP:
            ranges[-1][1] = en
            continue
        keep = min(KEEP_MAX, max(KEEP_MIN, KEEP_SHARE * gap))
        if any(c == clip and abs(ranges[-1][1] - t) < 0.15 for c, t in HOLD_AFTER):
            keep = min(gap, HOLD_KEEP)
        if gap - keep < 0.12:  # cutting out a sliver would only add a jump cut
            ranges[-1][1] = en
            continue
        ranges[-1][1] += 0.6 * keep
        ranges.append([st - 0.4 * keep, en])
    if ranges:
        ranges[-1][1] = min(dur, ranges[-1][1] + TAIL)
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
