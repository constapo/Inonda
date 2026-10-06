"""Procurement / bid-rigging red flags (OECD & OCP-style indicators)."""
import math
from collections import Counter, defaultdict
from . import Finding


def single_bidder(tenders):
    return [Finding("procurement.single_bidder", "medium",
            f"Tender {t['id']} had one bidder", {"tender": t["id"]})
            for t in tenders if len(t.get("bids", [])) == 1]


def just_below_threshold(tenders, threshold, margin=0.03):
    out = []
    for t in tenders:
        v = t.get("award_value")
        if v and threshold * (1 - margin) <= v < threshold:
            out.append(Finding("procurement.threshold_splitting", "medium",
                f"Award {v} sits just under review threshold {threshold}",
                {"tender": t["id"]}))
    return out


def identical_bids(tenders):
    out = []
    for t in tenders:
        vals = [b["amount"] for b in t.get("bids", [])]
        dup = [v for v, c in Counter(vals).items() if c > 1]
        if dup:
            out.append(Finding("procurement.identical_bids", "high",
                "Distinct bidders submitted identical amounts",
                {"tender": t["id"], "amounts": dup}))
    return out


def winner_concentration(tenders, share=0.5, min_n=10):
    by_buyer = defaultdict(Counter)
    for t in tenders:
        if t.get("winner"):
            by_buyer[t["buyer"]][t["winner"]] += 1
    out = []
    for buyer, c in by_buyer.items():
        n = sum(c.values())
        w, k = c.most_common(1)[0]
        if n >= min_n and k / n >= share:
            out.append(Finding("procurement.concentration", "high",
                f"{w} won {k}/{n} contracts from {buyer}",
                {"buyer": buyer, "winner": w}))
    return out


def benford(values, min_n=100, threshold=0.15):
    """First-digit Benford test using mean absolute deviation."""
    d = [int(str(abs(v)).lstrip("0.")[0]) for v in values if v]
    if len(d) < min_n:
        return []
    c = Counter(d)
    mad = sum(abs(c[i] / len(d) - math.log10(1 + 1 / i)) for i in range(1, 10)) / 9
    if mad > 0.015:
        return [Finding("procurement.benford", "low",
                "First-digit distribution deviates from Benford's law", {"mad": round(mad, 4), "n": len(d)})]
    return []


def run_all(tenders, threshold=None):
    f = single_bidder(tenders) + identical_bids(tenders) + winner_concentration(tenders)
    f += benford([t["award_value"] for t in tenders if t.get("award_value")])
    if threshold:
        f += just_below_threshold(tenders, threshold)
    return f
