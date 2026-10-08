#!/usr/bin/env python3
"""Assemble the Inonda.LTD ad: stills with slow motion + title cards + your
English narration + burned-in Greek subtitles (+ optional background music).

Run on your own Linux machine (needs ffmpeg with libass, python3, internet
for the first image download):

  # Option A — one recording of the whole script:
  python3 scripts/video-ad/assemble.py --voice ~/narration.m4a
  # Option B — one recording per scene (exact subtitle sync):
  #   put 01.m4a ... 13.m4a in docs/video-ad/voice/ and run with no --voice
  python3 scripts/video-ad/assemble.py --music ~/music.mp3   # music optional

Output: docs/video-ad/out/inonda-ad.mp4 (+ subtitles.el.srt next to it).
"""
import argparse
import json
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
AD = ROOT / "docs/video-ad"
FPS = 25
W, H = 1920, 1080
FADE = 0.35        # dip-to-black between shots, seconds
SCENE_GAP = 0.6    # silence between per-scene recordings
TAIL = 3.0         # hold end card after narration


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        sys.exit(f"command failed: {' '.join(map(str, cmd))}\n{r.stderr[-2000:]}")
    return r.stdout


def duration(path):
    return float(run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                      "-of", "default=nw=1:nk=1", str(path)]).strip())


def font():
    for q in ("DejaVu Sans:bold", "Noto Sans:bold", "Liberation Sans:bold"):
        f = subprocess.run(["fc-match", "-f", "%{file}", q], capture_output=True, text=True).stdout
        if f and Path(f).exists():
            return f
    sys.exit("no Greek-capable font found: install fonts-dejavu-core")


def fetch_images(scenes, img_dir):
    img_dir.mkdir(parents=True, exist_ok=True)
    for shot in (s for sc in scenes for s in sc):
        dst = img_dir / f"{shot['id']}{Path(shot['src']).suffix}"
        shot["file"] = dst
        if dst.exists():
            continue
        if shot["src"].startswith("http"):
            print(f"downloading {shot['id']}")
            with urllib.request.urlopen(shot["src"], timeout=120) as r:
                dst.write_bytes(r.read())
        else:
            shutil.copy(AD / shot["src"], dst)


def narration(args, work, n_scenes):
    """Return (wav path, per-scene spoken durations, gap after each scene)."""
    out = work / "narration.wav"
    if args.voice:
        run(["ffmpeg", "-y", "-loglevel", "error", "-i", args.voice, "-ac", "1", "-ar", "48000", out])
        total = duration(out)
        segs = json.loads((AD / "segments.json").read_text(encoding="utf-8"))
        words = [len(s.get("en", s["text"]).split()) for s in segs]
        return out, [total * w / sum(words) for w in words], 0.0
    files = []
    for i in range(1, n_scenes + 1):
        hits = sorted((AD / "voice").glob(f"{i:02}.*"))
        if not hits:
            sys.exit(f"missing docs/video-ad/voice/{i:02}.* (or pass --voice FILE)")
        files.append(hits[0])
    durs, parts = [], []
    for i, f in enumerate(files):
        wav = work / f"v{i:02}.wav"
        run(["ffmpeg", "-y", "-loglevel", "error", "-i", f, "-ac", "1", "-ar", "48000",
             "-af", f"apad=pad_dur={SCENE_GAP}", wav])
        durs.append(duration(wav) - SCENE_GAP)
        parts.append(wav)
    lst = work / "voice.txt"
    lst.write_text("".join(f"file '{p}'\n" for p in parts))
    run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, out])
    return out, durs, SCENE_GAP


def render_shot(shot, dur, idx, fontfile, work):
    frames = int(round(dur * FPS))
    # alternate gentle zoom-in, zoom-out and lateral pan for variety
    mode = idx % 3
    if mode == 0:
        z, x, y = "1+0.10*on/{f}", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    elif mode == 1:
        z, x, y = "1.10-0.10*on/{f}", "iw/2-(iw/zoom/2)", "ih/2-(ih/zoom/2)"
    else:
        z, x, y = "1.08", "(iw-iw/zoom)*on/{f}", "ih/2-(ih/zoom/2)"
    z, x = z.format(f=frames), x.format(f=frames)
    vf = [f"scale={W*2}:{H*2}:force_original_aspect_ratio=increase,crop={W*2}:{H*2}",
          f"zoompan=z='{z}':x='{x}':y='{y}':d={frames}:s={W}x{H}:fps={FPS}"]
    if shot.get("title"):
        tf = work / f"t_{shot['id']}.txt"
        tf.write_text(shot["title"], encoding="utf-8")
        end = shot["id"].startswith("13")
        vf.append(
            f"drawtext=fontfile='{fontfile}':textfile='{tf}':fontsize={46 if end else 52}"
            f":fontcolor=white:line_spacing=18:box=1:boxcolor=0x0B2545@0.72:boxborderw=28"
            f":x=(w-text_w)/2:y={'(h-text_h)/2' if end else '90'}"
            f":alpha='if(lt(t,0.6),t/0.6,1)'")
    vf.append(f"fade=t=in:st=0:d={FADE},fade=t=out:st={dur - FADE:.3f}:d={FADE}")
    out = work / f"shot_{idx:02}.mp4"
    run(["ffmpeg", "-y", "-loglevel", "error", "-loop", "1", "-i", shot["file"],
         "-vf", ",".join(vf), "-t", f"{dur:.3f}", "-r", str(FPS),
         "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-pix_fmt", "yuv420p", out])
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--voice", help="one audio file with the whole narration")
    ap.add_argument("--music", help="optional background music file")
    ap.add_argument("--music-volume", type=float, default=0.12)
    ap.add_argument("--work", type=Path, default=AD / "build")
    ap.add_argument("--out", type=Path, default=AD / "out/inonda-ad.mp4")
    args = ap.parse_args()
    for tool in ("ffmpeg", "ffprobe", "fc-match"):
        if not shutil.which(tool):
            sys.exit(f"{tool} not found: sudo apt install ffmpeg fontconfig")

    work = args.work
    work.mkdir(parents=True, exist_ok=True)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    scenes = json.loads((AD / "images.json").read_text(encoding="utf-8"))
    fetch_images(scenes, work / "img")

    voice, spoken, gap = narration(args, work, len(scenes))
    srt = args.out.with_name("subtitles.el.srt")
    run([sys.executable, ROOT / "scripts/video-ad/build_subs.py", "--gap", str(gap),
         "--out", srt, "--durations", *[f"{d:.3f}" for d in spoken]])

    fontfile = font()
    clips, idx = [], 0
    for s, shots in enumerate(scenes):
        scene_len = spoken[s] + gap + (TAIL if s == len(scenes) - 1 else 0)
        for shot in shots:
            print(f"rendering shot {shot['id']}")
            clips.append(render_shot(shot, scene_len / len(shots), idx, fontfile, work))
            idx += 1
    lst = work / "clips.txt"
    lst.write_text("".join(f"file '{c}'\n" for c in clips))
    video = work / "video.mp4"
    run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", video])

    total = duration(video)
    style = ("FontName=DejaVu Sans,FontSize=17,PrimaryColour=&H00FFFFFF,BorderStyle=3,"
             "OutlineColour=&H90000000,Outline=6,Shadow=0,MarginV=22")
    srt_esc = str(srt).replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-i", video, "-i", voice]
    afilter = f"[1:a]apad,atrim=0:{total:.3f},volume=1.0[v]"
    if args.music:
        cmd += ["-stream_loop", "-1", "-i", args.music]
        afilter += (f";[2:a]atrim=0:{total:.3f},volume={args.music_volume},"
                    f"afade=t=in:d=2,afade=t=out:st={total - 3:.3f}:d=3[m];"
                    "[v][m]amix=inputs=2:duration=first:normalize=0[a]")
    else:
        afilter = afilter.replace("[v]", "[a]")
    cmd += ["-filter_complex", f"[0:v]subtitles='{srt_esc}':force_style='{style}'[vo];{afilter}",
            "-map", "[vo]", "-map", "[a]", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
            "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", args.out]
    print("final render (burning Greek subtitles)…")
    run(cmd)
    print(f"done: {args.out}  ({total / 60:.2f} min)")


if __name__ == "__main__":
    main()
