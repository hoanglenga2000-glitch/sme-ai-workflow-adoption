from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent_tools.common import AGENT_ROOT, evidence_payload, time_call, write_jsonable


RULES = {
    "stage 2": [
        "08_Research_Grade_Deck/verified_metrics.json",
        "outputs/reports/stage2_large_model_results.md",
    ],
    "stage 1": [
        "08_Research_Grade_Deck/verified_metrics.json",
        "outputs/reports/model_results.md",
    ],
    "manifest": [
        "data/raw/manifest.jsonl",
        "data/raw/manifest_stage2.jsonl",
    ],
    "source": [
        "docs/data_sources.md",
        "outputs/reports/stage2_source_profile.json",
    ],
}


def cite_source(claim: str) -> dict:
    lowered = claim.lower()
    evidence = []
    for key, files in RULES.items():
        if key in lowered:
            evidence.extend(files)
    if not evidence:
        evidence = []
        status = "无法确认"
    else:
        status = "ok"
    return {
        "status": status,
        "claim": claim,
        "evidence_files": evidence_payload(evidence),
    }


if __name__ == "__main__":
    print(write_jsonable(time_call(cite_source, "Stage 2 model quality and evidence files")))
