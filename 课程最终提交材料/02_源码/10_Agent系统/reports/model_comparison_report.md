# Model Comparison Report

This report compares verified tabular models for the research agent.

## stage1
- description: SME mechanism interpretation layer
- rows: 553
- feature_count: 25
- best_model: `ridge`
- best_groupkfold_r2: 0.8680

### ridge
- group_kfold_r2_mean: 0.8680
- group_kfold_mae_mean: 1.8342
- time_holdout_r2: 0.9312
- top_features:
  - E_AI_TANY: 0.597010
  - E_AI_TML: 0.530275
  - E_AI_DA: 0.140894
  - E_AI_CC1SI_DA: 0.121978
  - E_AI_CC: 0.114176
  - deployment_readiness_index: 0.095155
  - E_AI_TNLG: 0.037708
  - E_AI_BLEG: 0.026324

### random_forest
- group_kfold_r2_mean: 0.8647
- group_kfold_mae_mean: 1.7212
- time_holdout_r2: 0.8516
- top_features:

### hist_gradient_boosting
- group_kfold_r2_mean: 0.8338
- group_kfold_mae_mean: 1.8771
- time_holdout_r2: 0.8131
- top_features:

## stage2
- description: GE10 industry and region external validation layer
- rows: 5814
- feature_count: 67
- best_model: `extra_trees`
- best_groupkfold_r2: 0.7137

### ridge
- group_kfold_r2_mean: 0.6813
- group_kfold_mae_mean: 2.3492
- time_holdout_r2: 0.6976
- industry_holdout_r2: 0.8639
- top_features:

### extra_trees
- group_kfold_r2_mean: 0.7137
- group_kfold_mae_mean: 2.0525
- time_holdout_r2: 0.7019
- industry_holdout_r2: 0.9521
- top_features:
  - ai_industry__E_AI_TML: 0.494969
  - ai_industry__E_AI_TNLG: 0.088643
  - digital_foundation_index: 0.035307
  - ai_industry__E_AI_CC: 0.022003
  - country: 0.020641
  - geo: 0.020431
  - nace_r2: 0.020219
  - deployment_readiness_index: 0.011671

### hist_gradient_boosting
- group_kfold_r2_mean: 0.6815
- group_kfold_mae_mean: 2.1758
- time_holdout_r2: 0.6955
- industry_holdout_r2: 0.9471
- top_features:

