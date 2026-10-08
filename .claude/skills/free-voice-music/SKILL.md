---
name: free-voice-music
description: Free-only voice, voice cloning, music, captions and real footage for videos — Chatterbox (MIT, clones the user's own voice locally), Kokoro (Apache-2.0 TTS), Piper, Whisper captions, ACE-Step music, and the free Adobe Stock video/audio collection through the connected Adobe tool. Use when the user wants narration, "my voice", background music, subtitles or stock footage without a paid plan, or when ElevenLabs/Krea/Veo hit a paywall.
metadata:
  version: "1.0"
  researched: "2026-10"
---

# Free voice, music and footage

Rule: only use tools that need no paid plan. If a step would need payment, say so
and offer the free alternative below. Do not swap to a paid provider silently.

## 1. Voice

| Need | Free tool | License | Where it runs |
|---|---|---|---|
| **The user's own voice, read automatically** | **Chatterbox** (Resemble AI) — clones a voice from a 10–30 s sample | MIT (commercial OK; output carries an inaudible watermark) | User's Linux machine. GPU fast; CPU works but is slow (minutes per scene) |
| Natural preset voices | **Kokoro-82M** | Apache-2.0 | CPU fine |
| Fast, robotic-ish | **Piper** | MIT (check each voice's licence) | CPU, very fast |
| Best quality, free | The user records it themselves (phone voice memo) | their own | — |

Avoid for commercial ads: Coqui XTTS-v2 (non-commercial CPML), F5-TTS weights
(CC-BY-NC), ElevenLabs free tier (no commercial licence, attribution). Only clone a
voice with its owner's consent.

Clone the user's voice for the Inonda ad (writes `docs/video-ad/voice/NN.wav`):

```bash
pip install chatterbox-tts torchaudio
python3 scripts/video-ad/voice_clone.py --sample ~/my_voice.wav   # 10–30 s, quiet room
```

Kokoro quick use:

```python
from kokoro import KPipeline; import soundfile as sf, numpy as np
pipe = KPipeline(lang_code="a")                      # "a" = American English
audio = np.concatenate([a for _, _, a in pipe(text, voice="am_michael")])
sf.write("out.wav", audio, 24000)
```

## 2. Captions and timing

- **Whisper** (MIT, `pip install openai-whisper`): `whisper voice.wav --language en
  --output_format srt` gives word-accurate timing. Use it to re-time subtitles to a
  real recording.
- The installed `video-editing` skill wraps Whisper + ffmpeg for burned-in captions.

## 3. Music

- **Adobe Stock free audio** — already connected. Call `asset_search` with
  `entityScope: "StockAsset"`, `filters: {"contentType": "Audio", "pricing": "free"}`.
  Then call `asset_license_and_download_stock`, which costs nothing for free assets.
  Download the URL within 1 hour.
- **ACE-Step 1.5** (open weights; confirm the licence file in its repo): run it locally
  with about 4 GB of VRAM, or use the free API key from acemusic.ai.
- Pixabay Music and the YouTube Audio Library are royalty-free, but you download from
  them by hand.
- Duck music under the voice with
  `sidechaincompress` + `amix`, at a music volume of about 0.10–0.15.

## 4. Real footage (most realistic, free)

- **Adobe Stock free videos**: `asset_search` with `contentType: "Video"` and
  `pricing: "free"`. Do not add an `orientation` filter, because it returns nothing
  for videos. Prefer 1920×1080 or larger landscape clips. License each clip and
  download it within 1 hour.
- **Pixabay** via the Orshot tool `orshot_search_stock_media` (type video). This
  library is smaller and some clips are cartoons, so check every result.
- Read the clip names, then extract a frame from each clip and look at it before
  using it.

## 5. Editing (free)

- ffmpeg (the `ffmpeg` skill), the `video-editing` skill, and
  `scripts/video-ad/edit_stock.py`. That script cuts clips on narration phrases,
  snaps each cut to a pause, and adds titles and Greek subtitles.
- Remotion (the `remotion-best-practices` skill) is free for individuals and companies
  with up to 3 employees. Larger companies need a paid Remotion licence.

## Not free (do not use without the user's approval)

ElevenLabs paid features (video, voice cloning, commercial voice), Krea video, Veo,
Kling, Runway, Modal/RunPod GPU hosting, and paid Adobe Stock assets
(`pricing: "core"`).
