"""Final composite: base video (v1/v2) + light grade + caption layer + audio mix -> renders/*.mp4 (4K).

Usage: python3 -I compose.py v1|v2
"""

import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
BUILD = HERE / "build"
RENDERS = HERE / "renders"

# gentle look: a touch more contrast and colour, soft vignette to pull the eye to her face
GRADE = "eq=contrast=1.05:saturation=1.08:gamma=0.98,vignette=angle=PI/5:mode=forward"


def main(version, suffix=""):
    RENDERS.mkdir(exist_ok=True)
    out = RENDERS / f"nikita3_{version}_4k{suffix}.mp4"
    subprocess.run([
        "ffmpeg", "-v", "error", "-stats", "-y",
        "-i", str(BUILD / f"base_{version}.mp4"),
        "-c:v", "libvpx-vp9", "-i", str(BUILD / "overlay.webm"),
        "-i", str(BUILD / "mix.wav"),
        "-filter_complex", f"[0:v]{GRADE},format=yuv420p[b];[1:v]format=yuva420p[o];[b][o]overlay=0:0:format=yuv420,format=yuv420p[v]",
        "-map", "[v]", "-map", "2:a",
        "-c:v", "libx264", "-preset", "slow", "-crf", "15", "-profile:v", "high", "-level", "5.2",
        "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
        "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-movflags", "+faststart", "-shortest", str(out)], check=True)
    print(out)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "")
