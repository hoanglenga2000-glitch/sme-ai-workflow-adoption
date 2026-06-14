from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import pandas as pd

from training.common import AGENT_ROOT, STAGE_CONFIGS, feature_columns, load_stage_frame, write_json


def main() -> None:
    try:
        import torch
    except Exception as exc:
        payload = {
            "status": "skipped",
            "reason": "torch not installed",
            "detail": str(exc),
            "recommended_environment": "A10 server with CUDA-enabled PyTorch",
        }
        write_json(AGENT_ROOT / "reports" / "ft_transformer_status.json", payload)
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    device = "cuda" if torch.cuda.is_available() else "cpu"
    stage = "stage2"
    config, df = load_stage_frame(stage)
    features = feature_columns(df, config)
    numeric = [col for col in features if pd.api.types.is_numeric_dtype(df[col])]
    categorical = [col for col in features if col not in numeric]
    payload = {
        "status": "prepared_only",
        "device": device,
        "stage": stage,
        "rows": int(len(df)),
        "numeric_features": len(numeric),
        "categorical_features": len(categorical),
        "note": "This script is a GPU readiness hook for deep tabular experiments on the A10 server. The primary production path remains tree-based models for accuracy and cost control.",
    }
    write_json(AGENT_ROOT / "reports" / "ft_transformer_status.json", payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
