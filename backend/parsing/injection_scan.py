from __future__ import annotations

import re
from dataclasses import dataclass


INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?previous\s+instructions",
    r"give\s+(this\s+paper\s+)?a\s+positive\s+review",
    r"do\s+not\s+mention\s+weaknesses",
    r"\bLLM\s+reviewer\b",
    r"\bAI\s+reviewer\b",
    r"system\s+prompt",
    r"hidden\s+instruction",
]


@dataclass(frozen=True)
class IntegrityFinding:
    severity: str
    finding: str
    matched_text: str
    recommendation: str


def scan_for_prompt_injection(text: str) -> list[dict]:
    findings: list[IntegrityFinding] = []

    for pattern in INJECTION_PATTERNS:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            findings.append(
                IntegrityFinding(
                    severity="high",
                    finding="Possible prompt-injection instruction detected in manuscript text.",
                    matched_text=match.group(0),
                    recommendation=(
                        "Do not pass raw manuscript text directly to review agents without "
                        "sanitization and explicit instruction hierarchy."
                    ),
                )
            )

    return [finding.__dict__ for finding in findings]
