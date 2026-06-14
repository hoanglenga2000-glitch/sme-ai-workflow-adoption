from __future__ import annotations

import sys
import unittest
from pathlib import Path


AGENT_ROOT = Path(__file__).resolve().parents[1]
ROOT = AGENT_ROOT.parent
sys.path.insert(0, str(AGENT_ROOT))

from agent_tools.agent_answer import agent_answer
from agent_tools.cite_source import cite_source
from rag.search_index import search_evidence
from training.common import ROOT


class AgentQualityContractTest(unittest.TestCase):
    def test_public_data_package_is_present(self) -> None:
        manifests = [
            ROOT / "data" / "raw" / "manifest.jsonl",
            ROOT / "data" / "raw" / "manifest_stage2.jsonl",
        ]
        processed = [
            ROOT / "data" / "processed" / "eurostat_ai_panel.csv",
            ROOT / "data" / "processed" / "stage2_industry_panel.csv",
        ]
        for path in manifests + processed:
            self.assertTrue(path.exists(), f"missing public data package file: {path}")

        raw_notice = ROOT / "data" / "raw" / "README.md"
        self.assertTrue(raw_notice.exists(), "raw data notice should explain why large source files are excluded")

    def test_rag_returns_at_most_five_chunks(self) -> None:
        payload = search_evidence("Stage 2 model metrics", top_k=5)
        self.assertLessEqual(len(payload["chunks"]), 5)

    def test_unknown_claim_is_not_confirmed(self) -> None:
        payload = cite_source("This proves all Chinese SMEs will adopt AI next year.")
        self.assertEqual(payload["status"], "无法确认")
        self.assertEqual(payload["evidence_files"], [])

    def test_agent_answer_contract(self) -> None:
        payload = agent_answer("Why is Stage 2 not an SME-only sample?")
        for key in ["answer", "tool_calls", "metrics_used", "evidence_files", "confidence", "limitations"]:
            self.assertIn(key, payload)


if __name__ == "__main__":
    unittest.main()
