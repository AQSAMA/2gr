# Research Paper Outline: Psychiatric Medication Use and Public Acceptance in Iraq
**Type:** Original Cross-Sectional Research Study

## Core Rule for This Outline
1. **Study results are reported ONLY from `survey_data_results.md`.**
2. `sources/` are used strictly for background, framework, and comparison in Chapters I, II, and V.
3. `figures/` are used to present visual outputs from the analyzed survey dataset in Chapter IV.

## ABSTRACT
*Scope Rule: Must summarize Background, Methods, Results (with hard numbers from the dataset), and Conclusion.*

## I. INTRODUCTION
*   **A. Background and Context** (The mental health burden in Iraq)
*   **B. Problem Statement** (The evidence gap regarding public acceptance)
*   **C. Study Objectives** (1. Evaluate recommendation willingness[Q8]. 2. Identify demographic/cognitive predictors. 3. Explore latent stigma phenotypes.)
*   **D. Study Significance** (Value of primary empirical data for Iraqi pharmacists and policymakers)

## II. LITERATURE REVIEW (SUPPORTIVE CONTEXT)
*Scope Rule: This chapter gives conceptual and regional context. It does NOT report the new survey as literature.*
*   **A. Stigma and Public Attitudes** (e.g., Sadik et al., 2010; Booth et al., 2024)
*   **B. Medication Beliefs and Acceptance** (e.g., Horne et al., 1999)
*   **C. Adherence and Determinants**
*   **D. Iraqi and Regional Service Realities**

## III. METHODOLOGY (ORIGINAL CROSS-SECTIONAL STUDY)
*Scope Rule: Delete all previous references to literature search strategies (PubMed, Scopus, etc.). Describe the actual survey.*
*   **A. Study Design and Setting** (Cross-sectional survey in Iraq)
*   **B. Participants and Sampling** (N=877, eligibility, recruitment)
*   **C. Survey Instrument and Variables** (Demographics, Likert-scale core beliefs Q11-Q13, general attitudes Q6-Q9, prior use Q31)
*   **D. Data Management and Statistical Analysis** (Describe the Python pipeline: Hierarchical Block Logistic Regression, Multinomial Logistic Regression, Mann-Whitney U for Contact Hypothesis, and K-Means clustering K=4)
*   **E. Ethical Considerations**

## IV. RESULTS (PRIMARY SURVEY FINDINGS)
*Scope Rule: Numeric results here come ONLY from `survey_data_results.md`. Must map the exact figures.*
*   **A. Sample Profile and Descriptive Statistics** (Integrate `figures/27_donut_main_questions.png`, `figures/31_gender_recommendation_breakdown.png`, `figures/19_likert_diverging_q11_q13.png`)
*   **B. Primary Analysis 1: Predictors of Recommendation Willingness** (Hierarchical Logistic Regression - Integrate `figures/03_primary_adjusted_or_forest.png`)
*   **C. Primary Analysis 2: Multinomial Analysis of Hesitation** (No/Yes/Not Sure - Integrate `figures/08_multinomial_key_predictor_comparison.png`)
*   **D. Sensitivity Analysis** (Adding Proximal Beliefs Q6/Q7)
*   **E. Exploratory Analysis 1: The Contact Hypothesis** (Users vs. Non-Users on core beliefs)
*   **F. Exploratory Analysis 2: Stigma Phenotypes** (K-means clustering - Integrate `figures/14_profile_means_heatmap.png`)

## V. DISCUSSION
*   **A. Interpretation of Primary Findings** (What the regressions and clusters mean in the Iraqi context)
*   **B. Comparison With Iraqi and Regional Literature** (Bridging the N=877 dataset with the sources from Chapter II)
*   **C. Implications for Pharmacy Practice and Public Health** (Actionable insights for patient counseling)
*   **D. Strengths and Limitations of the Present Study** (e.g., cross-sectional limits, convenience sampling skewed to university females)
*   **E. Priority Research Gaps** (Next empirical steps)

## VI. RECOMMENDATIONS & CONCLUSION
*   **A. Practice and Policy Recommendations** (Tied directly to survey findings, e.g., targeted counseling for phenotype profiles)
*   **B. Conclusion** (Data-driven final summary of the N=877 cohort)

## VII. REFERENCES
*Scope Rule: Must use APA 7th edition and draw exclusively from `references.md`.*

## VIII. APPENDICES
*   **Appendix A:** Demographics Summary and Additional Tables
*   **Appendix B:** Survey Instrument Variables
