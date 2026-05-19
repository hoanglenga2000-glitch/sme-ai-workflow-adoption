from __future__ import annotations

import json
import time
from pathlib import Path

import joblib
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.inspection import permutation_importance


AGENT_ROOT = Path(__file__).resolve().parents[1]
ROOT = AGENT_ROOT.parent
REPORTS = AGENT_ROOT / "reports"
ARTIFACTS = AGENT_ROOT / "training" / "artifacts"


def load_bundle(stage: str = "stage2") -> dict:
    if stage == "champion":
        champion = ARTIFACTS / "champion_model.joblib"
        if champion.exists():
            return joblib.load(champion)
        stage = "stage2"
    return joblib.load(ARTIFACTS / f"{stage}_best.joblib")


def load_stage_dataframe(stage: str = "stage2") -> pd.DataFrame:
    if stage == "stage1":
        path = ROOT / "data" / "processed" / "eurostat_ai_panel.csv"
    else:
        path = ROOT / "data" / "processed" / "stage2_industry_panel.csv"
    return pd.read_csv(path)


def evidence_payload(files: list[str]) -> list[str]:
    return [str(Path(f).as_posix()) for f in files]


def write_jsonable(payload: dict) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2)


def time_call(fn, *args, **kwargs):
    start = time.perf_counter()
    result = fn(*args, **kwargs)
    elapsed = time.perf_counter() - start
    if isinstance(result, dict):
        result["latency_seconds"] = round(elapsed, 4)
    return result


def compute_local_explanations(stage: str, row: pd.DataFrame) -> list[dict]:
    bundle = load_bundle(stage)
    feature_names = bundle["features"]
    train_df = load_stage_dataframe(stage)
    target = bundle["target"]
    pipe = bundle["pipeline"]
    data = train_df[feature_names + [target]].dropna(subset=[target]).copy()
    perm = permutation_importance(pipe, data[feature_names], data[target], n_repeats=5, random_state=42, n_jobs=1)
    table = pd.DataFrame({"feature": feature_names, "importance": perm.importances_mean}).sort_values("importance", ascending=False).head(10)
    values = row.iloc[0].to_dict()
    output = []
    for _, item in table.iterrows():
        output.append(
            {
                "feature": item["feature"],
                "importance": round(float(item["importance"]), 6),
                "input_value": values.get(item["feature"]),
            }
        )
    return output


def save_chart(df: pd.DataFrame, x: str, y: str, title: str, output_name: str) -> str:
    output_path = AGENT_ROOT / "reports" / output_name
    plt.figure(figsize=(8, 4.5))
    plt.plot(df[x], df[y], marker="o")
    plt.title(title)
    plt.xlabel(x)
    plt.ylabel(y)
    plt.tight_layout()
    plt.savefig(output_path, dpi=160)
    plt.close()
    return str(output_path)
