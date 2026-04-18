# IV. RESULTS

All numeric results in this chapter are reported directly from `survey_data_results.md` for the unified survey dataset (N=877).

## A. Sample Profile and Descriptive Statistics

The sample was predominantly female (71.95%; male 28.05%), young (18–25 years: 74.57%), and university-educated (university 78.92%; postgraduate 13.52%). Most respondents were single (78.44%), while 20.99% were married. Figure support for this section is provided by the mapped visuals `figures/27_donut_main_questions.png`, `figures/31_gender_recommendation_breakdown.png`, and `figures/19_likert_diverging_q11_q13.png`.

## B. Main Outcome Distributions

For the three core public-opinion outcomes, 23.65% answered Yes, 31.23% Not sure, and 45.12% No for medication safety; 30.80% Yes, 17.70% Not sure, and 51.49% No for social acceptability; and 57.65% Yes, 11.62% Not sure, and 30.72% No for recommendation willingness. For social concerns about interacting with someone taking psychiatric medications, 37.77% answered Yes, 13.09% Not sure, and 49.14% No.

Belief distributions also showed concern-oriented patterns. For Q11 (doctors prescribe more than necessary), 51.55% agreed, 34.67% were neutral, and 13.78% disagreed. For Q12 (most medications cause psychological or physical dependence), 67.40% agreed, 27.65% were neutral, and 4.95% disagreed. For Q13 (modern medications are safer than older ones), 51.95% agreed, 35.86% were neutral, and 12.18% disagreed.

## C. Hierarchical Logistic Regression (Primary Model)

This was the primary confirmatory model. Using complete-case data (n=647), model fit improved across blocks: Block 1 (demographics) had McFadden pseudo R²=0.0040 with LLR p=0.5037; Block 2 (adding prior use) had pseudo R²=0.0116 with LLR p=0.0847; and Block 3 (adding Q11, Q12, Q13, and fear) had pseudo R²=0.0686 with LLR p<0.0001. Figure support is `figures/03_primary_adjusted_or_forest.png`.

In the final primary block, significant adjusted predictors were Gender_Binary (OR 1.516, 95% CI 1.043 to 2.205, p=0.0294), Q11 (OR 0.830, 95% CI 0.696 to 0.991, p=0.0396), Q13 (OR 1.507, 95% CI 1.248 to 1.820, p<0.0001), and Fear_Binary (OR 0.504, 95% CI 0.358 to 0.711, p<0.0001). Non-significant predictors in the same block were Age_Binary (OR 0.961, p=0.8752), Edu_Binary (OR 1.381, p=0.3005), Married_Binary (OR 1.075, p=0.7904), PriorUse_Binary (OR 1.342, p=0.2645), and Q12 (OR 0.869, p=0.2008). The intercept was not significant (OR 1.128, 95% CI 0.298 to 4.273, p=0.8597).

A confirmatory sensitivity model that added Q6 and Q7 used n=406 and showed McFadden pseudo R²=0.2440 (fit type: mle). This model was separated from the primary block sequence due to conceptual proximity between Q6/Q7 and Q8.

## D. Multinomial Logistic Regression (No/Yes/Not Sure Structure)

This was the second confirmatory model and preserved the original No/Yes/Not sure outcome structure for Q8. The complete-case sample was n=837, and model log-likelihood was -748.910 (fit type: mle). Figure support is `figures/08_multinomial_key_predictor_comparison.png`.

In the Q8=1 equation, significant predictors were Gender_Binary (RRR 1.558, 95% CI 1.097 to 2.214, p=0.0133), Q12 (RRR 0.794, 95% CI 0.651 to 0.970, p=0.0239), and Q13 (RRR 1.585, 95% CI 1.328 to 1.892, p<0.0001). Other predictors in this equation were not significant: Age_Binary (p=0.8139), Edu_Binary (p=0.5797), Married_Binary (p=0.8903), PriorUse_Binary (p=0.1763), Q11 (p=0.1028), and the constant (p=0.9189).

In the Q8=2 equation, only Gender_Binary was significant (RRR 2.171, 95% CI 1.211 to 3.894, p=0.0093). Age_Binary (p=0.7983), Edu_Binary (p=0.5692), Married_Binary (p=0.1237), PriorUse_Binary (p=0.3373), Q11 (p=0.1799), Q12 (p=0.4438), Q13 (p=0.6404), and the constant (p=0.2170) were not significant.

## E. The Contact Hypothesis (Users vs Non-Users)

This section reports the confirmatory secondary contact analysis using Users vs Non-Users exactly as coded in the dataset. The comparison groups were Users (Q31=1, n=127) and Non-Users (Q31=0, n=716).

For Q11, users had a lower median (3.00) than non-users (4.00), with Mann-Whitney p=0.0428 and Cliff’s delta=-0.108; chi-square p=0.1170 and Cramer’s V=0.094 (N used=843). For Q12, medians were 4.00 in both groups, but the distribution difference was significant by Mann-Whitney (p=0.0317) with Cliff’s delta=-0.112; chi-square p=0.0428 and Cramer’s V=0.108 (N used=840). For Q13, users had a higher median (4.00) than non-users (3.00), with Mann-Whitney p=0.0002 and Cliff’s delta=0.198; chi-square p=0.0027 and Cramer’s V=0.139 (N used=842).

## F. Exploratory Stigma Phenotypes (Clearly Labeled)

This subsection is exploratory by design. K-means clustering on standardized Q11–Q13 tested k=2, k=3, and k=4, with silhouette scores of 0.274, 0.272, and 0.303, respectively. The selected solution was k=4. Figure support is `figures/14_profile_means_heatmap.png`.

The four profiles were: Profile 0 (n=183; Q11 mean 4.404, Q12 mean 4.115, Q13 mean 4.311), Profile 1 (n=230; Q11 mean 2.961, Q12 mean 2.804, Q13 mean 3.578), Profile 2 (n=232; Q11 mean 2.694, Q12 mean 4.250, Q13 mean 3.720), and Profile 3 (n=223; Q11 mean 4.359, Q12 mean 4.291, Q13 mean 2.610).

## G. Results Summary

The confirmatory analyses showed that model performance improved when belief and concern variables were added to demographics and prior use, with the strongest and most consistent effects involving gender, confidence in newer medications (Q13), and concern-related variables. The multinomial model confirmed that preserving the Not sure response adds structure that differs from simple binary coding. The Users vs Non-Users analysis showed measurable belief-distribution differences, and the stigma phenotype clustering provided an exploratory four-profile structure for future validation work.

<div style="page-break-after: always;"></div>
