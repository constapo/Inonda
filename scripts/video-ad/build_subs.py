#!/usr/bin/env python3
"""Build Greek subtitles (SRT) and a readable script from docs/video-ad/segments.json.

Timings are estimated from word count until a real voice recording exists.
After recording, pass --durations with one number of seconds per scene
(e.g. measured with ffprobe) to re-time the subtitles to the real voice.
"""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SEGMENTS = ROOT / "docs/video-ad/segments.json"
OUT_DIR = ROOT / "docs/video-ad"
WORDS_PER_SEC = 2.2   # calm Greek advertising narration
GAP = 0.6             # pause between scenes, seconds
MAX_CHARS = 84        # two lines of ~42 chars

# Spoken forms that should appear in written form on screen.
WRITTEN = {
    "ενενήντα τέσσερα, μηδέν ενενήντα ένα, έξι δεκαέξι": "+357 94 091 616",
    "inonda2026 στο outlook.com": "inonda2026@outlook.com",
    "όλο το εικοσιτετράωρο, επτά ημέρες την εβδομάδα": "24/7",
}


def chunks(text):
    """Split narration into subtitle-sized pieces on sentence/clause boundaries."""
    parts = re.split(r"(?<=[.;:!?])\s+|(?<=,)\s+", text)
    out, cur = [], ""
    for p in parts:
        if cur and len(cur) + 1 + len(p) > MAX_CHARS:
            out.append(cur)
            cur = p
        else:
            cur = f"{cur} {p}".strip()
    if cur:
        out.append(cur)
    return out


def wrap(line):
    if len(line) <= 42:
        return line
    mid = len(line) // 2
    cut = line.rfind(" ", 0, mid + 8)
    return line[:cut] + "\n" + line[cut + 1:] if cut > 0 else line


def ts(sec):
    ms = int(round(sec * 1000))
    h, ms = divmod(ms, 3600000)
    m, ms = divmod(ms, 60000)
    s, ms = divmod(ms, 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--durations", nargs="*", type=float,
                    help="real spoken length of each scene in seconds")
    args = ap.parse_args()

    segs = json.loads(SEGMENTS.read_text(encoding="utf-8"))
    if args.durations and len(args.durations) != len(segs):
        ap.error(f"need {len(segs)} durations, got {len(args.durations)}")

    srt, md, t, idx = [], [], 0.0, 1
    md.append("# Inonda.LTD — διαφημιστικό βίντεο (σενάριο)\n")
    for i, seg in enumerate(segs):
        spoken = seg["text"]
        shown = spoken
        for k, v in WRITTEN.items():
            shown = shown.replace(k, v)
        words = len(spoken.split())
        dur = args.durations[i] if args.durations else words / WORDS_PER_SEC
        pieces = chunks(shown)
        total = sum(len(p) for p in pieces)
        start = t
        for p in pieces:
            d = dur * len(p) / total
            srt.append(f"{idx}\n{ts(t)} --> {ts(t + d - 0.05)}\n{wrap(p)}\n")
            idx += 1
            t += d
        md.append(f"## {seg['scene']}  ({ts(start)[:8]}–{ts(t)[:8]}, ~{dur:.0f}s)\n")
        md.append(f"**Αφήγηση:** {spoken}\n")
        md.append(f"**Εικόνα (prompt):** {seg['visual']}\n")
        t += GAP

    md.insert(1, f"Συνολική διάρκεια: ~{t / 60:.1f} λεπτά\n")
    (OUT_DIR / "subtitles.el.srt").write_text("\n".join(srt), encoding="utf-8")
    (OUT_DIR / "script.md").write_text("\n".join(md), encoding="utf-8")
    print(f"scenes={len(segs)} subtitles={idx - 1} total={t:.1f}s ({t / 60:.2f} min)")


if __name__ == "__main__":
    main()
