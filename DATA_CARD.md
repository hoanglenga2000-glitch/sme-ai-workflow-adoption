# Data Card

This public repository contains official Eurostat source manifests, raw official files, processed modeling panels, sample files, and lightweight result tables for enterprise AI deployment preference research.

## Locked Public Facts

### Stage 1: SME Mechanism Interpretation Layer
- 553 panel rows, 544 modeling rows, 36 geo groups, 2021-2025
- Champion model: Ridge, GroupKFold R2=0.8302 (strict no-leakage)

### Stage 2: Industry/Region External Validation Layer
- 5,814 modeling rows, 36 geo groups, 50 industries, 2021-2025
- Champion model: ExtraTrees (500 trees x 3 seeds), GroupKFold R2=0.7245

### Source Data Chain
- 17 verified Eurostat official files
- 12,770,332 raw source rows
- 12,341,630 after program scan
- 856,880 feature-filtered rows
- 5,814 aggregated modeling panel

### Micro-evidence
- 538 questionnaire responses (aggregate statistics only, not per-sample database)
- Interview materials for mechanism triangulation

## Correct Wording

The accurate statement is that tens-of-millions-scale official source rows were filtered and aggregated into modeling panels. They were not directly used as training samples.

## Data Sources

All primary data comes from Eurostat enterprise ICT surveys. See `data_sources.md` for full provenance including API URLs, SHA256 hashes, and download timestamps.
