# Data Sources

This project uses official Eurostat SDMX-CSV sources as the final empirical basis. Each raw download is recorded in `data/raw/manifest.jsonl` or `data/raw/manifest_stage2.jsonl` with URL, HTTP status, byte size, timestamp, and SHA256 hash.

## Stage 1: SME Size-Class Mechanism Layer

| Source code | Role in study |
|---|---|
| `isoc_eb_ai` | AI technology adoption by enterprise size class; provides the target `E_AI_TPA` for AI workflow automation / decision support. |
| `isoc_cicce_use` | Cloud computing service use; proxy for deployment readiness and SaaS/cloud capability. |
| `isoc_e_dii` | Digital intensity; proxy for digital foundation. |
| `isoc_eb_das` | Data analytics use; proxy for data maturity. |
| `isoc_eb_bd` | Big data analytics; proxy for advanced analytics capability. |
| `isoc_ec_esels` | E-commerce sales; proxy for market digitization. |
| `isoc_ec_evals` | Value of e-commerce sales; proxy for digital transaction intensity. |
| `isoc_ske_itspe` | ICT specialists; proxy for internal technical capacity. |
| `isoc_ske_itts` | ICT training; proxy for workforce readiness. |
| `isoc_ske_itrcrs` | ICT recruitment difficulty; proxy for talent constraint. |

## Stage 2: Industry/Region External Validation Layer

| Source code | Role in study |
|---|---|
| `isoc_eb_ain2` | AI technology adoption by NACE industry; external validation target and AI capability features. |
| `isoc_cicce_usen2` | Cloud computing by NACE industry. |
| `isoc_e_diin2` | Digital intensity by NACE industry. |
| `isoc_eb_dan2` | Data analytics by NACE industry. |
| `isoc_eb_bdn2` | Big data analysis by NACE industry. |
| `isoc_ec_eseln2` | E-commerce sales by NACE industry. |
| `isoc_ec_evaln2` | E-commerce sales value by NACE industry. |
| `isoc_ske_itspen2` | ICT specialists by NACE industry. |
| `isoc_ske_ittn2` | ICT training by NACE industry. |
| `isoc_ske_itrcrn2` | ICT recruitment constraints by NACE industry. |
| `isoc_r_eb_ain2` | Regional AI indicators aggregated to country-industry features. |
| `isoc_r_cicce_usen2` | Regional cloud indicators aggregated to country-industry features. |
| `isoc_r_eb_dan2` | Regional data analytics indicators aggregated to country-industry features. |
| `sbs_sc_ovw` | Structural business statistics by size class. |
| `sbs_ovw_act` | Structural business statistics by activity. |
| `bd_9pm_r2` | High-growth enterprises and employment by NACE industry. |
| `bd_hg` | High-growth enterprises by NACE industry. |

## Figure Style References

The academic figures in `outputs/figures/academic/` follow a restrained scientific plotting style:

- `SciencePlots` for Matplotlib scientific paper/presentation styling.
- Nature figure guidance principles: labelled axes and tick marks, accessible colours, editable vector outputs, and avoiding small overlapping labels.

Both PNG and SVG outputs are provided so the PPT can use raster images while the report/repository keeps editable vector figures.
