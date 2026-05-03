from __future__ import annotations

import re
from pathlib import Path
from typing import BinaryIO


FIXTURE_DIR = Path(__file__).resolve().parents[1] / "fixtures"


FIXTURES = {
    "clean": {
        "label": "Clean computational paper",
        "paper_path": FIXTURE_DIR / "clean_paper.md",
        "results_path": FIXTURE_DIR / "results_clean.csv",
        "reported_result": 0.87,
        "expected_status": "passed",
    },
    "suspicious": {
        "label": "Suspicious/adversarial paper",
        "paper_path": FIXTURE_DIR / "suspicious_paper.md",
        "results_path": FIXTURE_DIR / "results_suspicious.csv",
        "reported_result": 0.91,
        "expected_status": "failed",
    },
}


def list_fixtures() -> list[dict]:
    return [
        {"id": fixture_id, "label": data["label"], "reported_result": data["reported_result"]}
        for fixture_id, data in FIXTURES.items()
    ]


def load_fixture_text(fixture_id: str) -> tuple[str, dict]:
    if fixture_id not in FIXTURES:
        fixture_id = "clean"

    fixture = FIXTURES[fixture_id]
    text = Path(fixture["paper_path"]).read_text(encoding="utf-8")
    return text, {"fixture_id": fixture_id, **fixture}


def extract_pdf_text(file: BinaryIO) -> str:
    try:
        import fitz  # PyMuPDF
    except Exception as exc:  # pragma: no cover - depends on optional runtime package
        raise RuntimeError("PyMuPDF is not installed; use a fixture or install requirements.txt.") from exc

    blob = file.read()
    with fitz.open(stream=blob, filetype="pdf") as doc:
        return "\n".join(page.get_text("text") for page in doc)


def parse_manuscript_text(text: str, source: str) -> dict:
    normalized = text.replace("\r\n", "\n").strip()
    title = _extract_title(normalized)
    abstract = _extract_section(normalized, "Abstract")
    methods = _extract_section(normalized, "Methods")
    results = _extract_section(normalized, "Results")
    data_code = _extract_section(normalized, "Data And Code")
    references = _extract_section(normalized, "References")
    claims = _extract_claims(normalized)

    return {
        "title": title,
        "abstract": abstract,
        "field_guess": _guess_field(normalized),
        "source": source,
        "claims": claims,
        "methods_summary": _squash(methods, 420),
        "results_summary": _squash(results, 420),
        "datasets_or_code_mentions": _extract_artifacts(data_code),
        "citations_or_related_work": _extract_references(references),
        "raw_text": normalized,
    }


def _extract_title(text: str) -> str:
    first_heading = re.search(r"^#\s+(.+)$", text, flags=re.MULTILINE)
    if first_heading:
        return first_heading.group(1).strip()

    first_non_empty = next((line.strip() for line in text.splitlines() if line.strip()), "Untitled manuscript")
    return first_non_empty[:160]


def _extract_section(text: str, heading: str) -> str:
    pattern = rf"^##\s+{re.escape(heading)}\s*$([\s\S]*?)(?=^##\s+|\Z)"
    match = re.search(pattern, text, flags=re.MULTILINE | re.IGNORECASE)
    return match.group(1).strip() if match else ""


def _extract_claims(text: str) -> list[str]:
    section = _extract_section(text, "Main Claims")
    claims = [line.strip("- ").strip() for line in section.splitlines() if line.strip().startswith("-")]
    if claims:
        return claims[:5]

    sentences = re.split(r"(?<=[.!?])\s+", _extract_section(text, "Abstract"))
    return [sentence.strip() for sentence in sentences if len(sentence.strip()) > 20][:5]


def _extract_artifacts(section: str) -> list[str]:
    artifacts = []
    for line in section.splitlines():
        if ":" in line:
            artifacts.append(line.strip())
    return artifacts


def _extract_references(section: str) -> list[str]:
    refs = [line.strip("- ").strip() for line in section.splitlines() if line.strip().startswith("-")]
    return refs[:5]


def _guess_field(text: str) -> str:
    lowered = text.lower()
    if "single-cell" in lowered or "gene" in lowered:
        return "computational biology"
    if "clinical" in lowered or "patient" in lowered:
        return "clinical/public health"
    if "benchmark" in lowered or "classifier" in lowered:
        return "machine learning systems"
    return "computational science"


def _squash(text: str, limit: int) -> str:
    compact = re.sub(r"\s+", " ", text).strip()
    return compact[: limit - 1] + "..." if len(compact) > limit else compact
