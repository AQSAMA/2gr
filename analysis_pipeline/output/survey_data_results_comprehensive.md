# Psychiatric Medication Use and Public Acceptance in Iraq — Unified Survey Analysis (N=877)

This script now provides a single unified output with main/clean models and clearly labeled exploratory analyses.

## Main/Clean Analysis (Publication-Ready)

## 1) Hierarchical Block Logistic Regression (Outcome: Q8 Yes vs No)

- Complete-case n (primary hierarchical models): **647**

| Model block | Formula summary | McFadden pseudo R² | LLR p-value |
|---|---|---:|---:|
| Block 1 (mle) | `Recommend_Binary ~ Age_Binary + Gender_Binary + Edu_Binary + Married_Binary` | 0.0040 | 0.5037 |
| Block 2 (mle) | `Recommend_Binary ~ Age_Binary + Gender_Binary + Edu_Binary + Married_Binary + PriorUse_Binary` | 0.0116 | 0.0847 |
| Block 3 (mle) | `Recommend_Binary ~ Age_Binary + Gender_Binary + Edu_Binary + Married_Binary + PriorUse_Binary + Q11 + Q12 + Q13 + Fear_Binary` | 0.0686 | <0.0001 |

### Final Primary Block (Block 3) — Adjusted Odds Ratios

| Predictor | Adjusted OR (95% CI) | p-value |
|---|---:|---:|
| Intercept | 1.128 (0.298 to 4.273) | 0.8597 |
| Age_Binary | 0.961 (0.583 to 1.582) | 0.8752 |
| Gender_Binary | 1.516 (1.043 to 2.205) | 0.0294 |
| Edu_Binary | 1.381 (0.750 to 2.542) | 0.3005 |
| Married_Binary | 1.075 (0.632 to 1.827) | 0.7904 |
| PriorUse_Binary | 1.342 (0.800 to 2.252) | 0.2645 |
| Q11 | 0.830 (0.696 to 0.991) | 0.0396 |
| Q12 | 0.869 (0.701 to 1.078) | 0.2008 |
| Q13 | 1.507 (1.248 to 1.820) | <0.0001 |
| Fear_Binary | 0.504 (0.358 to 0.711) | <0.0001 |

### Sensitivity Model Adding Proximal Beliefs (Q6/Q7)

- Complete-case n (sensitivity model): **406**
- McFadden pseudo R²: **0.2440**
- Fit type: **mle**
- This sensitivity model is reported separately because Q6 and Q7 are conceptually close to Q8 and can dominate explanatory variance.

## 2) Multinomial Logistic Regression Preserving Hesitation (Q8 = No / Yes / Not sure)

- Complete-case n: **837**
- Model log-likelihood: **-748.910**
- Fit type: **mle**

Reference outcome in statsmodels is the lowest coded category; coefficients are shown for non-reference outcome equations.

| Outcome equation | Predictor | Relative risk ratio (95% CI) | p-value |
|---|---|---:|---:|
| Q8=1 vs ref | const | 0.936 (0.264 to 3.317) | 0.9189 |
| Q8=1 vs ref | Age_Binary | 0.947 (0.599 to 1.496) | 0.8139 |
| Q8=1 vs ref | Gender_Binary | 1.558 (1.097 to 2.214) | 0.0133 |
| Q8=1 vs ref | Edu_Binary | 1.177 (0.661 to 2.095) | 0.5797 |
| Q8=1 vs ref | Married_Binary | 0.967 (0.598 to 1.563) | 0.8903 |
| Q8=1 vs ref | PriorUse_Binary | 1.387 (0.863 to 2.229) | 0.1763 |
| Q8=1 vs ref | Q11 | 0.873 (0.742 to 1.028) | 0.1028 |
| Q8=1 vs ref | Q12 | 0.794 (0.651 to 0.970) | 0.0239 |
| Q8=1 vs ref | Q13 | 1.585 (1.328 to 1.892) | <0.0001 |
| Q8=2 vs ref | const | 0.304 (0.046 to 2.013) | 0.2170 |
| Q8=2 vs ref | Age_Binary | 1.094 (0.549 to 2.180) | 0.7983 |
| Q8=2 vs ref | Gender_Binary | 2.171 (1.211 to 3.894) | 0.0093 |
| Q8=2 vs ref | Edu_Binary | 1.300 (0.526 to 3.211) | 0.5692 |
| Q8=2 vs ref | Married_Binary | 1.713 (0.863 to 3.399) | 0.1237 |
| Q8=2 vs ref | PriorUse_Binary | 1.401 (0.704 to 2.789) | 0.3373 |
| Q8=2 vs ref | Q11 | 0.846 (0.662 to 1.080) | 0.1799 |
| Q8=2 vs ref | Q12 | 0.890 (0.660 to 1.199) | 0.4438 |
| Q8=2 vs ref | Q13 | 1.064 (0.820 to 1.381) | 0.6404 |

## Exploratory Analysis (Clearly Labeled)


## 3) Contact Hypothesis: Users vs Non-Users on Core Beliefs (Q11-Q13)

- Users (Q31=1): **127**
- Non-users (Q31=0): **716**

| Item | User median | Non-user median | Mann-Whitney U p-value | Cliff's delta | Chi-square p-value | Cramer's V | N used |
|---|---:|---:|---:|---:|---:|---:|---:|
| Q11 (Doctors prescribe medications more than necessary) | 3.00 | 4.00 | 0.0428 | -0.108 | 0.1170 | 0.094 | 843 |
| Q12 (Most medications cause psychological or physical dependence) | 4.00 | 4.00 | 0.0317 | -0.112 | 0.0428 | 0.108 | 840 |
| Q13 (Modern medications are safer than older ones) | 4.00 | 3.00 | 0.0002 | 0.198 | 0.0027 | 0.139 | 842 |

## 4) Exploratory Stigma Phenotypes (K-Means on Standardized Q11-Q13)

| k | Silhouette score |
|---:|---:|
| 2 | 0.274 |
| 3 | 0.272 |
| 4 | 0.303 |

- Selected k by maximum silhouette: **4**

| Profile | Size n | Q11 mean | Q12 mean | Q13 mean |
|---:|---:|---:|---:|---:|
| 0 | 183 | 4.404 | 4.115 | 4.311 |
| 1 | 230 | 2.961 | 2.804 | 3.578 |
| 2 | 232 | 2.694 | 4.250 | 3.720 |
| 3 | 223 | 4.359 | 4.291 | 2.610 |

## 5) Notes for Manuscript Positioning

- Hierarchical and multinomial modeling are suitable main-text analyses because they preserve response structure and clarify incremental explanatory value.
- K-means profiling should be presented as an exploratory secondary analysis.
- For stronger latent construct validation in future work, ordinal EFA/CFA with polychoric correlations is recommended on appropriately scoped item blocks.
