#!/usr/bin/env python3
"""Download a multi-source official Eurostat data lake for SME AI adoption research."""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "raw"
RAW.mkdir(parents=True, exist_ok=True)
MANIFEST = RAW / "manifest.jsonl"
UA = "sme-ai-workflow-adoption-research/0.2"

EUROSTAT_DATASETS = {
    "isoc_eb_ai": "Artificial intelligence by size class of enterprise",
    "isoc_cicce_use": "Cloud computing services by size class of enterprise",
    "isoc_e_dii": "Digital Intensity by size class of enterprise",
    "isoc_eb_das": "Data analytics by size class of enterprise",
    "isoc_eb_bd": "Big data analysis by size class of enterprise",
    "isoc_ec_esels": "E-commerce sales of enterprises by size class of enterprise",
    "isoc_ec_evals": "Value of e-commerce sales by size class of enterprise",
    "isoc_ske_itspe": "Enterprises that employ ICT specialists by size class of enterprise",
    "isoc_ske_itts": "Enterprises that provided ICT skills training by size class of enterprise",
    "isoc_ske_itrcrs": "Enterprises that recruited or tried to recruit ICT specialists by size class",
}

@dataclass
class ManifestEntry:
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


def write_manifest(entry: ManifestEntry) -> None:
    with MANIFEST.open("a", encoding="utf-8") as f:
        f.write(json.dumps(asdict(entry), ensure_ascii=False) + "\n")


def download(url: str, out: Path, source_id: str, title: str, required: bool = False, timeout: int = 180) -> ManifestEntry:
    out.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc).isoformat()
    try:
        with requests.get(url, headers={"User-Agent": UA}, timeout=timeout, stream=True) as r:
            ctype = r.headers.get("content-type")
            if r.status_code != 200:
                entry = ManifestEntry(source_id, title, url, None, r.status_code, ctype, 0, None, now, False, f"HTTP {r.status_code}")
                write_manifest(entry)
                if required:
                    raise RuntimeError(f"Download failed {r.status_code}: {url}")
                return entry
            tmp = out.with_suffix(out.suffix + ".part")
            n = 0
            with tmp.open("wb") as f:
                for chunk in r.iter_content(1024 * 1024):
                    if chunk:
                        f.write(chunk)
                        n += len(chunk)
            tmp.replace(out)
            entry = ManifestEntry(source_id, title, url, str(out.relative_to(ROOT)), r.status_code, ctype, n, sha256_file(out), now, True)
            write_manifest(entry)
            return entry
    except Exception as exc:
        entry = ManifestEntry(source_id, title, url, None, None, None, 0, None, now, False, repr(exc))
        write_manifest(entry)
        if required:
            raise
        return entry


def main() -> None:
    if MANIFEST.exists():
        MANIFEST.unlink()
    for code, title in EUROSTAT_DATASETS.items():
        url = f"https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/{code}?format=SDMX-CSV"
        download(url, RAW / "eurostat" / f"{code}_sdmx.csv", f"eurostat_{code}", title, required=True)

    census_files = {
        "census_btos_ai_supplement_2026": "https://www.census.gov/hfp/btos/downloads/AI_Supplement_Table_2026.xlsx",
        "census_btos_ai_core_questions": "https://www.census.gov/hfp/btos/downloads/AI%20Core%20Questions.xlsx",
        "census_btos_sector_by_employment_size": "https://www.census.gov/hfp/btos/downloads/Sector%20by%20Employment%20Size%20Class.xlsx",
        "census_btos_core_ai_content_pdf": "https://www.census.gov/hfp/btos/downloads/BTOS%20Core%20and%20AI%20Content.pdf",
    }
    for sid, url in census_files.items():
        suffix = ".pdf" if url.lower().endswith(".pdf") else ".xlsx"
        download(url, RAW / "census_btos" / f"{sid}{suffix}", sid, "U.S. Census BTOS AI supplementary file", required=False)

    print(MANIFEST.read_text(encoding="utf-8"))

if __name__ == "__main__":
    main()
