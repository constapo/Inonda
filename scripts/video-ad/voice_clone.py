#!/usr/bin/env python3
"""Read the Inonda ad script in YOUR OWN voice, free and locally (Chatterbox, MIT).

  pip install chatterbox-tts torchaudio
  python3 scripts/video-ad/voice_clone.py --sample ~/my_voice.wav

--sample: 10–30 s of you speaking English clearly in a quiet room (wav/mp3/m4a).
Writes docs/video-ad/voice/01.wav … 13.wav; then re-render the ad with
scripts/video-ad/edit_stock.py, which picks these files up automatically.
"""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AD = ROOT / "docs/video-ad"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--sample", required=True, help="recording of your voice")
    ap.add_argument("--device", default=None, help="cuda / cpu (auto if omitted)")
    ap.add_argument("--exaggeration", type=float, default=0.45, help="0.3 calm … 0.7 lively")
    args = ap.parse_args()

    import torch
    import torchaudio
    from chatterbox.tts import ChatterboxTTS

    device = args.device or ("cuda" if torch.cuda.is_available() else "cpu")
    print(f"loading Chatterbox on {device} (first run downloads the model)…")
    model = ChatterboxTTS.from_pretrained(device=device)

    segs = json.loads((AD / "segments.json").read_text(encoding="utf-8"))
    out_dir = AD / "voice"
    out_dir.mkdir(parents=True, exist_ok=True)
    for i, seg in enumerate(segs, 1):
        out = out_dir / f"{i:02}.wav"
        print(f"scene {i}/{len(segs)} → {out.name}")
        wav = model.generate(seg["en"], audio_prompt_path=args.sample,
                             exaggeration=args.exaggeration)
        torchaudio.save(str(out), wav, model.sr)
    print("done — now run: python3 scripts/video-ad/edit_stock.py --clips <stock dir> "
          "--music <music.wav>")


if __name__ == "__main__":
    main()
