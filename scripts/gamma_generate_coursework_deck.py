from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "12_机械学习完整案例展示PPT"
GAMMA_PPTX = OUT / "Gamma_AI_企业AI部署偏好与治理机制研究_机械学习展示.pptx"
GAMMA_RESULT = OUT / "gamma_generation_result.json"

API_BASE = "https://public-api.gamma.app/v1.0"


def request_json(url: str, method: str = "GET", payload: dict | None = None, api_key: str | None = None) -> dict:
    data = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(url, method=method, data=data)
    req.add_header("Content-Type", "application/json")
    if api_key:
        req.add_header("X-API-KEY", api_key)
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            return json.loads(body)
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Gamma API HTTP {exc.code}: {body[:1000]}") from exc


def download(url: str, path: Path) -> None:
    with urllib.request.urlopen(url, timeout=180) as resp:
        path.write_bytes(resp.read())


def build_input_text() -> str:
    outline = (OUT / "gamma_import_outline.md").read_text(encoding="utf-8") if (OUT / "gamma_import_outline.md").exists() else ""
    return f"""
# 企业 AI 部署偏好与治理机制研究：机器学习完整案例展示

请生成一套 14 页中文机器学习课程展示 PPT。风格：白底、深灰正文、低饱和蓝主色、少量橙色强调；不要花哨科技风，不要虚构数据图，不要把 AI 生成图片当作统计图。

核心事实必须保持：
- Stage 1：553 行面板，544 行可建模样本，36 个 geo，2021, 2023-2025，Ridge，GroupKFold R2=0.8680，MAE=1.8342。
- Stage 2：5,814 行建模面板，36 个 geo，50 个行业，2021, 2023-2025，ExtraTrees，长跑 GroupKFold R2=0.7245，MAE=1.9646。
- 源数据链：12,770,332 raw official rows -> 12,341,630 scanned rows -> 856,880 feature-filtered rows -> 5,814 modeling-panel rows。
- 正确表述：千万级官方源数据经过筛选和聚合形成建模面板，不是千万样本直接训练。
- Stage 2 是行业/区域外部验证层，不是 SME-only。
- 机器学习支持预测和机制解释，不证明因果。
- 问卷和访谈是私密辅助证据，不放入公开仓库。

每页需要一个明确 claim 和一个 proof object。结构如下：

{outline}
"""


def main() -> None:
    api_key = os.environ.get("GAMMA_API_KEY")
    if not api_key:
        raise SystemExit("GAMMA_API_KEY environment variable is required. Do not write the key into files.")
    OUT.mkdir(parents=True, exist_ok=True)
    payload = {
        "inputText": build_input_text(),
        "additionalInstructions": (
            "Generate an editable academic presentation in Chinese. "
            "Use clean charts placeholders only where charts are described; do not invent new metrics. "
            "Keep all numbers exactly as provided. Avoid decorative sci-fi style."
        ),
        "textMode": "preserve",
        "format": "presentation",
        "numCards": 14,
        "cardSplit": "inputTextBreaks",
        "exportAs": "pptx",
        "textOptions": {"language": "zh", "tone": "professional", "audience": "college machine learning course instructor"},
    }
    try:
        created = request_json(f"{API_BASE}/generations", method="POST", payload=payload, api_key=api_key)
    except Exception as exc:
        GAMMA_RESULT.write_text(
            json.dumps(
                {
                    "ok": False,
                    "stage": "create_generation",
                    "error": str(exc),
                    "note": "API key was read from GAMMA_API_KEY and is not stored in this file. Local artifact-tool PPTX remains the authoritative deck.",
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        raise
    generation_id = created.get("generationId") or created.get("id") or created.get("generation", {}).get("id")
    if not generation_id:
        raise RuntimeError(f"Could not find generation id in response: {created}")

    final = None
    for _ in range(90):
        status = request_json(f"{API_BASE}/generations/{generation_id}", api_key=api_key)
        final = status
        state = str(status.get("status") or "").lower()
        if state in {"completed", "complete", "succeeded", "success", "failed", "error"}:
            break
        time.sleep(5)

    result_public = {
        "generationId": generation_id,
        "status": final.get("status") if isinstance(final, dict) else None,
        "gammaUrl": final.get("gammaUrl") if isinstance(final, dict) else None,
        "exportDownloaded": False,
        "exportPath": None,
        "note": "API key was read from GAMMA_API_KEY and is not stored in this file.",
    }
    export_url = final.get("exportUrl") if isinstance(final, dict) else None
    if export_url:
        download(export_url, GAMMA_PPTX)
        result_public["exportDownloaded"] = True
        result_public["exportPath"] = str(GAMMA_PPTX)
    GAMMA_RESULT.write_text(json.dumps(result_public, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
