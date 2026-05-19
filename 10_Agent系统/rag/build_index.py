from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path


AGENT_ROOT = Path(__file__).resolve().parents[1]
ROOT = AGENT_ROOT.parent

FILES = [
    ROOT / "docs" / "data_sources.md",
    ROOT / "outputs" / "reports" / "stage2_large_model_results.md",
    ROOT / "08_Research_Grade_Deck" / "verified_metrics.json",
    ROOT / "09_Agent训练规划" / "项目总结与Agent训练路线.md",
    AGENT_ROOT / "reports" / "model_comparison_report.md",
    AGENT_ROOT / "reports" / "model_registry.json",
]


def chunk_text(text: str) -> list[str]:
    raw = [part.strip() for part in re.split(r"\n\s*\n", text) if part.strip()]
    return [part[:1200] for part in raw]


def main() -> None:
    entries = []
    for path in FILES:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        for idx, chunk in enumerate(chunk_text(text), start=1):
            entries.append(
                {
                    "file": str(path.relative_to(ROOT).as_posix()),
                    "chunk_id": idx,
                    "text": chunk,
                    "created_at_utc": datetime.now(timezone.utc).isoformat(),
                    "terms": sorted(set(re.findall(r"[A-Za-z0-9_]{3,}", chunk.lower()))),
                }
            )
    output_path = AGENT_ROOT / "rag" / "evidence_index.json"
    output_path.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"chunks": len(entries), "output": str(output_path)}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
