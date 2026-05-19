from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


AGENT_ROOT = Path(__file__).resolve().parents[1]
ROOT = AGENT_ROOT.parent


def main() -> None:
    metrics_path = AGENT_ROOT / "reports" / "model_metrics.json"
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    lines = ["# Agent Evaluation Report", ""]
    lines.append("This report summarizes the model-side and agent-side evaluation contract.")
    lines.append("")
    for stage_result in metrics["stages"]:
        best_model = stage_result["models"][stage_result["best_model"]]
        lines.append(f"## {stage_result['stage']}")
        lines.append(f"- best_model: `{stage_result['best_model']}`")
        lines.append(f"- group_kfold_r2_mean: {best_model['r2_mean']:.4f}")
        lines.append(f"- group_kfold_mae_mean: {best_model['mae_mean']:.4f}")
        if best_model["time_holdout"]:
            lines.append(f"- time_holdout_r2: {best_model['time_holdout']['r2']:.4f}")
        if best_model["industry_holdout"]:
            lines.append(f"- industry_holdout_r2: {best_model['industry_holdout']['r2']:.4f}")
        lines.append("- token strategy: return features, metrics, and evidence file paths only; never inject raw tables into prompts.")
        lines.append("- hallucination guard: no evidence means `无法确认`.")
        lines.append("")
    lines.append("## Agent Metrics Contract")
    lines.append("- numeric_accuracy: values must match source CSV/JSON exactly")
    lines.append("- citation_accuracy: every claim must point to repository files")
    lines.append("- tool_success_rate: tools must return schema-valid JSON")
    lines.append("- token_budget_proxy: no tool returns more than 20 rows or 5 evidence chunks")
    lines.append("- latency_targets_seconds: indicator query <= 2, prediction <= 3, chart render <= 6")
    lines.append("")
    report_path = AGENT_ROOT / "reports" / "agent_evaluation_report.md"
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"report": str(report_path), "status": "ok"}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
