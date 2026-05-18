# Research Quality And Data Validation Report

## Conclusion

The current dataset is sufficient for a professional course-level and research-oriented machine-learning case. It has two complementary empirical layers: Stage 1 models SME size-class adoption mechanisms, while Stage 2 validates the mechanism over a much larger industry/regional official-data cross-section. Stage 2 should not be described as SME-size specific because its industry tables use `GE10`; it strengthens external validity rather than replacing Stage 1.

## Cross-Sectional Sufficiency

| dataset                    |   rows |   columns |   geo_count |   country_count |   year_min |   year_max |   year_count |   size_classes |   nace_count |   target_nonnull |   target_coverage |   duplicate_keys |   mean_numeric_missing_rate |   target_min |   target_p25 |   target_median |   target_p75 |   target_max |
|:---------------------------|-------:|----------:|------------:|----------------:|-----------:|-----------:|-------------:|---------------:|-------------:|-----------------:|------------------:|-----------------:|----------------------------:|-------------:|-------------:|----------------:|-------------:|-------------:|
| stage1_size_class_panel    |   2323 |       100 |          42 |              42 |       2010 |       2025 |           16 |              4 |          nan |              544 |            0.2342 |                0 |                      0.6808 |            0 |       2.3187 |          4.4125 |       9.955  |         57.3 |
| stage2_industry_panel_GE10 |   5814 |        80 |          36 |              36 |       2021 |       2025 |            4 |              1 |           50 |             5814 |            1      |                0 |                      0.4682 |            0 |       1.5662 |          3.455  |       7.0675 |        100   |

## Cleaning And Retention Outcomes

| stage                         |   raw_or_long_rows |   panel_rows |   model_rows |   retention_to_panel |   retention_to_model |
|:------------------------------|-------------------:|-------------:|-------------:|---------------------:|---------------------:|
| stage1_official_multisource   |             134367 |         2323 |          544 |               0.0173 |               0.004  |
| stage2_large_sources_profiled |           12770332 |         5814 |         5814 |               0.0005 |               0.0005 |
| stage2_indicator_filtering    |           12341630 |       856880 |         5814 |               0.0694 |               0.0005 |

Stage 2 official source profile: 17 files, 12,770,332 rows, 10,453,354 non-null observations. Indicator filtering retained 856,880 mechanism-relevant rows from 12,341,630 scanned rows.

## Model Evidence

Stage 1 best model: `ridge`, R2=0.889, MAE=1.636.

Stage 2 best model: `extra_trees`, R2=0.833, MAE=1.457.

## Leakage And Validity Checks

Target leakage controls are in place: direct target fields are excluded from feature sets. Stage 2 excludes `target_workflow_automation` and `ai_industry__E_AI_TPA`; Stage 1 excludes the target field and target-derived variables in the leakage-controlled run.

## Data Quality Notes

- All model data come from official Eurostat API downloads; Census BTOS attempts are documented but not used where access returned HTTP 403.
- Stage 2 raw files are gzip-compressed SDMX-CSV with SHA256 hashes in `manifest_stage2.jsonl` on the A10 server.
- Missingness is expected because not every indicator exists for every country/year/industry; the pipeline uses coverage thresholds and median/mode imputation inside reproducible sklearn pipelines.
- Duplicates are checked at panel key level. If duplicate keys are nonzero, they result from multiple source indicators before pivoting, not duplicate final target rows.
- Stage 2 uses GE10 industry cross-sections; SME-specific claims should rely on Stage 1 size-class evidence.

## Files For PPT

- `outputs/reports/research_quality_validation.md`
- `outputs/reports/stage2_source_profile.md`
- `outputs/reports/stage2_large_model_results.md`
- `outputs/tables/research_quality_summary.csv`
- `outputs/tables/cleaning_retention_summary.csv`
- `outputs/tables/stage2_feature_importance.csv`
