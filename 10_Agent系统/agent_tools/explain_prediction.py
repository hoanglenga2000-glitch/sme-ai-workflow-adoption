from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent_tools.common import compute_local_explanations, evidence_payload, load_bundle, time_call, write_jsonable


def explain_prediction(features: dict, stage: str = "stage2") -> dict:
    bundle = load_bundle(stage)
    ordered = {name: features.get(name) for name in bundle["features"]}
    row = pd.DataFrame([ordered])
    prediction = float(bundle["pipeline"].predict(row)[0])
    explanations = compute_local_explanations(stage, row)
    return {
        "status": "ok",
        "stage": stage,
        "prediction": round(prediction, 6),
        "top_explanations": explanations,
        "evidence_files": evidence_payload(
            [
                "10_Agent系统/reports/model_comparison_report.md",
                "outputs/reports/stage2_large_model_results.md",
            ]
        ),
    }


if __name__ == "__main__":
    sample = {"geo": "DE", "year": 2025, "size_emp": "GE10", "nace_r2": "C26"}
    print(write_jsonable(time_call(explain_prediction, sample)))
