"""Final composite: base video + light grade + caption layer + audio mix -> renders/*.mp4.

Usage: python3 -I compose.py v1|v2 [--preview]   (--preview = fast 1080p review copy)
"""

import pathlib
import subprocess
import sys

HERE = pathlib.Path(__file__).resolve().parent
BUILD = HERE / "build"
RENDERS = HERE / "renders"

# gentle look: a touch more contrast and colour, soft vignette to pull the eye to her face
GRADE = "eq=contrast=1.05:saturation=1.08:gamma=0.98,vignette=angle=PI/5:mode=forward"


def main(version, preview=False):
    RENDERS.mkdir(exist_ok=True)
    out = RENDERS / f"manisha3_{version}_{'preview_1080p' if preview else '4k'}.mp4"
    scale = "scale=1080:1920:flags=lanczos," if preview else ""  # base preview is 1080p already; harmless
    subprocess.run([
        "ffmpeg", "-v", "error", "-stats", "-y",
        "-i", str(BUILD / f"base_{version}{'_preview' if preview else ''}.mp4"),
        "-c:v", "libvpx-vp9", "-i", str(BUILD / f"overlay_{version}_{1080 if preview else 2160}.webm"),
        "-i", str(BUILD / "mix.wav"),
        "-filter_complex", f"[0:v]{scale}{GRADE},format=yuv420p[b];[1:v]format=yuva420p[o];[b][o]overlay=0:0:format=yuv420,format=yuv420p[v]",
        "-map", "[v]", "-map", "2:a",
        "-c:v", "libx264", *(["-preset", "veryfast", "-crf", "20"] if preview else
                             ["-preset", "medium", "-crf", "15", "-profile:v", "high", "-level", "5.2"]),
        "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
        "-c:a", "aac", "-b:a", "320k", "-ar", "48000", "-movflags", "+faststart", "-shortest", str(out)], check=True)
    print(out)


if __name__ == "__main__":
    main(sys.argv[1], "--preview" in sys.argv)
