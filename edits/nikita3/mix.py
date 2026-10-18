"""Mix the reel audio: cleaned voice + timed sound effects (+ optional ducked music bed) -> build/mix.wav.

Voice is the hero: rumble cut, light denoise, gentle compression, loudness to -14 LUFS.
SFX are accents only: every effect is levelled so its loudest moment sits SFX_UNDER_DB below
Nikita's normal speaking level, then ducked further whenever she is talking over it.
SFX come from the bundled HyperFrames library (Pixabay licence), placed from cues.json.
"""

import json
import pathlib
import subprocess

import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
BUILD = HERE / "build"
SFX_DIR = pathlib.Path.home() / ".claude/skills/media-use/audio/assets/sfx"
CUES = json.load(open(HERE / "cues.json"))
SR = 48000
SFX_UNDER_DB = 1  # effect peaks sit ~1 dB under her typical level, i.e. below her loudest words (references: effects peak about level with the voice)
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
    """Short-window RMS levels in dBFS (100 ms windows catch the punch of short hits)."""
    mono = a.mean(axis=1)
    w = int(win * SR)
    n = len(mono) // w
    if n == 0:
        return np.array([20 * np.log10(np.sqrt((mono ** 2).mean()) + 1e-9)])
    rms = np.sqrt((mono[: n * w].reshape(n, w) ** 2).mean(axis=1))
    return 20 * np.log10(rms + 1e-9)


def main():
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(BUILD / "voice_raw.wav"), "-af", VOICE_CHAIN,
                    str(BUILD / "voice.wav")], check=True)
    voice = decode(BUILD / "voice.wav")
    levels = window_db(voice)
    speaking_db = float(np.percentile(levels[levels > levels.max() - 30], 75))  # her normal speaking level

    n = len(voice)
    bed = np.zeros((n, 2), np.float32)
    cache = {}
    for s in CUES["sfx"]:
        if s["name"] not in cache:
            snd = decode(SFX_DIR / f"{s['name']}.mp3")
            cache[s["name"]] = (snd, float(window_db(snd).max()))
        snd, peak_db = cache[s["name"]]
        trim_db = max(-2.0, min(0.0, 20 * np.log10(s["gain"] / 0.55)))  # per-cue emphasis, never above the cap
        g = 10 ** ((speaking_db - SFX_UNDER_DB + trim_db - peak_db) / 20)
        i = int(s["t"] * SR)
        j = min(n, i + len(snd))
        bed[i:j] += snd[: j - i] * g
    write(BUILD / "sfx.wav", bed)

    duck = "sidechaincompress=threshold=0.1:ratio=1.5:attack=10:release=150:makeup=1"
    master = "alimiter=limit=0.84:attack=3:release=50:level=disabled,aresample=48000[out]"
    if MUSIC:
        graph = ("[0]asplit=3[v][k1][k2];"
                 f"[1]aresample=48000,aformat=channel_layouts=stereo,volume={MUSIC_DB}dB,"
                 f"afade=t=in:d=0.6,afade=t=out:st={CUES['duration'] - 1.6:.2f}:d=1.6,atrim=0:{CUES['duration']:.3f}[m];"
                 "[m][k1]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=350:makeup=1[md];"
                 f"[2][k2]{duck}[sd];[v][md][sd]amix=inputs=3:duration=first:normalize=0,{master}")
        inputs = ["-i", str(BUILD / "voice.wav"), "-i", str(HERE / "assets/music.wav"), "-i", str(BUILD / "sfx.wav")]
    else:
        graph = f"[0]asplit=2[v][k];[1][k]{duck}[sd];[v][sd]amix=inputs=2:duration=first:normalize=0,{master}"
        inputs = ["-i", str(BUILD / "voice.wav"), "-i", str(BUILD / "sfx.wav")]
    subprocess.run([
        "ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", graph,
        "-map", "[out]", "-ar", "48000", "-c:a", "pcm_s16le", str(BUILD / "mix.wav")], check=True)

    # report: how far under her voice each effect actually lands in the bed
    for s in CUES["sfx"]:
        i = int(s["t"] * SR)
        seg = bed[i:i + int(0.6 * SR)]
        print(f"  {s['t']:7.2f}s {s['name']:<14} {window_db(seg).max() - speaking_db:+.1f} dB vs voice")
    stats = subprocess.run(["ffmpeg", "-i", str(BUILD / "mix.wav"), "-af", "ebur128=peak=true", "-f", "null", "-"],
                           capture_output=True, text=True).stderr
    summary = stats[stats.rfind("Summary:"):]
    print(BUILD / "mix.wav", " ".join(summary.split())[:200])


if __name__ == "__main__":
    main()
