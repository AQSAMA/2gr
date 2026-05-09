// Editable Typst source for the graduation project.
// Generated from content/*.md by production/src/build_typst_content.py.
// The design follows common university thesis conventions: bordered A4 pages,
// formal title page, compact front matter, automatic contents, and figure lists.

#set document(title: "Psychiatric Medication Use and Public Acceptance in Iraq", author: "Abdul Rahman Wakaa Ali, Ali Basem Hammoud, Shifa Safi Aboud, Zainab Mashal Nayef")

#let navy = rgb("#102a43")
#let gold = rgb("#b58b2a")
#let ink = rgb("#111827")
#let pale = rgb("#f7f9fc")
#let citation-color = rgb("#2c5282")
#let page-border = rect(width: 100%, height: 100%, stroke: 0.8pt + navy)
#let running-head = state("running-head", "")
#let set-running-head(s) = running-head.update(s)

// The running head sits at the top RIGHT and is suppressed on the first
// page of every chapter. Chapter-title pages already disable the header
// via `set page(header: none)`; content pages mark the opening page with a
// `<section-start>` label so this context block knows to hide the head on
// that page only.
#let regular-page-header = context {
  let head = running-head.get()
  if head != "" {
    let page-num = here().page()
    let markers = query(<section-start>).filter(m => m.location().page() == page-num)
    if markers.len() == 0 {
      align(right)[#text(size: 9pt, fill: navy, style: "italic")[#head]]
    }
  }
}

#set page(paper: "a4", margin: 1.5cm, background: page-border, header: regular-page-header)
#set text(font: ("Times New Roman", "Times"), size: 14pt, fill: ink)
#set par(leading: 0.55em, justify: true)

// Muted academic navy for parenthetical in-text citations such as
// "(Author, 2020)" or "(Author et al., 2020; Other, 2019)". The leading
// capital letter in the required lookbehind avoids matching numeric
// parentheses like "(p=0.0001)" or "(adjusted OR 0.504, ...)".
#show regex("\([A-Z][^()]*?\d{4}[a-z]?\)"): it => text(fill: citation-color, it)

#show heading.where(level: 1): it => block(above: 10pt, below: 8pt)[
  #text(size: 18pt, weight: "bold", fill: navy)[#it.body]
  #linebreak()
  #line(length: 100%, stroke: 0.7pt + gold)
]
#show heading.where(level: 2): it => block(above: 8pt, below: 6pt)[
  #text(size: 16pt, weight: "bold", fill: navy)[#it.body]
]
#show figure: it => block(above: 10pt, below: 12pt, inset: 6pt, stroke: 0.35pt + rgb("#c9d4e5"))[#align(center)[#it]]

#let center-line(s, size: 14pt, weight: "regular", fill: ink) = align(center)[#text(size: size, weight: weight, fill: fill)[#s]]
#let p(s) = par(first-line-indent: 1.27cm, justify: true)[#s]
#let refp(s) = block(above: 3pt, below: 5pt)[
  #set text(size: 12pt)
  #par(first-line-indent: 0pt, hanging-indent: 0.5in, justify: true)[#s]
]
#let h1(s) = heading(level: 1, outlined: true)[#s]
#let section-title(s) = [
  #pagebreak(weak: true)
  #[#metadata(none) <section-start>]
  #h1(s)
]
#let h2(s) = heading(level: 2, outlined: true)[#s]
#let fig(path, caption-text) = figure(image(path, width: 90%), caption: [#caption-text])

#let front-title(s) = [
  #align(center)[
    #box(width: 80%, inset: 10pt, stroke: 0.7pt + gold, fill: pale)[
      #text(size: 22pt, weight: "bold", fill: navy)[#s]
    ]
  ]
]

#let chapter-page(chapter, title) = [
  #pagebreak(weak: true)
  #set page(header: none)
  #align(center + horizon)[
    #box(width: 84%, inset: 28pt, stroke: 1pt + navy, fill: pale)[
      #align(center)[
        #text(size: 32pt, weight: "bold", fill: navy)[#chapter]
        #v(8pt)
        #line(length: 55%, stroke: 0.8pt + gold)
        #v(8pt)
        #text(size: 20pt, weight: "bold", fill: navy)[#title]
      ]
    ]
  ]
  #pagebreak()
  #set page(header: regular-page-header)
]

#let start-main-numbering() = [
  #pagebreak(weak: true)
  #set page(numbering: "1", number-align: top + center)
  #counter(page).update(1)
]

// Cover page: unnumbered. Certification begins on the second page.
#set page(numbering: none)
#align(center)[
  #image("../figures/University_logo.png", width: 2.25cm)
  #v(0.16cm)
  #text(size: 15pt, weight: "bold", fill: navy)[Republic of Iraq] \
  #text(size: 15pt, weight: "bold", fill: navy)[Ministry of Higher Education and Scientific Research] \
  #text(size: 15pt, weight: "bold", fill: navy)[University of Al-Maarif] \
  #text(size: 15pt, weight: "bold", fill: navy)[College of Pharmacy]
  #v(0.35cm)
  #box(width: 88%, inset: 12pt, stroke: 1pt + gold, fill: pale)[
    #text(size: 24pt, weight: "bold", fill: navy)[Psychiatric Medication Use and Public Acceptance in Iraq]
  ]
  #v(0.32cm)
  #text(size: 14pt)[A Project Submitted to] \
  #text(size: 13pt)[The College of Pharmacy, University of Al-Maarif, Department of Clinical Pharmacy, in Partial Fulfillment for the Bachelor of Pharmacy]
  #v(0.28cm)
  #text(size: 14pt, weight: "bold")[By] \
  #text(size: 20pt, weight: "bold", fill: navy)[Abdul Rahman Wakaa Ali\
Ali Basem Hammoud\
Shifa Safi Aboud\
Zainab Mashal Nayef]
  #v(0.25cm)
  #text(size: 14pt, weight: "bold")[Supervised by:] \
  #text(size: 20pt, weight: "bold", fill: navy)[Hameed Adnan] \
  #text(size: 16pt)[Supervisor's Degree]
  #v(0.18cm)
  #text(size: 14pt)[May, 2026]
]

// Roman-numbered preliminary pages. Numbering stays Roman through every
// front-matter spread and switches to Arabic the moment the abstract opens.
#pagebreak()
#set page(numbering: "i", number-align: top + center)
#counter(page).update(1)
#front-title[Certification of the Supervisor]
#p("I certify that this project entitled “Psychiatric Medication Use and Public Acceptance in Iraq” was prepared by the fifth-year students Abdul Rahman Wakaa Ali, Ali Basem Hammoud, Shifa Safi Aboud, Zainab Mashal Nayef under my supervision at the College of Pharmacy/University of Al-Maarif in partial fulfillment of the graduation requirements for the Bachelor Degree in Pharmacy.")
#align(right)[#text(weight: "bold")[Supervisor's name: Hameed Adnan]]
#v(0.55cm)
#front-title[Dedication]
#p("We dedicate this work to our families, whose patience made long study days easier, and to every Iraqi patient who deserves safe, respectful, and evidence-based mental health care. We also dedicate it to the teachers and pharmacists who taught us that science becomes meaningful when it serves people with honesty and compassion.")
#v(0.35cm)
#front-title[Acknowledgment]
#p("We thank Dr. Hameed Adnan for his supervision, guidance, and careful advice throughout this project. We are also grateful to the College of Pharmacy at University of Al-Maarif, to the participants who gave their time to answer the survey, and to our colleagues who supported the data collection and revision process.")

#pagebreak()
#front-title[Table of Contents]
// The table of contents is tightened to fit a single page. We keep depth 2
// so readers still see chapter + section structure, but compact the entry
// size and spacing so the full outline renders inside one A4 page.
#{
  show outline.entry: it => block(above: 0.15em, below: 0.15em, text(size: 10pt, it))
  outline(title: none, depth: 2, indent: auto)
}

#pagebreak()
#front-title[List of Figures]
#outline(title: none, target: figure.where(kind: image))
#v(0.4cm)
#front-title[List of Tables]
#p("No manuscript tables are currently embedded as formal Typst tables in this editable source. Statistical results are reported in the text and figures.")
#v(0.4cm)
#front-title[List of Abbreviations]
#par(first-line-indent: 0pt)[AOR: Adjusted Odds Ratio \
CI: Confidence Interval \
LLR: Likelihood Ratio Test \
MLE: Maximum Likelihood Estimation \
OR: Odds Ratio \
PTSD: Post-Traumatic Stress Disorder \
RRR: Relative Risk Ratio \
Q6/Q7/Q8/Q9/Q11/Q12/Q13: Survey question item codes used in analysis and reporting \
R²: Coefficient of determination, reported as pseudo R² in logistic model fit summaries]



#start-main-numbering()
#set-running-head("")
#section-title("ABSTRACT")
#p("Psychiatric medication acceptance in Iraq remains a public health challenge because mental health needs are high while treatment hesitation persists. This study examined psychiatric medication use and public acceptance in Iraq using an original cross-sectional survey with supportive literature context. We analyzed responses from 877 participants using descriptive statistics, hierarchical logistic regression, multinomial logistic regression, Users vs Non-Users comparisons, and exploratory stigma-phenotype analysis.")
#p("The sample was mostly female, young, and university educated. Public attitudes were mixed: recommendation willingness was higher than perceived safety and acceptability, showing that many respondents were open to treatment in principle but still worried about medication risks. In adjusted models, recommendation was more likely among women and among respondents who trusted newer psychiatric medications, and less likely among those with stronger fear and overprescribing concerns. In the multinomial model, dependence concern reduced the likelihood of clear recommendation. Users also reported more favorable beliefs than non-users, especially for confidence in modern medications.")
#p("These findings indicate ambivalent public attitudes rather than uniform rejection. The strongest barriers were fear, mistrust, and dependence concerns, more than most demographic factors. Compared with Iraqi and regional literature, the results suggest a persistent trust-and-literacy gap that affects treatment uptake. Policy and practice should prioritize pharmacist-led counseling, integrated primary mental health care, and anti-stigma communication to improve medication acceptance and reduce Iraq’s treatment gap.")
#chapter-page("Chapter One", "Introduction")
#set-running-head("Introduction")
#section-title("I. INTRODUCTION")
#h2("A. Background and Context")
#p("Iraq’s mental health burden developed under repeated war, displacement, sanctions, and political instability. This history still shapes how people understand psychiatric care today. Evidence from Iraqi and regional reporting shows that exposure to conflict, bereavement, and social disruption increased anxiety, depression, and trauma-related conditions in both urban and displaced populations (Saied et al., 2023; Younis & Khunda, 2020).")
#p("At the same time, service capacity did not expand at the same pace as need. Iraqi psychiatry moved through periods of growth and then major workforce loss, especially after conflict-related migration waves, which left a long gap between population demand and specialist availability (Younis & Khunda, 2020; Sadik et al., 2010).")
#p("Current system-level indicators support this gap. National commentary describes a continuing shortage of psychiatrists, limited specialized facilities, and weak access in many areas outside major centers (Saied et al., 2023). Earlier Iraqi public-health work also documented a high burden of common mental disorders and a very low proportion of people with mental disorders receiving formal treatment (Sadik et al., 2010). Evidence from post-conflict care literature further shows that service use is shaped not only by availability, but also by fear of labeling, social judgment, and delayed help-seeking even when symptoms are significant (Burnam et al., 2009).")
#p("These structural and social conditions make psychiatric medication use a public-health issue, not only a clinical issue. When access to specialist follow-up is limited, decisions about whether psychiatric medicines are acceptable, safe, or socially risky often move into family and community spaces. In Iraq, those decisions are influenced by collective memory of conflict, concerns about dependence, and distrust of mental health services, while public education and mental health literacy remain uneven across groups (Saied et al., 2023; Sadik et al., 2010).")
#h2("B. Problem Statement")
#p("Iraq faces a double challenge. The first challenge is a treatment-capacity gap, with limited workforce and service coverage relative to the burden of mental disorders. The second challenge is a public-acceptance gap, where stigma and negative social beliefs can reduce care-seeking, delay treatment initiation, and weaken long-term medication use. Iraqi evidence indicates that many people recognize biological and psychosocial causes of mental illness, yet still hold restrictive social attitudes about people living with mental disorders (Sadik et al., 2010). This pattern means awareness alone does not automatically produce acceptance.")
#p("The available literature gives strong signals on stigma and service barriers, but it does not provide a current, integrated Iraqi cross-sectional picture focused directly on psychiatric medication acceptance in the general public. The present study addresses this local evidence gap by using a dedicated survey framework that links demographic factors, prior medication exposure, core beliefs about psychiatric medicines, and willingness to recommend treatment.")
#h2("C. Study Aim and Research Questions")
#p("This study aims to measure psychiatric medication acceptance in Iraq and identify factors associated with willingness to recommend psychiatric medication when needed.")
#p("The study asks four linked questions. First, what is the distribution of public responses on core acceptance outcomes, including perceived safety, acceptability, recommendation willingness, and social concern? Second, after adjustment for demographic characteristics and prior psychiatric medication use, which beliefs independently predict recommendation willingness? Third, when hesitation is preserved as a separate response category, how do predictors differ across no, yes, and not sure recommendation responses? Fourth, do people with personal experience of psychiatric medication differ from non-users in key belief items related to prescribing trust, dependence concerns, and perceptions of medication progress?")
#h2("D. Study Significance")
#p("This study has direct value for pharmacy practice in Iraq. Pharmacists are often the most accessible health professionals in daily care pathways, especially when specialist psychiatric follow-up is delayed. Clear evidence on which beliefs are associated with acceptance can help pharmacists provide targeted counseling, address dependence fears, and improve communication with patients and families.")
#p("The study also supports clinicians, educators, and health planners. For clinical teams, it clarifies where social perceptions may interfere with evidence-based treatment. For pharmacy and medical education, it provides Iraq-specific data that can strengthen teaching on stigma-sensitive counseling and psychopharmacology communication. For policy and service planning, it offers current local evidence that can support anti-stigma messaging, community engagement, and integration of mental health support in primary-care and public-health programs.")
#section-title("II. LITERATURE REVIEW (SUPPORTIVE CONTEXT)")
#h2("A. Stigma and Public Attitudes")
#p("Evidence across Arab and international settings shows that stigma remains a major barrier to mental health care, but its expression varies by culture, service structure, and public literacy. In Arab populations, stigma does not operate only as individual prejudice. It is reinforced by family reputation concerns, social exclusion risks, and public narratives that connect mental illness with danger, moral weakness, or shame (Zolezzi et al., 2018; Booth et al., 2024). This multi-layered pattern helps explain why people may verbally support treatment in principle while still discouraging disclosure or formal care in practice.")
#p("Comparative evidence also shows that stigma influences both treatment timing and treatment pathway. Reviews on help-seeking report that public stigma, self-stigma, and institutional stigma can independently reduce formal service use, with delayed care commonly observed in groups exposed to prolonged conflict stress (Rasheed et al., 2026). Although military populations differ from civilian Iraqi populations, the mechanism is relevant to Iraq because conflict exposure and social labeling pressures are shared contextual factors.")
#p("Iraqi university evidence adds local detail to this pattern. Among Baghdad students, stigma levels were not random; they were associated with psychosocial conditions such as psychological well-being and social support, suggesting that stigma reduction requires both educational and psychosocial interventions rather than awareness messages alone (Hussein Alwan et al., 2025). This finding aligns with broader conservative-community literature showing that stigma is sustained by social norms and can also influence health workers’ attitudes, which then affects patient trust and continuity of care (Booth et al., 2024).")
#p("Regional and international trends indicate gradual improvement in acceptance of psychiatric professionals and treatment in some settings, yet medication-specific hesitation often remains higher than psychotherapy acceptance (Angermeyer et al., 2017). For Iraq, this contrast matters because medication is frequently the first scalable intervention in a constrained service system. If medication acceptance lags behind service expansion, the practical benefit of system investment will remain limited.")
#h2("B. Medication Beliefs and Acceptance")
#p("Medication acceptance is strongly linked to how people cognitively represent necessity, harm, dependence risk, and long-term control. The Beliefs about Medicines framework shows that adherence behavior is shaped by a balance between perceived need and perceived harm, not by knowledge level alone (Horne et al., 1999). This model remains useful for psychiatric medications because concern-driven non-use can occur even when people acknowledge treatment effectiveness.")
#p("Population data outside Iraq show that favorable attitudes toward psychiatric medication can increase over time, but risk perceptions may remain stable. In the United States, willingness to use psychiatric medication rose across survey waves, while concern about medication risks did not decline at the same rate (Mojtabai, 2009). Although this evidence comes from an earlier period and a different health system, the split between rising acceptance and persistent risk concern remains useful for Iraqi interpretation, where awareness can improve faster than trust in long-term medication safety.")
#p("Gulf-region literacy evidence shows that low or uneven mental health literacy coexists with persistent negative attitudes and stigma, including among some health-related groups (Elyamani et al., 2021). Iraqi refugee evidence supports this point by showing that even in highly trauma-exposed populations, recognition of formal psychiatric labels can remain low while selective trust in specific forms of help remains high (Slewa-Younan et al., 2014). Taken together, these findings suggest that communication approaches framed around understandable explanations of benefit, safety monitoring, and expected treatment course may be more acceptable than label-centered messaging alone.")
#h2("C. Adherence and Determinants")
#p("Adherence evidence consistently shows that non-adherence is multi-determined and cannot be explained by one variable. Systematic synthesis identifies social support, socioeconomic position, depression burden, treatment costs, and health-system barriers as recurrent determinants, while some demographic effects vary by context and measurement method (Gast & Mathes, 2019). This indicates that adherence strategies in Iraq should combine clinical counseling with structural supports rather than relying on patient motivation alone.")
#p("Psychiatric-specific evidence highlights a strong relationship between stigma processes and medication behavior. In mental health settings, internalized stigma is associated with poorer adherence, higher relapse pressure, and reduced social functioning (Abdisa et al., 2020). Intervention reviews in schizophrenia show that information-only psychoeducation often has limited effect, whereas approaches that include motivational, behavioral, and community-support components show better adherence outcomes (Zygmunt et al., 2002).")
#p("Family and caregiver context adds another layer that is highly relevant to Iraqi social structure. Systematic review evidence in child and adolescent psychiatry shows that parental beliefs, family functioning, and caregiver mental health influence adherence trajectories (Kalaman et al., 2023). In Iraq, where family decision-making remains central in treatment choices, this supports a practice model in which counseling targets both patient and family belief systems.")
#h2("D. Iraqi and Regional Service Realities")
#p("Recent Iraqi prescribing evidence shows a meaningful gap between guideline principles and inpatient practice in high-acuity psychiatric care. Data from Baghdad report substantial antipsychotic polypharmacy and a notable proportion of high-dose prescribing, with specific prescribing patterns associated with elevated high-dose exposure (Nassr & Wadeea, 2026). This matters for public acceptance because visible adverse effects and complex regimens can strengthen community fears about psychiatric medication safety.")
#p("Community and student-level Iraqi evidence reflects parallel concerns. Research in Basra medical-group students reports measurable psychotropic drug use patterns alongside anxiety and depression burden, suggesting that even health-educated populations may face unresolved medication and mental health challenges (Kadhim et al., 2024). At the care-seeking level, Iraqi psychiatric-clinic evidence indicates frequent prior or concurrent use of faith-healing pathways, often before psychiatric consultation, which can delay formal treatment and fragment continuity of care (Younis et al., 2020).")
#p("Regional systems research supports service integration as a practical direction. Reviews from the Middle East and North Africa describe chronic workforce imbalance, urban-rural disparity, funding constraints, and stigma-linked access barriers, despite policy development and educational advances (Okasha et al., 2025). In low- and middle-income settings, integration of mental health services into primary care shows benefit for access and outcomes, although implementation quality and local adaptation remain decisive (Cubillos et al., 2021). For Iraq, this suggests that medication acceptance should be addressed as part of integrated primary-care mental health strategy, not as a stand-alone communication issue.")
#chapter-page("Chapter Two", "Materials and Methods")
#set-running-head("Materials and Methods")
#section-title("III. METHODOLOGY (ORIGINAL CROSS-SECTIONAL STUDY)")
#h2("A. Study Design and Setting")
#p("This study used an original cross-sectional survey design to examine psychiatric medication use and public acceptance in Iraq. The analytic dataset included 877 respondent records after questionnaire cleaning and standardization, as documented in the unified analysis outputs and preprocessing workflow. The design was observational and non-interventional, and all analyses were conducted on de-identified survey records.")
#p("The available materials indicate an Iraq-focused online questionnaire dataset with Arabic item wording translated into English for analysis. The dataset does not include governorate identifiers, institution identifiers, or site-level fields, so the setting is reported as an Iraq-wide online sample rather than a facility-based sample.")
#p("Reporting constraints: The available project files did not provide a verifiable calendar field or protocol record for the exact data-collection month/year range, did not document the original dissemination channels in a reproducible log, and did not include a formal eligibility sheet beyond what can be inferred from the final dataset structure.")
#h2("B. Participants and Sampling")
#p("The study analyzed all available respondent records retained after preprocessing of the source questionnaire file. Preprocessing removed the questionnaire label row, normalized text encoding and spacing, mapped Arabic response options to numeric categories, and checked unmapped values before analysis. The cleaned dataset contained 877 participants and represented the achieved analytic sample for descriptive analyses. For inferential models, we applied complete-case handling within each model-specific variable set, so analytic sample size differed by model according to missingness in required fields.")
#p("Based on the observed dataset structure and cleaning workflow, inclusion for the analytic dataset required a valid respondent row under the 29-variable questionnaire schema after removal of the non-respondent label row. Exclusion at preprocessing level applied to the label row and any non-mappable residual text entries; no unmapped text values remained after cleaning. For model estimation, additional model-specific exclusion was applied through complete-case handling when required covariates or outcomes were missing. Recruitment is therefore reported as an achieved online non-probability sample captured in the dataset, with no recoverable record of platform-specific invitation channels.")
#h2("C. Survey Instrument")
#p("The survey instrument included 29 variables covering demographics, public attitudes toward psychiatric medication, medication beliefs, social concern, and prior personal use. Demographic fields captured age group, gender, educational level, and marital status. Core public-acceptance items measured perceived safety, acceptability of psychiatric medication in comparison with treatment for chronic medical conditions, willingness to recommend psychiatric medication, and concern about interacting with a person using psychiatric medication. Belief items included perceptions of overprescribing, dependence risk, and whether modern psychiatric medicines are safer than older options.")
#p("The instrument also included an extended block of personal medication-belief items. In the cleaned data, this extended block showed substantial missingness and reflected a subgroup module, so the primary inferential models focused on the core variables that were broadly available across the full sample.")
#p("To make code references explicit for readers, the study used a fixed question-code map in all chapters. Q6 referred to perceived safety of psychiatric medication, Q7 referred to acceptability of psychiatric medication relative to treatment for chronic medical illness, Q8 referred to willingness to recommend psychiatric medication, and Q9 referred to social concern about interacting with a person using psychiatric medication. Q11 referred to the statement that doctors prescribe psychiatric medications more than necessary, Q12 referred to the statement that most psychiatric medications cause psychological or physical dependence, Q13 referred to the statement that modern psychiatric medications are safer than older ones, and Q31 identified prior psychiatric medication use status.")
#h2("D. Variables and Operational Definitions")
#p("The primary outcome for the main binary logistic models was recommendation willingness, coded from the recommendation item as yes versus no. In the multinomial model, the same outcome preserved three response categories: no, yes, and not sure.")
#p("The main predictor set included binary demographic indicators and key belief variables. Age was recoded as 18 to 25 years versus older groups. Education was recoded as university or postgraduate versus lower educational levels. Marital status was recoded as married or previously married versus single. Gender was recoded as female versus male. Prior psychiatric medication use was coded as yes versus no. A concern indicator was coded from the social-concern item as yes versus no. Belief items on overprescribing, dependence, and modern-versus-older medication safety were modeled as ordinal Likert predictors.")
#p("To avoid conceptual overlap with the recommendation outcome, two proximal items, perceived safety and disease-model acceptability, were excluded from the primary hierarchical model and tested separately in a sensitivity model.")
#h2("E. Data Management and Statistical Analysis")
#p("Data management followed a predefined cleaning pipeline. First, the source spreadsheet label row was removed, and all text fields were normalized to handle spacing and encoding inconsistencies. Second, Arabic response categories were mapped to numeric codes using fixed dictionaries for demographics, Likert responses, yes or no items, and yes or no or not sure items. Third, all mapped fields were converted to numeric types where possible, and unmapped residual text values were checked.")
#p("Missingness was quantified per variable. Core variables used in the main models had low missingness, while subgroup medication-belief items had high missingness. Therefore, each inferential model used complete-case records for its own covariate set rather than global listwise deletion across all questionnaire items. This model-specific complete-case strategy preserved the largest feasible denominator for each analysis, but it also means each model reflects only respondents with fully observed values for that model’s required fields.")
#h2("Denominator Policy for Reporting")
#p("The study denominator policy was defined before chapter-level reporting to keep descriptive and model-based estimates transparent and consistent. The total survey sample was N=877 respondents after preprocessing and cleaning. For descriptive statistics, each percentage used the variable-level valid-response denominator for that specific item, which means percentages were calculated as a share of valid responses for that item rather than the full N when item missingness was present. For inferential analyses, each model used complete-case denominators based on all required variables in that model: n=647 for the primary hierarchical logistic regression, n=406 for the sensitivity logistic model that added Q6 and Q7, and n=837 for the multinomial logistic regression. Contact-hypothesis analyses also used item-level complete denominators that varied by tested item (Q11 N=843, Q12 N=840, Q13 N=842), with group counts reported as Users n=127 and Non-Users n=716 under Q31 coding.")
#p("The analysis sequence followed the project’s documented workflow used to generate the unified survey results report. We first estimated hierarchical logistic regression in three blocks for recommendation willingness, progressing from demographic factors to prior medication use and then to belief variables and concern indicator. The complete-case sample for this primary hierarchical model set was 647 respondents. We reported adjusted odds ratios with 95% confidence intervals, model likelihood-ratio p-values, and McFadden pseudo R-squared values.")
#p("Second, we estimated a sensitivity logistic model that added perceived safety and acceptability items to test robustness while acknowledging their conceptual proximity to the recommendation outcome. The sensitivity complete-case sample was 406 respondents, mainly because adding these proximal items introduced additional missingness filters.")
#p("Third, we estimated multinomial logistic regression to preserve the no, yes, and not sure structure of recommendation responses and reported relative risk ratios with 95% confidence intervals. The multinomial complete-case sample was 837 respondents, reflecting broader data availability for that reduced covariate set.")
#p("Fourth, we tested the contact hypothesis as Users vs Non-Users by comparing core belief items with Mann-Whitney U tests and Cliff’s delta effect sizes, with supplementary chi-square and Cramer’s V statistics for association structure.")
#p("Fifth, we conducted exploratory stigma-phenotype profiling using k-means clustering on standardized core belief items, selected cluster number by silhouette score, and reported cluster means and sizes as exploratory findings.")
#h2("F. Ethical Considerations")
#p("The analysis used de-identified survey data and reported aggregate findings only. No personal identifiers were used in the analytic outputs. The available dataset was handled as anonymized observational data for academic research use, and reporting was limited to group-level summaries.")
#h2("G. Methodological Limitations")
#p("Because the design is cross-sectional, associations should not be interpreted as causal effects. Complete-case modeling produced model-specific analytic samples (n=647 in the primary hierarchical model, n=406 in the sensitivity model, and n=837 in the multinomial model) and may introduce selection effects if missingness is not random. The achieved sample was dominated by younger and university-educated respondents, which may limit generalizability to older or less-educated Iraqi populations. Some instrument blocks had substantial missingness, so primary inference relied on the most complete and policy-relevant core variables.")
#chapter-page("Chapter Three", "Results")
#set-running-head("Results")
#section-title("IV. RESULTS")
#h2("IV.A Sample Profile and Descriptive Statistics")
#p("The final survey dataset included 877 respondents, and all percentages in this chapter follow the denominator policy defined in Methodology: percentages are reported as the percentage of valid responses for that item for descriptives, while model findings use model-specific complete-case denominators. Demographic distributions were therefore calculated as percentage of valid responses for that item (gender n=870, age n=873, educational level n=873, marital status n=872). Gender distribution was 71.95% female (n=626) and 28.05% male (n=244), as percentage of valid responses for that item. Age distribution was concentrated in younger participants, with 74.57% aged 18–25 years (n=651), 17.53% aged 26–35 years (n=153), 5.04% aged 36–45 years (n=44), 2.75% aged 46–60 years (n=24), and 0.11% older than 60 years (n=1), as percentage of valid responses for that item. Educational level was primarily university or postgraduate, with 78.92% university (n=689) and 13.52% postgraduate (n=118), while high school represented 6.99% (n=61) and primary represented 0.57% (n=5), as percentage of valid responses for that item. Marital status was 78.44% single (n=684), 20.99% married (n=183), 0.34% divorced (n=3), and 0.23% widowed (n=2), as percentage of valid responses for that item.")
#p("To keep model reporting readable, this chapter repeats each questionnaire code with a brief definition when it appears. Q6 refers to safety perception of psychiatric medication, Q7 refers to acceptability of psychiatric medication, Q8 refers to willingness to recommend psychiatric medication, and Q9 refers to social concern about interacting with a person who uses psychiatric medication. Q11 refers to the belief that doctors prescribe psychiatric medications more than necessary, Q12 refers to the belief that most psychiatric medications cause psychological or physical dependence, Q13 refers to the belief that modern psychiatric medications are safer than older ones, and Q31 refers to prior psychiatric medication use status.")
#p("Across core belief items, agreement levels were high for two statements and moderate for one statement. For Q11 (doctors prescribe psychiatric medications more than necessary), 51.55% agreed, 34.67% were neutral, and 13.78% disagreed. For Q12 (most psychiatric medications cause psychological or physical dependence), 67.40% agreed, 27.65% were neutral, and 4.95% disagreed. For Q13 (modern psychiatric medications are safer than older ones), 51.95% agreed, 35.86% were neutral, and 12.18% disagreed. The main question structure is shown in the corresponding figure below. The gender-stratified recommendation pattern is shown in the corresponding figure below. The diverging Likert distribution for Q11 and Q13 is shown in the corresponding figure below.")
#fig("../figures/27_donut_main_questions.png", "Figure 1. 27 donut main questions")
#fig("../figures/31_gender_recommendation_breakdown.png", "Figure 2. 31 gender recommendation breakdown")
#fig("../figures/19_likert_diverging_q11_q13.png", "Figure 3. 19 likert diverging q11 q13")
#h2("IV.B Main Outcome Distributions")
#p("The primary attitude outcomes showed mixed acceptance patterns. For Q6 (safety perception), 23.65% answered yes, 31.23% answered not sure, and 45.12% answered no. For Q7 (acceptability), 30.80% answered yes, 17.70% answered not sure, and 51.49% answered no. For Q8 (recommendation willingness), 57.65% answered yes, 11.62% answered not sure, and 30.72% answered no. For Q9 (social concern), 37.77% answered yes, 13.09% answered not sure, and 49.14% answered no.")
#p("Bivariate correlations among core variables were as follows: Q11 (belief that doctors prescribe psychiatric medications more than necessary) with Q12 (belief that most psychiatric medications cause psychological or physical dependence), r=0.269; Q13 (belief that modern psychiatric medications are safer than older ones) with Q11, r=-0.066; Q13 with Q12, r=-0.038; recommendation willingness (Q8) with Q11, r=-0.086; recommendation willingness (Q8) with Q12, r=-0.087; recommendation willingness (Q8) with Q13, r=0.077; acceptability (Q7) with recommendation willingness (Q8), r=0.232; and social concern (Q9) with recommendation willingness (Q8), r=-0.042.")
#h2("IV.C Hierarchical Logistic Regression (Primary Model)")
#p("The primary hierarchical logistic regression used a binary recommendation outcome (Q8, willingness to recommend psychiatric medication, yes vs no) with complete-case n=647. Model fit improved across blocks, with McFadden pseudo R² increasing from 0.0040 in Block 1 to 0.0116 in Block 2 and 0.0686 in Block 3. The Block 1 likelihood ratio p-value was 0.5037, Block 2 p-value was 0.0847, and Block 3 p-value was <0.0001.")
#p("In the final primary block, the largest directional effect was fear, which was associated with substantially lower recommendation odds (adjusted OR 0.504, 95% CI 0.358 to 0.711, p<0.0001). Q13 (belief that modern psychiatric medications are safer than older ones) showed a moderate positive effect size, with higher confidence in newer medications associated with higher recommendation odds (adjusted OR 1.507, 95% CI 1.248 to 1.820, p<0.0001). Gender showed a smaller-to-moderate positive shift (adjusted OR 1.516, 95% CI 1.043 to 2.205, p=0.0294), while Q11 (belief that doctors prescribe psychiatric medications more than necessary) showed a small inverse effect (adjusted OR 0.830, 95% CI 0.696 to 0.991, p=0.0396). Age, educational level, marital status, prior use (Q31), and Q12 (belief that most psychiatric medications cause psychological or physical dependence) were not statistically significant in this final block. The adjusted effect profile is visualized in the corresponding figure below.")
#fig("../figures/03_primary_adjusted_or_forest.png", "Figure 4. 03 primary adjusted or forest")
#p("A separate sensitivity model that added Q6 (safety perception) and Q7 (acceptability) used complete-case n=406 and produced McFadden pseudo R² of 0.2440 (fit type: mle). This model was reported as a sensitivity analysis because Q6 and Q7 are proximal to the recommendation outcome.")
#h2("IV.D Multinomial Logistic Regression (No/Yes/Not Sure Structure)")
#p("Multinomial logistic regression preserved the three-category recommendation structure with complete-case n=837 and model log-likelihood -748.910 (fit type: mle). The outcome categories were coded as No (reference), Yes, and Not sure, corresponding to Q8=0, Q8=1, and Q8=2.")
#p("For the first non-reference equation (Q8=1 Yes vs reference No, where Q8 is willingness to recommend psychiatric medication), Q13 (belief that modern psychiatric medications are safer than older ones) showed the strongest positive practical shift (RRR 1.585, 95% CI 1.328 to 1.892, p<0.0001), with gender showing a moderate positive shift (RRR 1.558, 95% CI 1.097 to 2.214, p=0.0133). Q12 (belief that most psychiatric medications cause psychological or physical dependence) showed a small-to-moderate inverse shift (RRR 0.794, 95% CI 0.651 to 0.970, p=0.0239). Other predictors in this equation were not statistically significant.")
#p("For the second non-reference equation (Q8=2 Not sure vs reference No, where Q8 is willingness to recommend psychiatric medication), gender showed the largest shift in the multinomial model (RRR 2.171, 95% CI 1.211 to 3.894, p=0.0093), indicating a stronger practical effect than in the Yes-vs-No equation, while age, education, marital status, prior use (Q31, prior psychiatric medication use), Q11 (belief that doctors prescribe psychiatric medications more than necessary), Q12 (belief that most psychiatric medications cause psychological or physical dependence), and Q13 (belief that modern psychiatric medications are safer than older ones) were not statistically significant. The comparative predictor pattern is displayed in the corresponding figure below.")
#fig("../figures/08_multinomial_key_predictor_comparison.png", "Figure 5. 08 multinomial key predictor comparison")
#h2("IV.E The Contact Hypothesis (Users vs Non-Users)")
#p("The contact analysis compared Users vs Non-Users using prior use status from Q31 (prior psychiatric medication use; Users n=127, Non-Users n=716). Mann-Whitney U tests were statistically significant for Q11 (belief that doctors prescribe psychiatric medications more than necessary), Q12 (belief that most psychiatric medications cause psychological or physical dependence), and Q13 (belief that modern psychiatric medications are safer than older ones), while chi-square tests were statistically significant for Q12 and Q13 but not for Q11.")
#p("For Q11 (belief that doctors prescribe psychiatric medications more than necessary), the Users median was 3.00 and the Non-Users median was 4.00, with small inverse practical differences (Cliff’s delta -0.108; Cramer’s V=0.094), Mann-Whitney U p=0.0428, chi-square p=0.1170, and N=843. For Q12 (belief that most psychiatric medications cause psychological or physical dependence), both medians were 4.00, with small inverse practical differences (Cliff’s delta -0.112; Cramer’s V=0.108), Mann-Whitney U p=0.0317, chi-square p=0.0428, and N=840. For Q13 (belief that modern psychiatric medications are safer than older ones), the Users median was 4.00 and the Non-Users median was 3.00, with the largest contact effect in this section, approaching moderate by rank effect size (Cliff’s delta 0.198) and remaining small-to-moderate by nominal association (Cramer’s V=0.139), Mann-Whitney U p=0.0002, chi-square p=0.0027, and N=842.")
#h2("IV.F Exploratory Stigma Phenotypes (Clearly Labeled)")
#p("Exploratory k-means clustering on standardized Q11–Q13 (Q11: belief that doctors prescribe psychiatric medications more than necessary; Q12: belief that most psychiatric medications cause psychological or physical dependence; Q13: belief that modern psychiatric medications are safer than older ones) evaluated k=2, k=3, and k=4. Silhouette scores were 0.274 for k=2, 0.272 for k=3, and 0.303 for k=4, so k=4 was selected by maximum silhouette criterion. These k-means profiles are data-driven exploratory groupings, not confirmed latent classes. The silhouette values indicate relative fit among the tested k values in this dataset, and they do not establish a definitive underlying class structure.")
#p("The four profiles had the following mean structures. Profile 0 (n=183) showed Q11 mean 4.404, Q12 mean 4.115, and Q13 mean 4.311. Profile 1 (n=230) showed Q11 mean 2.961, Q12 mean 2.804, and Q13 mean 3.578. Profile 2 (n=232) showed Q11 mean 2.694, Q12 mean 4.250, and Q13 mean 3.720. Profile 3 (n=223) showed Q11 mean 4.359, Q12 mean 4.291, and Q13 mean 2.610. Profile-level mean contrasts are shown in the corresponding figure below.")
#fig("../figures/14_profile_means_heatmap.png", "Figure 6. 14 profile means heatmap")
#h2("IV.G Results Summary")
#p("The survey included 877 participants and showed a sample pattern with higher female representation and concentration in younger, university-educated, and single respondents based on variable-specific valid denominators. In descriptive outcomes, recommendation willingness had the highest yes proportion (57.65%), while safety and acceptability showed higher no proportions than yes proportions. In the primary hierarchical logistic model (n=647), the strongest statistically supported predictors in the final block were gender, Q11, Q13, and fear. In the multinomial model (n=837), gender remained significant in both non-reference equations, while Q13 and Q12 were significant in one non-reference equation only. In Users vs Non-Users analyses, Mann-Whitney tests were significant for Q11, Q12, and Q13, and chi-square tests were significant for Q12 and Q13 only. Exploratory phenotype analysis identified a four-profile solution with the highest silhouette score among tested cluster counts.")
#pagebreak()
#chapter-page("Chapter Four", "Discussion")
#set-running-head("Discussion")
#section-title("V. DISCUSSION")
#h2("A. Interpretation of Primary Findings")
#p("This cross-sectional survey shows a mixed public position toward psychiatric medication in Iraq rather than uniform rejection or uniform support. Recommendation willingness was 57.65%, while 11.62% were not sure and 30.72% were against recommendation. Acceptability was lower: 30.80% considered psychiatric medication acceptable, 17.70% were not sure, and 51.49% considered it unacceptable. Safety perception was similarly low: 23.65% considered medication safe, 31.23% were not sure, and 45.12% considered it unsafe. This pattern suggests that many respondents accept medication in selected situations but still carry safety concerns and social hesitation.")
#p("The primary regression results clarify which beliefs matter most in this ambivalence. In practical magnitude terms, fear was the strongest directional predictor and showed a substantial inverse association with recommendation (adjusted OR 0.504, p<0.0001). Agreement with Q13, the belief that modern psychiatric medicines are safer than older ones, showed a moderate positive association (adjusted OR 1.507, p<0.0001). Female gender showed a smaller-to-moderate positive shift (adjusted OR 1.516, p=0.0294), while stronger agreement with Q11, the belief that doctors prescribe psychiatric medications more than necessary, showed a small inverse shift (adjusted OR 0.830, p=0.0396). These findings show that recommendation behavior in Iraq is shaped more by trust and safety perception than by basic demographics.")
#p("The multinomial model adds useful detail for hesitant respondents. For recommendation “Yes” vs “No” (reference category), Q13, the belief that modern psychiatric medicines are safer than older ones, showed the largest positive practical shift (RRR 1.585, p<0.0001), gender showed a moderate positive shift (RRR 1.558, p=0.0133), and Q12, the belief that most psychiatric medications cause psychological or physical dependence, showed a small-to-moderate inverse shift (RRR 0.794, p=0.0239). For the “Not sure” category, gender had the strongest multinomial shift overall (RRR 2.171, p=0.0093), while most attitudinal predictors were weaker and not statistically significant. This indicates that uncertainty is not only a neutral midpoint; it reflects unresolved risk beliefs that require targeted communication.")
#p("The Users vs Non-Users analysis supports a contact effect. Compared with non-users, users reported lower overprescribing concerns on Q11, the belief that doctors prescribe psychiatric medications more than necessary (median 3 vs 4, p=0.0428), and lower dependence concern intensity on Q12, the belief that most psychiatric medications cause psychological or physical dependence (p=0.0317), and they were more likely to agree with Q13, the belief that modern medications are safer than older ones (median 4 vs 3, p=0.0002). Practical differences were small for Q11 and Q12 by both rank and nominal metrics (Q11: Cliff’s delta -0.108, Cramer’s V=0.094; Q12: Cliff’s delta -0.112, Cramer’s V=0.108), while Q13 showed the strongest contact contrast, approaching moderate by Cliff’s delta (0.198) and small-to-moderate by Cramer’s V (0.139). In practical terms, direct or family-level exposure to psychiatric medication appears to improve trust, but it does not fully remove stigma.")
#h2("B. Comparison With Iraqi and Regional Literature")
#p("The present survey aligns with earlier Iraqi evidence that public understanding and stigma can coexist. Sadik et al. (2010) reported that many Iraqis accepted biomedical causes of mental illness while still expressing strong social distance and blame. Our findings show a comparable duality: many respondents would recommend medication, yet large proportions still consider it unsafe or socially problematic. Evidence from Baghdad university students also reports persistent stigma despite high educational exposure, which is consistent with the current sample profile where high education did not independently remove negative medication beliefs (Hussein Alwan et al., 2025).")
#p("Regional literature helps explain why concern about dependence and overprescribing remained strong in our models. Arab mental health literacy studies report persistent misconceptions about psychiatric disorders and treatment, including stigma-related beliefs and limited confidence in professional care in student and community groups (Elyamani et al., 2021). Our Q12 distribution, where 67.40% agreed with the statement that most psychiatric medications cause dependence, is consistent with that broader pattern. At the same time, the positive effect of Q13, confidence that modern psychiatric medications are safer than older ones, suggests that confidence in newer medications can partially offset this concern when communication is clear.")
#p("The findings also fit Iraqi service-use realities. Iraqi clinicians have reported that many patients still visit faith healers before or alongside psychiatric care, with barriers linked to accessibility, cultural beliefs, and mistrust of formal services (Younis et al., 2020). This pathway helps interpret why recommendation willingness in our sample was higher than perceived safety and acceptability. People may approve treatment in principle but still delay formal care when risk perceptions and social narratives remain unresolved.")
#p("Our results are also compatible with broader adherence evidence. Systematic reviews show that adherence is strongly affected by social support, stigma, and perceived treatment burden rather than diagnosis alone (Gast & Mathes, 2019; Abdisa et al., 2020). The current survey did not measure longitudinal adherence, but the strong effects of fear and dependence beliefs indicate that these same mechanisms are active at the acceptance stage in Iraq. In this sense, acceptance barriers and adherence barriers likely sit on the same pathway.")
#h2("C. Implications for Pharmacy Practice and Public Health")
#p("For Iraqi pharmacy practice, the data show that counseling should prioritize three messages: realistic safety information on modern psychiatric medications, clear distinction between therapeutic dependence and substance misuse, and transparent explanation of prescribing decisions. The regression results indicate that these topics are directly linked to recommendation behavior, so they should become standard counseling content in both community pharmacies and hospital settings.")
#p("The multinomial findings suggest a separate communication track for respondents who are uncertain rather than opposed. In practical counseling terms, the “Not sure” group should be approached as a confidence-building audience, because the model shows that common attitudinal predictors did not separate them from “No” as strongly as they did for “Yes,” while female gender remained associated with uncertainty. Pharmacists should therefore avoid treating uncertainty as hidden refusal and instead use short, structured conversations that verify what the person still does not understand about safety, expected benefit, and monitoring. By contrast, communication for respondents who say “No” should directly address the specific beliefs that distinguished acceptance from refusal in the model, especially Q12, the belief that most psychiatric medications cause psychological or physical dependence, and Q13, the belief that modern psychiatric medications are safer than older ones, with explicit explanation of how treatment plans are individualized and reviewed over time.")
#p("Pharmacists can also use contact-informed communication. Because users showed more favorable attitudes on key items, pharmacists can normalize treatment by integrating lived-experience narratives and family-focused counseling during dispensing and follow-up. This approach is feasible in Iraq, where pharmacists are often more accessible than psychiatrists. It may reduce fear and uncertainty before stigma leads to treatment delay.")
#p("At public health level, the results support integrating anti-stigma and medication-literacy components into primary care mental health services. Regional evidence shows that integrated primary care models improve outcomes in low-resource settings when they combine clinical care with structured education and follow-up (Cubillos et al., 2021). For Iraq, this means linking physician diagnosis, pharmacist counseling, and brief public education in one pathway rather than treating these as separate activities.")
#h2("D. Strengths and Limitations of the Present Study")
#p("The study has several strengths. It provides one of the larger recent Iraqi datasets on psychiatric medication acceptance (N=877), preserves response structure through multinomial modeling, and complements the primary model with contact-group and exploratory phenotype analyses. This analytic sequence gives more policy-relevant information than single binary comparisons.")
#p("The study also has limits. First, the cross-sectional design does not establish causality, so the reported associations should not be interpreted as directional effects over time. Second, complete-case modeling created model-specific analytic samples, with n=647 for the primary hierarchical model, n=406 for the sensitivity model, and n=837 for the multinomial model. This reduction from the full descriptive sample (N=877) can introduce selection bias if respondents with missing values differ systematically in stigma beliefs or medication experience, and it narrows how far the adjusted model estimates can be generalized to the wider Iraqi public. Third, the sample was mostly female and highly university-educated, so findings may not fully represent older, rural, or less educated Iraqi populations. Fourth, self-reported attitudes are vulnerable to social desirability bias and may either understate or overstate stigma.")
#h2("E. Priority Research Gaps")
#p("Future Iraqi research should test whether targeted pharmacist-led counseling can reduce fear and dependence beliefs and then improve actual treatment initiation and adherence. Longitudinal follow-up is needed to connect acceptance attitudes with refill behavior, persistence, and relapse outcomes. Multisite sampling across governorates should also examine urban-rural differences and service-access disparities, especially in areas with lower specialist density.")
#p("The exploratory stigma phenotypes identified in this study also need confirmatory work. These k-means profiles are data-driven exploratory groupings, and the silhouette values from k=2 to k=4 indicate relative fit only among the tested options rather than confirmed latent classes. Subsequent studies should validate these profiles with larger and more demographically balanced samples and apply confirmatory approaches before using profile labels as stable population categories, then evaluate whether each profile responds differently to educational messages, clinician communication style, and family involvement. This would allow Iraq to move from general anti-stigma messaging toward stratified interventions that match the dominant belief pattern in each subgroup.")
#pagebreak()
#chapter-page("Chapter Five", "Conclusions and Suggestions")
#set-running-head("Conclusions and Suggestions")
#section-title("VI. RECOMMENDATIONS")
#h2("A. Policy-Level Recommendations")
#p("The Iraqi Ministry of Health should adopt a national psychiatric medication acceptance strategy that links stigma reduction with medication safety communication. The survey shows that fear and low confidence in modern medication safety are central barriers. Policy messaging should therefore move beyond general awareness and directly address these beliefs. Standardized language should correct dependence misconceptions, explain modern medication safety, and acknowledge local cultural concerns. As an initial step, the Ministry can assign a joint technical group from the Mental Health Directorate, Pharmacy Directorate, and Primary Care Directorate. This group should produce one national counseling package and one public communication package for pilot implementation in selected governorates within 12 months.")
#p("National guidance should also formalize integrated mental health care in primary care settings, with defined roles for psychiatrists, primary care physicians, and pharmacists. Regional evidence supports integrated models for improving access and outcomes in resource-limited systems (Cubillos et al., 2021; Okasha et al., 2025). For Iraq, this model can reduce specialist bottlenecks and create earlier treatment contact points.")
#p("Policy should also support public campaigns that include religious and community leaders to address care delays linked to traditional help-seeking pathways (Younis et al., 2020). The aim is not to dismiss cultural practices, but to align them with timely referral to formal mental health services.")
#h2("B. Practice-Level Recommendations (Pharmacists, Physicians, Primary Care)")
#p("Pharmacists should implement structured counseling at first dispensing and refill visits for psychiatric medications. Counseling should cover expected benefits, common adverse effects, misconceptions about inevitable addiction, and signs that require physician follow-up. The present survey findings justify this focus because beliefs on overprescribing, dependence, and safety were statistically linked to recommendation behavior.")
#p("Physicians should use brief shared-decision communication in outpatient and inpatient settings, especially when introducing or changing treatment. Clear explanation of why a specific medicine is selected can reduce overprescribing suspicion and improve trust. In hospital settings, monthly prescribing audits led by senior psychiatrists and clinical pharmacists should monitor high-dose and polypharmacy patterns. Audit findings should trigger direct prescriber feedback and case-review meetings for outlier patterns, given documented Iraqi concerns about prescribing intensity in inpatient care (Nassr & Wadeea, 2026).")
#p("Primary care teams should create a simple referral-feedback loop between clinics and community pharmacies so patients receive consistent messages. Inconsistency across providers can strengthen uncertainty, which remained visible in the multinomial model.")
#h2("C. Education and Awareness Recommendations")
#p("Pharmacy and medical curricula in Iraq should include practical training on stigma-sensitive communication about psychiatric medication. Students should learn how to address dependence concerns, social blame, and family objections in clear Arabic and English clinical language. This recommendation is supported by local and regional evidence showing that stigma remains present even among highly educated groups (Hussein Alwan et al., 2025; Elyamani et al., 2021).")
#p("Public education campaigns should prioritize message testing before national rollout. Because the survey identified exploratory belief profiles, one uniform message will likely have limited impact. Campaigns should adapt tone and content to subgroups with high fear, high dependence concern, or high distrust of prescribing.")
#h2("D. Research Recommendations")
#p("Future Iraqi studies should evaluate intervention effectiveness rather than only describing attitudes. Priority designs include pragmatic trials of pharmacist-led counseling, integrated primary care psychoeducation, and contact-based anti-stigma messaging. Outcomes should include both belief change and behavioral endpoints such as clinic attendance, initiation of prescribed treatment, refill continuity, and relapse-related hospitalization.")
#p("Researchers should also conduct repeated cross-sectional surveys with harmonized measures to monitor trend changes in acceptance, safety perception, and recommendation willingness over time. This will allow policymakers to track whether reforms produce measurable public attitude improvement.")
#section-title("VII. CONCLUSION")
#h2("A. What the Cross-Sectional Study Adds")
#p("This study adds current Iraqi primary data showing that public acceptance of psychiatric medication is not binary. Many respondents supported recommending treatment, yet large proportions still doubted safety and social acceptability. Key predictors were attitudinal beliefs and fear rather than most demographic variables, which identifies practical targets for intervention.")
#h2("B. What the Combined Evidence (Survey + Literature) Indicates for Iraq")
#p("When interpreted with Iraqi and regional literature, the survey indicates that Iraq faces a trust-and-literacy gap more than a simple awareness gap. People may recognize mental health needs but still hesitate because of dependence concerns, overprescribing beliefs, and stigma shaped by social and cultural context. This pattern is consistent with earlier Iraqi public attitude studies and wider Arab mental health literacy findings.")
#p("The evidence also indicates that pharmacists are positioned to close this gap. In a system with limited specialist capacity, pharmacist-led counseling and coordinated primary care communication can translate treatment availability into treatment acceptance.")
#h2("C. Closing Evidence-Based Statement")
#p("The evidence from this study supports a clear national direction for Iraq: improve psychiatric medication acceptance by reducing fear, correcting dependence myths, and strengthening trust in modern treatment through integrated, pharmacist-inclusive care. If policy and practice align around these targets, Iraq can reduce treatment delay, improve adherence pathways, and narrow the mental health treatment gap.")
#pagebreak()
#set-running-head("References")
#section-title("VIII. REFERENCES")
#refp("Abdisa, Eba, Ginenus Fekadu, Shimelis Girma, et al. “Self-Stigma and Medication Adherence among Patients with Mental Illness Treated at Jimma University Medical Center, Southwest Ethiopia.” International Journal of Mental Health Systems 14, no. 1 (2020): 56. https://doi.org/10.1186/s13033-020-00391-6.")
#refp("Angermeyer, Matthias C., Sandra Van Der Auwera, Mauro G. Carta, and Georg Schomerus. “Public Attitudes towards Psychiatry and Psychiatric Treatment at the Beginning of the 21st Century: A Systematic Review and Meta‐analysis of Population Surveys.” World Psychiatry 16, no. 1 (2017): 50–61. https://doi.org/10.1002/wps.20383.")
#refp("Booth, Wendy A., Mabrouka Abuhmida, and Felix Anyanwu. “Mental Health Stigma: A Conundrum for Healthcare Practitioners in Conservative Communities.” Frontiers in Public Health 12 (May 2024): 1384521. https://doi.org/10.3389/fpubh.2024.1384521.")
#refp("Burnam, M. Audrey, Lisa S. Meredith, Terri Tanielian, and Lisa H. Jaycox. “Mental Health Care For Iraq And Afghanistan War Veterans.” Health Affairs 28, no. 3 (2009): 771–82. https://doi.org/10.1377/hlthaff.28.3.771.")
#refp("Cubillos, Leonardo, Sophia M. Bartels, William C. Torrey, et al. “The Effectiveness and Cost-Effectiveness of Integrating Mental Health Services in Primary Care in Low- and Middle-Income Countries: Systematic Review.” BJPsych Bulletin 45, no. 1 (2021): 40–52. https://doi.org/10.1192/bjb.2020.35.")
#refp("Elyamani, Rowaida, Sarah Naja, Ayman Al-Dahshan, Hamed Hamoud, Mohammed Iheb Bougmiza, and Noora Alkubaisi. “Mental Health Literacy in Arab States of the Gulf Cooperation Council: A Systematic Review.” PLOS ONE 16, no. 1 (2021): e0245156. https://doi.org/10.1371/journal.pone.0245156.")
#refp("Gast, Alina, and Tim Mathes. “Medication Adherence Influencing Factors—an (Updated) Overview of Systematic Reviews.” Systematic Reviews 8, no. 1 (2019): 112. https://doi.org/10.1186/s13643-019-1014-8.")
#refp("Horne, Robert, John Weinman, and Maittew Hankins. “The Beliefs about Medicines Questionnaire: The Development and Evaluation of a New Method for Assessing the Cognitive Representation of Medication.” Psychology & Health 14, no. 1 (1999): 1–24. https://doi.org/10.1080/08870449908407311.")
#refp("Hussein Alwan, Iman, Mohammed Fadhil Ali, and Zeyad Tariq Madalla. “Factors Influencing Stigma Toward Mental Illness Among Students at the University of Baghdad.” International Journal of Body, Mind and Culture 12, no. 6 (2025): 161–70. https://doi.org/10.61838/ijbmc.v12i5.945.")
#refp("Kadhim, Sheima Nadim, Zainab Haroon Ahmed, and Muntadher Luay Abdulsahib. “ANXIETY, DEPRESSION, AND PSYCHOTROPIC DRUGS USAGE BY UNIVERSITY STUDENTS OF MEDICAL GROUP IN BASRA, IRAQ.” Universal Journal of Pharmaceutical Research, ahead of print, May 15, 2024. https://doi.org/10.22270/ujpr.v9i2.1081.")
#refp("Kalaman, Clarisse Roswini, Norhayati Ibrahim, Vinorra Shaker, et al. “Parental Factors Associated with Child or Adolescent Medication Adherence: A Systematic Review.” Healthcare 11, no. 4 (2023): 501. https://doi.org/10.3390/healthcare11040501.")
#refp("Mojtabai, Ramin. “Americans’ Attitudes Toward Psychiatric Medications: 1998–2006.” Psychiatric Services 60, no. 8 (2009): 1015–23. https://doi.org/10.1176/ps.2009.60.8.1015.")
#refp("Nassr, Ola A., and Raghad F. Wadeea. “Prevalence and Predictors of High-Dose Antipsychotic Therapy among Adult Psychiatric Inpatients in Baghdad, Iraq.” South African Journal of Psychiatry 32, no. 0 (2026): a2606. https://doi.org/10.4102/SAJPSYCHIATRY.v32i0.2606.")
#refp("Okasha, Tarek, Nermin M. Shaker, and Dina Aly El-Gabry. “Mental Health Services in Egypt, the Middle East, and North Africa.” International Review of Psychiatry 37, nos. 3–4 (2025): 306–14. https://doi.org/10.1080/09540261.2024.2400143.")
#refp("Rasheed, Sana, Eisha Kashif, Rida Arif, et al. “The Impact of Stigma on Health Care-Seeking Behavior in Military Personnel with Mental Health Challenges.” Annals of Medicine and Surgery (2012) 88, no. 1 (2026): 630–36. https://doi.org/10.1097/MS9.0000000000004569.")
#refp("Sadik, Sabah, Marie Bradley, Saad Al-Hasoon, and Rachel Jenkins. “Public Perception of Mental Health in Iraq.” International Journal of Mental Health Systems 4, no. 1 (2010): 26. https://doi.org/10.1186/1752-4458-4-26.")
#refp("Saied, AbdulRahman A., Sirwan Khalid Ahmed, Asmaa A. Metwally, and Hani Aiash. “Iraq’s Mental Health Crisis: A Way Forward?” The Lancet 402, no. 10409 (2023): 1235–36. https://doi.org/10.1016/S0140-6736(23)01283-7.")
#refp("Slewa-Younan, Shameran, Jonathan Mond, Elise Bussion, et al. “Mental Health Literacy of Resettled Iraqi Refugees in Australia: Knowledge about Posttraumatic Stress Disorder and Beliefs about Helpfulness of Interventions.” BMC Psychiatry 14, no. 1 (2014): 320. https://doi.org/10.1186/s12888-014-0320-x.")
#refp("Younis, Maha S., and Deema Khunda. “Maha Sulaiman Younis: A Personal History of Psychiatry in Iraq through War and Conflict.” GLOBAL PSYCHIATRY ARCHIVES 3, no. 2 (2020): 113–18. https://doi.org/10.52095/gpa.2020.1355.")
#refp("Younis, Maha S., Riyadh K. Lafta, and Saba Dhiaa. “Faith Healers Are Taking over the Role of Psychiatrists in Iraq.” Qatar Medical Journal 2019, no. 3 (2020). https://doi.org/10.5339/qmj.2019.13.")
#refp("Zolezzi, Monica, Maha Alamri, Shahd Shaar, and Daniel Rainkie. “Stigma Associated with Mental Illness and Its Treatment in the Arab Culture: A Systematic Review.” International Journal of Social Psychiatry 64, no. 6 (2018): 597–609. https://doi.org/10.1177/0020764018789200.")
#refp("Zygmunt, Annette, Mark Olfson, Carol A. Boyer, and David Mechanic. “Interventions to Improve Medication Adherence in Schizophrenia.” American Journal of Psychiatry 159, no. 10 (2002): 1653–64. https://doi.org/10.1176/appi.ajp.159.10.1653.")
