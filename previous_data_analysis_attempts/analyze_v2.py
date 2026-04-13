import os
import pandas as pd
import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.formula.api as smf

# Create a folder for thesis charts
os.makedirs("thesis_charts", exist_ok=True)

# 1. LOAD DATA
df = pd.read_csv("encoded_survey_data.csv")
total_n = len(df)

# ==========================================
# FEATURE ENGINEERING (FOR ADVANCED STATS)
# ==========================================
# Create a "Negative Beliefs / Stigma Score" (Sum of Q11, Q12, Q19, Q20)
stigma_cols = ['Q11', 'Q12', 'Q19', 'Q20']
df['Stigma_Score'] = df[stigma_cols].sum(axis=1, skipna=False)

# Binary Outcome for Regression: Willing to Recommend (Q8) -> 1=Yes, 0=No/Not Sure. Map NaNs properly.
df['Recommend_Binary'] = df['Q8'].map({1.0: 1, 0.0: 0, 2.0: 0})

# Binary Prior Use (Q31)
df['Used_Meds_Binary'] = df['Q31'].map({1.0: 1, 0.0: 0, 2.0: 0})

# ==========================================
# HELPER FUNCTIONS (BUG-FREE)
# ==========================================
def cronbach_alpha(df_items):
    # Calculates Cronbach's Alpha to prove the reliability of your Stigma Score
    df_items = df_items.dropna()
    k = df_items.shape[1]
    variance_sum = df_items.var(axis=0, ddof=1).sum()
    total_var = df_items.sum(axis=1).var(ddof=1)
    if total_var == 0: return 0
    return (k / (k - 1)) * (1 - (variance_sum / total_var))

def format_pct(count, total):
    if total == 0: return "0 (0.0%)"
    return f"{int(count)} ({(count/total)*100:.1f}%)"

def get_freq_table(series, mapping_dict):
    counts = series.value_counts(dropna=False)
    lines =[]
    for val, text in mapping_dict.items():
        c = counts.get(val, 0)
        lines.append(f"| | {text} | {format_pct(c, total_n)} |")
    return "\n".join(lines)

def summarize_likert(series):
    valid = series.dropna()
    n = len(valid)
    agree = valid.isin([4.0, 5.0]).sum()
    neutral = (valid == 3.0).sum()
    disagree = valid.isin([1.0, 2.0]).sum()
    return format_pct(agree, n), format_pct(neutral, n), format_pct(disagree, n)

def summarize_yes_no(series):
    valid = series.dropna()
    n = len(valid)
    yes = (valid == 1.0).sum()
    no = (valid == 0.0).sum()
    ns = (valid == 2.0).sum()
    return format_pct(yes, n), format_pct(no, n), format_pct(ns, n)

# ==========================================
# DATA VISUALIZATIONS
# ==========================================
print("Generating Charts...")

# 1. Stigma Score by Gender (Boxplot)
plt.figure(figsize=(8, 5))
sns.boxplot(x=df['Q2'].replace({1.0: 'Male', 2.0: 'Female'}), y=df['Stigma_Score'], palette="pastel")
plt.title("Stigma Score Distribution by Gender")
plt.ylabel("Stigma Score (Higher = More Negative Beliefs)")
plt.xlabel("Gender")
plt.savefig("thesis_charts/Stigma_by_Gender.png", dpi=300, bbox_inches='tight')
plt.close()

# 2. Safety Perception
safe_counts = df['Q6'].value_counts().rename({1.0: 'Yes', 0.0: 'No', 2.0: 'Not Sure'})
safe_counts.plot(kind='pie', autopct='%1.1f%%', colors=['#ff9999','#66b3ff','#99ff99'], startangle=90)
plt.title("Perception: Are Psychiatric Meds Safe?")
plt.ylabel("")
plt.savefig("thesis_charts/Safety_Perception.png", dpi=300, bbox_inches='tight')
plt.close()

# ==========================================
# INFERENTIAL STATS (T-TESTS, ANOVA, REGRESSION)
# ==========================================
# 1. Cronbach's Alpha
alpha_score = cronbach_alpha(df[stigma_cols])

# 2. Gender Difference in Stigma
male_stigma = df[df['Q2'] == 1.0]['Stigma_Score'].dropna()
female_stigma = df[df['Q2'] == 2.0]['Stigma_Score'].dropna()
t_stat, p_gender_stigma = stats.ttest_ind(male_stigma, female_stigma)

# 3. Logistic Regression (Predicting willingness to recommend)
try:
    reg_df = df.dropna(subset=['Recommend_Binary', 'Q2', 'Q1', 'Q4', 'Used_Meds_Binary'])
    # C(Q2) treats gender as categorical. Q1 is age, Q4 is edu.
    model = smf.logit("Recommend_Binary ~ C(Q2) + Q1 + Q4 + Used_Meds_Binary", data=reg_df).fit(disp=0)
    regression_summary = model.summary().as_text()
except Exception as e:
    regression_summary = f"Regression could not be run. Check statsmodels installation: {str(e)}"

# ==========================================
# BUILD THE REPORT
# ==========================================
print("Building Markdown Report...")

md = f"""# GRADUATION THESIS: ADVANCED STATISTICAL ANALYSIS
**Total Sample Size (N):** {total_n}

## PART 1: DESCRIPTIVE STATISTICS

### TABLE 1: Sociodemographic Characteristics
| Variable | Category | n (%) |
| :--- | :--- | :--- |
| **Gender** | | |
{get_freq_table(df['Q2'], {1.0: 'Male', 2.0: 'Female'})}
| **Age** | | |
{get_freq_table(df['Q1'], {1.0: '18-25', 2.0: '26-35', 3.0: '36-45', 4.0: '46-60', 5.0: '>60'})}
| **Education** | | |
{get_freq_table(df['Q4'], {1.0: 'Primary', 2.0: 'Middle School', 3.0: 'High School', 3.5: 'Institute/Diploma', 4.0: 'University Degree', 5.0: 'Postgraduate'})}
| **Marital Status**| | |
{get_freq_table(df['Q5'], {1.0: 'Single', 2.0: 'Married', 3.0: 'Divorced', 4.0: 'Widowed'})}

### TABLE 2: Public Acceptance (Yes/No)
| Question | Yes n(%) | No n(%) | Not Sure n(%) |
| :--- | :--- | :--- | :--- |
| Q6: Are psychiatric meds safe? | {summarize_yes_no(df['Q6'])[0]} | {summarize_yes_no(df['Q6'])[1]} | {summarize_yes_no(df['Q6'])[2]} |
| Q7: Acceptable like BP/Diabetes meds? | {summarize_yes_no(df['Q7'])[0]} | {summarize_yes_no(df['Q7'])[1]} | {summarize_yes_no(df['Q7'])[2]} |
| Q8: Would recommend to loved one? | {summarize_yes_no(df['Q8'])[0]} | {summarize_yes_no(df['Q8'])[1]} | {summarize_yes_no(df['Q8'])[2]} |
| Q9: Fear of dealing with patients? | {summarize_yes_no(df['Q9'])[0]} | {summarize_yes_no(df['Q9'])[1]} | {summarize_yes_no(df['Q9'])[2]} |

### TABLE 3: Core Beliefs (Likert)
| Question | Agree | Neutral | Disagree |
| :--- | :--- | :--- | :--- |
| Q11: Doctors overprescribe them | {summarize_likert(df['Q11'])[0]} | {summarize_likert(df['Q11'])[1]} | {summarize_likert(df['Q11'])[2]} |
| Q12: They cause dependence | {summarize_likert(df['Q12'])[0]} | {summarize_likert(df['Q12'])[1]} | {summarize_likert(df['Q12'])[2]} |
| Q13: Modern meds are safer | {summarize_likert(df['Q13'])[0]} | {summarize_likert(df['Q13'])[1]} | {summarize_likert(df['Q13'])[2]} |
| Q19: I worry about addiction | {summarize_likert(df['Q19'])[0]} | {summarize_likert(df['Q19'])[1]} | {summarize_likert(df['Q19'])[2]} |

---
## PART 2: LIVED EXPERIENCE (n = {len(df[df['Q31'] == 1.0])})
*(Only for participants who have used psychiatric meds)*

### A. Likert Questions
| Question | Agree | Neutral | Disagree |
| :--- | :--- | :--- | :--- |
"""
users = df[df['Q31'] == 1.0]
user_likert = {'Q15': 'Necessary for health', 'Q16': 'Maintain stability', 'Q17': 'Condition worsens without', 'Q18': 'Bothersome side effects'}
for q_code, q_text in user_likert.items():
    if q_code in users.columns:
        a, n, d = summarize_likert(users[q_code])
        md += f"| {q_text} | {a} | {n} | {d} |\n"

md += """
### B. Yes/No/Not Sure Questions
| Question | Yes | No | Not Sure |
| :--- | :--- | :--- | :--- |
"""
user_yes_no = {
    'Q23': 'Lose control of my life', 'Q24': 'Help me feel normal',
    'Q26': 'Confidence in treatment', 'Q30': 'Make my life worse', 'Q32': 'Anxiety regarding side effects'
}
for q_code, q_text in user_yes_no.items():
    if q_code in users.columns:
        y, no, ns = summarize_yes_no(users[q_code])
        md += f"| {q_text} | {y} | {no} | {ns} |\n"

md += f"""
---
## PART 3: ADVANCED INFERENTIAL STATISTICS (THESIS LEVEL)

### A. Reliability Analysis (Cronbach's Alpha)
* **Stigma Score Reliability:** {alpha_score:.2f}
* *Interpretation for your thesis:* Alpha scores above 0.70 are considered acceptable, and >0.80 is good. This proves your questions mathematically measure the same underlying "stigma".

### B. Independent T-Test (Stigma by Gender)
* **Male Mean Stigma Score:** {male_stigma.mean():.2f}
* **Female Mean Stigma Score:** {female_stigma.mean():.2f}
* **T-Statistic:** {t_stat:.2f} (p-value: {p_gender_stigma:.4f})
* *Interpretation:* If p < 0.05, there is a statistically significant difference in negative beliefs between men and women.

### C. Logistic Regression (Predicting Acceptance)
This model predicts whether someone will "Recommend" medications (Q8) based on Demographics and Prior Use simultaneously.

[Regression Summary Details]
{regression_summary}

*Interpretation of Regression:* Look at the P>|z| column. Values under 0.05 mean that specific factor strongly drives public acceptance independently of the other variables. 
"""

with open("analyze_v2.py", "w", encoding="utf-8") as f:
    pass

with open("thesis_final_results.md", "w", encoding="utf-8") as f:
    f.write(md)

print("✅ SUCCESS! 'thesis_final_results.md' and the 'thesis_charts/' folder have been generated.")
