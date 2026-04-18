# Survey Visualization Summary

This is an auto-generated chart summary created by `analysis_pipeline/visualize.py` from `analysis_pipeline/output/analysis_results.json`.
Generated at: 2026-04-18T10:27:00.669422+00:00

## Chart 01: Hierarchical model pseudo R² by block

![Hierarchical model pseudo R² by block](01_hierarchical_pseudo_r2.png)

**Caption:** Block-wise McFadden pseudo R² from the hierarchical logistic regression.

**Quick analysis:** Block 3 shows the largest increase in pseudo R², indicating the most substantial improvement in model fit.

## Chart 02: LLR significance by hierarchical block

![LLR significance by hierarchical block](02_hierarchical_llr_significance.png)

**Caption:** Transformed LLR p-values for each hierarchical block.

**Quick analysis:** Block 3 achieves statistical significance (p < 0.05), while Blocks 1 and 2 do not reach the conventional threshold.

## Chart 03: Primary adjusted OR forest plot

![Primary adjusted OR forest plot](03_primary_adjusted_or_forest.png)

**Caption:** Adjusted odds ratios with 95% confidence intervals for Block 3 predictors.

**Quick analysis:** 4 predictors are statistically significant at p<0.05, with clear protective and risk-direction effects.

## Chart 04: Primary effect direction chart

![Primary effect direction chart](04_primary_effect_direction_log2or.png)

**Caption:** log2-transformed adjusted odds ratios to show effect direction around zero.

**Quick analysis:** Positive values indicate higher odds of recommending medication, while negative values indicate lower odds.

## Chart 05: Primary predictor significance ranking

![Primary predictor significance ranking](05_primary_predictor_significance.png)

**Caption:** Predictor-level p-value strength for the primary logistic model.

**Quick analysis:** Q13 and Fear_Binary exhibit the lowest p-values among adjusted predictors, indicating the most robust statistical associations.

## Chart 06: Multinomial forest plot (Q8=Yes)

![Multinomial forest plot (Q8=Yes)](06_multinomial_q8yes_rrr_forest.png)

**Caption:** Relative risk ratios for the Q8=Yes outcome equation.

**Quick analysis:** Gender, Q12, and Q13 are the clearest differentiators in the Yes-vs-reference contrast.

## Chart 07: Multinomial forest plot (Q8=Not sure)

![Multinomial forest plot (Q8=Not sure)](07_multinomial_q8unsure_rrr_forest.png)

**Caption:** Relative risk ratios for the Q8=Not sure outcome equation.

**Quick analysis:** Gender remains the main significant factor in the hesitation profile.

## Chart 08: Multinomial key predictor comparison

![Multinomial key predictor comparison](08_multinomial_key_predictor_comparison.png)

**Caption:** Side-by-side RRR values for key predictors across Yes and Not sure outcomes.

**Quick analysis:** Q13 shows a larger relative risk ratio for Yes responses, whereas Q11 and Q12 have relative risk ratios closer to 1.0 in the Not sure equation.

## Chart 09: Multinomial significance heatmap

![Multinomial significance heatmap](09_multinomial_pvalue_heatmap.png)

**Caption:** Heatmap of predictor significance across multinomial outcome equations.

**Quick analysis:** Darker cells identify where evidence is strongest, especially for Q13 in the Yes equation.

## Chart 10: Contact hypothesis median comparison

![Contact hypothesis median comparison](10_contact_group_medians.png)

**Caption:** Users vs non-users median responses for Q11–Q13.

**Quick analysis:** Users show lower skepticism on Q11 and higher confidence on Q13 compared with non-users.

## Chart 11: Contact effect sizes

![Contact effect sizes](11_contact_effect_sizes.png)

**Caption:** Effect-size metrics for group differences in Q11–Q13.

**Quick analysis:** Effects are small but consistent, with Q13 showing the strongest directional separation.

## Chart 12: Contact p-value strength

![Contact p-value strength](12_contact_pvalue_strength.png)

**Caption:** Statistical strength of Mann-Whitney and Chi-square tests for Q11–Q13.

**Quick analysis:** Q13 has the strongest evidence of group separation across both statistical tests.

## Chart 13: Silhouette score trend

![Silhouette score trend](13_silhouette_by_k.png)

**Caption:** Silhouette scores for candidate k values in exploratory profile clustering.

**Quick analysis:** k=4 gives the best separation, matching the final model choice.

## Chart 14: Profile means heatmap

![Profile means heatmap](14_profile_means_heatmap.png)

**Caption:** Heatmap of profile-level means across Q11, Q12, and Q13.

**Quick analysis:** Profiles show distinct belief combinations, especially around confidence in newer medications (Q13).

## Chart 15: Profile size distribution

![Profile size distribution](15_profile_size_distribution.png)

**Caption:** Share of respondents (N=877) in each exploratory stigma profile.

**Quick analysis:** Profile 2 is the largest segment, but the distribution remains relatively balanced overall.

## Chart 16: Gender distribution

![Gender distribution](16_demographics_gender_distribution.png)

**Caption:** Gender composition of the survey sample (N=877).

**Quick analysis:** The sample is predominantly female, which should be considered when interpreting attitude prevalence estimates.

## Chart 17: Age-group distribution

![Age-group distribution](17_demographics_age_distribution.png)

**Caption:** Age-group distribution of respondents (N=877).

**Quick analysis:** Most respondents are in the 18–25 group, so results mainly reflect younger public attitudes.

## Chart 18: Education-level distribution

![Education-level distribution](18_demographics_education_distribution.png)

**Caption:** Education-level distribution among respondents (N=877).

**Quick analysis:** University-level education is the largest category in this sample.

## Chart 19: Diverging Likert chart (Q11–Q13)

![Diverging Likert chart (Q11–Q13)](19_likert_diverging_q11_q13.png)

**Caption:** Disagree/Neutral/Agree percentages for Q11, Q12, and Q13.

**Quick analysis:** Q11 and Q12 lean toward agreement with concern-focused statements, while Q13 shows stronger positive confidence in newer medications.

## Chart 20: Correlation matrix heatmap

![Correlation matrix heatmap](20_correlation_matrix_primary_beliefs.png)

**Caption:** Pearson correlations among core belief items and acceptance/recommendation indicators.

**Quick analysis:** The matrix provides a quick view of how stigma-related beliefs move together and where overlap may influence multivariable modeling.

## Chart 21: Acceptance by prior-use subgroup

![Acceptance by prior-use subgroup](21_acceptance_by_prior_use.png)

**Caption:** Recommendation acceptance rate among respondents with and without prior psychiatric medication use.

**Quick analysis:** The cleaned dataset does not include a direct trusted-source variable, so prior medication exposure is used as the closest subgroup context for acceptance differences.

## Chart 22: Marital-status distribution

![Marital-status distribution](22_demographics_marital_distribution.png)

**Caption:** Marital-status profile of participants (N=877).

**Quick analysis:** Most participants are single, which aligns with the young age structure of the sample.

## Chart 23: Safety-perception distribution

![Safety-perception distribution](23_safety_perception_distribution.png)

**Caption:** Distribution of responses to whether psychiatric medications are safe.

**Quick analysis:** Safety perception is mixed, with a substantial uncertain segment that may be responsive to targeted counseling.

## Chart 24: Acceptability distribution

![Acceptability distribution](24_acceptability_distribution.png)

**Caption:** Distribution of responses about accepting psychiatric medications like chronic-disease treatment.

**Quick analysis:** Negative and uncertain acceptability responses remain prominent, which complements the modeled hesitation findings.

## Chart 25: Recommendation response distribution

![Recommendation response distribution](25_recommendation_distribution.png)

**Caption:** Distribution of responses to recommending psychiatric medications to someone close.

**Quick analysis:** A majority report willingness to recommend, but a notable minority still declines or remains unsure.

## Chart 26: Social-interaction concern distribution

![Social-interaction concern distribution](26_social_concern_distribution.png)

**Caption:** Distribution of concern about interacting with people using psychiatric medications.

**Quick analysis:** Social-contact concern remains common enough to signal persistent stigma in everyday interactions.

## Chart 27: Donut charts for main questions

![Donut charts for main questions](27_donut_main_questions.png)

**Caption:** Donut infographic view for safety, acceptability, and recommendation responses.

**Quick analysis:** This compact format gives a quick social-media-style snapshot of the three core public opinion outcomes.

## Chart 28: Safety waffle chart

![Safety waffle chart](28_waffle_safety_yes_share.png)

**Caption:** 100-cell waffle chart showing the share answering Yes on safety.

**Quick analysis:** The grid format translates percentages into an intuitive 'out of 100 people' visual.

## Chart 29: Safety yes-vs-no chart

![Safety yes-vs-no chart](29_safety_yes_no_decisive.png)

**Caption:** Direct Yes versus No comparison for safety among decisive responses.

**Quick analysis:** This focuses the safety debate on respondents with a clear position.

## Chart 30: Experience-gap chart

![Experience-gap chart](30_experience_gap_recommendation.png)

**Caption:** Recommendation acceptance rates among respondents with and without prior medication experience.

**Quick analysis:** A clear gap between experienced and non-experienced respondents highlights the role of personal exposure.

## Chart 31: Gender breakdown of recommendation opinions

![Gender breakdown of recommendation opinions](31_gender_recommendation_breakdown.png)

**Caption:** Within-gender distribution of Yes/Not sure/No responses for recommendation.

**Quick analysis:** The side-by-side format highlights how recommendation sentiment differs between women and men.
