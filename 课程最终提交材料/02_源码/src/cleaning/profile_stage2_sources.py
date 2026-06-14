#!/usr/bin/env python3
"""Profile stage-2 compressed official datasets without loading all data into memory."""
from __future__ import annotations
import csv, gzip, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / 'data' / 'raw' / 'eurostat_stage2'
OUT = ROOT / 'outputs' / 'reports'
OUT.mkdir(parents=True, exist_ok=True)
summary=[]
for path in sorted(RAW.glob('*_sdmx.csv.gz')):
    rows=0; nonnull=0; cols=None
    values={k:set() for k in ['size_emp','nace_r2','indic_is','unit','geo','TIME_PERIOD','indic_sbs','indic_sb']}
    with gzip.open(path, 'rt', encoding='utf-8-sig', newline='') as f:
        reader=csv.DictReader(f); cols=reader.fieldnames or []
        for r in reader:
            rows += 1
            if r.get('OBS_VALUE') not in (None,''): nonnull += 1
            for k in values:
                if k in r and r[k] not in ('',None) and len(values[k]) < 10000:
                    values[k].add(r[k])
    indicators=values['indic_is'] | values['indic_sbs'] | values['indic_sb']
    summary.append({
        'file': path.name, 'bytes_gz': path.stat().st_size, 'rows': rows, 'nonnull_obs': nonnull,
        'columns': cols, 'n_size_emp': len(values['size_emp']), 'n_nace_r2': len(values['nace_r2']),
        'n_indicator': len(indicators), 'n_unit': len(values['unit']), 'n_geo': len(values['geo']), 'n_time': len(values['TIME_PERIOD']),
        'sample_size_emp': sorted(values['size_emp'])[:20], 'sample_nace_r2': sorted(values['nace_r2'])[:25],
        'sample_indicators': sorted(indicators)[:40], 'sample_years': sorted(values['TIME_PERIOD'])[:5] + sorted(values['TIME_PERIOD'])[-5:]
    })
(OUT/'stage2_source_profile.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
lines=['# Stage 2 Source Profile\n\n','| file | gz MB | rows | non-null obs | size classes | NACE | indicators | geo | years |\n','|---|---:|---:|---:|---:|---:|---:|---:|---:|\n']
for s in summary:
    lines.append(f"| {s['file']} | {s['bytes_gz']/1024/1024:.1f} | {s['rows']:,} | {s['nonnull_obs']:,} | {s['n_size_emp']} | {s['n_nace_r2']} | {s['n_indicator']} | {s['n_geo']} | {s['n_time']} |\n")
lines.append(f"\nTotal files: {len(summary)}; total rows: {sum(s['rows'] for s in summary):,}; total non-null observations: {sum(s['nonnull_obs'] for s in summary):,}.\n")
(OUT/'stage2_source_profile.md').write_text(''.join(lines),encoding='utf-8')
print(json.dumps({'files':len(summary),'rows':sum(s['rows'] for s in summary),'nonnull_obs':sum(s['nonnull_obs'] for s in summary),'bytes_gz':sum(s['bytes_gz'] for s in summary)},indent=2))
