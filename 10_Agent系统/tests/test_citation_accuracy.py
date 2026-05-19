from __future__ import annotations

import sys
import unittest
from pathlib import Path


AGENT_ROOT = Path(__file__).resolve().parents[1]
ROOT = AGENT_ROOT.parent
sys.path.insert(0, str(AGENT_ROOT))

from agent_tools.cite_source import cite_source


class CitationAccuracyTest(unittest.TestCase):
    def test_known_claim_returns_verified_files(self) -> None:
        payload = cite_source("Stage 2 model evidence")
        self.assertEqual(payload["status"], "ok")
        self.assertIn("08_Research_Grade_Deck/verified_metrics.json", payload["evidence_files"])


if __name__ == "__main__":
    unittest.main()
