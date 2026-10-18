"""Generate the background music bed locally with MusicGen (no account needed).

Generates one seed clip, then crossfade-loops it to the reel length.
Usage: python3 -I music.py --seconds 95 -o assets/music.wav
"""

import argparse

import numpy as np
import soundfile as sf
import torch
from transformers import AutoProcessor, MusicgenForConditionalGeneration

PROMPT = ("bright playful lo-fi pop instrumental, soft plucked acoustic guitar, warm rhodes piano, "
          "light finger snaps and soft kick, positive curious educational vibe, 100 bpm, clean modern mix, no vocals")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seconds", type=float, required=True)
    ap.add_argument("--seed-seconds", type=float, default=24)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--model", default="facebook/musicgen-small")
    ap.add_argument("-o", "--output", required=True)
    args = ap.parse_args()

    torch.manual_seed(args.seed)
    torch.set_num_threads(4)
    proc = AutoProcessor.from_pretrained(args.model)
    model = MusicgenForConditionalGeneration.from_pretrained(args.model)
    inputs = proc(text=[PROMPT], padding=True, return_tensors="pt")
    tokens = int(args.seed_seconds * model.config.audio_encoder.frame_rate)
    with torch.no_grad():
        audio = model.generate(**inputs, max_new_tokens=tokens, do_sample=True, guidance_scale=3.0)
    sr = model.config.audio_encoder.sampling_rate
    seed = audio[0, 0].numpy().astype(np.float32)

    # loop with 2 s equal-power crossfades until long enough
    xf = int(2.0 * sr)
    out = seed.copy()
    ramp = np.linspace(0, np.pi / 2, xf)
    while len(out) < args.seconds * sr:
        tail, head = out[-xf:], seed[:xf]
        out = np.concatenate([out[:-xf], tail * np.cos(ramp) + head * np.sin(ramp), seed[xf:]])
    out = out[: int(args.seconds * sr)]
    fade = int(3.0 * sr)
    out[-fade:] *= np.linspace(1, 0, fade)
    out /= max(1e-6, np.abs(out).max()) / 0.9
    sf.write(args.output, out, sr)
    print(f"{args.output}: {len(out) / sr:.1f}s at {sr} Hz")


if __name__ == "__main__":
    main()
