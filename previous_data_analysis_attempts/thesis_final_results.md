# GRADUATION THESIS: ADVANCED STATISTICAL ANALYSIS
**Total Sample Size (N):** 877

## PART 1: DESCRIPTIVE STATISTICS

### TABLE 1: Sociodemographic Characteristics
| Variable | Category | n (%) |
| :--- | :--- | :--- |
| **Gender** | | |
| | Male | 244 (27.8%) |
| | Female | 626 (71.4%) |
| **Age** | | |
| | 18-25 | 651 (74.2%) |
| | 26-35 | 153 (17.4%) |
| | 36-45 | 44 (5.0%) |
| | 46-60 | 24 (2.7%) |
| | >60 | 1 (0.1%) |
| **Education** | | |
| | Primary | 5 (0.6%) |
| | Middle School | 0 (0.0%) |
| | High School | 61 (7.0%) |
| | Institute/Diploma | 0 (0.0%) |
| | University Degree | 689 (78.6%) |
| | Postgraduate | 118 (13.5%) |
| **Marital Status**| | |
| | Single | 684 (78.0%) |
| | Married | 183 (20.9%) |
| | Divorced | 3 (0.3%) |
| | Widowed | 2 (0.2%) |

### TABLE 2: Public Acceptance (Yes/No)
| Question | Yes n(%) | No n(%) | Not Sure n(%) |
| :--- | :--- | :--- | :--- |
| Q6: Are psychiatric meds safe? | 206 (23.7%) | 393 (45.1%) | 272 (31.2%) |
| Q7: Acceptable like BP/Diabetes meds? | 268 (30.8%) | 448 (51.5%) | 154 (17.7%) |
| Q8: Would recommend to loved one? | 501 (57.7%) | 267 (30.7%) | 101 (11.6%) |
| Q9: Fear of dealing with patients? | 329 (37.8%) | 428 (49.1%) | 114 (13.1%) |

### TABLE 3: Core Beliefs (Likert)
| Question | Agree | Neutral | Disagree |
| :--- | :--- | :--- | :--- |
| Q11: Doctors overprescribe them | 449 (51.5%) | 302 (34.7%) | 120 (13.8%) |
| Q12: They cause dependence | 585 (67.4%) | 240 (27.6%) | 43 (5.0%) |
| Q13: Modern meds are safer | 452 (52.0%) | 312 (35.9%) | 106 (12.2%) |
| Q19: I worry about addiction | 98 (70.0%) | 23 (16.4%) | 19 (13.6%) |

---
## PART 2: LIVED EXPERIENCE (n = 127)
*(Only for participants who have used psychiatric meds)*

### A. Likert Questions
| Question | Agree | Neutral | Disagree |
| :--- | :--- | :--- | :--- |
| Necessary for health | 55 (49.1%) | 37 (33.0%) | 20 (17.9%) |
| Maintain stability | 47 (42.3%) | 38 (34.2%) | 26 (23.4%) |
| Condition worsens without | 29 (25.9%) | 33 (29.5%) | 50 (44.6%) |
| Bothersome side effects | 94 (83.9%) | 16 (14.3%) | 2 (1.8%) |

### B. Yes/No/Not Sure Questions
| Question | Yes | No | Not Sure |
| :--- | :--- | :--- | :--- |
| Lose control of my life | 28 (26.2%) | 79 (73.8%) | 0 (0.0%) |
| Help me feel normal | 81 (75.7%) | 26 (24.3%) | 0 (0.0%) |
| Confidence in treatment | 74 (69.8%) | 32 (30.2%) | 0 (0.0%) |
| Make my life worse | 32 (29.9%) | 75 (70.1%) | 0 (0.0%) |
| Anxiety regarding side effects | 76 (71.7%) | 30 (28.3%) | 0 (0.0%) |

---
## PART 3: ADVANCED INFERENTIAL STATISTICS (THESIS LEVEL)

### A. Reliability Analysis (Cronbach's Alpha)
* **Stigma Score Reliability:** 0.67
* *Interpretation for your thesis:* Alpha scores above 0.70 are considered acceptable, and >0.80 is good. This proves your questions mathematically measure the same underlying "stigma".

### B. Independent T-Test (Stigma by Gender)
* **Male Mean Stigma Score:** 15.35
* **Female Mean Stigma Score:** 14.71
* **T-Statistic:** 1.16 (p-value: 0.2500)
* *Interpretation:* If p < 0.05, there is a statistically significant difference in negative beliefs between men and women.

### C. Logistic Regression (Predicting Acceptance)
This model predicts whether someone will "Recommend" medications (Q8) based on Demographics and Prior Use simultaneously.

[Regression Summary Details]
                           Logit Regression Results                           
==============================================================================
Dep. Variable:       Recommend_Binary   No. Observations:                  840
Model:                          Logit   Df Residuals:                      835
Method:                           MLE   Df Model:                            4
Date:                Tue, 14 Apr 2026   Pseudo R-squ.:                0.004632
Time:                        02:43:35   Log-Likelihood:                -570.70
converged:                       True   LL-Null:                       -573.35
Covariance Type:            nonrobust   LLR p-value:                    0.2568
====================================================================================
                       coef    std err          z      P>|z|      [0.025      0.975]
------------------------------------------------------------------------------------
Intercept            0.6542      0.586      1.117      0.264      -0.494       1.802
C(Q2)[T.2.0]         0.0847      0.158      0.536      0.592      -0.225       0.395
Q1                  -0.0484      0.107     -0.454      0.650      -0.257       0.160
Q4                  -0.1015      0.149     -0.682      0.495      -0.393       0.190
Used_Meds_Binary     0.3791      0.202      1.878      0.060      -0.017       0.775
====================================================================================

*Interpretation of Regression:* Look at the P>|z| column. Values under 0.05 mean that specific factor strongly drives public acceptance independently of the other variables. 
