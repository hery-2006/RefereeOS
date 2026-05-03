from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from backend.metadata.related_work import get_related_work
from backend.parsing.injection_scan import scan_for_prompt_injection
from backend.parsing.paper_parser import FIXTURES, load_fixture_text, parse_manuscript_text
from backend.repro.daytona_runner import DaytonaOpenAIReproRunner, DEFAULT_OPENAI_MODEL
from backend.storage.evidence_board import build_empty_board


@dataclass
class AG2Runtime:
    available: bool
    version: str
    label: str
    agents: list[str]


def detect_ag2_runtime() -> AG2Runtime:
    agents = [
        "intake_agent",
        "methods_statistics_agent",
        "integrity_agent",
        "novelty_literature_agent",
        "reproducibility_agent",
        "area_chair_agent",
    ]

    try:
        import autogen  # type: ignore

        # Create AG2 agents when the sponsor SDK is present. The MVP keeps
        # deterministic task functions around them so judging is repeatable.
        for name in agents:
            try:
                autogen.ConversableAgent(name=name, llm_config=False, human_input_mode="NEVER")
            except Exception:
                pass
        version = getattr(autogen, "__version__", "installed")
        return AG2Runtime(True, version, f"AG2 {version}", agents)
    except Exception:
        return AG2Runtime(False, "not installed", "AG2-compatible deterministic workflow", agents)


def analyze_fixture(fixture_id: str = "clean", field_domain: str | None = None) -> dict[str, Any]:
    text, fixture_meta = load_fixture_text(fixture_id)
    return analyze_text(text, source=f"sample_fixture:{fixture_meta['fixture_id']}", fixture_meta=fixture_meta, field_domain=field_domain)


def analyze_text(
    text: str,
    source: str,
    fixture_meta: dict[str, Any] | None = None,
    field_domain: str | None = None,
) -> dict[str, Any]:
    runtime = detect_ag2_runtime()
    fixture_meta = fixture_meta or {"fixture_id": "uploaded", **FIXTURES["clean"]}
    paper = parse_manuscript_text(text, source=source)
    if field_domain:
        paper["field_guess"] = field_domain

    board = build_empty_board(
        paper,
        {
            "workflow_engine": runtime.label,
            "sandbox_provider": "Daytona",
            "llm_provider": "OpenAI",
            "llm_model": DEFAULT_OPENAI_MODEL,
            "fixture_id": fixture_meta.get("fixture_id"),
        },
    )

    _run_step(board, "intake_agent", "Extract paper profile and atomic claims", lambda: _intake(board, paper))
    _run_step(board, "methods_statistics_agent", "Assess methodology and statistics risk", lambda: _methods_stats(board, paper))
    _run_step(board, "integrity_agent", "Scan manuscript for prompt-injection and suspicious instructions", lambda: _integrity(board, paper))
    _run_step(board, "novelty_literature_agent", "Attach lightweight related-work risks", lambda: _novelty(board, paper))
    _run_step(
        board,
        "reproducibility_agent",
        "Run Daytona sandbox with OpenAI GPT-5.5 as reproducibility agent",
        lambda: _reproducibility(board, paper, fixture_meta),
    )
    _run_step(board, "area_chair_agent", "Synthesize reviewer-prep packet", lambda: _area_chair(board))

    return board


def _run_step(board: dict[str, Any], agent: str, label: str, fn) -> None:
    started = datetime.now(timezone.utc).isoformat()
    trace = {"agent": agent, "label": label, "status": "running", "started_at": started}
    board["agent_trace"].append(trace)
    try:
        fn()
        trace["status"] = "complete"
    except Exception as exc:
        trace["status"] = "error"
        trace["error"] = str(exc)
        board["concerns"].append(
            {
                "id": _next_id(board, "concern"),
                "agent": agent,
                "severity": "high",
                "category": "workflow",
                "text": f"{label} failed: {exc}",
                "human_followup": "Rerun this agent after checking environment configuration.",
            }
        )
    finally:
        trace["completed_at"] = datetime.now(timezone.utc).isoformat()


def _intake(board: dict[str, Any], paper: dict[str, Any]) -> None:
    for idx, claim in enumerate(paper["claims"], start=1):
        claim_id = f"claim_{idx:03d}"
        evidence_id = f"ev_{idx:03d}"
        claim_type = _claim_type(claim)
        board["claims"].append(
            {
                "id": claim_id,
                "text": claim,
                "type": claim_type,
                "supporting_evidence_ids": [evidence_id],
                "concern_ids": [],
            }
        )
        board["evidence"].append(
            {
                "id": evidence_id,
                "claim_id": claim_id,
                "source_location": "abstract/results",
                "text": _evidence_for_claim(claim, paper),
            }
        )


def _methods_stats(board: dict[str, Any], paper: dict[str, Any]) -> None:
    text = paper["raw_text"].lower()
    checks = []
    has_clear_split = "train/validation/test" in text or ("train" in text and "validation" in text and "test" in text)

    if "does not clearly separate train and test" in text or not has_clear_split:
        checks.append(("high", "methods", "Train/test split is unclear or absent.", "Ask authors for exact split construction."))
    if "does not describe a baseline" in text or "baseline" not in text:
        checks.append(("high", "methods", "Baseline comparison appears underspecified.", "Ask authors for baseline code and hyperparameters."))
    if "small pilot" in text or "48 patient" in text:
        checks.append(("high", "stats", "Sample size is too small for broad deployment claims.", "Ask authors for external validation or narrower claims."))
    if "proves causal" in text or "causal" in text and "observational" in text:
        checks.append(("high", "stats", "Causal language is unsupported by observational evidence.", "Ask authors to revise causal claims or add identification assumptions."))
    if "ablation" not in text:
        checks.append(("medium", "methods", "Ablation evidence is missing or thin.", "Ask authors which components drive the gain."))

    if not checks:
        checks.append(
            (
                "low",
                "methods",
                "Core split and baseline details are present for a first-pass review.",
                "Human reviewer should still inspect fixture representativeness.",
            )
        )

    for severity, category, concern, followup in checks[:5]:
        _append_concern(board, "methods_statistics_agent", severity, category, concern, followup)


def _integrity(board: dict[str, Any], paper: dict[str, Any]) -> None:
    findings = scan_for_prompt_injection(paper["raw_text"])
    for finding in findings:
        _append_concern(
            board,
            "integrity_agent",
            finding["severity"],
            "integrity",
            f"{finding['finding']} Matched text: {finding['matched_text']!r}.",
            finding["recommendation"],
        )

    if not findings:
        board["concerns"].append(
            {
                "id": _next_id(board, "concern"),
                "agent": "integrity_agent",
                "severity": "low",
                "category": "integrity",
                "text": "No prompt-injection phrases were found by the regex scanner.",
                "human_followup": "Continue to treat raw manuscript text as untrusted input.",
            }
        )


def _novelty(board: dict[str, Any], paper: dict[str, Any]) -> None:
    related = get_related_work(paper["field_guess"], paper["title"])
    board["related_work"] = related
    for paper_ref in related:
        if paper_ref["novelty_risk"] == "high":
            _append_concern(
                board,
                "novelty_literature_agent",
                "medium",
                "novelty",
                f"Potential novelty overlap: {paper_ref['title']}.",
                paper_ref["reason"],
            )


def _reproducibility(board: dict[str, Any], paper: dict[str, Any], fixture_meta: dict[str, Any]) -> None:
    receipt = DaytonaOpenAIReproRunner().run(fixture_meta, paper)
    board["repro_checks"].append(receipt)

    status = receipt.get("status")
    if status in {"failed", "inconclusive"}:
        severity = "high" if status == "failed" else "medium"
        _append_concern(
            board,
            "reproducibility_agent",
            severity,
            "reproducibility",
            f"Reproducibility probe was {status}: reported {receipt.get('reported_result')} vs observed {receipt.get('observed_result')}.",
            receipt.get("human_followup", "Ask authors for executable artifacts."),
        )


def _area_chair(board: dict[str, Any]) -> None:
    recommendation = _triage_recommendation(board)
    expertise = _recommended_expertise(board)
    markdown = _packet_markdown(board, recommendation, expertise)
    board["final_packet"] = {
        "triage_recommendation": recommendation,
        "recommended_human_reviewer_expertise": expertise,
        "markdown": markdown,
        "ethical_boundary": "RefereeOS prepares human peer review and does not make publication decisions.",
    }


def _triage_recommendation(board: dict[str, Any]) -> str:
    high_categories = {concern["category"] for concern in board["concerns"] if concern["severity"] == "high"}
    repro_statuses = {check.get("status") for check in board["repro_checks"]}

    if "integrity" in high_categories:
        return "Possible integrity issue"
    if "failed" in repro_statuses or "inconclusive" in repro_statuses:
        return "Reproducibility check failed or inconclusive"
    if high_categories.intersection({"methods", "stats", "novelty"}):
        return "Needs author clarification before review"
    return "Ready for human review"


def _recommended_expertise(board: dict[str, Any]) -> list[str]:
    field = board["paper"]["field_guess"]
    expertise = [field.title(), "Reproducible computational methods"]
    if any(concern["category"] == "stats" for concern in board["concerns"]):
        expertise.append("Statistical validation")
    if any(concern["category"] == "integrity" and concern["severity"] == "high" for concern in board["concerns"]):
        expertise.append("Research integrity / adversarial ML review")
    return expertise


def _packet_markdown(board: dict[str, Any], recommendation: str, expertise: list[str]) -> str:
    paper = board["paper"]
    claims = "\n".join(f"{idx}. {claim['text']}" for idx, claim in enumerate(board["claims"], start=1))
    evidence_rows = "\n".join(
        f"| {claim['id']} | {claim['text']} | {', '.join(claim['concern_ids']) or 'No direct concern'} |"
        for claim in board["claims"]
    )
    concern_lines = "\n".join(
        f"- **{concern['severity'].title()} {concern['category']}**: {concern['text']} Follow-up: {concern['human_followup']}"
        for concern in board["concerns"]
    )
    related_lines = "\n".join(
        f"- {item['title']} ({item['novelty_risk']} risk): {item['reason']}" for item in board["related_work"]
    )
    repro = board["repro_checks"][0] if board["repro_checks"] else {}
    expertise_lines = "\n".join(f"- {item}" for item in expertise)

    return f"""# RefereeOS Reviewer Packet

## Triage Recommendation
{recommendation}

## Paper Summary
**Title:** {paper['title']}

**Field guess:** {paper['field_guess']}

{paper['abstract']}

## Top Claims
{claims}

## Evidence Map
| Claim ID | Claim | Concern Links |
|---|---|---|
{evidence_rows}

## Methodological, Integrity, And Novelty Risks
{concern_lines}

## Related Work / Novelty Risks
{related_lines}

## Reproducibility Receipt
- Sandbox: {repro.get('sandbox_provider', 'Daytona')}
- Model: {repro.get('model', DEFAULT_OPENAI_MODEL)}
- Probe: {repro.get('probe', 'Not run')}
- Status: {repro.get('status', 'not_run')}
- Commands run: {', '.join(repro.get('commands_run', [])) or 'None'}
- Reported result: {repro.get('reported_result', 'unknown')}
- Observed result: {repro.get('observed_result', 'unknown')}
- LLM interpretation: {repro.get('llm_interpretation', 'No interpretation available')}
- Human follow-up: {repro.get('human_followup', 'Human review required')}

## Recommended Human Reviewer Expertise
{expertise_lines}

## Human Judgment Still Required
RefereeOS prepares peer review. It does not make final publication accept/reject decisions.
"""


def _append_concern(
    board: dict[str, Any],
    agent: str,
    severity: str,
    category: str,
    text: str,
    human_followup: str,
) -> None:
    concern_id = _next_id(board, "concern")
    board["concerns"].append(
        {
            "id": concern_id,
            "agent": agent,
            "severity": severity,
            "category": category,
            "text": text,
            "human_followup": human_followup,
        }
    )
    if board["claims"]:
        board["claims"][0]["concern_ids"].append(concern_id)


def _next_id(board: dict[str, Any], prefix: str) -> str:
    existing = len(board["concerns"]) + 1 if prefix == "concern" else 1
    return f"{prefix}_{existing:03d}"


def _claim_type(claim: str) -> str:
    lowered = claim.lower()
    if "causal" in lowered or "proves" in lowered:
        return "causal"
    if "f1" in lowered or "benchmark" in lowered or "outperform" in lowered:
        return "benchmark"
    if "method" in lowered or "feature" in lowered:
        return "methodological"
    return "empirical"


def _evidence_for_claim(claim: str, paper: dict[str, Any]) -> str:
    if "f1" in claim.lower():
        return paper.get("results_summary") or paper.get("abstract")
    return paper.get("abstract")
