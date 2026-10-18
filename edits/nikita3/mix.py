"""Mix the reel audio: cleaned voice + timed sound effects (+ optional ducked music bed) -> build/mix.wav.

Voice is the hero: rumble cut, light denoise, gentle compression, loudness to -14 LUFS.
SFX are levelled by perceived loudness (EBU R128 momentary, so bass hits count properly) to peak about
SFX_OVER_LU above her typical speaking loudness, like the reference reels -- clearly heard, short, never long
enough to bury a sentence.
SFX come from the bundled HyperFrames library (Pixabay licence), placed from cues.json.
"""

import json
import pathlib
import re
import subprocess

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
BUILD = HERE / "build"
SFX_DIR = pathlib.Path.home() / ".claude/skills/media-use/audio/assets/sfx"
CUES = json.load(open(HERE / "cues.json"))
SR = 48000
SFX_OVER_LU = 1.0  # effect peaks sit ~1 LU above her typical speaking loudness, as in the reference reels
MUSIC = False  # off for now (user request); set True to lay assets/music.wav under the voice
MUSIC_DB = -10  # music bed ~ -30 LUFS, ~16 dB under the voice before ducking

VOICE_CHAIN = ("aformat=channel_layouts=mono,highpass=f=80,afftdn=nr=8:nf=-45,"
               "acompressor=threshold=-20dB:ratio=3:attack=5:release=90:makeup=2,"
               "loudnorm=I=-14:TP=-2:LRA=7,aresample=48000,aformat=channel_layouts=stereo")


def decode(path):
    pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(pcm, np.float32).reshape(-1, 2)


def write(path, a):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", str(path)],
                   input=np.ascontiguousarray(a, np.float32).tobytes(), check=True)


def window_db(a, win=0.1):
    """Short-window RMS levels in dBFS (used only for the report)."""
    mono = a.mean(axis=1)
    w = int(win * SR)
    n = len(mono) // w
    if n == 0:
        return np.array([20 * np.log10(np.sqrt((mono ** 2).mean()) + 1e-9)])
    rms = np.sqrt((mono[: n * w].reshape(n, w) ** 2).mean(axis=1))
    return 20 * np.log10(rms + 1e-9)


def momentary_lufs(a):
    """Loudest 400 ms momentary loudness (EBU R128, K-weighted) -- how loud it sounds, bass included."""
    pad = np.zeros((SR, 2), np.float32)
    log = subprocess.run(["ffmpeg", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", "-af", "ebur128",
                          "-f", "null", "-"], input=np.concatenate([a, pad]).astype(np.float32).tobytes(),
                         capture_output=True).stderr.decode()
    vals = [float(v) for v in re.findall(r"M:\s*(-?[\d.]+)", log)]
    return max(vals) if vals else -70.0


def main():
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(BUILD / "voice_raw.wav"), "-af", VOICE_CHAIN,
                    str(BUILD / "voice.wav")], check=True)
    voice = decode(BUILD / "voice.wav")
    log = subprocess.run(["ffmpeg", "-i", str(BUILD / "voice.wav"), "-af", "ebur128", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    m = np.array([float(v) for v in re.findall(r"M:\s*(-?[\d.]+)", log)])
    speaking_lufs = float(np.median(m[m > -30]))  # her typical momentary loudness while talking
    speaking_db = float(np.percentile(window_db(voice), 75))

    n = len(voice)
    bed = np.zeros((n, 2), np.float32)
    cache = {}
    for s in CUES["sfx"]:
        if s["name"] not in cache:
            src = HERE / s["file"] if "file" in s else SFX_DIR / f"{s['name']}.mp3"
            cache[s["name"]] = decode(src)
        snd = cache[s["name"]]
        if "from" in s:  # use a slice of a long effect (e.g. the riser's 3 s build)
            a, b = int(s["from"] * SR), int((s["from"] + s["dur"]) * SR)
            snd = snd[a:b].copy()
            fi, fo = int(0.15 * SR), int(0.08 * SR)
            snd[:fi] *= np.linspace(0, 1, fi)[:, None]
            snd[-fo:] *= np.linspace(1, 0, fo)[:, None]
        trim = s.get("lu", 0.0)  # per-cue offset in LU around SFX_OVER_LU
        g = 10 ** ((speaking_lufs + SFX_OVER_LU + trim - momentary_lufs(snd)) / 20)
        i = int(s["t"] * SR)
        j = min(n, i + len(snd))
        bed[i:j] += snd[: j - i] * g
    write(BUILD / "sfx.wav", bed)

    master = "alimiter=limit=0.78:attack=2:release=50:level=disabled,aresample=48000[out]"
    if MUSIC:
        graph = ("[0]asplit=2[v][k1];"
                 f"[1]aresample=48000,aformat=channel_layouts=stereo,volume={MUSIC_DB}dB,"
                 f"afade=t=in:d=0.6,afade=t=out:st={CUES['duration'] - 1.6:.2f}:d=1.6,atrim=0:{CUES['duration']:.3f}[m];"
                 "[m][k1]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=350:makeup=1[md];"
                 f"[v][md][2]amix=inputs=3:duration=first:normalize=0,{master}")
        inputs = ["-i", str(BUILD / "voice.wav"), "-i", str(HERE / "assets/music.wav"), "-i", str(BUILD / "sfx.wav")]
    else:
        graph = f"[0][1]amix=inputs=2:duration=first:normalize=0,{master}"
        inputs = ["-i", str(BUILD / "voice.wav"), "-i", str(BUILD / "sfx.wav")]
    subprocess.run([
        "ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", graph,
        "-map", "[out]", "-ar", "48000", "-c:a", "pcm_s16le", str(BUILD / "mix.wav")], check=True)

    # report: how far under her voice each effect actually lands in the bed
    for s in CUES["sfx"]:
        i = int(s["t"] * SR)
        seg = bed[i:i + int(0.6 * SR)]
        print(f"  {s['t']:7.2f}s {s['name']:<14} placed")
    stats = subprocess.run(["ffmpeg", "-i", str(BUILD / "mix.wav"), "-af", "ebur128=peak=true", "-f", "null", "-"],
                           capture_output=True, text=True).stderr
    summary = stats[stats.rfind("Summary:"):]
    print(BUILD / "mix.wav", " ".join(summary.split())[:200])


if __name__ == "__main__":
    main()
