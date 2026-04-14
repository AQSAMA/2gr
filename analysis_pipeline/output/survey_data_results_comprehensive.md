# Psychiatric Medication Use and Public Acceptance in Iraq — Unified Survey Analysis (N=877)

This script now provides a single unified output with main/clean models and clearly labeled exploratory analyses.

## Main/Clean Analysis (Publication-Ready)

## 1) Hierarchical Block Logistic Regression (Outcome: Q8 Yes vs No)

- Complete-case n (primary hierarchical models): **647**

| Model block | Formula summary | McFadden pseudo R² | LLR p-value |
|---|---|---:|---:|
| Block 1 (regularized) | `Recommend_Binary ~ C(Age_Group3) + C(Q2) + C(Edu_Group3) + C(Marital_Group2)` | 0.0050 | 0.5264 |
| Block 2 (regularized) | `Recommend_Binary ~ C(Age_Group3) + C(Q2) + C(Edu_Group3) + C(Marital_Group2) + PriorUse_Binary` | 0.0127 | 0.1020 |
| Block 3 (regularized) | `Recommend_Binary ~ C(Age_Group3) + C(Q2) + C(Edu_Group3) + C(Marital_Group2) + PriorUse_Binary + Q11 + Q12 + Q13 + Fear_Binary` | 0.0698 | <0.0001 |

### Final Primary Block (Block 3) — Adjusted Odds Ratios

| Predictor | Adjusted OR (95% CI) | p-value |
|---|---:|---:|
| Intercept | NA | 0.9996 |
| C(Age_Group3)[T.1.0] | NA | 0.9996 |
| C(Age_Group3)[T.2.0] | NA | 0.9996 |
| C(Q2)[T.2.0] | 1.505 (1.039 to 2.181) | 0.0307 |
| C(Edu_Group3)[T.3.0] | 1.385 (0.754 to 2.542) | 0.2936 |
| C(Marital_Group2)[T.2.0] | 1.056 (0.653 to 1.710) | 0.8231 |
| PriorUse_Binary | 1.343 (0.800 to 2.254) | 0.2649 |
| Q11 | 0.830 (0.695 to 0.990) | 0.0386 |
| Q12 | 0.869 (0.701 to 1.078) | 0.2029 |
| Q13 | 1.506 (1.245 to 1.820) | <0.0001 |
| Fear_Binary | 0.502 (0.356 to 0.708) | <0.0001 |

### Sensitivity Model Adding Proximal Beliefs (Q6/Q7)

- Complete-case n (sensitivity model): **406**
- McFadden pseudo R²: **0.2440**
- Fit type: **mle**
- This sensitivity model is reported separately because Q6 and Q7 are conceptually close to Q8 and can dominate explanatory variance.

## 2) Multinomial Logistic Regression Preserving Hesitation (Q8 = No / Yes / Not sure)

- Complete-case n: **837**
- Model log-likelihood: **-748.073**
- Fit type: **regularized**

Reference outcome in statsmodels is the lowest coded category; coefficients are shown for non-reference outcome equations.

| Outcome equation | Predictor | Relative risk ratio (95% CI) | p-value |
|---|---|---:|---:|
| Q8=1 vs ref | const | NA | 0.9995 |
| Q8=1 vs ref | Age_Group3_1 | NA | 0.9995 |
| Q8=1 vs ref | Age_Group3_2 | NA | 0.9995 |
| Q8=1 vs ref | Q2_2 | NA | 0.0136 |
| Q8=1 vs ref | Edu_Group3_3 | NA | 0.5632 |
| Q8=1 vs ref | Marital_Group2_2 | NA | 0.8410 |
| Q8=1 vs ref | Q31_1 | NA | 0.1749 |
| Q8=1 vs ref | Q11 | NA | 0.1003 |
| Q8=1 vs ref | Q12 | NA | 0.0245 |
| Q8=1 vs ref | Q13 | NA | <0.0001 |
| Q8=2 vs ref | const | NA | 1.0000 |
| Q8=2 vs ref | Age_Group3_1 | NA | 1.0000 |
| Q8=2 vs ref | Age_Group3_2 | NA | 1.0000 |
| Q8=2 vs ref | Q2_2 | NA | 0.0092 |
| Q8=2 vs ref | Edu_Group3_3 | NA | 0.5992 |
| Q8=2 vs ref | Marital_Group2_2 | NA | 0.0630 |
| Q8=2 vs ref | Q31_1 | NA | 0.3343 |
| Q8=2 vs ref | Q11 | NA | 0.1852 |
| Q8=2 vs ref | Q12 | NA | 0.4262 |
| Q8=2 vs ref | Q13 | NA | 0.6637 |

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

## 5) Exploratory Mediation (Associational): Q31 -> Q6 -> Q8

- Analysis sample (Q31/Q6/Q8 coded as binary Yes/No only): **n=522**
- a-path (Q31 -> Q6) log-odds coefficient: **0.9254**
- b-path (Q6 -> Q8, adjusted for Q31) log-odds coefficient: **2.2889**
- Direct effect c' (Q31 -> Q8 controlling mediator): **0.1838**
- Total effect c (Q31 -> Q8 without mediator): **0.5621**
- Indirect effect a*b (log-odds scale): **2.1181**
- Bootstrap 95% CI for indirect effect: **1.0314 to 3.4909** (successful resamples=1500)
- Interpretation note: this cross-sectional mediation is exploratory and should not be interpreted as causal.

## 6) User-Subset Visual Profile

- Radar chart saved to: `analysis_pipeline/output/user_experience_radar.png`
- Mean raw item values used for radar chart:

| Item | Mean (1-5) |
|---|---:|
| Q15 (I believe psychiatric medications are necessary for my health) | 3.411 |
| Q16 (Psychiatric medications keep me stable) | 3.234 |
| Q17 (Without psychiatric medications, my condition would worsen) | 2.786 |
| Q18 (Psychiatric medications cause bothersome side effects) | 4.161 |
| Q19 (I worry about habituation or addiction to psychiatric medications) | 3.901 |
| Q20 (Psychiatric medications may harm my health in the long term) | 3.928 |

## 7) Notes for Manuscript Positioning

- Hierarchical and multinomial modeling are suitable main-text analyses because they preserve response structure and clarify incremental explanatory value.
- K-means profiling and mediation should be presented as exploratory secondary analyses.
- For stronger latent construct validation in future work, ordinal EFA/CFA with polychoric correlations is recommended on appropriately scoped item blocks.
