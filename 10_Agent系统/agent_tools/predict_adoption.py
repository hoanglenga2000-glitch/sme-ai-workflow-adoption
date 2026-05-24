from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent_tools.common import ARTIFACTS, evidence_payload, load_bundle, time_call, write_jsonable


def predict_adoption(features: dict, stage: str = "champion") -> dict:
    try:
        bundle = load_bundle(stage)
    except FileNotFoundError:
        requested = "stage2" if stage == "champion" else stage
        artifact = ARTIFACTS / f"{requested}_best.joblib"
        return {
            "status": "unavailable",
            "stage": requested,
            "model": None,
            "prediction": None,
            "feature_count": 0,
            "message": f"Model artifact is not included in the public repository: {artifact.as_posix()}",
            "reproduce_command": "python 10_Agent系统/training/train_champion.py --force",
            "evidence_files": evidence_payload(
                [
                    "10_Agent系统/reports/model_comparison_report.md",
                    "10_Agent系统/reports/model_registry.json",
                    "08_Research_Grade_Deck/verified_metrics.json",
                ]
            ),
        }
    ordered = {name: features.get(name) for name in bundle["features"]}
    frame = pd.DataFrame([ordered])
    prediction = float(bundle["pipeline"].predict(frame)[0])
    return {
        "status": "ok",
        "stage": bundle.get("stage", stage),
        "model": bundle["metrics"]["model"],
        "prediction": round(prediction, 6),
        "feature_count": len(bundle["features"]),
        "evidence_files": evidence_payload(
            [
                "10_Agent系统/reports/model_comparison_report.md",
                "10_Agent系统/reports/model_registry.json",
                "08_Research_Grade_Deck/verified_metrics.json",
            ]
        ),
    }


if __name__ == "__main__":
    sample = {"geo": "DE", "year": 2025, "size_emp": "GE10", "nace_r2": "C26"}
    print(write_jsonable(time_call(predict_adoption, sample)))
