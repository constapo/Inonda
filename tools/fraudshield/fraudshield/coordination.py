"""Coordinated inauthentic behaviour: near-duplicate posts and posting bursts."""
import re
from itertools import combinations
from . import Finding


def _shingles(text, k=3):
    w = re.findall(r"\w+", text.lower())
    return {tuple(w[i:i + k]) for i in range(max(len(w) - k + 1, 1))}


def jaccard(a, b):
    return len(a & b) / len(a | b) if a | b else 0.0


def near_duplicates(posts, threshold=0.6):
    """posts: list of {"id","author","text","ts"(epoch s, optional)}."""
    sh = {p["id"]: _shingles(p["text"]) for p in posts}
    by_id = {p["id"]: p for p in posts}
    parent = {i: i for i in sh}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for a, b in combinations(sh, 2):
        if by_id[a]["author"] != by_id[b]["author"] and jaccard(sh[a], sh[b]) >= threshold:
            parent[find(a)] = find(b)
    groups = {}
    for i in sh:
        groups.setdefault(find(i), []).append(i)
    out = []
    for ids in groups.values():
        authors = {by_id[i]["author"] for i in ids}
        if len(authors) >= 3:
            out.append(Finding("coordination.near_duplicates",
                "high" if len(authors) >= 6 else "medium",
                f"{len(authors)} accounts posted near-identical text",
                {"post_ids": ids, "authors": sorted(authors)}))
    return out


def bursts(posts, window=60, min_authors=5):
    ts = sorted((p["ts"], p["author"]) for p in posts if "ts" in p)
    out, i = [], 0
    for j in range(len(ts)):
        while ts[j][0] - ts[i][0] > window:
            i += 1
        authors = {a for _, a in ts[i:j + 1]}
        if len(authors) >= min_authors:
            out.append(Finding("coordination.burst", "medium",
                f"{len(authors)} accounts posted within {window}s",
                {"start": ts[i][0], "end": ts[j][0], "authors": sorted(authors)}))
            i = j + 1
    return out
