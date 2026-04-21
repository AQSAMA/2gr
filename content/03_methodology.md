# III. METHODOLOGY (ORIGINAL CROSS-SECTIONAL STUDY)

## A. Study Design and Setting

This study used an original cross-sectional survey design to examine psychiatric medication use and public acceptance in Iraq. The analytic dataset included 877 respondent records after questionnaire cleaning and standardization, as documented in the unified analysis outputs and preprocessing workflow. The design was observational and non-interventional, and all analyses were conducted on de-identified survey records.

The available materials indicate an Iraq-focused online questionnaire dataset with Arabic item wording translated into English for analysis. The dataset does not include governorate identifiers, institution identifiers, or site-level fields, so the setting is reported as an Iraq-wide online sample rather than a facility-based sample.

**Reporting constraints:** The available project files did not provide a verifiable calendar field or protocol record for the exact data-collection month/year range, did not document the original dissemination channels in a reproducible log, and did not include a formal eligibility sheet beyond what can be inferred from the final dataset structure.

## B. Participants and Sampling

The study analyzed all available respondent records retained after preprocessing of the source questionnaire file. Preprocessing removed the questionnaire label row, normalized text encoding and spacing, mapped Arabic response options to numeric categories, and checked unmapped values before analysis. The cleaned dataset contained 877 participants and represented the achieved analytic sample for descriptive analyses. For inferential models, we applied complete-case handling within each model-specific variable set, so analytic sample size differed by model according to missingness in required fields.

Based on the observed dataset structure and cleaning workflow, inclusion for the analytic dataset required a valid respondent row under the 29-variable questionnaire schema after removal of the non-respondent label row. Exclusion at preprocessing level applied to the label row and any non-mappable residual text entries; no unmapped text values remained after cleaning. For model estimation, additional model-specific exclusion was applied through complete-case handling when required covariates or outcomes were missing. Recruitment is therefore reported as an achieved online non-probability sample captured in the dataset, with no recoverable record of platform-specific invitation channels.

## C. Survey Instrument

The survey instrument included 29 variables covering demographics, public attitudes toward psychiatric medication, medication beliefs, social concern, and prior personal use. Demographic fields captured age group, gender, educational level, and marital status. Core public-acceptance items measured perceived safety, acceptability of psychiatric medication in comparison with treatment for chronic medical conditions, willingness to recommend psychiatric medication, and concern about interacting with a person using psychiatric medication. Belief items included perceptions of overprescribing, dependence risk, and whether modern psychiatric medicines are safer than older options.

The instrument also included an extended block of personal medication-belief items. In the cleaned data, this extended block showed substantial missingness and reflected a subgroup module, so the primary inferential models focused on the core variables that were broadly available across the full sample.

## D. Variables and Operational Definitions

The primary outcome for the main binary logistic models was recommendation willingness, coded from the recommendation item as yes versus no. In the multinomial model, the same outcome preserved three response categories: no, yes, and not sure.

The main predictor set included binary demographic indicators and key belief variables. Age was recoded as 18 to 25 years versus older groups. Education was recoded as university or postgraduate versus lower educational levels. Marital status was recoded as married or previously married versus single. Gender was recoded as female versus male. Prior psychiatric medication use was coded as yes versus no. A concern indicator was coded from the social-concern item as yes versus no. Belief items on overprescribing, dependence, and modern-versus-older medication safety were modeled as ordinal Likert predictors.

To avoid conceptual overlap with the recommendation outcome, two proximal items, perceived safety and disease-model acceptability, were excluded from the primary hierarchical model and tested separately in a sensitivity model.

## E. Data Management and Statistical Analysis

Data management followed a predefined cleaning pipeline. First, the source spreadsheet label row was removed, and all text fields were normalized to handle spacing and encoding inconsistencies. Second, Arabic response categories were mapped to numeric codes using fixed dictionaries for demographics, Likert responses, yes or no items, and yes or no or not sure items. Third, all mapped fields were converted to numeric types where possible, and unmapped residual text values were checked.

Missingness was quantified per variable. Core variables used in the main models had low missingness, while subgroup medication-belief items had high missingness. Therefore, each inferential model used complete-case records for its own covariate set rather than global listwise deletion across all questionnaire items.

The analysis sequence followed the project’s documented workflow used to generate the unified survey results report. We first estimated hierarchical logistic regression in three blocks for recommendation willingness, progressing from demographic factors to prior medication use and then to belief variables and concern indicator. The complete-case sample for this primary hierarchical model set was 647 respondents. We reported adjusted odds ratios with 95% confidence intervals, model likelihood-ratio p-values, and McFadden pseudo R-squared values.

Second, we estimated a sensitivity logistic model that added perceived safety and acceptability items to test robustness while acknowledging their conceptual proximity to the recommendation outcome. The sensitivity complete-case sample was 406 respondents.

Third, we estimated multinomial logistic regression to preserve the no, yes, and not sure structure of recommendation responses and reported relative risk ratios with 95% confidence intervals. The multinomial complete-case sample was 837 respondents.

Fourth, we tested the contact hypothesis as Users vs Non-Users by comparing core belief items with Mann-Whitney U tests and Cliff’s delta effect sizes, with supplementary chi-square and Cramer’s V statistics for association structure.

Fifth, we conducted exploratory stigma-phenotype profiling using k-means clustering on standardized core belief items, selected cluster number by silhouette score, and reported cluster means and sizes as exploratory findings.

## F. Ethical Considerations

The analysis used de-identified survey data and reported aggregate findings only. No personal identifiers were used in the analytic outputs. The available dataset was handled as anonymized observational data for academic research use, and reporting was limited to group-level summaries.

## G. Methodological Limitations

Because the design is cross-sectional, associations should not be interpreted as causal effects. Complete-case modeling can reduce sample size for specific analyses and may introduce selection effects if missingness is not random. The achieved sample was dominated by younger and university-educated respondents, which may limit generalizability to older or less-educated Iraqi populations. Some instrument blocks had substantial missingness, so primary inference relied on the most complete and policy-relevant core variables.
