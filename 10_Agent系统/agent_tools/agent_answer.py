from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from agent_tools.cite_source import cite_source
from agent_tools.common import AGENT_ROOT, time_call, write_jsonable
from rag.search_index import NO_EVIDENCE_LABEL, search_evidence


def _metrics() -> dict:
    path = AGENT_ROOT / "reports" / "model_registry.json"
    if path.exists():
        registry = json.loads(path.read_text(encoding="utf-8"))
        return {
            "champion_model": registry.get("champion_model"),
            "champion_stage": registry.get("champion_stage"),
            "group_kfold_r2_mean": registry.get("metrics", {}).get("r2_mean"),
            "group_kfold_mae_mean": registry.get("metrics", {}).get("mae_mean"),
        }
    return {}


def agent_answer(question: str) -> dict:
    lowered = question.lower()
    unsupported_markers = ["all chinese", "所有中国", "next year", "will adopt", "证明所有"]
    retrieved = search_evidence(question, top_k=5)
    citation = cite_source(question)
    evidence_files = sorted(set(retrieved.get("evidence_files", []) + citation.get("evidence_files", [])))
    metrics = _metrics()
    if any(marker in lowered for marker in unsupported_markers):
        answer = "无法确认：当前研究数据主要来自 Eurostat，不能外推为所有中国中小企业的未来采纳结论。"
        confidence = 0.0
        limitations = ["The claim exceeds the verified research boundary."]
        evidence_files = []
    elif not retrieved["chunks"] and citation["status"] == NO_EVIDENCE_LABEL:
        answer = "无法确认：当前证据索引中没有足够材料支持该结论。"
        confidence = 0.0
        limitations = ["No verified evidence chunk matched the question."]
    else:
        answer = "该回答应基于工具结果和检索证据生成；当前工具返回了可追溯证据文件，数值结论需调用对应查询或预测工具确认。"
        confidence = 0.75 if evidence_files else 0.25
        limitations = ["This deterministic academic agent does not fabricate unsupported numeric values."]
    return {
        "answer": answer,
        "tool_calls": [
            {"tool": "search_evidence", "args": {"query": question, "top_k": 5}, "status": retrieved["status"]},
            {"tool": "cite_source", "args": {"claim": question}, "status": citation["status"]},
        ],
        "metrics_used": metrics,
        "evidence_files": evidence_files,
        "confidence": confidence,
        "limitations": limitations,
    }


if __name__ == "__main__":
    print(write_jsonable(time_call(agent_answer, "Why is Stage 2 not an SME-only sample?")))
