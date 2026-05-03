from __future__ import annotations


RELATED_WORK_FIXTURES = {
    "computational biology": [
        {
            "title": "Compact gene panels for cell-state annotation",
            "source": "demo Semantic Scholar fixture",
            "novelty_risk": "medium",
            "reason": "Overlaps with the same feature-pruning benchmark theme.",
        },
        {
            "title": "Reproducible evaluation in computational biology",
            "source": "demo Semantic Scholar fixture",
            "novelty_risk": "low",
            "reason": "Relevant evaluation guidance, not a direct method overlap.",
        },
        {
            "title": "Sparse classifiers for single-cell RNA-seq cohorts",
            "source": "demo Semantic Scholar fixture",
            "novelty_risk": "medium",
            "reason": "Potential prior art for the sparse classifier claim.",
        },
    ],
    "clinical/public health": [
        {
            "title": "Evaluation leakage in medical machine learning",
            "source": "demo OpenAlex fixture",
            "novelty_risk": "high",
            "reason": "Directly relevant to unclear train/test split concerns.",
        },
        {
            "title": "Clinical prediction under dataset shift",
            "source": "demo OpenAlex fixture",
            "novelty_risk": "medium",
            "reason": "Challenges broad deployability across hospitals.",
        },
        {
            "title": "Limits of small observational health datasets",
            "source": "demo OpenAlex fixture",
            "novelty_risk": "high",
            "reason": "Contradicts broad causal claims from a pilot sample.",
        },
    ],
}


def get_related_work(field_guess: str, title: str) -> list[dict]:
    for field, papers in RELATED_WORK_FIXTURES.items():
        if field in field_guess:
            return papers

    return [
        {
            "title": f"Prior work potentially related to {title[:70]}",
            "source": "demo metadata fixture",
            "novelty_risk": "medium",
            "reason": "Use live Semantic Scholar/OpenAlex lookup as a stretch path.",
        }
    ]
