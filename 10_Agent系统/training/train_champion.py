from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path

import joblib

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from training.common import (
    AGENT_ROOT,
    ARTIFACTS,
    REPORTS,
    ROOT,
    STAGE_CONFIGS,
    academic_score,
    audit_all_manifests,
    dataset_fingerprint,
    feature_columns,
    leakage_audit,
    load_stage_frame,
    runtime_snapshot,
    write_json,
)


def optuna_status() -> dict:
    try:
        import optuna

        return {"available": True, "version": optuna.__version__, "mode": "ready_for_a10_sweeps"}
    except Exception as exc:
        return {"available": False, "reason": str(exc), "mode": "fallback_deterministic_grid"}


def load_metrics() -> dict:
    return json.loads((REPORTS / "model_metrics.json").read_text(encoding="utf-8"))


def select_champion(metrics: dict, stage: str) -> dict:
    stage_payload = next(item for item in metrics["stages"] if item["stage"] == stage)
    candidates = []
    for model_name, model_metrics in stage_payload["models"].items():
        candidates.append(
            {
                "model": model_name,
                "academic_score": academic_score(model_metrics),
                "metrics": model_metrics,
            }
        )
    candidates.sort(key=lambda item: item["academic_score"], reverse=True)
    return {"stage": stage, "stage_payload": stage_payload, "ranking": candidates, "winner": candidates[0]}


def ensure_metrics(force: bool) -> None:
    if not force and (REPORTS / "model_metrics.json").exists():
        return
    from training.train_models import main as train_models_main

    train_models_main()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", default="stage2", choices=sorted(STAGE_CONFIGS))
    parser.add_argument("--force", action="store_true", help="rerun model training before champion selection")
    args = parser.parse_args()

    ensure_metrics(args.force)
    manifest_audit = audit_all_manifests()
    if not manifest_audit["ok"]:
        write_json(REPORTS / "champion_training_failed.json", {"status": "failed", "manifest_audit": manifest_audit})
        raise SystemExit("manifest hash audit failed")

    metrics = load_metrics()
    champion = select_champion(metrics, args.stage)
    config, df = load_stage_frame(args.stage)
    features = feature_columns(df, config)
    leak = leakage_audit(args.stage, features)
    if not leak["ok"]:
        write_json(REPORTS / "champion_training_failed.json", {"status": "failed", "leakage_audit": leak})
        raise SystemExit("feature leakage audit failed")

    source_artifact = ARTIFACTS / f"{args.stage}_best.joblib"
    champion_artifact = ARTIFACTS / "champion_model.joblib"
    bundle = joblib.load(source_artifact)
    bundle["champion_selection"] = {
        "academic_score": champion["winner"]["academic_score"],
        "ranking": champion["ranking"],
        "selection_rule": "maximize group-kfold-first academic score with time/industry/stability penalties",
    }
    joblib.dump(bundle, champion_artifact)

    registry = {
        "status": "ok",
        "champion_stage": args.stage,
        "champion_model": champion["winner"]["model"],
        "champion_artifact": str(champion_artifact.relative_to(ROOT).as_posix()),
        "academic_score": champion["winner"]["academic_score"],
        "metrics": champion["winner"]["metrics"],
        "dataset_fingerprint": dataset_fingerprint([cfg.csv_path for cfg in STAGE_CONFIGS.values()]),
        "manifest_audit": manifest_audit,
        "leakage_audit": leak,
        "optuna": optuna_status(),
        "ft_transformer_status_file": "10_Agent系统/reports/ft_transformer_status.json",
        "runtime": runtime_snapshot(),
    }
    write_json(REPORTS / "model_registry.json", registry)
    shutil.copyfile(REPORTS / "model_registry.json", ARTIFACTS / "model_registry.json")
    print(json.dumps(registry, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
