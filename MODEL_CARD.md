# Model Card

The public research prototype uses two main modeling layers:

- Stage 1: SME mechanism interpretation layer, Ridge regression, country-level GroupKFold R2 about 0.8680.
- Stage 2: industry / region external validation layer, ExtraTrees, country-level GroupKFold R2 about 0.7137.

Historical holdout, A10 GPU, and classroom metrics are retained as training logs only. They should not replace the final GroupKFold registry metrics.
