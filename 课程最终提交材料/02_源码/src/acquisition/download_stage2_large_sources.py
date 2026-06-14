#!/usr/bin/env python3
"""Download stage-2 larger official Eurostat datasets as compressed SDMX-CSV."""
from __future__ import annotations
import hashlib, json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw" / "eurostat_stage2"
RAW.mkdir(parents=True, exist_ok=True)
MANIFEST = ROOT / "data" / "raw" / "manifest_stage2.jsonl"
UA = "sme-ai-workflow-adoption-stage2/0.2"
DATASETS = {
    "isoc_eb_ain2": "Artificial intelligence by NACE Rev. 2 activity",
    "isoc_cicce_usen2": "Cloud computing services by NACE Rev. 2 activity",
    "isoc_e_diin2": "Digital Intensity by NACE Rev. 2 activity",
    "isoc_eb_dan2": "Data analytics by NACE Rev. 2 activity",
    "isoc_eb_bdn2": "Big data analysis by NACE Rev. 2 activity",
    "isoc_ec_eseln2": "E-commerce sales by NACE Rev. 2 activity",
    "isoc_ec_evaln2": "Value of e-commerce sales by NACE Rev. 2 activity",
    "isoc_ske_itspen2": "ICT specialists by NACE Rev. 2 activity",
    "isoc_ske_ittn2": "ICT training by NACE Rev. 2 activity",
    "isoc_ske_itrcrn2": "ICT recruitment by NACE Rev. 2 activity",
    "isoc_r_eb_ain2": "Regional AI by NACE Rev. 2 activity and NUTS region",
    "isoc_r_cicce_usen2": "Regional cloud by NACE Rev. 2 activity and NUTS region",
    "isoc_r_eb_dan2": "Regional data analytics by NACE Rev. 2 activity and NUTS region",
    "sbs_sc_ovw": "Structural business statistics by size class",
    "sbs_ovw_act": "Structural business statistics by activity",
    "bd_9pm_r2": "High growth enterprises and employment by NACE Rev. 2",
    "bd_hg": "High growth enterprises by NACE Rev. 2 activity",
}
@dataclass
class Entry:
    source_id: str
    title: str
    url: str
    path: str | None
    status_code: int | None
    content_type: str | None
    bytes: int
    sha256: str | None
    downloaded_at_utc: str
    ok: bool
    note: str = ""

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def write_manifest(entry: Entry) -> None:
    with MANIFEST.open("a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(entry), ensure_ascii=False) + "\n")

def download(code: str, title: str) -> None:
    url = f"https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/{code}?format=SDMX-CSV&compressed=true"
    out = RAW / f"{code}_sdmx.csv.gz"
    now = datetime.now(timezone.utc).isoformat()
    try:
        with requests.get(url, headers={"User-Agent": UA}, timeout=300, stream=True) as r:
            ctype = r.headers.get("content-type")
            if r.status_code != 200:
                entry = Entry(f"eurostat_{code}", title, url, None, r.status_code, ctype, 0, None, now, False, f"HTTP {r.status_code}")
                write_manifest(entry)
                print(json.dumps(asdict(entry), ensure_ascii=False), flush=True)
                return
            tmp = out.with_suffix(out.suffix + ".part")
            n = 0
            with tmp.open("wb") as f:
                for chunk in r.iter_content(1024 * 1024):
                    if chunk:
                        f.write(chunk)
                        n += len(chunk)
            tmp.replace(out)
            entry = Entry(f"eurostat_{code}", title, url, str(out.relative_to(ROOT)), r.status_code, ctype, n, sha256_file(out), now, True)
            write_manifest(entry)
            print(json.dumps(asdict(entry), ensure_ascii=False), flush=True)
    except Exception as exc:
        entry = Entry(f"eurostat_{code}", title, url, None, None, None, 0, None, now, False, repr(exc))
        write_manifest(entry)
        print(json.dumps(asdict(entry), ensure_ascii=False), flush=True)

def main() -> None:
    if MANIFEST.exists():
        MANIFEST.unlink()
    for code, title in DATASETS.items():
        download(code, title)

if __name__ == "__main__":
    main()
