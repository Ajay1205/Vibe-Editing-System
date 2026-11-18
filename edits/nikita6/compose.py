"""Final composite: base video + light grade + caption layer + audio mix -> renders/*.mp4.

Usage: python3 -I compose.py v1|v2 [--preview] [--crf N]   (--preview = fast 1080p review copy)
--crf N: master CRF (default 15). Use 16 when the master must be ONE file under the 400 MiB chat limit for an
Instagram upload (user, 18 Nov: a Reel can't be split; Instagram re-encodes anyway). Output gets a _crfN suffix.
--start S: trial-reel variation that starts S seconds into the reel (pick S in a pause, never inside a word).
Picture, captions and mix are all cut from the same 4K parts; 30 ms audio fade-in. Output gets a _fromS suffix.
"""

import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
BUILD = HERE / "build"
RENDERS = HERE / "renders"

# brighter, cleaner look (user note 18 Nov: the footage looked too dark): lift shadows and mids with a soft curve,
# highlights kept, a touch less orange; no vignette
GRADE = ("curves=master='0/0 0.2/0.30 0.5/0.66 0.8/0.89 1/1',eq=contrast=1.03:saturation=1.04,"
         "colorbalance=rm=-0.03:bm=0.03")


def main(version, preview=False, crf=15, start=0.0):
    RENDERS.mkdir(exist_ok=True)
    out = RENDERS / f"nikita6_{version}_{'preview_1080p' if preview else '4k'}{'' if preview or crf == 15 else f'_crf{crf}'}{f'_from{start:g}s' if start else ''}.mp4"
    ss = ["-ss", f"{start:.3f}"] if start else []
    scale = "scale=1080:1920:flags=lanczos," if preview else ""  # base preview is 1080p already; harmless
    subprocess.run([
        "ffmpeg", "-v", "error", "-stats", "-y",
        *ss, "-i", str(BUILD / f"base_{version}{'_preview' if preview else ''}.mp4"),
        *ss, "-c:v", "libvpx-vp9", "-i", str(BUILD / f"overlay_{version}_{1080 if preview else 2160}.webm"),
        *ss, "-i", str(BUILD / "mix.wav"),
        "-filter_complex", f"[0:v]{scale}{GRADE},format=yuv420p[b];[1:v]format=yuva420p[o];[b][o]overlay=0:0:format=yuv420,format=yuv420p[v]",
        *(["-af", "afade=t=in:d=0.03"] if start else []),
        "-map", "[v]", "-map", "2:a",
        "-c:v", "libx264", *(["-preset", "veryfast", "-crf", "20"] if preview else
                             ["-preset", "medium", "-crf", str(crf), "-profile:v", "high", "-level", "5.2"]),
        "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
        "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-movflags", "+faststart", "-shortest", str(out)], check=True)
    print(out)


if __name__ == "__main__":
    crf = int(sys.argv[sys.argv.index("--crf") + 1]) if "--crf" in sys.argv else 15
    start = float(sys.argv[sys.argv.index("--start") + 1]) if "--start" in sys.argv else 0.0
    main(sys.argv[1], "--preview" in sys.argv, crf, start)
