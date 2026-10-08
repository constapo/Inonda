---
name: free-visual-generation
description: Generate images and video at zero cost using free tiers — Pollinations, Hugging Face (Spaces + Inference), Cloudflare Workers AI, Gemini API free tier, and local ComfyUI (Wan, LTX-Video, HunyuanVideo, FLUX). Use when the user asks for "free" generation, wants to save credits, or wants extra model diversity beyond the paid connectors in ai-visual-generation. Also lists web-only free generators that cannot be automated.
metadata:
  version: "1.0"
  researched: "2026-10"
---

# Free visual generation

Free tiers change often. If a call fails with a quota or authentication error,
tell the user. Do not silently fall back to a paid provider.

The paid multi-model route (Veo, Kling, Seedance, Runway through ElevenLabs, Krea
and vidIQ) is the `ai-visual-generation` skill. Use this skill when cost matters.
You can also use it as an extra source of model diversity alongside the paid route.

## Keys

All keys live in the user's `.env` file, which is git-ignored. Never commit a key
and never print one.

| Variable | Where to get it (free) |
|---|---|
| `POLLINATIONS_API_KEY` | Sign up at pollinations.ai, then create a secret `sk_` key. Use it server-side only. |
| `HF_TOKEN` | huggingface.co → Settings → Access Tokens. Create a "read" token. |
| `CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_API_TOKEN` | Cloudflare dashboard → Workers AI → create a token with Workers AI access. |
| `GEMINI_API_KEY` | aistudio.google.com → Get API key. |

Before calling a provider, check that its variable is set (`[ -n "$VAR" ]`). If it is
not set, tell the user which key to create and skip that provider.

## Tier A: free APIs an agent can call

### 1. Pollinations: images and video, widest free catalog
- Base URL: `https://gen.pollinations.ai`. Every generation call needs
  `Authorization: Bearer $POLLINATIONS_API_KEY`.
- The free allowance is "quest pollen". Check the remaining balance with the account
  balance endpoint.
- Image models include `black-forest-labs/flux.1-schnell` (default for the
  OpenAI-style endpoint), `tongyi-mai/z-image-turbo` (default for `/image/`),
  `qwen/qwen-image-3`, `alibaba/wan-2.7-image`, `bytedance/seedream-5.0-lite`,
  `x-ai/grok-imagine-image`, `recraft/recraft-v4.1-vector` (SVG) and
  `ideogram-ai/ideogram-v4-turbo`. The premium models use up pollen quickly.
- Video models include `alibaba/wan-2.2-fast`, `alibaba/wan-2.6`,
  `bytedance/seedance-2.0-mini`, `x-ai/grok-imagine-video-1.5-lite`,
  `minimax/minimax-h3` and `google/veo-3.1-fast` (default).
- Get the live model list from the public model-catalogue endpoint. Do not hardcode it.

```bash
mkdir -p out
# Image (GET form)
curl -sf -H "Authorization: Bearer $POLLINATIONS_API_KEY" \
  "https://gen.pollinations.ai/image/$(python3 -c 'import urllib.parse,sys;print(urllib.parse.quote(sys.argv[1]))' "$PROMPT")?model=black-forest-labs/flux.1-schnell&width=1024&height=1024" \
  -o out/pollinations.jpg
# Image (OpenAI-compatible)
curl -sf https://gen.pollinations.ai/v1/images/generations \
  -H "Authorization: Bearer $POLLINATIONS_API_KEY" -H "Content-Type: application/json" \
  -d "{\"model\":\"black-forest-labs/flux.1-schnell\",\"prompt\":$(jq -Rn --arg p "$PROMPT" '$p'),\"size\":\"1024x1024\"}"
# Video (GET form, same auth)
curl -sf -H "Authorization: Bearer $POLLINATIONS_API_KEY" \
  "https://gen.pollinations.ai/video/<url-encoded prompt>?model=alibaba/wan-2.2-fast" -o out/pollinations.mp4
```

### 2. Hugging Face: open models and community Spaces
- The `hf` MCP server is configured in `.mcp.json` and uses `HF_TOKEN`. Its tools
  search for Spaces and call Gradio Spaces directly. Free GPU Spaces queue jobs, so
  expect waits.
- Good free Spaces to try: FLUX.1-schnell / FLUX.1-dev (images), Qwen-Image,
  LTX-Video, Wan 2.x, HunyuanVideo (video). Search at the time of use, because Space
  names and status change.
- Without MCP, use `pip install gradio_client`, then
  `Client("<owner>/<space>", hf_token=os.environ["HF_TOKEN"]).predict(...)`.
  Run `client.view_api()` first to see the exact arguments.
- Inference Providers have a small monthly free credit for text-to-image models,
  for example `black-forest-labs/FLUX.1-schnell`.

### 3. Cloudflare Workers AI: reliable free images
- 10,000 Neurons per day free, reset at 00:00 UTC. With FLUX.1 schnell that is about
  25 images per day (capped at 250 steps per day, up to 1024²).
- Models: `@cf/black-forest-labs/flux-1-schnell`,
  `@cf/bytedance/stable-diffusion-xl-lightning`, `@cf/lykon/dreamshaper-8-lcm`.

```bash
curl -sf "https://api.cloudflare.com/client/v4/accounts/$CLOUDFLARE_ACCOUNT_ID/ai/run/@cf/black-forest-labs/flux-1-schnell" \
  -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" \
  -d "{\"prompt\":$(jq -Rn --arg p "$PROMPT" '$p'),\"steps\":4}" \
  | jq -r '.result.image' | base64 -d > out/cloudflare.jpg
```

### 4. Gemini API free tier: Gemini Flash Image ("Nano Banana")
- The free tier is small (reports range from about 50 to 500 per day) and some image
  models need billing enabled. If the API returns `RESOURCE_EXHAUSTED`, stop and tell
  the user.
- Veo has no free API tier. The free Veo route is the Google Flow website (Tier C).

## Tier B: free and local, on the user's own Linux machine

**ComfyUI** with open models is free and has no quotas, but it needs a decent NVIDIA
GPU: 8–12 GB VRAM for FLUX schnell, SDXL, Wan 2.2 5B and LTX-Video; 24 GB or more for
Wan 14B and HunyuanVideo.

```bash
git clone https://github.com/comfyanonymous/ComfyUI && cd ComfyUI
python3 -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
python main.py --listen 127.0.0.1 --port 8188
```

Download the model weights from Hugging Face into `ComfyUI/models/` by following each
model's ComfyUI example workflow. To let agents drive ComfyUI, add a ComfyUI MCP
server (for example `joenorton/comfyui-mcp-server`, served at
`http://127.0.0.1:9000/mcp`). Read its README before installing it.

## Tier C: free web apps with no API (use by hand, not as agents)

These sites give free credits only through their website. Scripting or scraping them
breaks their terms of service and risks a ban, so recommend them for manual use only.

| Service | Free allowance (approx., Sept 2026) | Notes |
|---|---|---|
| Kling (klingai.com) | ~66 credits per day | Most daily volume; 720p, 5s clips |
| Google Flow (Veo 3.1 Lite) | ~50 credits per day (~5 clips) | Best free quality; watermarked |
| Dreamina / CapCut | Daily credits | Seedance-based; images and video |
| Krea | 100 compute units per day for images | Already connected (paid connector) |
| PixVerse | Daily credits | Effects; low resolution on the free plan |
| Hailuo (MiniMax) | Small daily or trial allowance | Good with human faces |
| Pika | ~80 credits per month | 480p |
| Runway | 125 one-time credits | Do not renew |
| Meta AI, Microsoft Designer / Bing Image Creator, Grok Imagine, Adobe Firefly, Leonardo, Ideogram | Free daily or monthly credits | Images (some video) |

OpenAI Sora no longer has a free route; its consumer app shut down in April 2026.

## Workflow

1. Check which keys are set. Use every free Tier A provider that has a key, plus
   ComfyUI if it is running locally.
2. Send the same prompt to 2–4 providers or models for diversity. Save the results as
   `out/<provider>-<model>.<ext>`.
3. Show the user the results side by side with each provider and model named, then
   recommend one.
4. If the user needs higher quality than the free results, offer the paid
   `ai-visual-generation` route and say what it would cost.
