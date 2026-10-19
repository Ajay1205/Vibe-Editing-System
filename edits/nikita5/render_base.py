"""Render the 4K rough cut with the zoom plan for one version, plus the cut voice track.

Picture: each kept segment is decoded straight from the raw 4K .mov, the zoom is applied per
frame on the YUV planes (Lanczos), and everything goes to one high-quality encode.
Versions:
  v1  gentle reframe (face bigger, wall trimmed) + soft punches on key words
  v2  original raw framing + light punch-ins that keep her face in place (its captions sit above her head)

Usage: python3 -I render_base.py v1|v2|voice [--preview]   (--preview = 1080p, fast)
"""

import json
import math
import pathlib
import subprocess
import sys

import cv2
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
RAW = HERE.parents[1] / "footage" / "nikita5" / "raw"
BUILD = HERE / "build"
EDL = json.load(open(HERE / "edl.json"))
CUES = json.load(open(HERE / "cues.json"))
FPS = EDL["fps"]
W, H = 2160, 3840
FACE = (0.48, 0.53)  # face centre in the raw frame (x, y as a fraction); set per clip below
# 5.1-5.3 were shot in 4K, 5.4-5.6 in 1080p (upscaled with Lanczos while decoding, framed slightly differently)
FACES = {"n51": (0.48, 0.53), "n52": (0.48, 0.53), "n53": (0.48, 0.53),
         "n54": (0.46, 0.55), "n55": (0.46, 0.55), "n56": (0.46, 0.55)}

VERSIONS = {
    #       base zoom, punch zoom (small, big), punch in/hold/out seconds, how far the face is lifted when zoomed
    "v1": {"base": 1.22, "small": 1.27, "big": 1.32, "tin": 0.25, "hold": 0.8, "tout": 0.5, "lift": 0.09},
    "v2": {"base": 1.00, "small": 1.07, "big": 1.12, "tin": 0.22, "hold": 0.7, "tout": 0.45, "lift": 0.0},
}


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def ease_out(x):
    x = min(1.0, max(0.0, x))
    return 1 - (1 - x) ** 3


def zoom_at(t, v):
    z = v["base"]
    for p in CUES["punches"]:
        target = v[p["kind"]]
        d = t - p["t"]
        if -0.0 <= d < v["tin"]:
            z = max(z, v["base"] + (target - v["base"]) * ease_out(d / v["tin"]))
        elif v["tin"] <= d < v["tin"] + v["hold"]:
            z = max(z, target)
        elif v["tin"] + v["hold"] <= d < v["tin"] + v["hold"] + v["tout"]:
            k = ease((d - v["tin"] - v["hold"]) / v["tout"])
            z = max(z, target + (v["base"] - target) * k)
    # section flashes: a quick zoom snap that settles back
    for f in CUES["flashes"]:
        d = t - f
        if 0 <= d < 0.5:
            z = max(z, v["base"] + 0.05 * (1 - ease_out(d / 0.5)))
    return z


def window(z, lift):
    """Crop window centre for zoom z: optionally pulls the face up (by `lift` of the frame) as we zoom in."""
    k = min(1.0, (z - 1.0) / 0.25)
    face_target = 0.54 - lift * k
    cy = FACE[1] + (0.5 - face_target) / z
    cx = FACE[0]
    half_w, half_h = 0.5 / z, 0.5 / z
    cx = min(max(cx, half_w), 1 - half_w)
    cy = min(max(cy, half_h), 1 - half_h)
    return cx, cy


def warp_plane(plane, z, cx, cy, out_w, out_h, interp):
    h, w = plane.shape
    s = z * out_w / w
    m = np.float32([[s, 0, out_w / 2 - s * cx * w], [0, s, out_h / 2 - s * cy * h]])
    return cv2.warpAffine(plane, m, (out_w, out_h), flags=interp, borderMode=cv2.BORDER_REPLICATE)


def render_video(name, preview):
    v = VERSIONS[name]
    ow, oh = (1080, 1920) if preview else (W, H)
    BUILD.mkdir(exist_ok=True)
    out = BUILD / f"base_{name}{'_preview' if preview else ''}.mp4"
    enc = subprocess.Popen(
        ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "yuv420p", "-s", f"{ow}x{oh}",
         "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "veryfast" if preview else "medium",
         "-crf", "20" if preview else "12", "-pix_fmt", "yuv420p", "-color_primaries", "bt709",
         "-color_trc", "bt709", "-colorspace", "bt709", str(out)],
        stdin=subprocess.PIPE)
    frame_no = 0
    global FACE
    for seg in EDL["segments"]:
        FACE = FACES[seg["clip"]]
        src = RAW / f"nikita_5.{seg['clip'][-1]}.mov"
        dec = subprocess.Popen(
            ["ffmpeg", "-v", "error", "-ss", f"{seg['in']:.4f}", "-i", str(src), "-frames:v", str(seg["frames"]),
             "-vf", f"fps={FPS},scale=2160:3840:flags=lanczos:out_color_matrix=bt709:out_range=tv,format=yuv420p",
             "-f", "rawvideo", "-"], stdout=subprocess.PIPE)
        ysz, csz = W * H, (W // 2) * (H // 2)
        got = 0
        last = None
        while got < seg["frames"]:
            buf = dec.stdout.read(ysz + 2 * csz)
            if len(buf) < ysz + 2 * csz:
                buf = last  # pad a short decode with the previous frame
                if buf is None:
                    raise SystemExit(f"no frames decoded for {seg}")
            last = buf
            t = frame_no / FPS
            z = zoom_at(t, v)
            cx, cy = window(z, v["lift"])
            y = np.frombuffer(buf, np.uint8, ysz).reshape(H, W)
            u = np.frombuffer(buf, np.uint8, csz, ysz).reshape(H // 2, W // 2)
            vv = np.frombuffer(buf, np.uint8, csz, ysz + csz).reshape(H // 2, W // 2)
            if abs(z - 1.0) < 1e-4 and not preview:
                planes = (y, u, vv)
            else:
                interp = cv2.INTER_LANCZOS4 if not preview else cv2.INTER_AREA
                planes = (warp_plane(y, z, cx, cy, ow, oh, interp),
                          warp_plane(u, z, cx, cy, ow // 2, oh // 2, interp),
                          warp_plane(vv, z, cx, cy, ow // 2, oh // 2, interp))
            for p in planes:
                enc.stdin.write(np.ascontiguousarray(p).tobytes())
            got += 1
            frame_no += 1
        dec.stdout.close()
        dec.wait()
        print(f"\r{name}: {frame_no}/{EDL['frames']} frames", end="", flush=True)
    enc.stdin.close()
    enc.wait()
    print(f"\n{out}")


def render_voice():
    """Cut the voice with the same frame-accurate ranges; 6 ms fades at every join remove clicks."""
    BUILD.mkdir(exist_ok=True)
    sr = 48000
    parts = []
    cache = {}
    for seg in EDL["segments"]:
        clip = seg["clip"]
        if clip not in cache:
            pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", str(RAW / f"nikita_5.{clip[-1]}.mov"), "-vn",
                                  "-ac", "1", "-ar", str(sr), "-f", "f32le", "-"], capture_output=True, check=True)
            cache[clip] = np.frombuffer(pcm.stdout, np.float32)
        a = cache[clip]
        n = round(seg["frames"] * sr / FPS)
        s = round(seg["in"] * sr)
        piece = a[s:s + n].copy()
        piece = np.pad(piece, (0, n - len(piece)))
        f = int(0.006 * sr)
        piece[:f] *= np.linspace(0, 1, f)
        piece[-f:] *= np.linspace(1, 0, f)
        parts.append(piece)
    voice = np.concatenate(parts)
    out = BUILD / "voice_raw.wav"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "f32le", "-ar", str(sr), "-ac", "1", "-i", "-",
                    str(out)], input=voice.tobytes(), check=True)
    print(f"{out}: {len(voice) / sr:.3f}s")


if __name__ == "__main__":
    what = sys.argv[1]
    if what == "voice":
        render_voice()
    else:
        render_video(what, "--preview" in sys.argv)
