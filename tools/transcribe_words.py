"""Word-timed transcript with faster-whisper, for languages Parakeet doesn't cover (e.g. Hindi/Hinglish).

Audio is decoded with ffmpeg and passed as an array, because faster-whisper's own
PyAV decoding breaks with PyAV 19 in this environment.

Usage:
    python3 -I tools/transcribe_words.py clip.mp4 -o clip.words.json --language hi --model large-v3
"""

import argparse
import json
import subprocess

import numpy as np
from faster_whisper import WhisperModel


def load_audio(path):
    pcm = subprocess.run(
        ["ffmpeg", "-v", "error", "-i", path, "-ac", "1", "-ar", "16000", "-f", "s16le", "-"],
        capture_output=True, check=True,
    ).stdout
    return np.frombuffer(pcm, np.int16).astype(np.float32) / 32768.0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("media")
    ap.add_argument("-o", "--output", required=True)
    ap.add_argument("--model", default="large-v3")
    ap.add_argument("--language", default=None, help="e.g. hi, en; omit to auto-detect")
    ap.add_argument("--prompt", default=None, help="initial prompt: names, key words, spelling style")
    args = ap.parse_args()

    model = WhisperModel(args.model, device="cpu", compute_type="int8")
    segments, info = model.transcribe(
        load_audio(args.media),
        language=args.language,
        word_timestamps=True,
        initial_prompt=args.prompt,
        vad_filter=False,
        condition_on_previous_text=False,
    )
    words, segs = [], []
    for s in segments:
        segs.append({"start": round(s.start, 2), "end": round(s.end, 2), "text": s.text.strip()})
        for w in s.words or []:
            words.append({"text": w.word.strip(), "start": round(w.start, 2), "end": round(w.end, 2),
                          "p": round(w.probability, 2)})

    with open(args.output, "w", encoding="utf-8") as f:
        json.dump({"language": info.language, "duration": round(info.duration, 2),
                   "segments": segs, "words": words}, f, ensure_ascii=False, indent=1)
    print(f"{args.output}: {len(words)} words, language={info.language}")


if __name__ == "__main__":
    main()
