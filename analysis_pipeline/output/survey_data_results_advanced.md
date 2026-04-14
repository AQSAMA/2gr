# Advanced Statistical Extension — Psychiatric Medication Use and Public Acceptance in Iraq (N=877)

This report appends advanced analyses to the baseline script without replacing existing baseline outputs.

## 1) Hierarchical Block Logistic Regression (Outcome: Q8 Yes vs No)

- Complete-case n (primary hierarchical models): **647**

| Model block | Formula summary | McFadden pseudo R² | LLR p-value |
|---|---|---:|---:|
| Block 1 (mle) | `Recommend_Binary ~ C(Age_Group3) + C(Q2) + C(Edu_Group3) + C(Marital_Group2)` | 0.0050 | 0.5264 |
| Block 2 (mle) | `Recommend_Binary ~ C(Age_Group3) + C(Q2) + C(Edu_Group3) + C(Marital_Group2) + PriorUse_Binary` | 0.0127 | 0.1020 |
| Block 3 (mle) | `Recommend_Binary ~ C(Age_Group3) + C(Q2) + C(Edu_Group3) + C(Marital_Group2) + PriorUse_Binary + Q11 + Q12 + Q13 + Fear_Binary` | -inf | 1.0000 |

### Final Primary Block (Block 3) — Adjusted Odds Ratios

| Predictor | Adjusted OR (95% CI) | p-value |
|---|---:|---:|
| Intercept | 0.000 (0.000 to 0.000) | <0.0001 |
| C(Age_Group3)[T.1.0] | 485165195.410 (485165195.410 to 485165195.410) | <0.0001 |
| C(Age_Group3)[T.2.0] | 485165195.410 (485165195.410 to 485165195.410) | <0.0001 |
| C(Q2)[T.2.0] | 1.546 (1.067 to 2.241) | 0.0215 |
| C(Edu_Group3)[T.3.0] | 1.429 (0.779 to 2.622) | 0.2483 |
| C(Marital_Group2)[T.2.0] | 1.098 (0.677 to 1.781) | 0.7041 |
| PriorUse_Binary | 1.335 (0.795 to 2.242) | 0.2738 |
| Q11 | 0.835 (0.700 to 0.997) | 0.0463 |
| Q12 | 0.881 (0.710 to 1.092) | 0.2479 |
| Q13 | 1.535 (1.269 to 1.856) | <0.0001 |
| Fear_Binary | 0.510 (0.362 to 0.720) | 0.0001 |

### Sensitivity Model Adding Proximal Beliefs (Q6/Q7)

- Complete-case n (sensitivity model): **406**
- McFadden pseudo R²: **0.2440**
- Fit type: **mle**
- This sensitivity model is reported separately because Q6 and Q7 are conceptually close to Q8 and can dominate explanatory variance.

## 2) Multinomial Logistic Regression Preserving Hesitation (Q8 = No / Yes / Not sure)

- Complete-case n: **837**
- Model log-likelihood: **-748.073**

Reference outcome in statsmodels is the lowest coded category; coefficients are shown for non-reference outcome equations.

| Outcome equation | Predictor | Relative risk ratio (95% CI) | p-value |
|---|---|---:|---:|
| Q8=1 vs ref | const | NA | NA |
| Q8=1 vs ref | Age_Group3_1 | NA | NA |
| Q8=1 vs ref | Age_Group3_2 | NA | NA |
| Q8=1 vs ref | Q2_2 | 1.547 (1.094 to 2.187) | 0.0136 |
| Q8=1 vs ref | Edu_Group3_3 | 1.185 (0.667 to 2.107) | 0.5632 |
| Q8=1 vs ref | Marital_Group2_2 | 0.956 (0.616 to 1.483) | 0.8410 |
| Q8=1 vs ref | Q31_1 | 1.389 (0.864 to 2.232) | 0.1749 |
| Q8=1 vs ref | Q11 | 0.872 (0.741 to 1.027) | 0.1003 |
| Q8=1 vs ref | Q12 | 0.795 (0.651 to 0.971) | 0.0245 |
| Q8=1 vs ref | Q13 | 1.584 (1.326 to 1.892) | <0.0001 |
| Q8=2 vs ref | const | 0.007 (0.000 to 485165195.410) | 1.0000 |
| Q8=2 vs ref | Age_Group3_1 | 52.464 (0.000 to 485165195.410) | 1.0000 |
| Q8=2 vs ref | Age_Group3_2 | 38.775 (0.000 to 485165195.410) | 1.0000 |
| Q8=2 vs ref | Q2_2 | 2.157 (1.209 to 3.848) | 0.0092 |
| Q8=2 vs ref | Edu_Group3_3 | 1.273 (0.517 to 3.137) | 0.5992 |
| Q8=2 vs ref | Marital_Group2_2 | 1.761 (0.970 to 3.198) | 0.0630 |
| Q8=2 vs ref | Q31_1 | 1.404 (0.705 to 2.797) | 0.3343 |
| Q8=2 vs ref | Q11 | 0.847 (0.663 to 1.083) | 0.1852 |
| Q8=2 vs ref | Q12 | 0.886 (0.657 to 1.194) | 0.4262 |
| Q8=2 vs ref | Q13 | 1.060 (0.816 to 1.376) | 0.6637 |

## 3) Contact Hypothesis: Users vs Non-Users on Core Beliefs (Q11-Q13)

- Users (Q31=1): **127**
- Non-users (Q31=0): **716**

| Item | User median | Non-user median | Mann-Whitney U p-value | Cliff's delta | Chi-square p-value | Cramer's V | N used |
|---|---:|---:|---:|---:|---:|---:|---:|
| Q11 (الأطباء يصفون الأدوية أكثر مما يجب) | 3.00 | 4.00 | 0.0428 | -0.108 | 0.1170 | 0.094 | 843 |
| Q12 (معظم الأدوية تسبب اعتمادًا نفسيًا أو جسديًا) | 4.00 | 4.00 | 0.0317 | -0.112 | 0.0428 | 0.108 | 840 |
| Q13 (الأدوية الحديثة أكثر أمانًا من القديمة) | 4.00 | 3.00 | 0.0002 | 0.198 | 0.0027 | 0.139 | 842 |

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

- Radar chart saved to: `/home/runner/work/2gr/2gr/analysis_pipeline/output/user_experience_radar.png`
- Mean raw item values used for radar chart:

| Item | Mean (1-5) |
|---|---:|
| Q15 (أعتقد أن الأدوية النفسية ضرورية لصحتي) | 3.411 |
| Q16 (الأدوية النفسية تحافظ على استقراري) | 3.234 |
| Q17 (بدون الأدوية النفسية ستتدهور حالتي) | 2.786 |
| Q18 (الأدوية النفسية تسبب آثارًا جانبية مزعجة) | 4.161 |
| Q19 (أشعر بالقلق من التعود أو الإدمان على الأدوية النفسية) | 3.901 |
| Q20 (الأدوية النفسية قد تضر بصحتي على المدى الطويل) | 3.928 |

## 7) Notes for Manuscript Positioning

- Hierarchical and multinomial modeling are suitable main-text analyses because they preserve response structure and clarify incremental explanatory value.
- K-means profiling and mediation should be presented as exploratory secondary analyses.
- For stronger latent construct validation in future work, ordinal EFA/CFA with polychoric correlations is recommended on appropriately scoped item blocks.
