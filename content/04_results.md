# IV. RESULTS

The survey enrolled 877 respondents and produced the data summarized in the tables below. The full standalone survey report is available as a companion DOCX (`survey_results.docx`). Section IV.A onwards interprets these results in detail.

## Sample Demographics

| Variable | Category | Count | % |
|---|---|---:|---:|
| Gender | Female | 626 | 71.95 |
| Gender | Male | 244 | 28.05 |
| Age | 18–25 | 651 | 74.57 |
| Age | 26–35 | 153 | 17.53 |
| Age | 36–45 | 44 | 5.04 |
| Age | 46–60 | 24 | 2.75 |
| Age | > 60 | 1 | 0.11 |
| Education | University | 689 | 78.92 |
| Education | Postgraduate | 118 | 13.52 |
| Education | High School | 61 | 6.99 |
| Education | Primary | 5 | 0.57 |
| Marital status | Single | 684 | 78.44 |
| Marital status | Married | 183 | 20.99 |
| Marital status | Divorced | 3 | 0.34 |
| Marital status | Widowed | 2 | 0.23 |

## Main Attitudes and Beliefs

| Item | Yes (%) | Not sure (%) | No (%) |
|---|---:|---:|---:|
| Q6 — Safety perception | 23.65 | 31.23 | 45.12 |
| Q7 — Acceptability | 30.80 | 17.70 | 51.49 |
| Q8 — Recommendation willingness | 57.65 | 11.62 | 30.72 |
| Q9 — Social concern | 37.77 | 13.09 | 49.14 |

| Belief item (5-point Likert) | Disagree (%) | Neutral (%) | Agree (%) |
|---|---:|---:|---:|
| Q11 — Doctors prescribe medications more than necessary | 13.78 | 34.67 | 51.55 |
| Q12 — Most medications cause psychological or physical dependence | 4.95 | 27.65 | 67.40 |
| Q13 — Modern medications are safer than older ones | 12.18 | 35.86 | 51.95 |

## Hierarchical Logistic Regression — Final Block (n = 647)

| Predictor | Adjusted OR (95% CI) | p-value |
|---|---:|---:|
| Gender (female) | 1.516 (1.043–2.205) | 0.0294 |
| Age (18–25) | 0.961 (0.583–1.582) | 0.8752 |
| Education (university or postgraduate) | 1.381 (0.750–2.542) | 0.3005 |
| Marital status (married or previously married) | 1.075 (0.632–1.827) | 0.7904 |
| Prior psychiatric medication use | 1.342 (0.800–2.252) | 0.2645 |
| Q11 — Overprescription belief | 0.830 (0.696–0.991) | 0.0396 |
| Q12 — Dependence belief | 0.869 (0.701–1.078) | 0.2008 |
| Q13 — Modern safety belief | 1.507 (1.248–1.820) | < 0.0001 |
| Fear of psychiatric medication | 0.504 (0.358–0.711) | < 0.0001 |

Hierarchical model fit improved across blocks: McFadden pseudo R² rose from 0.0040 in Block 1 (demographics only) to 0.0116 in Block 2 (adding prior use) and 0.0686 in Block 3 (adding belief items and fear), with the Block 3 likelihood-ratio p-value reaching < 0.0001.

## Multinomial Logistic Regression (n = 837)

| Predictor | RRR Yes vs No (95% CI) | p (Yes) | RRR Not sure vs No (95% CI) | p (Not sure) |
|---|---:|---:|---:|---:|
| Gender (female) | 1.558 (1.097–2.214) | 0.0133 | 2.171 (1.211–3.894) | 0.0093 |
| Age (18–25) | 0.947 (0.599–1.496) | 0.8139 | 1.094 (0.549–2.180) | 0.7983 |
| Education (university or postgraduate) | 1.177 (0.661–2.095) | 0.5797 | 1.300 (0.526–3.211) | 0.5692 |
| Marital status (married or previously married) | 0.967 (0.598–1.563) | 0.8903 | 1.713 (0.863–3.399) | 0.1237 |
| Prior psychiatric medication use | 1.387 (0.863–2.229) | 0.1763 | 1.401 (0.704–2.789) | 0.3373 |
| Q11 — Overprescription belief | 0.873 (0.742–1.028) | 0.1028 | 0.846 (0.662–1.080) | 0.1799 |
| Q12 — Dependence belief | 0.794 (0.651–0.970) | 0.0239 | 0.890 (0.660–1.199) | 0.4438 |
| Q13 — Modern safety belief | 1.585 (1.328–1.892) | < 0.0001 | 1.064 (0.820–1.381) | 0.6404 |

## Contact Hypothesis: Users vs Non-Users on Core Beliefs

| Belief item | User median | Non-user median | Mann-Whitney U p | Cliff's delta |
|---|---:|---:|---:|---:|
| Q11 — Overprescription | 3.00 | 4.00 | 0.0428 | −0.108 |
| Q12 — Dependence | 4.00 | 4.00 | 0.0317 | −0.112 |
| Q13 — Modern safety | 4.00 | 3.00 | 0.0002 | 0.198 |

Users (Q31 = yes): n = 127. Non-users: n = 716.

## Exploratory Stigma Phenotypes (k = 4 by silhouette)

| Profile | n | Q11 mean | Q12 mean | Q13 mean |
|---:|---:|---:|---:|---:|
| 0 | 183 | 4.404 | 4.115 | 4.311 |
| 1 | 230 | 2.961 | 2.804 | 3.578 |
| 2 | 232 | 2.694 | 4.250 | 3.720 |
| 3 | 223 | 4.359 | 4.291 | 2.610 |

Silhouette scores favored k = 4 (silhouette 0.303) over k = 2 (0.274) and k = 3 (0.272). These profiles are exploratory groupings, not confirmed latent classes.

## IV.A Sample Profile and Descriptive Statistics

The final survey dataset included 877 respondents, and all percentages in this chapter follow the denominator policy defined in Methodology: percentages are reported as the percentage of valid responses for that item for descriptives, while model findings use model-specific complete-case denominators. Demographic distributions were therefore calculated as percentage of valid responses for that item (gender n=870, age n=873, educational level n=873, marital status n=872). Gender distribution was 71.95% female (n=626) and 28.05% male (n=244), as percentage of valid responses for that item. Age distribution was concentrated in younger participants, with 74.57% aged 18–25 years (n=651), 17.53% aged 26–35 years (n=153), 5.04% aged 36–45 years (n=44), 2.75% aged 46–60 years (n=24), and 0.11% older than 60 years (n=1), as percentage of valid responses for that item. Educational level was primarily university or postgraduate, with 78.92% university (n=689) and 13.52% postgraduate (n=118), while high school represented 6.99% (n=61) and primary represented 0.57% (n=5), as percentage of valid responses for that item. Marital status was 78.44% single (n=684), 20.99% married (n=183), 0.34% divorced (n=3), and 0.23% widowed (n=2), as percentage of valid responses for that item.

To keep model reporting readable, this chapter repeats each questionnaire code with a brief definition when it appears. Q6 refers to safety perception of psychiatric medication, Q7 refers to acceptability of psychiatric medication, Q8 refers to willingness to recommend psychiatric medication, and Q9 refers to social concern about interacting with a person who uses psychiatric medication. Q11 refers to the belief that doctors prescribe psychiatric medications more than necessary, Q12 refers to the belief that most psychiatric medications cause psychological or physical dependence, Q13 refers to the belief that modern psychiatric medications are safer than older ones, and Q31 refers to prior psychiatric medication use status.

Across core belief items, agreement levels were high for two statements and moderate for one statement. For Q11 (doctors prescribe psychiatric medications more than necessary), 51.55% agreed, 34.67% were neutral, and 13.78% disagreed. For Q12 (most psychiatric medications cause psychological or physical dependence), 67.40% agreed, 27.65% were neutral, and 4.95% disagreed. For Q13 (modern psychiatric medications are safer than older ones), 51.95% agreed, 35.86% were neutral, and 12.18% disagreed. The main question structure is shown in [figures/27_donut_main_questions.png](../figures/27_donut_main_questions.png). The gender-stratified recommendation pattern is shown in [figures/31_gender_recommendation_breakdown.png](../figures/31_gender_recommendation_breakdown.png). The diverging Likert distribution for Q11 and Q13 is shown in [figures/19_likert_diverging_q11_q13.png](../figures/19_likert_diverging_q11_q13.png).

## IV.B Main Outcome Distributions

The primary attitude outcomes showed mixed acceptance patterns. For Q6 (safety perception), 23.65% answered yes, 31.23% answered not sure, and 45.12% answered no. For Q7 (acceptability), 30.80% answered yes, 17.70% answered not sure, and 51.49% answered no. For Q8 (recommendation willingness), 57.65% answered yes, 11.62% answered not sure, and 30.72% answered no. For Q9 (social concern), 37.77% answered yes, 13.09% answered not sure, and 49.14% answered no.

Bivariate correlations among core variables were as follows: Q11 (belief that doctors prescribe psychiatric medications more than necessary) with Q12 (belief that most psychiatric medications cause psychological or physical dependence), r=0.269; Q13 (belief that modern psychiatric medications are safer than older ones) with Q11, r=-0.066; Q13 with Q12, r=-0.038; recommendation willingness (Q8) with Q11, r=-0.086; recommendation willingness (Q8) with Q12, r=-0.087; recommendation willingness (Q8) with Q13, r=0.077; acceptability (Q7) with recommendation willingness (Q8), r=0.232; and social concern (Q9) with recommendation willingness (Q8), r=-0.042.

## IV.C Hierarchical Logistic Regression (Primary Model)

The primary hierarchical logistic regression used a binary recommendation outcome (Q8, willingness to recommend psychiatric medication, yes vs no) with complete-case n=647. Model fit improved across blocks, with McFadden pseudo R² increasing from 0.0040 in Block 1 to 0.0116 in Block 2 and 0.0686 in Block 3. The Block 1 likelihood ratio p-value was 0.5037, Block 2 p-value was 0.0847, and Block 3 p-value was <0.0001.

In the final primary block, the largest directional effect was fear, which was associated with substantially lower recommendation odds (adjusted OR 0.504, 95% CI 0.358 to 0.711, p<0.0001). Q13 (belief that modern psychiatric medications are safer than older ones) showed a moderate positive effect size, with higher confidence in newer medications associated with higher recommendation odds (adjusted OR 1.507, 95% CI 1.248 to 1.820, p<0.0001). Gender showed a smaller-to-moderate positive shift (adjusted OR 1.516, 95% CI 1.043 to 2.205, p=0.0294), while Q11 (belief that doctors prescribe psychiatric medications more than necessary) showed a small inverse effect (adjusted OR 0.830, 95% CI 0.696 to 0.991, p=0.0396). Age, educational level, marital status, prior use (Q31), and Q12 (belief that most psychiatric medications cause psychological or physical dependence) were not statistically significant in this final block. The adjusted effect profile is visualized in [figures/03_primary_adjusted_or_forest.png](../figures/03_primary_adjusted_or_forest.png).

A separate sensitivity model that added Q6 (safety perception) and Q7 (acceptability) used complete-case n=406 and produced McFadden pseudo R² of 0.2440 (fit type: mle). This model was reported as a sensitivity analysis because Q6 and Q7 are proximal to the recommendation outcome.

## IV.D Multinomial Logistic Regression (No/Yes/Not Sure Structure)

Multinomial logistic regression preserved the three-category recommendation structure with complete-case n=837 and model log-likelihood -748.910 (fit type: mle). The outcome categories were coded as No (reference), Yes, and Not sure, corresponding to Q8=0, Q8=1, and Q8=2.

For the first non-reference equation (Q8=1 Yes vs reference No, where Q8 is willingness to recommend psychiatric medication), Q13 (belief that modern psychiatric medications are safer than older ones) showed the strongest positive practical shift (RRR 1.585, 95% CI 1.328 to 1.892, p<0.0001), with gender showing a moderate positive shift (RRR 1.558, 95% CI 1.097 to 2.214, p=0.0133). Q12 (belief that most psychiatric medications cause psychological or physical dependence) showed a small-to-moderate inverse shift (RRR 0.794, 95% CI 0.651 to 0.970, p=0.0239). Other predictors in this equation were not statistically significant.

For the second non-reference equation (Q8=2 Not sure vs reference No, where Q8 is willingness to recommend psychiatric medication), gender showed the largest shift in the multinomial model (RRR 2.171, 95% CI 1.211 to 3.894, p=0.0093), indicating a stronger practical effect than in the Yes-vs-No equation, while age, education, marital status, prior use (Q31, prior psychiatric medication use), Q11 (belief that doctors prescribe psychiatric medications more than necessary), Q12 (belief that most psychiatric medications cause psychological or physical dependence), and Q13 (belief that modern psychiatric medications are safer than older ones) were not statistically significant. The comparative predictor pattern is displayed in [figures/08_multinomial_key_predictor_comparison.png](../figures/08_multinomial_key_predictor_comparison.png).

## IV.E The Contact Hypothesis (Users vs Non-Users)

The contact analysis compared Users vs Non-Users using prior use status from Q31 (prior psychiatric medication use; Users n=127, Non-Users n=716). Mann-Whitney U tests were statistically significant for Q11 (belief that doctors prescribe psychiatric medications more than necessary), Q12 (belief that most psychiatric medications cause psychological or physical dependence), and Q13 (belief that modern psychiatric medications are safer than older ones), while chi-square tests were statistically significant for Q12 and Q13 but not for Q11.

For Q11 (belief that doctors prescribe psychiatric medications more than necessary), the Users median was 3.00 and the Non-Users median was 4.00, with small inverse practical differences (Cliff’s delta -0.108; Cramer’s V=0.094), Mann-Whitney U p=0.0428, chi-square p=0.1170, and N=843. For Q12 (belief that most psychiatric medications cause psychological or physical dependence), both medians were 4.00, with small inverse practical differences (Cliff’s delta -0.112; Cramer’s V=0.108), Mann-Whitney U p=0.0317, chi-square p=0.0428, and N=840. For Q13 (belief that modern psychiatric medications are safer than older ones), the Users median was 4.00 and the Non-Users median was 3.00, with the largest contact effect in this section, approaching moderate by rank effect size (Cliff’s delta 0.198) and remaining small-to-moderate by nominal association (Cramer’s V=0.139), Mann-Whitney U p=0.0002, chi-square p=0.0027, and N=842.

## IV.F Exploratory Stigma Phenotypes (Clearly Labeled)

Exploratory k-means clustering on standardized Q11–Q13 (Q11: belief that doctors prescribe psychiatric medications more than necessary; Q12: belief that most psychiatric medications cause psychological or physical dependence; Q13: belief that modern psychiatric medications are safer than older ones) evaluated k=2, k=3, and k=4. Silhouette scores were 0.274 for k=2, 0.272 for k=3, and 0.303 for k=4, so k=4 was selected by maximum silhouette criterion. These k-means profiles are data-driven exploratory groupings, not confirmed latent classes. The silhouette values indicate relative fit among the tested k values in this dataset, and they do not establish a definitive underlying class structure.

The four profiles had the following mean structures. Profile 0 (n=183) showed Q11 mean 4.404, Q12 mean 4.115, and Q13 mean 4.311. Profile 1 (n=230) showed Q11 mean 2.961, Q12 mean 2.804, and Q13 mean 3.578. Profile 2 (n=232) showed Q11 mean 2.694, Q12 mean 4.250, and Q13 mean 3.720. Profile 3 (n=223) showed Q11 mean 4.359, Q12 mean 4.291, and Q13 mean 2.610. Profile-level mean contrasts are shown in [figures/14_profile_means_heatmap.png](../figures/14_profile_means_heatmap.png).

## IV.G Results Summary

The survey included 877 participants and showed a sample pattern with higher female representation and concentration in younger, university-educated, and single respondents based on variable-specific valid denominators. In descriptive outcomes, recommendation willingness had the highest yes proportion (57.65%), while safety and acceptability showed higher no proportions than yes proportions. In the primary hierarchical logistic model (n=647), the strongest statistically supported predictors in the final block were gender, Q11, Q13, and fear. In the multinomial model (n=837), gender remained significant in both non-reference equations, while Q13 and Q12 were significant in one non-reference equation only. In Users vs Non-Users analyses, Mann-Whitney tests were significant for Q11, Q12, and Q13, and chi-square tests were significant for Q12 and Q13 only. Exploratory phenotype analysis identified a four-profile solution with the highest silhouette score among tested cluster counts.

<div style="page-break-after: always;"></div>
