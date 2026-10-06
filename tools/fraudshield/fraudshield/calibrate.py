"""Calibrate detector thresholds against labelled cases.

Cases: [{"input": ..., "label": 0/1}]. A detector is a callable (input, **params) -> bool.
"""
from itertools import product


def metrics(preds, labels):
    tp = sum(p and l for p, l in zip(preds, labels))
    fp = sum(p and not l for p, l in zip(preds, labels))
    fn = sum((not p) and l for p, l in zip(preds, labels))
    prec = tp / (tp + fp) if tp + fp else 0.0
    rec = tp / (tp + fn) if tp + fn else 0.0
    f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
    return {"precision": prec, "recall": rec, "f1": f1, "tp": tp, "fp": fp, "fn": fn}


def sweep(detector, cases, grid, min_precision=0.9):
    """Return the param set with best recall subject to precision >= min_precision
    (falls back to best F1). grid: {"param": [values]}."""
    labels = [bool(c["label"]) for c in cases]
    best = None
    names = list(grid)
    for combo in product(*grid.values()):
        params = dict(zip(names, combo))
        m = metrics([detector(c["input"], **params) for c in cases], labels)
        key = (m["precision"] >= min_precision, m["recall"] if m["precision"] >= min_precision else m["f1"])
        if best is None or key > best[0]:
            best = (key, params, m)
    return {"params": best[1], "metrics": best[2]}
