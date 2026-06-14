from __future__ import annotations

import json
import math
import re
from pathlib import Path

AGENT_ROOT = Path(__file__).resolve().parents[1]
ROOT = AGENT_ROOT.parent
NO_EVIDENCE_LABEL = "无法确认"


def tokenize(text: str) -> set[str]:
    return set(re.findall(r"[\w_]{2,}", text.lower(), flags=re.UNICODE))


def load_index() -> list[dict]:
    path = AGENT_ROOT / "rag" / "evidence_index.json"
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def search_evidence(query: str, top_k: int = 5) -> dict:
    entries = load_index()
    query_terms = tokenize(query)
    scored = []
    for entry in entries:
        terms = set(entry.get("terms", []))
        overlap = len(query_terms.intersection(terms))
        if not overlap:
            continue
        length_penalty = 1.0 / math.sqrt(max(len(terms), 1))
        score = overlap * length_penalty
        scored.append((score, entry))
    scored.sort(key=lambda item: item[0], reverse=True)
    chunks = []
    for score, entry in scored[:top_k]:
        chunks.append(
            {
                "file": entry["file"],
                "chunk_id": entry["chunk_id"],
                "score": round(float(score), 6),
                "text": entry["text"][:900],
            }
        )
    status = "ok" if chunks else NO_EVIDENCE_LABEL
    return {
        "status": status,
        "query": query,
        "chunks": chunks,
        "evidence_files": sorted({chunk["file"] for chunk in chunks}),
        "ragas_proxy": {
            "context_precision": 1.0 if chunks else 0.0,
            "faithfulness_guard": "answer must quote only retrieved files",
            "answer_relevance_proxy": min(1.0, len(chunks) / max(top_k, 1)),
        },
    }
