#!/usr/bin/env python3
"""Edit the Inonda.LTD ad from real stock footage + per-scene narration.

Inputs
  docs/video-ad/segments.json   narration text (en) + Greek subtitles (text)
  docs/video-ad/shots.json      per scene: clips cut on narration phrases
  docs/video-ad/voice/NN.mp3    narration audio, one file per scene
  --clips DIR                   stock clips named <id>.mov

Each shot ends where its phrase ("upto") ends in the narration: the cut point
is estimated from character position and snapped to the nearest pause found
with silencedetect, so visuals change exactly when the voice moves on.

Output: docs/video-ad/out/inonda-ad.mp4 (+ subtitles.el.srt)
"""
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from build_subs import WRITTEN, chunks, ts, wrap  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
AD = ROOT / "docs/video-ad"
W, H, FPS = 1920, 1080, 30
GAP = 1.0      # pause between scenes
TAIL = 5.0     # end card hold after last word
INTRO = {"clip": "1513585409", "ss": 1, "dur": 4.0, "intro": True}  # title shot, no voice
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def run(cmd):
    r = subprocess.run([str(c) for c in cmd], capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"failed: {' '.join(map(str, cmd))[:300]}\n{r.stderr[-1500:]}")
    return r.stdout + r.stderr


def duration(p):
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                      "-of", "csv=p=0", p]).strip())


def pauses(audio):
    out = run(["ffmpeg", "-hide_banner", "-i", audio, "-af",
               "silencedetect=noise=-35dB:d=0.12", "-f", "null", "-"])
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", out)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", out)]
    return [(s + e) / 2 for s, e in zip(starts, ends)]


def cut_points(text, shots, dur, mids):
    """Time (s) at which each shot ends, snapped to narration pauses."""
    cuts, pos = [], 0
    for k, shot in enumerate(shots):
        if k == len(shots) - 1:
            cuts.append(dur)
            break
        i = text.find(shot["upto"], pos)
        if i < 0:
            sys.exit(f"phrase not found: {shot['upto']!r} in {text!r}")
        pos = i + len(shot["upto"])
        est = dur * pos / len(text)
        near = [m for m in mids if abs(m - est) < 0.8 and (not cuts or m > cuts[-1] + 0.6)]
        cuts.append(min(near, key=lambda m: abs(m - est)) if near else est)
    return cuts


def drawtext(text, work, name, size, y, box="0x0B2545@0.72"):
    tf = work / f"{name}.txt"
    tf.write_text(text, encoding="utf-8")
    return (f"drawtext=fontfile='{FONT}':textfile='{tf}':fontsize={size}:fontcolor=white"
            f":line_spacing=16:box=1:boxcolor={box}:boxborderw=26:x=(w-text_w)/2:y={y}"
            f":alpha='if(lt(t,0.5),t/0.5,1)'")


def render_shot(shot, dur, idx, clips, work):
    src = clips / f"{shot['clip']}.mov"
    avail = duration(src) - shot.get("ss", 0)
    vf = []
    if dur > avail:  # gently slow the clip down rather than freezing it
        vf.append(f"setpts={min(dur / avail, 2.0):.3f}*PTS")
    vf += [f"scale={W}:{H}:force_original_aspect_ratio=increase", f"crop={W}:{H}",
           f"fps={FPS}", "eq=saturation=1.06:contrast=1.03"]
    if shot.get("endcard"):
        vf.append("drawbox=x=0:y=0:w=iw:h=ih:color=black@0.45:t=fill")
        vf.append(drawtext("Inonda.LTD\nΔωρεάν αξιολόγηση ακινήτου\n"
                           "+357 94 091 616 (Διευθυντής)\n+357 94 091 613 (Τεχνικός)\n"
                           "inonda2026@outlook.com · Λευκωσία & όλη η Κύπρος",
                           work, f"t{idx}", 54, "(h-text_h)/2-60", box="0x0B2545@0.0"))
    elif shot.get("title"):
        vf.append(drawtext(shot["title"], work, f"t{idx}", 50, 80))
    if shot.get("intro"):
        vf.append(drawtext("Inonda.LTD\nΣυντήρηση & επισκευές ακινήτων\nΛευκωσία & όλη η Κύπρος",
                           work, "t0", 64, "(h-text_h)/2"))
    frames = max(1, round(dur * FPS))
    out = work / f"shot_{idx:03}.mp4"
    run(["ffmpeg", "-y", "-loglevel", "error", "-ss", shot.get("ss", 0), "-i", src,
         "-an", "-vf", ",".join(vf), "-frames:v", frames, "-r", FPS,
         "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", out])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--clips", type=Path, required=True)
    ap.add_argument("--work", type=Path, default=AD / "build-stock")
    ap.add_argument("--out", type=Path, default=AD / "out/inonda-ad.mp4")
    ap.add_argument("--music", help="optional background music")
    args = ap.parse_args()
    work = args.work
    work.mkdir(parents=True, exist_ok=True)
    args.out.parent.mkdir(parents=True, exist_ok=True)

    segs = json.loads((AD / "segments.json").read_text(encoding="utf-8"))
    plan = json.loads((AD / "shots.json").read_text(encoding="utf-8"))
    assert len(segs) == len(plan) == 13

    srt, wavs, n = [], [], 1
    clips_out = [render_shot(INTRO, INTRO["dur"], 0, args.clips, work)]
    intro_wav = work / "intro.wav"
    run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i",
         "anullsrc=r=48000:cl=stereo", "-t", INTRO["dur"], intro_wav])
    wavs.append(intro_wav)
    t = INTRO["dur"]
    for s, (seg, shots) in enumerate(zip(segs, plan)):
        mp3 = AD / "voice" / f"{s + 1:02}.mp3"
        dur = duration(mp3)
        last = s == len(plan) - 1
        hold = TAIL if last else GAP
        wav = work / f"v{s:02}.wav"
        run(["ffmpeg", "-y", "-loglevel", "error", "-i", mp3, "-ac", "2", "-ar", "48000",
             "-af", f"apad=pad_dur={hold}", wav])
        wavs.append(wav)
        cuts = cut_points(seg["en"], shots, dur, pauses(mp3))
        prev = 0.0
        for k, (shot, end) in enumerate(zip(shots, cuts)):
            length = end - prev + (hold if k == len(shots) - 1 else 0)
            print(f"scene {s + 1} shot {k + 1}: {shot['clip']} {length:.2f}s")
            clips_out.append(render_shot(shot, length, len(clips_out), args.clips, work))
            prev = end
        # Greek subtitles, spread over the spoken part of the scene
        shown = seg["text"]
        for k, v in WRITTEN.items():
            shown = shown.replace(k, v)
        pieces = chunks(shown)
        total = sum(len(p) for p in pieces)
        st = t
        for p in pieces:
            d = dur * len(p) / total
            srt.append(f"{n}\n{ts(st)} --> {ts(st + d - 0.05)}\n{wrap(p)}\n")
            n += 1
            st += d
        t += dur + hold

    srt_path = args.out.with_name("subtitles.el.srt")
    srt_path.write_text("\n".join(srt), encoding="utf-8")
    (work / "clips.txt").write_text("".join(f"file '{c}'\n" for c in clips_out))
    (work / "voice.txt").write_text("".join(f"file '{w}'\n" for w in wavs))
    video, voice = work / "video.mp4", work / "voice.wav"
    run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
         "-i", work / "clips.txt", "-c", "copy", video])
    run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0",
         "-i", work / "voice.txt", voice])

    total = duration(voice)
    style = ("FontName=DejaVu Sans,FontSize=17,PrimaryColour=&H00FFFFFF,BorderStyle=3,"
             "OutlineColour=&H99000000,Outline=6,Shadow=0,MarginV=24")
    srt_esc = str(srt_path).replace(":", "\\:").replace("'", "\\'")
    vchain = (f"[0:v]subtitles='{srt_esc}':force_style='{style}',"
              f"fade=t=in:d=0.6,fade=t=out:st={total - 1.2:.2f}:d=1.2[vo]")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", video, "-i", voice]
    if args.music:
        cmd += ["-stream_loop", "-1", "-i", args.music]
        achain = (f"[2:a]atrim=0:{total:.2f},volume=0.10,afade=t=in:d=2,"
                  f"afade=t=out:st={total - 3:.2f}:d=3[m];[1:a][m]amix=inputs=2:duration=first:"
                  "normalize=0,loudnorm=I=-16:TP=-1.5[a]")
    else:
        achain = "[1:a]loudnorm=I=-16:TP=-1.5[a]"
    cmd += ["-filter_complex", f"{vchain};{achain}", "-map", "[vo]", "-map", "[a]",
            "-t", f"{total:.2f}", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", args.out]
    print("final render…")
    run(cmd)
    print(f"done: {args.out} ({total / 60:.2f} min, {len(clips_out)} shots)")


if __name__ == "__main__":
    main()
