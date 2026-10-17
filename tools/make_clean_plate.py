"""Build an empty-room "clean plate" from a talking-head take, without filming one.

Needs the take and the person cutout from:
    npx hyperframes remove-background take.mp4 -o take.fg.webm

How it works:
  1. Sample frames across the take, plus the matching cutout alpha (where the person is).
  2. For every pixel, take the median colour over the samples where the person was NOT there.
     Anything the person uncovered at any moment comes back as the real room.
  3. Pixels the person covered the whole time are filled by inpainting and reported:
     LaMa (AI, needs onnxruntime + huggingface_hub) with --ai, else OpenCV's fast fill.

Usage:
    python3 -I tools/make_clean_plate.py take.mp4 take.fg.webm -o clean_plate.png --ai
"""

import argparse
import json
import subprocess
import sys
import warnings

import cv2
import numpy as np


def probe(path):
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-select_streams", "v:0",
         "-show_entries", "stream=width,height:format=duration", "-of", "json", path],
        capture_output=True, check=True, text=True,
    ).stdout
    info = json.loads(out)
    s = info["streams"][0]
    return s["width"], s["height"], float(info["format"]["duration"])


def read_frames(path, times, w, h, rgba=False):
    """Decode one frame at each time. VP9 alpha needs the libvpx decoder."""
    pix = "rgba" if rgba else "rgb24"
    ch = 4 if rgba else 3
    frames = []
    for t in times:
        cmd = ["ffmpeg", "-v", "error"]
        if rgba:
            cmd += ["-c:v", "libvpx-vp9"]
        cmd += ["-ss", f"{t:.3f}", "-i", path, "-frames:v", "1",
                "-vf", f"scale={w}:{h}", "-pix_fmt", pix, "-f", "rawvideo", "-"]
        raw = subprocess.run(cmd, capture_output=True, check=True).stdout
        if len(raw) < w * h * ch:
            continue
        frames.append(np.frombuffer(raw[: w * h * ch], np.uint8).reshape(h, w, ch))
    return frames


def lama_fill(plate, hole):
    """Fill the hole with LaMa on a square crop around it, resized to the model's 512x512."""
    import onnxruntime as ort
    from huggingface_hub import hf_hub_download

    model = hf_hub_download("Carve/LaMa-ONNX", "lama_fp32.onnx")
    sess = ort.InferenceSession(model, providers=["CPUExecutionProvider"])

    h, w = hole.shape
    ys, xs = np.nonzero(hole)
    pad = max(32, int(0.5 * max(np.ptp(ys), np.ptp(xs))))
    side = min(max(np.ptp(ys), np.ptp(xs)) + 2 * pad, h, w)
    cy, cx = (ys.min() + ys.max()) // 2, (xs.min() + xs.max()) // 2
    y0 = int(np.clip(cy - side // 2, 0, h - side))
    x0 = int(np.clip(cx - side // 2, 0, w - side))
    crop = plate[y0:y0 + side, x0:x0 + side]
    mcrop = hole[y0:y0 + side, x0:x0 + side]

    img = cv2.resize(crop, (512, 512), interpolation=cv2.INTER_AREA).astype(np.float32) / 255.0
    msk = (cv2.resize(mcrop.astype(np.uint8), (512, 512), interpolation=cv2.INTER_NEAREST) > 0).astype(np.float32)
    out = sess.run(None, {"image": img.transpose(2, 0, 1)[None], "mask": msk[None, None]})[0][0]
    out = out.transpose(1, 2, 0)
    if out.max() <= 1.5:
        out = out * 255.0
    out = cv2.resize(out.clip(0, 255).astype(np.uint8), (side, side), interpolation=cv2.INTER_CUBIC)

    filled = plate.copy()
    region = filled[y0:y0 + side, x0:x0 + side]
    region[mcrop] = out[mcrop]
    return filled


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("video", help="original take (mp4/mov)")
    ap.add_argument("cutout", help="person cutout with alpha from hyperframes remove-background (.webm)")
    ap.add_argument("-o", "--output", default="clean_plate.png")
    ap.add_argument("--samples", type=int, default=60, help="frames sampled across the take")
    ap.add_argument("--start", type=float, default=0.0, help="only sample from this time (s)")
    ap.add_argument("--end", type=float, default=None, help="only sample up to this time (s)")
    ap.add_argument("--grow", type=int, default=0,
                    help="pixels to grow the person mask by (default: 1%% of frame width), hides soft edges and shadows")
    ap.add_argument("--hole-mask", default=None, help="optional PNG of the pixels that were never uncovered")
    ap.add_argument("--ai", action="store_true", help="fill never-uncovered pixels with LaMa instead of OpenCV")
    args = ap.parse_args()

    w, h, dur = probe(args.video)
    end = min(args.end or dur, dur) - 0.05
    times = np.linspace(args.start, end, args.samples)
    grow = args.grow or max(3, w // 100)

    rgb = read_frames(args.video, times, w, h)
    cut = read_frames(args.cutout, times, w, h, rgba=True)
    n = min(len(rgb), len(cut))
    if n == 0:
        sys.exit("No frames decoded. Check both files.")

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * grow + 1, 2 * grow + 1))
    stack = np.stack(rgb[:n]).astype(np.float32)
    person = np.stack([cv2.dilate((c[..., 3] > 16).astype(np.uint8), kernel) for c in cut[:n]]).astype(bool)

    stack[person] = np.nan
    with np.errstate(all="ignore"), warnings.catch_warnings():
        warnings.simplefilter("ignore", RuntimeWarning)  # all-NaN columns are the hole, handled below
        plate = np.nanmedian(stack, axis=0)
    hole = np.isnan(plate[..., 0])
    plate = np.nan_to_num(plate).clip(0, 255).astype(np.uint8)

    hole_pct = 100.0 * hole.mean()
    if hole.any():
        if args.ai:
            plate = lama_fill(plate, hole)
        else:
            radius = max(5, w // 200)
            plate = cv2.inpaint(plate, hole.astype(np.uint8) * 255, radius, cv2.INPAINT_TELEA)
    if args.hole_mask:
        cv2.imwrite(args.hole_mask, hole.astype(np.uint8) * 255)

    cv2.imwrite(args.output, cv2.cvtColor(plate, cv2.COLOR_RGB2BGR))
    print(json.dumps({
        "output": args.output,
        "frames_used": n,
        "never_uncovered_pct": round(hole_pct, 2),
        "note": "0% = real room everywhere; the higher this is, the more of the plate is guessed by inpainting",
    }))


if __name__ == "__main__":
    main()
