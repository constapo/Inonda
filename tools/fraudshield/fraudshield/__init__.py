"""FraudShield: heuristic detectors for AI-enabled fraud and corruption signals.

Every detector returns a list of Finding objects. Findings are leads for a human
investigator, never verdicts.
"""
from dataclasses import dataclass, field


@dataclass
class Finding:
    detector: str
    severity: str  # "low" | "medium" | "high"
    summary: str
    evidence: dict = field(default_factory=dict)
