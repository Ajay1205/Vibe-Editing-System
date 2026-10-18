"""Render the 4K rough cut of the Nikita 4 reel with its zoom plan, plus the cut voice track.

Picture: each kept segment is decoded straight from the raw 4K .mov, the zoom is applied per frame on the
YUV planes (Lanczos), and everything goes to one high-quality encode. One version ("v1"): raw framing with calm
punch-ins on the English lines only.

Usage: python3 -I render_base.py v1|voice [--preview]   (--preview = 1080p, fast)
"""

import json
import math
import pathlib
import subprocess
import sys

import cv2
import numpy as np

HERE = pathlib.Path(__file__).resolve().parent
RAW = HERE.parents[1] / "footage" / "nikita4" / "raw"
BUILD = HERE / "build"
EDL = json.load(open(HERE / "edl.json"))
CUES = json.load(open(HERE / "cues.json"))
FPS = EDL["fps"]
W, H = 2160, 3840
FACE = (0.48, 0.53)  # Nikita's face centre in the raw frame (x, y as a fraction)

VERSIONS = {
    # v1 (v3 look, "Close & Bold"): shots from cues.json alternate a medium and a close framing with a hard
    # cut-in on every English line, each shot slowly pushing in by `drift`. ft = where her face sits (0 = top).
    "v1": {"mid": (1.30, 0.40), "ask": (1.46, 0.385), "close": (1.68, 0.36), "drift": 0.035, "glide": 0.55},
}


def ease(x):
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def ease_out(x):
    x = min(1.0, max(0.0, x))
    return 1 - (1 - x) ** 3


def shot_state(k, t, v):
    """Framing of shot k at time t: its zoom slowly pushing in over the shot's length."""
    shots = CUES["shots"]
    sh = shots[k]
    t1 = shots[k + 1]["t"] if k + 1 < len(shots) else EDL["duration"]
    z, ft = v[sh["kind"]]
    p = ease((t - sh["t"]) / max(0.5, t1 - sh["t"]))
    return z * (1 + v["drift"] * p), ft


def smoother(x):
    x = min(1.0, max(0.0, x))
    return x * x * x * (x * (6 * x - 15) + 10)


def zoom_at(t, v):
    """Zoom and face height for output time t. Shot changes glide (user note: hard zoom jumps weren't smooth):
    the move starts a little before the shot's cue and eases in and out over v['glide'] seconds."""
    shots = CUES["shots"]
    g = v["glide"]
    k = 0
    for i, sh in enumerate(shots):
        if sh["t"] - 0.6 * g <= t + 1e-6:
            k = i
    z, ft = shot_state(k, max(t, shots[k]["t"]), v)
    if k > 0:
        x = (t - (shots[k]["t"] - 0.6 * g)) / g
        if x < 1:
            zp, fp = shot_state(k - 1, t, v)
            w = smoother(x)
            z, ft = zp + (z - zp) * w, fp + (ft - fp) * w
    return z, ft


def window(z, ft):
    """Crop window centre for zoom z with her face at height ft of the output frame."""
    cy = FACE[1] + (0.5 - ft) / z
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
    for seg in EDL["segments"]:
        src = RAW / f"nikita_4.{seg['clip'][-1]}.mov"
        dec = subprocess.Popen(
            ["ffmpeg", "-v", "error", "-ss", f"{seg['in']:.4f}", "-i", str(src), "-frames:v", str(seg["frames"]),
             "-vf", f"fps={FPS},scale=out_color_matrix=bt709:out_range=tv,format=yuv420p",
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
            z, ft = zoom_at(t, v)
            cx, cy = window(z, ft)
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
            pcm = subprocess.run(["ffmpeg", "-v", "error", "-i", str(RAW / f"nikita_4.{clip[-1]}.mov"), "-vn",
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
