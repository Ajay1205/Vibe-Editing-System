"""Mix the reel audio: cleaned voice + timed sound effects (+ optional ducked music bed) -> build/mix.wav.

Voice: rumble cut, light denoise, gentle compression, loudness to -14 LUFS (Instagram level).
Music: sits about 20 dB under the voice and is ducked further whenever she speaks.
SFX: bundled HyperFrames library (Pixabay licence), placed from cues.json.
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
SFX_LEVEL = 0.6
MUSIC = False  # off for now (user request); set True to lay assets/music.wav under the voice
MUSIC_DB = -10  # music bed ~ -30 LUFS, ~16 dB under the voice before ducking


def decode(path):
    pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-ac", "2", "-ar", str(SR), "-f", "f32le", "-"],
                         capture_output=True, check=True).stdout
    return np.frombuffer(pcm, np.float32).reshape(-1, 2)


def write(path, a):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(SR), "-ac", "2", "-i", "-", str(path)],
                   input=np.ascontiguousarray(a, np.float32).tobytes(), check=True)


def main():
    n = int(round(CUES["duration"] * SR))
    bed = np.zeros((n, 2), np.float32)
    cache = {}
    for s in CUES["sfx"]:
        if s["name"] not in cache:
            cache[s["name"]] = decode(SFX_DIR / f"{s['name']}.mp3")
        a = cache[s["name"]] * s["gain"] * SFX_LEVEL
        i = int(s["t"] * SR)
        j = min(n, i + len(a))
        bed[i:j] += a[: j - i]
    write(BUILD / "sfx.wav", bed)

    voice = ("[0]aformat=channel_layouts=mono,highpass=f=80,afftdn=nr=8:nf=-45,"
             "acompressor=threshold=-20dB:ratio=3:attack=5:release=90:makeup=2,"
             "loudnorm=I=-14:TP=-2:LRA=7,aresample=48000")
    master = "alimiter=limit=0.79:attack=3:release=50:level=disabled,loudnorm=I=-14:TP=-1.5:LRA=7,aresample=48000[out]"
    if MUSIC:
        graph = (f"{voice},asplit=2[v][key];"
                 # music: level, fade in/out, duck under the voice
                 f"[1]aresample=48000,aformat=channel_layouts=stereo,volume={MUSIC_DB}dB,"
                 f"afade=t=in:d=0.6,afade=t=out:st={CUES['duration'] - 1.6:.2f}:d=1.6,atrim=0:{CUES['duration']:.3f}[m];"
                 "[key]aformat=channel_layouts=stereo[k];"
                 "[m][k]sidechaincompress=threshold=0.03:ratio=6:attack=20:release=350:makeup=1[md];"
                 f"[v]aformat=channel_layouts=stereo[vs];[vs][md][2]amix=inputs=3:duration=first:normalize=0,{master}")
        inputs = ["-i", str(BUILD / "voice_raw.wav"), "-i", str(HERE / "assets/music.wav"), "-i", str(BUILD / "sfx.wav")]
    else:
        graph = f"{voice},aformat=channel_layouts=stereo[vs];[vs][1]amix=inputs=2:duration=first:normalize=0,{master}"
        inputs = ["-i", str(BUILD / "voice_raw.wav"), "-i", str(BUILD / "sfx.wav")]
    subprocess.run([
        "ffmpeg", "-v", "error", "-y", *inputs, "-filter_complex", graph,
        "-map", "[out]", "-ar", "48000", "-c:a", "pcm_s16le", str(BUILD / "mix.wav")], check=True)
    stats = subprocess.run(["ffmpeg", "-i", str(BUILD / "mix.wav"), "-af", "ebur128=peak=true", "-f", "null", "-"],
                           capture_output=True, text=True).stderr
    summary = stats[stats.rfind("Summary:"):]
    print(BUILD / "mix.wav", " ".join(summary.split())[:200])


if __name__ == "__main__":
    main()
