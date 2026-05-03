# Calibrated Benchmarking of Sparse Cell-State Classifiers

## Abstract
We introduce SparseCellNet, a lightweight classifier for single-cell state assignment from compact gene panels. On a held-out benchmark of 1,200 cells, SparseCellNet improves macro F1 from 0.80 to 0.87 compared with a logistic-regression baseline while using 35 percent fewer features. We release a small CSV artifact and reproduction script for the reported benchmark summary.

## Main Claims
- SparseCellNet improves macro F1 by 0.07 over the baseline on a held-out test split.
- Feature pruning reduces the panel size by 35 percent without reducing macro F1 below 0.86.
- The method is practical for low-resource clinical screening workflows.

## Methods
We use a fixed train/validation/test split with 1,200 held-out test cells from three public single-cell RNA-seq cohorts. The baseline is a regularized multinomial logistic regression model trained on the same input features. Hyperparameters are selected on validation data only, and the final test set is evaluated once.

## Results
SparseCellNet reaches a reported macro F1 of 0.87 on the test split. The released artifact contains per-class precision and recall values used by the reproduction script to recalculate the macro F1 summary.

## Data And Code
Artifact: `results_clean.csv`
Script: `reproduce_metric.py`
Reported result: 0.87

## References
- Smith et al. 2024. Compact gene panels for cell-state annotation.
- Jones et al. 2023. Regularized classifiers for single-cell benchmarks.
- Lee et al. 2025. Reproducible evaluation in computational biology.
