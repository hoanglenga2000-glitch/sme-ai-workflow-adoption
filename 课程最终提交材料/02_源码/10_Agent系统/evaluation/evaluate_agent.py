from __future__ import annotations

import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent_tools.agent_answer import agent_answer
from agent_tools.cite_source import cite_source
from agent_tools.predict_adoption import predict_adoption
from agent_tools.query_indicator import query_indicator
from agent_tools.recommend_deployment import recommend_deployment

AGENT_ROOT = Path(__file__).resolve().parents[1]
ROOT = AGENT_ROOT.parent


def timed(name: str, fn, *args, **kwargs) -> dict:
    start = time.perf_counter()
    payload = fn(*args, **kwargs)
    elapsed = time.perf_counter() - start
    return {"name": name, "latency_seconds": round(elapsed, 4), "payload": payload}


def main() -> None:
    cases = [
        timed("stage_boundary_answer", agent_answer, "Why is Stage 2 not an SME-only sample?"),
        timed("metric_citation", cite_source, "Stage 2 model metrics"),
        timed("indicator_lookup", query_indicator, "DE", "C26", 2025, "ai_industry__E_AI_TML"),
        timed("prediction", predict_adoption, {"geo": "DE", "year": 2025, "size_emp": "GE10", "nace_r2": "C26"}),
        timed("deployment_recommendation", recommend_deployment, {"efficiency_need_proxy": 18, "security_concern_index": 12, "deployment_readiness_index": 68}),
        timed("unknown_claim", agent_answer, "Claim that this model proves all Chinese SMEs will adopt AI next year."),
    ]
    tool_success = sum(1 for case in cases if case["payload"].get("status", "ok") in {"ok", "无法确认"} or "answer" in case["payload"])
    hallucination_cases = [case for case in cases if case["name"] == "unknown_claim"]
    hallucination_rate = 0.0 if all("无法确认" in case["payload"].get("answer", "") for case in hallucination_cases) else 1.0
    supported_cases = [case for case in cases if case["name"] != "unknown_claim"]
    citation_cases = [case for case in supported_cases if case["payload"].get("evidence_files")]
    report = {
        "status": "ok",
        "cases": cases,
        "summary": {
            "case_count": len(cases),
            "tool_success_rate": round(tool_success / len(cases), 4),
            "citation_accuracy_proxy": round(len(citation_cases) / len(supported_cases), 4),
            "hallucination_rate": hallucination_rate,
            "average_latency_seconds": round(sum(case["latency_seconds"] for case in cases) / len(cases), 4),
            "token_cost_policy": "large tables never enter prompts; tools return bounded JSON and evidence paths",
        },
    }
    output = AGENT_ROOT / "reports" / "agent_quality_eval.json"
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    md = [
        "# Agent Quality Evaluation",
        "",
        f"- tool_success_rate: {report['summary']['tool_success_rate']}",
        f"- citation_accuracy_proxy: {report['summary']['citation_accuracy_proxy']}",
        f"- hallucination_rate: {report['summary']['hallucination_rate']}",
        f"- average_latency_seconds: {report['summary']['average_latency_seconds']}",
        "- token_cost_policy: large tables never enter prompts; tools return bounded JSON and evidence paths",
        "",
        "## Cases",
    ]
    for case in cases:
        md.append(f"- {case['name']}: {case['latency_seconds']}s")
    (AGENT_ROOT / "reports" / "agent_quality_eval.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"], ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
