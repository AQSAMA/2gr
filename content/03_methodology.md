# III. METHODOLOGY (ORIGINAL CROSS-SECTIONAL STUDY)

## A. Study Design and Setting

This study used an original cross-sectional survey design to measure public views on psychiatric medications in Iraq at one time point. The analytical dataset contained 877 responses, and all inferential analyses were conducted on this survey dataset as reported in `survey_data_results.md`.

## B. Participants and Sampling

Participants were members of the Iraqi public who completed the survey instrument. The achieved sample size was 877. The sample was analytically retained with item-level complete-case handling for each model, so the effective sample size varied by analysis depending on missing responses in model variables.

## C. Survey Instrument

The questionnaire included sociodemographic items and belief/attitude items related to psychiatric medication use. Demographic variables included age (Q1), gender (Q2), educational level (Q4), and marital status (Q5). Core outcome and perception items included recommendation willingness (Q8), social concern (Q9), belief items on prescribing and dependence (Q11 and Q12), confidence in newer medications (Q13), and prior personal use history (Q31). Response structures included binary and three-category public-attitude items (No/Yes/Not sure) and five-point Likert items.

## D. Variables and Operational Definitions

The primary confirmatory outcome was recommendation willingness (Q8). For binary logistic modeling, Q8 was recoded as `Recommend_Binary` with Yes=1 and No=0, while Not sure responses were excluded from that binary model. For multinomial modeling, Q8 was preserved as a three-category outcome (No/Yes/Not sure). The demographic predictors were recoded into binary covariates: `Age_Binary` (18–25 vs older groups), `Gender_Binary` (female vs male coding), `Edu_Binary` (university/postgraduate vs lower education), and `Married_Binary` (ever-married categories vs single). `PriorUse_Binary` was derived from Q31 (Users vs Non-Users), and `Fear_Binary` was derived from Q9 (Yes vs No). Belief predictors Q11, Q12, and Q13 were modeled as ordinal Likert scores.

## E. Data Management and Statistical Analysis

The analysis started with descriptive summaries for demographics, core outcome distributions, and key belief distributions. Confirmatory modeling then followed a hierarchical block logistic regression pipeline for the binary outcome (Q8 Yes vs No), using complete-case data (n=647). Block 1 included demographic covariates only. Block 2 added prior medication use. Block 3 added belief and concern variables (Q11, Q12, Q13, and Fear_Binary). Incremental model fit was evaluated using McFadden pseudo R² and likelihood-ratio test p-values.

A predefined sensitivity model added proximal belief items Q6 and Q7 to the primary binary framework and was reported separately (complete-case n=406) because these items are conceptually close to Q8 and may dominate explanatory variance.

A second confirmatory model was a multinomial logistic regression that preserved hesitation in Q8 (No/Yes/Not sure), fit on complete-case data (n=837). Results were reported as relative risk ratios with 95% confidence intervals and p-values.

Secondary hypothesis testing evaluated the contact hypothesis using Users vs Non-Users (Q31) on Q11–Q13. Group comparisons used Mann-Whitney U tests, Cliff’s delta effect sizes, and chi-square tests with Cramer’s V.

Exploratory profiling used k-means clustering on standardized Q11–Q13 scores, testing k=2, k=3, and k=4 and selecting the profile solution by maximum silhouette score.

## F. Ethical Considerations

The analytical file contained de-identified coded survey responses, and no direct personal identifiers were included in the dataset used for analysis. Results are reported in aggregate form to protect participant privacy.

## G. Methodological Limitations

Because this was a cross-sectional survey, the analyses identify associations rather than causal effects. The sample composition was not demographically balanced, with females representing 71.95% of respondents, participants aged 18–25 representing 74.57%, and university-educated participants representing 78.92%. Complete-case modeling reduced analyzable observations in inferential models (n=647 in the primary hierarchical models and n=406 in the Q6/Q7 sensitivity model), which may introduce selection effects. All outcomes and predictors were self-reported, so response bias and social desirability bias remain possible. The stigma-phenotype analysis was exploratory and should be interpreted as hypothesis-generating rather than confirmatory.

<div style="page-break-after: always;"></div>
