"""Weak stylometric signals for machine-generated text.

These are NOT reliable AI-text detectors (none exist). They flag statistical
oddities worth a human look, e.g. a batch of 'independent' reviews that all share
the same uniform sentence rhythm and stock phrases.
"""
import re
import statistics
from . import Finding

STOCK = [
    "as an ai", "i hope this message finds you well", "in conclusion",
    "it is important to note", "delve into", "tapestry", "i cannot assist",
    "regenerate response", "furthermore", "overall, this",
]


def _sentences(t):
    return [s for s in re.split(r"(?<=[.!?])\s+", t.strip()) if s]


def analyze_text(text: str):
    findings = []
    sents = _sentences(text)
    words = re.findall(r"\w+", text.lower())
    if len(words) < 40:
        return findings
    lens = [len(re.findall(r"\w+", s)) for s in sents]
    if len(lens) >= 5:
        cv = statistics.pstdev(lens) / (statistics.mean(lens) or 1)
        if cv < 0.25:
            findings.append(Finding("text.burstiness", "low",
                "Unusually uniform sentence length", {"cv": round(cv, 3)}))
    hits = [p for p in STOCK if p in text.lower()]
    if hits:
        sev = "high" if "as an ai" in hits or "regenerate response" in hits else "low"
        findings.append(Finding("text.stock_phrases", sev,
            "Contains boilerplate typical of LLM output", {"phrases": hits}))
    ttr = len(set(words)) / len(words)
    if ttr < 0.35:
        findings.append(Finding("text.repetition", "low",
            "Low lexical diversity", {"type_token_ratio": round(ttr, 3)}))
    return findings
