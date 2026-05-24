# Model Card

The public research prototype uses two main modeling layers:

- Stage 1: SME mechanism interpretation layer, Ridge regression, country-level GroupKFold R2=0.8680, MAE=1.8342.
- Stage 2: industry / region external validation layer, ExtraTrees, country-level GroupKFold R2=0.7245 (long-run 500 trees x 3 seeds), MAE=1.9646.

Historical holdout, A10 GPU, and classroom metrics are retained as training logs only. They should not replace the final GroupKFold registry metrics.
