# IV. RESULTS

## IV.A Sample Profile and Descriptive Statistics

The final survey dataset included 877 respondents. Gender distribution was 71.95% female (n=626) and 28.05% male (n=244). Age distribution was concentrated in younger participants, with 74.57% aged 18–25 years (n=651), 17.53% aged 26–35 years (n=153), 5.04% aged 36–45 years (n=44), 2.75% aged 46–60 years (n=24), and 0.11% older than 60 years (n=1). Educational level was primarily university or postgraduate, with 78.92% university (n=689) and 13.52% postgraduate (n=118), while high school represented 6.99% (n=61) and primary represented 0.57% (n=5). Marital status was 78.44% single (n=684), 20.99% married (n=183), 0.34% divorced (n=3), and 0.23% widowed (n=2).

Across core belief items, agreement levels were high for two statements and moderate for one statement. For Q11, 51.55% agreed, 34.67% were neutral, and 13.78% disagreed. For Q12, 67.40% agreed, 27.65% were neutral, and 4.95% disagreed. For Q13, 51.95% agreed, 35.86% were neutral, and 12.18% disagreed. Visual summaries of the main question structure, gender-stratified recommendation pattern, and diverging Likert distributions are shown in `../figures/27_donut_main_questions.png`, `../figures/31_gender_recommendation_breakdown.png`, and `../figures/19_likert_diverging_q11_q13.png`.

## IV.B Main Outcome Distributions

The primary attitude outcomes showed mixed acceptance patterns. For safety perception, 23.65% answered yes, 31.23% answered not sure, and 45.12% answered no. For acceptability, 30.80% answered yes, 17.70% answered not sure, and 51.49% answered no. For recommendation willingness, 57.65% answered yes, 11.62% answered not sure, and 30.72% answered no. For social concerns, 37.77% answered yes, 13.09% answered not sure, and 49.14% answered no.

Bivariate correlation patterns among core variables were modest in magnitude. Q11 and Q12 were positively correlated (r=0.269), while Q13 had small negative correlations with Q11 (r=-0.066) and Q12 (r=-0.038). Recommendation had small negative correlations with Q11 (r=-0.086) and Q12 (r=-0.087), and a small positive correlation with Q13 (r=0.077). Acceptance and recommendation were positively correlated (r=0.232). Concern showed weak correlations with all listed variables, including recommendation (r=-0.042).

## IV.C Hierarchical Logistic Regression (Primary Model)

The primary hierarchical logistic regression used a binary recommendation outcome (Q8 yes vs no) with complete-case n=647. Model fit improved across blocks, with McFadden pseudo R² increasing from 0.0040 in Block 1 to 0.0116 in Block 2 and 0.0686 in Block 3. The Block 1 likelihood ratio p-value was 0.5037, Block 2 p-value was 0.0847, and Block 3 p-value was <0.0001.

In the final primary block, gender, Q11, Q13, and fear were statistically significant predictors. Gender had adjusted OR 1.516 (95% CI 1.043 to 2.205, p=0.0294). Q11 had adjusted OR 0.830 (95% CI 0.696 to 0.991, p=0.0396). Q13 had adjusted OR 1.507 (95% CI 1.248 to 1.820, p<0.0001). Fear had adjusted OR 0.504 (95% CI 0.358 to 0.711, p<0.0001). Age, educational level, marital status, prior use, and Q12 were not statistically significant in this final block. The adjusted effect profile is visualized in `../figures/03_primary_adjusted_or_forest.png`.

A separate sensitivity model that added Q6 and Q7 used complete-case n=406 and produced McFadden pseudo R² of 0.2440 (fit type: mle). This model was reported as a sensitivity analysis because Q6 and Q7 are proximal to the recommendation outcome.

## IV.D Multinomial Logistic Regression (No/Yes/Not Sure Structure)

Multinomial logistic regression preserved the three-category recommendation structure with complete-case n=837 and model log-likelihood -748.910 (fit type: mle). Coefficients were estimated for non-reference equations based on the software coding structure.

For the first non-reference equation (Q8=1 vs reference), gender was positively associated with response likelihood (RRR 1.558, 95% CI 1.097 to 2.214, p=0.0133), Q12 was inversely associated (RRR 0.794, 95% CI 0.651 to 0.970, p=0.0239), and Q13 was positively associated (RRR 1.585, 95% CI 1.328 to 1.892, p<0.0001). Other predictors in this equation were not statistically significant.

For the second non-reference equation (Q8=2 vs reference), gender remained statistically significant (RRR 2.171, 95% CI 1.211 to 3.894, p=0.0093), while age, education, marital status, prior use, Q11, Q12, and Q13 were not statistically significant. The comparative predictor pattern is displayed in `../figures/08_multinomial_key_predictor_comparison.png`.

## IV.E The Contact Hypothesis (Users vs Non-Users)

The contact analysis compared Users vs Non-Users using prior use status (users n=127, non-users n=716). Nonparametric tests showed statistically significant group differences across all three core belief items.

For Q11, the user median was 3.00 and the non-user median was 4.00 (Mann-Whitney U p=0.0428), with Cliff’s delta -0.108 and chi-square p=0.1170 (Cramer’s V=0.094, N=843). For Q12, both medians were 4.00 but distributional difference remained significant (Mann-Whitney U p=0.0317), with Cliff’s delta -0.112 and chi-square p=0.0428 (Cramer’s V=0.108, N=840). For Q13, the user median was 4.00 and the non-user median was 3.00 (Mann-Whitney U p=0.0002), with Cliff’s delta 0.198 and chi-square p=0.0027 (Cramer’s V=0.139, N=842).

## IV.F Exploratory Stigma Phenotypes (Clearly Labeled)

Exploratory k-means clustering on standardized Q11–Q13 evaluated k=2, k=3, and k=4. Silhouette scores were 0.274 for k=2, 0.272 for k=3, and 0.303 for k=4, so k=4 was selected by maximum silhouette criterion.

The four profiles had the following mean structures. Profile 0 (n=183) showed Q11 mean 4.404, Q12 mean 4.115, and Q13 mean 4.311. Profile 1 (n=230) showed Q11 mean 2.961, Q12 mean 2.804, and Q13 mean 3.578. Profile 2 (n=232) showed Q11 mean 2.694, Q12 mean 4.250, and Q13 mean 3.720. Profile 3 (n=223) showed Q11 mean 4.359, Q12 mean 4.291, and Q13 mean 2.610. Profile-level mean contrasts are shown in `../figures/14_profile_means_heatmap.png`.

## IV.G Results Summary

The survey included 877 participants and was dominated by female, younger, university-educated, and single respondents. In descriptive outcomes, recommendation willingness had the highest yes proportion (57.65%), while safety and acceptability showed higher no proportions than yes proportions. In the primary hierarchical logistic model (n=647), the strongest statistically supported predictors in the final block were gender, Q11, Q13, and fear. In the multinomial model (n=837), gender remained significant in both non-reference equations, while Q13 and Q12 were significant in one non-reference equation only. In Users vs Non-Users analyses, all core belief items showed significant distributional differences by Mann-Whitney testing, with small effect sizes. Exploratory phenotype analysis identified a four-profile solution with the highest silhouette score among tested cluster counts.
