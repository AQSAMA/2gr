// Survey Data Results — Typst source
// Compiled separately from the main research paper.
// Generated from analysis_pipeline/output/survey_data_results_comprehensive.md

#set document(title: "Survey Data Results — Psychiatric Medication Use and Public Acceptance in Iraq", author: "Abdul Rahman Wakaa Ali, Ali Basem Hammoud, Shifa Safi Aboud, Zainab Mashal Nayef")

#let navy = rgb("#102a43")
#let gold = rgb("#b58b2a")
#let ink = rgb("#111827")
#let pale = rgb("#f7f9fc")
#let page-border = rect(width: 100%, height: 100%, stroke: 0.8pt + navy)

#set page(paper: "a4", margin: (top: 2cm, bottom: 2cm, left: 1.8cm, right: 1.8cm), background: page-border, numbering: "1")
#set text(font: ("Times New Roman", "Times"), size: 11pt, fill: ink)
#set par(leading: 0.6em, justify: true)

#show heading.where(level: 1): it => block(above: 18pt, below: 10pt)[
  #text(size: 16pt, weight: "bold", fill: navy)[#it.body]
  #v(-4pt)
  #line(length: 100%, stroke: 0.6pt + gold)
]
#show heading.where(level: 2): it => block(above: 14pt, below: 8pt)[
  #text(size: 13pt, weight: "bold", fill: navy)[#it.body]
]
#show heading.where(level: 3): it => block(above: 10pt, below: 6pt)[
  #text(size: 11.5pt, weight: "bold", fill: ink)[#it.body]
]

#show table: set text(size: 9.5pt)
#set table(stroke: 0.4pt + rgb("#c9d4e5"), inset: 5pt)
#show figure: set block(breakable: true)

// ===== Title Page =====
#align(center + horizon)[
  #box(width: 88%, inset: 20pt, stroke: 1pt + navy, fill: pale)[
    #align(center)[
      #text(size: 20pt, weight: "bold", fill: navy)[Survey Data Results]
      #v(10pt)
      #line(length: 50%, stroke: 0.7pt + gold)
      #v(10pt)
      #text(size: 14pt, fill: ink)[Psychiatric Medication Use and Public Acceptance in Iraq]
      #v(6pt)
      #text(size: 12pt, fill: ink)[Unified Analysis (N = 877)]
    ]
  ]
]

#pagebreak()
#counter(page).update(1)

// ===== Table of Contents =====
#outline(title: [Contents], depth: 2)

#pagebreak()

// ===== Main Analysis =====

= Hierarchical Block Logistic Regression

The primary outcome variable is recommendation willingness (Q8: Yes vs.\ No). Complete-case sample size for hierarchical models: *n* = 647.

== Model Comparison

Three nested blocks were fitted sequentially to evaluate incremental explanatory contributions.

#figure(
  table(
    columns: (2fr, 4fr, 1fr, 1fr),
    align: (left, left, right, right),
    table.header(
      [*Block*], [*Predictors*], [*McFadden R²*], [*LLR _p_-value*],
    ),
    [Block 1 (Demographics)],
    [Age, Gender, Education, Marital status],
    [0.0040], [0.5037],

    [Block 2 (+ Prior Use)],
    [Block 1 + Prior medication use],
    [0.0116], [0.0847],

    [Block 3 (+ Beliefs & Fear)],
    [Block 2 + Q11, Q12, Q13, Fear],
    [0.0686], [< 0.0001],
  ),
  caption: [Hierarchical model fit statistics across sequential blocks.],
)

Block 3 demonstrates a statistically significant improvement in model fit (LLR _p_ < 0.0001), indicating that attitudinal variables (belief items Q11–Q13 and fear of psychiatric medication) substantially improve prediction of recommendation willingness beyond demographic and prior-use factors.

== Final Model — Adjusted Odds Ratios (Block 3)

#figure(
  table(
    columns: (3fr, 2fr, 1fr),
    align: (left, right, right),
    table.header(
      [*Predictor*], [*Adjusted OR (95% CI)*], [*_p_-value*],
    ),
    [Intercept], [1.128 (0.298–4.273)], [0.8597],
    [Age (binary)], [0.961 (0.583–1.582)], [0.8752],
    [Gender (binary)], [1.516 (1.043–2.205)], [0.0294],
    [Education (binary)], [1.381 (0.750–2.542)], [0.3005],
    [Marital status (binary)], [1.075 (0.632–1.827)], [0.7904],
    [Prior use (binary)], [1.342 (0.800–2.252)], [0.2645],
    [Q11 — Overprescription belief], [0.830 (0.696–0.991)], [0.0396],
    [Q12 — Dependence belief], [0.869 (0.701–1.078)], [0.2008],
    [Q13 — Modern safety belief], [1.507 (1.248–1.820)], [< 0.0001],
    [Fear (binary)], [0.504 (0.358–0.711)], [< 0.0001],
  ),
  caption: [Adjusted odds ratios from the final hierarchical logistic regression (Block 3).],
)

Gender, belief that modern medications are safer (Q13), and fear of psychiatric medication emerged as statistically significant predictors. Fear halved the odds of recommending psychiatric medications (AOR = 0.504), while endorsement of modern medication safety nearly doubled them (AOR = 1.507 per unit increase).

== Sensitivity Model with Proximal Beliefs (Q6/Q7)

A supplementary model adding safety perception (Q6) and acceptability (Q7) was fitted on a reduced sample (*n* = 406) because these items are conceptually proximate to the outcome and may inflate explanatory variance.

- McFadden pseudo R²: *0.2440*
- Fit type: MLE

This model is reported separately to avoid conflation of proximal predictors with distal attitudinal measures.

#pagebreak()

= Multinomial Logistic Regression

This model preserves the three-category structure of Q8 (No / Yes / Not sure) rather than collapsing hesitant respondents. Complete-case sample: *n* = 837. Model log-likelihood: −748.910.

The reference category is the lowest coded group (Q8 = No). Coefficients express relative risk ratios for endorsing "Yes" or "Not sure" compared with "No."

== Q8 = Yes vs.\ Reference (No)

#figure(
  table(
    columns: (3fr, 2fr, 1fr),
    align: (left, right, right),
    table.header(
      [*Predictor*], [*RRR (95% CI)*], [*_p_-value*],
    ),
    [Intercept], [0.936 (0.264–3.317)], [0.9189],
    [Age (binary)], [0.947 (0.599–1.496)], [0.8139],
    [Gender (binary)], [1.558 (1.097–2.214)], [0.0133],
    [Education (binary)], [1.177 (0.661–2.095)], [0.5797],
    [Marital status (binary)], [0.967 (0.598–1.563)], [0.8903],
    [Prior use (binary)], [1.387 (0.863–2.229)], [0.1763],
    [Q11 — Overprescription belief], [0.873 (0.742–1.028)], [0.1028],
    [Q12 — Dependence belief], [0.794 (0.651–0.970)], [0.0239],
    [Q13 — Modern safety belief], [1.585 (1.328–1.892)], [< 0.0001],
  ),
  caption: [Relative risk ratios for Q8 = Yes vs.\ No.],
)

== Q8 = Not Sure vs.\ Reference (No)

#figure(
  table(
    columns: (3fr, 2fr, 1fr),
    align: (left, right, right),
    table.header(
      [*Predictor*], [*RRR (95% CI)*], [*_p_-value*],
    ),
    [Intercept], [0.304 (0.046–2.013)], [0.2170],
    [Age (binary)], [1.094 (0.549–2.180)], [0.7983],
    [Gender (binary)], [2.171 (1.211–3.894)], [0.0093],
    [Education (binary)], [1.300 (0.526–3.211)], [0.5692],
    [Marital status (binary)], [1.713 (0.863–3.399)], [0.1237],
    [Prior use (binary)], [1.401 (0.704–2.789)], [0.3373],
    [Q11 — Overprescription belief], [0.846 (0.662–1.080)], [0.1799],
    [Q12 — Dependence belief], [0.890 (0.660–1.199)], [0.4438],
    [Q13 — Modern safety belief], [1.064 (0.820–1.381)], [0.6404],
  ),
  caption: [Relative risk ratios for Q8 = Not Sure vs.\ No.],
)

Gender is significant across both outcome equations. The belief that modern medications are safer (Q13) is strongly predictive of endorsing "Yes" but not "Not sure," suggesting that this belief discriminates between active recommendation and mere hesitation.

#pagebreak()

= Contact Hypothesis: Users vs.\ Non-Users on Core Beliefs

This exploratory analysis examines whether personal experience with psychiatric medication (Q31) is associated with different belief profiles on items Q11–Q13. Users: *n* = 127; Non-users: *n* = 716.

#figure(
  table(
    columns: (3fr, 1fr, 1fr, 1fr, 1fr, 1fr, 1fr),
    align: (left, right, right, right, right, right, right),
    table.header(
      [*Item*], [*User Mdn*], [*Non-user Mdn*], [*M-W _p_*], [*Cliff's _d_*], [*χ² _p_*], [*Cramér's _V_*],
    ),
    [Q11 — Overprescription], [3.00], [4.00], [0.0428], [−0.108], [0.1170], [0.094],
    [Q12 — Dependence], [4.00], [4.00], [0.0317], [−0.112], [0.0428], [0.108],
    [Q13 — Modern safety], [4.00], [3.00], [0.0002], [0.198], [0.0027], [0.139],
  ),
  caption: [Comparison of core belief items between medication users and non-users.],
)

Users endorsed significantly higher agreement with modern medication safety (Q13) and somewhat lower agreement with overprescription concern (Q11) compared with non-users. Effect sizes are small but consistent with contact hypothesis predictions.

#pagebreak()

= Exploratory Stigma Phenotypes (K-Means Clustering)

Standardised scores on Q11–Q13 were submitted to K-means clustering. Silhouette analysis favoured *k* = 4.

== Cluster Selection

#figure(
  table(
    columns: (1fr, 1fr),
    align: (center, center),
    table.header(
      [*k*], [*Silhouette Score*],
    ),
    [2], [0.274],
    [3], [0.272],
    [4], [0.303],
  ),
  caption: [Silhouette scores for candidate cluster solutions.],
)

== Profile Characterisation

#figure(
  table(
    columns: (1fr, 1fr, 1fr, 1fr, 1fr),
    align: (center, right, right, right, right),
    table.header(
      [*Profile*], [*n*], [*Q11 Mean*], [*Q12 Mean*], [*Q13 Mean*],
    ),
    [0], [183], [4.404], [4.115], [4.311],
    [1], [230], [2.961], [2.804], [3.578],
    [2], [232], [2.694], [4.250], [3.720],
    [3], [223], [4.359], [4.291], [2.610],
  ),
  caption: [Mean belief scores by cluster profile (k = 4).],
)

Profile 0 reflects uniformly high agreement across all three belief dimensions. Profile 3 shows high overprescription and dependence concern but low endorsement of modern safety — a pattern potentially indicative of generalised pharmacological scepticism. Profile 1 shows moderate-to-low scores on all items, while Profile 2 combines low overprescription concern with high dependence concern. These profiles warrant further investigation with confirmatory approaches.

#pagebreak()

= Demographics Summary

#figure(
  table(
    columns: (2fr, 2fr, 1fr, 1fr),
    align: (left, left, right, right),
    table.header(
      [*Variable*], [*Category*], [*Count*], [*%*],
    ),
    table.cell(rowspan: 2)[Gender],
    [Male], [244], [28.05],
    [Female], [626], [71.95],
    table.hline(stroke: 0.3pt + rgb("#e0e0e0")),
    table.cell(rowspan: 5)[Age],
    [18–25], [651], [74.57],
    [26–35], [153], [17.53],
    [36–45], [44], [5.04],
    [46–60], [24], [2.75],
    [> 60], [1], [0.11],
    table.hline(stroke: 0.3pt + rgb("#e0e0e0")),
    table.cell(rowspan: 4)[Education],
    [Primary], [5], [0.57],
    [High School], [61], [6.99],
    [University], [689], [78.92],
    [Postgraduate], [118], [13.52],
    table.hline(stroke: 0.3pt + rgb("#e0e0e0")),
    table.cell(rowspan: 4)[Marital Status],
    [Single], [684], [78.44],
    [Married], [183], [20.99],
    [Divorced], [3], [0.34],
    [Widowed], [2], [0.23],
  ),
  caption: [Demographic characteristics of respondents (N = 877).],
)

#pagebreak()

= Core Beliefs — Likert Distribution

#figure(
  table(
    columns: (3fr, 1fr, 1fr, 1fr),
    align: (left, right, right, right),
    table.header(
      [*Question*], [*Disagree %*], [*Neutral %*], [*Agree %*],
    ),
    [Q11 — Doctors prescribe medications more than necessary], [13.78], [34.67], [51.55],
    [Q12 — Most medications cause psychological or physical dependence], [4.95], [27.65], [67.40],
    [Q13 — Modern medications are safer than older ones], [12.18], [35.86], [51.95],
  ),
  caption: [Distribution of agreement on core belief items (collapsed Likert categories).],
)

= Correlation Matrix: Primary Beliefs

#figure(
  table(
    columns: (2fr, 1fr, 1fr, 1fr, 1fr, 1fr, 1fr),
    align: (left, right, right, right, right, right, right),
    table.header(
      [*Variable*], [*Q11*], [*Q12*], [*Q13*], [*Concern*], [*Accept.*], [*Recommend*],
    ),
    [Q11], [1.000], [0.269], [−0.066], [0.059], [−0.085], [−0.086],
    [Q12], [0.269], [1.000], [−0.038], [0.058], [−0.163], [−0.087],
    [Q13], [−0.066], [−0.038], [1.000], [−0.105], [0.026], [0.077],
    [Concern], [0.059], [0.058], [−0.105], [1.000], [−0.040], [−0.042],
    [Acceptance], [−0.085], [−0.163], [0.026], [−0.040], [1.000], [0.232],
    [Recommend], [−0.086], [−0.087], [0.077], [−0.042], [0.232], [1.000],
  ),
  caption: [Spearman correlation matrix among primary belief and attitude variables.],
)

= Acceptance by Prior Use

#figure(
  table(
    columns: (2fr, 1fr, 1fr),
    align: (left, right, right),
    table.header(
      [*Prior Use*], [*Recommend Yes %*], [*Sample _n_*],
    ),
    [Yes], [65.08], [126],
    [No], [55.80], [715],
  ),
  caption: [Recommendation willingness by prior psychiatric medication use.],
)

= General Attitudes Distribution

#figure(
  table(
    columns: (3fr, 1fr, 1fr, 1fr),
    align: (left, right, right, right),
    table.header(
      [*Question*], [*Yes %*], [*Not Sure %*], [*No %*],
    ),
    [Safety perception (Q6)], [23.65], [31.23], [45.12],
    [Acceptability (Q7)], [30.80], [17.70], [51.49],
    [Recommendation willingness (Q8)], [57.65], [11.62], [30.72],
    [Social concerns (Q9)], [37.77], [13.09], [49.14],
  ),
  caption: [Response distribution for general attitude items.],
)

#pagebreak()

= Notes for Manuscript Positioning

- Hierarchical and multinomial modelling are suitable main-text analyses because they preserve response structure and clarify incremental explanatory value.
- K-means profiling should be presented as an exploratory secondary analysis.
- For stronger latent construct validation in future work, ordinal EFA/CFA with polychoric correlations is recommended on appropriately scoped item blocks.

#pagebreak()

= Survey Instrument — Full Question List

The following table presents all questions administered in the survey along with their response options.

#figure(
  table(
    columns: (1fr, 4fr, 3fr),
    align: (center, left, left),
    table.header(
      [*Code*], [*Question (Arabic)*], [*Response Options*],
    ),
    [Q1], [العمر \ (Age)], [18–25 / 26–35 / 36–45 / 46–60 / > 60],
    [Q2], [الجنس \ (Gender)], [Male / Female],
    [Q4], [المستوى التعليمي \ (Educational level)], [Primary / Middle School / High School / Institute-Diploma / University / Postgraduate],
    [Q5], [الحالة الاجتماعية \ (Marital status)], [Single / Married / Divorced / Widowed],
    table.hline(stroke: 0.5pt + gold),
    [Q6], [هل تعتقد أن الأدوية النفسية آمنة؟ \ (Do you believe psychiatric medications are safe?)], [Yes / No / Not sure],
    [Q7], [هل ترى أن استخدامها مقبول مثل أدوية الضغط والسكري؟ \ (Is their use acceptable like hypertension or diabetes drugs?)], [Yes / No / Not sure],
    [Q8], [هل تنصح شخصًا مقربًا باستخدامها إذا احتاج إليها؟ \ (Would you advise someone close to use them if needed?)], [Yes / No / Not sure],
    [Q9], [هل لديك تخوف من التعامل مع شخص يتناول أدوية نفسية؟ \ (Do you fear interacting with someone on psychiatric medication?)], [Yes / No / Not sure],
    table.hline(stroke: 0.5pt + gold),
    [Q11], [الأطباء يصفون الأدوية أكثر مما يجب \ (Doctors prescribe medications more than necessary)], [5-point Likert: Strongly disagree to Strongly agree],
    [Q12], [معظم الأدوية تسبب اعتمادًا نفسيًا أو جسديًا \ (Most medications cause psychological or physical dependence)], [5-point Likert],
    [Q13], [الأدوية الحديثة أكثر أمانًا من القديمة \ (Modern medications are safer than older ones)], [5-point Likert],
    table.hline(stroke: 0.5pt + gold),
    [Q15], [أعتقد أن الأدوية النفسية ضرورية لصحتي \ (I believe psychiatric medications are necessary for my health)], [5-point Likert],
    [Q16], [الأدوية النفسية تحافظ على استقراري \ (Psychiatric medications maintain my stability)], [5-point Likert],
    [Q17], [بدون الأدوية النفسية ستتدهور حالتي \ (Without psychiatric medications my condition would deteriorate)], [5-point Likert],
    [Q18], [الأدوية النفسية تسبب آثارًا جانبية مزعجة \ (Psychiatric medications cause unpleasant side effects)], [5-point Likert],
    [Q19], [أشعر بالقلق من التعود أو الإدمان على الأدوية النفسية \ (I worry about habituation or addiction to psychiatric medications)], [5-point Likert],
    [Q20], [الأدوية النفسية قد تضر بصحتي على المدى الطويل \ (Psychiatric medications may harm my long-term health)], [5-point Likert],
    table.hline(stroke: 0.5pt + gold),
    [Q22], [أشعر بتحسن عند استخدام الأدوية النفسية \ (I feel better when using psychiatric medications)], [5-point Likert],
    [Q23], [الأدوية تجعلني أفقد السيطرة على حياتي \ (Medications make me lose control of my life)], [5-point Likert],
    [Q24], [الأدوية تساعدني أن أكون أكثر طبيعية \ (Medications help me be more normal)], [5-point Likert],
    [Q25], [الأدوية تسبب لي مشاكل \ (Medications cause me problems)], [5-point Likert],
    [Q26], [الأدوية تجعلني أثق بقدرتي على العلاج \ (Medications make me trust my ability to recover)], [5-point Likert],
    [Q27], [استخدام الأدوية يشعرني بالخوف \ (Using medications makes me feel afraid)], [5-point Likert],
    [Q28], [الأدوية النفسية تساعدني على أن أكون بحالة أفضل \ (Psychiatric medications help me be in a better state)], [5-point Likert],
    [Q29], [الأدوية النفسية تساعدني على أن أكون بحالة أفضل \ (Psychiatric medications help me be in a better state)], [5-point Likert],
    [Q30], [الأدوية تجعل حياتي أسوأ \ (Medications make my life worse)], [5-point Likert],
    table.hline(stroke: 0.5pt + gold),
    [Q31], [هل تستخدم أو سبق أن استخدمت دواء نفسي؟ \ (Do you use or have you previously used psychiatric medication?)], [Yes / No],
    [Q32], [الأدوية تسبب لي قلقًا بشأن آثارها \ (Medications cause me anxiety about their effects)], [5-point Likert],
  ),
  caption: [Complete survey instrument with question codes and response formats.],
)
