---
name: ai-visual-generation
description: Generate AI video and images with Veo, Kling, Seedance, Runway, MiniMax/Hailuo, Wan, LTX, FLUX, Seedream, GPT-Image, Gemini and more through the connected ElevenLabs, Krea and vidIQ connectors. Use when asked to "make a video", "animate this image", "generate a clip/ad/reel", "use Veo/Kling/Seedance/Runway", "compare models", or to create design visuals where trying several models gives a better result.
metadata:
  version: "1.0"
---

# AI visual generation (multi-model)

Working rule: **more model diversity = better final pick.** For any important shot,
run the same brief through 2–3 different models, then compare and keep the best.

## Where each model lives

Every model below is reached through a connector that is already connected to this
account. No local install or API key is needed. Load the tool with ToolSearch first.

| Model family | Best for | Connector → tool | model id(s) |
|---|---|---|---|
| **Google Veo 3.1** | Cinematic shots, native audio and spoken dialogue | ElevenLabs → `creative_generate_video` | `veo-3.1-generate-001`, `veo-3.1-fast-generate-001`, `veo-3.1-lite-generate-001` |
| | | vidIQ → `vidiq_generate_video` | `veo-3.1`, `veo-3.1-fast`, `veo-3.1-lite` |
| **Kling 3 / O3** | 4K@60fps, up to 15s, multi-shot (6 angles), lip-sync, character consistency | ElevenLabs | `kling-3-pro`, `kling-o3-pro`, `kling-2.6-pro`, `kling-2.5-turbo`, `*-motion-control`, `kling-o3-edit-video` |
| | | vidIQ | `kling-3`, `kling-3-pro` |
| **ByteDance Seedance 2 / 2.5** | Realistic motion, multi-shot storytelling, mixed text+image+video+audio input | ElevenLabs | `bytedance-seedance-v2.5`, `bytedance-seedance-v2`, `-v2-fast`, `-v2-mini`, `-v2.5-edit`, `-v2.5-extend` |
| | | vidIQ | `seedance-2`, `seedance-2-fast` (up to 9 reference images) |
| **Runway Gen-4.5 / Aleph** | Stylised, silent cinematic video; Aleph edits existing footage; Act-Two for performance capture | ElevenLabs | `runway-gen4-5`, `runway-gen4-turbo`, `runway-aleph2`, `runway-act-two`, `runway-ruby` |
| **MiniMax Hailuo H3** | Long, flexible durations (4–15s), up to 2K | ElevenLabs / vidIQ | `minimax-h3`, `minimax-h3-max` |
| **Wan, LTX, FLUX video** | Cheap drafts, audio-driven video, edits | ElevenLabs | `wan-2.6`, `ltx-v2-fast`, `ltx-audio-to-video`, `flux-3-video` |
| **Talking heads / lip-sync** | Animating a portrait to an audio track, or dubbing | ElevenLabs | `bytedance-omnihuman-v1.5`, `creatify-aurora`, `heygen-avatar4`, `sync-lipsync-v3` |
| **Images** | Stills, keyframes, product shots, posters | ElevenLabs → `creative_generate_image` | `gpt-image-2`, `gemini-3-pro-image`, `bytedance-seedream-5-pro`, `flux-3-image`, `recraft-v4`, `runway-gen4-image`, `krea-2-large` |
| **Krea catalog** | Second source for most of the above and Krea's own models | Krea → `list_models` then `generate_video` / `generate_image` | read the ids from `list_models` |

The model lists change often. Before you choose, check what the account can actually
run with ElevenLabs `creative_get_flow_node_types` or Krea `list_models`. Do not rely
on this table alone.

## Workflow

1. **Brief.** Collect the subject, action, setting, mood, camera, duration, aspect ratio
   (16:9, 9:16 or 1:1), audio needs and any reference images. Ask only for what is
   actually missing.
2. **Pick 2–3 contrasting models** from the table, for example:
   - Dialogue or sound needed: Veo 3.1 + Kling 3 Pro (both produce native audio)
   - Realistic motion or action: Seedance 2.5 + Kling 3 Pro
   - Artistic or stylised look: Runway Gen-4.5 + Seedance 2.5
   - Fast, cheap exploration: `veo-3.1-fast`, `seedance-v2-fast` or `ltx-v2-fast`
3. **Get the prompting guide.** For an unfamiliar model call ElevenLabs
   `creative_get_model_guide`. For Seedance or Kling on Krea call `get_prompting_guide`.
4. **Price first.** Call `creative_generate_video` with `estimate_only: true` and show
   the user the total credit cost. Wait for their approval before spending.
5. **Generate on one flow.** Call `creative_create_flow` once, then pass its `flow_id` to
   every generation so the results sit side by side on one canvas.
6. **Poll** `creative_get_flow_run_status` (wait `poll_after_seconds` between calls)
   until `all_completed` or `has_failures`. For vidIQ, poll `vidiq_job_poll`. The Krea
   widget polls by itself.
7. **Compare and deliver.** Name each model, give its result link and a one-line note on
   its strengths, and recommend one. Give the user the flow URL so they can keep editing.

## Prompt structure for video

```
[Shot type + camera move] of [subject + appearance] [action] in [setting],
[lighting / time of day], [style / film look], [mood].
Audio: [dialogue in quotes / ambient sound / music]  (Veo, Kling, Seedance only)
```

Write one action per shot. Name the camera move ("slow dolly-in", "orbit left",
"handheld"). Runway produces no audio, so add an ElevenLabs `sfx`, `music` or `tts`
node plus a `composition` node when the clip needs sound.

## Image-to-video

1. Generate or upload the keyframe image on the same flow. For local files use
   `creative_create_asset_upload`; for URLs use `creative_attach_reference_file`.
2. Pass that image's node id in `connect_from` on the video call.
3. To combine several shots, generate each one on the same flow and wire them into a
   `composition` node.

## Rules

- **Every generation costs credits.** Never call a generation tool a second time to
  "retry". Check status instead. Re-run only when the user asks for a new version.
- To build on one of several variations, pin it with `creative_add_flow_asset_node`
  (pass its `generation_id`) and connect from that node.
- If generation fails with a content-policy error, change the prompt before trying again.
- If a connector reports insufficient credits, tell the user which service needs topping
  up. Do not switch to another paid provider without asking.
- Save chosen files under `/assets/generated/` only when the user wants them in the repo.

## Optional direct APIs (not installed)

If the connectors are ever unavailable, each vendor also offers a direct API that needs
the user's own key, kept in `.env` and never committed:

- Google Veo: Gemini API / Vertex AI
- Kling: Kling AI developer API
- Seedance: BytePlus ModelArk
- Runway: `dev.runwayml.com`
- Aggregators that serve most of these models behind one key: fal.ai, Replicate
