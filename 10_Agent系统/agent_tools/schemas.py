from __future__ import annotations

NO_EVIDENCE_LABEL = "无法确认"

TOOL_SCHEMAS = {
    "query_indicator": {
        "input": {"country": "str|null", "industry": "str|null", "year": "int|null", "indicator": "str", "stage": "stage1|stage2"},
        "output": {"status": "ok|error", "rows": "list[dict]", "evidence_files": "list[str]"},
    },
    "predict_adoption": {
        "input": {"features": "dict", "stage": "stage1|stage2"},
        "output": {"status": "ok|error", "prediction": "float", "model": "str", "evidence_files": "list[str]"},
    },
    "agent_answer": {
        "output": {
            "answer": "str",
            "tool_calls": "list[dict]",
            "metrics_used": "dict",
            "evidence_files": "list[str]",
            "confidence": "float",
            "limitations": "list[str]",
        }
    },
}


def assert_evidence(payload: dict) -> dict:
    if not payload.get("evidence_files"):
        payload["status"] = NO_EVIDENCE_LABEL
        payload["evidence_files"] = []
    return payload
