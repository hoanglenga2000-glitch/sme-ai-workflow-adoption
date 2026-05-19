from __future__ import annotations

import json
from pathlib import Path


AGENT_ROOT = Path(__file__).resolve().parents[1]
ROOT = AGENT_ROOT.parent
import sys

sys.path.insert(0, str(AGENT_ROOT))

from rag.search_index import search_evidence


def main() -> None:
    queries = [
        "Stage 2 cannot be stated as SME-only evidence",
        "manifest hash verification",
        "tree models better than mlp",
    ]
    results = {query: search_evidence(query, top_k=5) for query in queries}
    output_path = AGENT_ROOT / "reports" / "rag_eval.json"
    output_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"queries": len(queries), "output": str(output_path)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
