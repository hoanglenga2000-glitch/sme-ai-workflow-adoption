from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from training.common import (
    AGENT_ROOT,
    REPORTS,
    STAGE_CONFIGS,
    evaluate_group_kfold,
    evaluate_industry_holdout,
    evaluate_time_holdout,
    feature_columns,
    load_stage_frame,
    model_factories,
    save_bundle,
    top_feature_importance,
    write_json,
)


def run_stage(stage: str) -> dict:
    config, df = load_stage_frame(stage)
    features = feature_columns(df, config)
    factories = model_factories()
    if config.preferred_models:
        factories = {name: factory for name, factory in factories.items() if name in config.preferred_models}
    stage_results: dict[str, dict] = {}
    best_name = None
    best_r2 = float("-inf")
    best_payload = None
    for model_name, factory in factories.items():
        result = evaluate_group_kfold(df, config, features, model_name, factory)
        result["metrics"]["time_holdout"] = evaluate_time_holdout(df, config, features, factory)
        result["metrics"]["industry_holdout"] = evaluate_industry_holdout(df, config, features, factory)
        result["metrics"]["top_features"] = []
        stage_results[model_name] = result["metrics"]
        if result["metrics"]["r2_mean"] > best_r2:
            best_r2 = result["metrics"]["r2_mean"]
            best_name = model_name
            best_payload = {
                "stage": stage,
                "description": config.description,
                "features": features,
                "target": config.target,
                "group_col": config.group_col,
                "pipeline": result["pipeline"],
                "metrics": result["metrics"],
            }
    best_payload["metrics"]["top_features"] = top_feature_importance(
        best_payload["pipeline"],
        df[best_payload["features"] + [config.target]].dropna(subset=[config.target]),
        best_payload["features"],
        config.target,
    )
    stage_results[best_name]["top_features"] = best_payload["metrics"]["top_features"]
    bundle_path = AGENT_ROOT / "training" / "artifacts" / f"{stage}_best.joblib"
    save_bundle(bundle_path, best_payload)
    return {
        "stage": stage,
        "description": config.description,
        "rows": int(len(df)),
        "feature_count": len(features),
        "best_model": best_name,
        "best_r2": best_r2,
        "artifact_path": str(bundle_path.relative_to(Path.cwd())),
        "models": stage_results,
    }


def render_report(payload: dict) -> str:
    lines = ["# Model Comparison Report", ""]
    lines.append("This report compares verified tabular models for the research agent.")
    lines.append("")
    for stage_result in payload["stages"]:
        lines.append(f"## {stage_result['stage']}")
        lines.append(f"- description: {stage_result['description']}")
        lines.append(f"- rows: {stage_result['rows']}")
        lines.append(f"- feature_count: {stage_result['feature_count']}")
        lines.append(f"- best_model: `{stage_result['best_model']}`")
        lines.append(f"- best_groupkfold_r2: {stage_result['best_r2']:.4f}")
        lines.append("")
        for model_name, metrics in stage_result["models"].items():
            lines.append(f"### {model_name}")
            lines.append(f"- group_kfold_r2_mean: {metrics['r2_mean']:.4f}")
            lines.append(f"- group_kfold_mae_mean: {metrics['mae_mean']:.4f}")
            if metrics["time_holdout"]:
                lines.append(f"- time_holdout_r2: {metrics['time_holdout']['r2']:.4f}")
            if metrics["industry_holdout"]:
                lines.append(f"- industry_holdout_r2: {metrics['industry_holdout']['r2']:.4f}")
            lines.append("- top_features:")
            for row in metrics["top_features"][:8]:
                lines.append(f"  - {row['feature']}: {row['importance_mean']:.6f}")
            lines.append("")
    return "\n".join(lines) + "\n"


def main() -> None:
    payload = {"stages": [run_stage(stage) for stage in STAGE_CONFIGS]}
    write_json(REPORTS / "model_metrics.json", payload)
    (REPORTS / "model_comparison_report.md").write_text(render_report(payload), encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
