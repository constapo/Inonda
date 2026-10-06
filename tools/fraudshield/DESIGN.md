# FraudShield design

Goal: help investigators spot **AI-enabled fraud and corruption** early: synthetic
documents, deepfake-backed claims, bot-driven manipulation, and rigged procurement.

## Threat model
| Threat | Example | Signal used | Module |
|---|---|---|---|
| Fake review/comment campaigns | LLM-written astroturf from many accounts | near-duplicate clusters across authors, posting bursts | `coordination` |
| Synthetic text in filings/bids | Mass-generated "independent" letters | stylometry, LLM boilerplate | `text` |
| Bid rigging / capture | identical bids, one winner, just-under-threshold awards | OECD-style red flags, Benford | `procurement` |
| Forged or swapped documents | altered contract, AI-regenerated "original" | hash manifest, later C2PA | `provenance` |

## Principles
1. Findings are **leads, not verdicts**. Each carries evidence and a severity; humans decide.
2. No single detector is trusted. AI-text detection in particular is unreliable and is only a weak signal.
3. Prefer **provenance (prove authentic)** over **detection (guess fake)** wherever possible.
4. Privacy: process only data the investigator is entitled to; log every run.

## Roadmap
- v0 (this prototype): stdlib heuristics, CLI, JSON output.
- v1: ingest open data (OCDS procurement feeds, public registries); graph of owners/bidders to find shared directors/addresses.
- v2: C2PA verification for images/video; deepfake classifiers as pluggable, calibrated models.
- v3: case-management UI, analyst feedback loop to tune thresholds, evaluation on labelled cases.

## Known limits
Heuristics have false positives (a legitimate form letter looks like a bot campaign; small markets look concentrated). Thresholds are placeholders and need calibration on real labelled data before any operational use.
