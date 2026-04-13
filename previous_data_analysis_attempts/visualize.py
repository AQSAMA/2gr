import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

# 1. Setup & Style
os.makedirs('assets', exist_ok=True)
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_context("paper", font_scale=1.2)

# Load Data
df = pd.read_csv("encoded_survey_data.csv")

# ---------------------------------------------------------
# Figure 1: Demographics & Prior Use (Donut Charts)
# ---------------------------------------------------------
fig1, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 5))

# Gender
gender_counts = df['Q2'].value_counts()
labels_g = ['Female', 'Male'] if 2.0 in gender_counts.index else ['Male', 'Female']
sizes_g = [gender_counts.get(2.0, 0), gender_counts.get(1.0, 0)]
ax1.pie(sizes_g, labels=labels_g, autopct='%1.1f%%', startangle=90, colors=['#ff9999','#66b3ff'], wedgeprops=dict(width=0.4, edgecolor='w'))
ax1.set_title('Gender Distribution', pad=15, fontweight='bold')

# Prior Use
use_counts = df['Q31'].value_counts()
labels_u = ['No', 'Yes', 'Not Sure']
sizes_u = [use_counts.get(0.0, 0), use_counts.get(1.0, 0), use_counts.get(2.0, 0)]
ax2.pie(sizes_u, labels=labels_u, autopct='%1.1f%%', startangle=90, colors=['#99ff99','#ffcc99', '#c2c2f0'], wedgeprops=dict(width=0.4, edgecolor='w'))
ax2.set_title('Prior Use of Psychiatric Meds', pad=15, fontweight='bold')

plt.tight_layout()
plt.savefig('assets/fig1_demographics.png', dpi=300, bbox_inches='tight')
plt.close()

# ---------------------------------------------------------
# Figure 2: The Stigma & Beliefs Spectrum (Stacked Bar)
# ---------------------------------------------------------
questions = {
    'Q11': 'Doctors Overprescribe Them',
    'Q12': 'They Cause Dependence/Addiction',
    'Q20': 'They Cause Long-term Harm'
}

results = {'Disagree': [], 'Neutral': [], 'Agree': []}
ylabels = []

for q_code, q_text in questions.items():
    counts = df[q_code].dropna().value_counts(normalize=True) * 100
    disagree = counts.get(1.0, 0) + counts.get(2.0, 0)
    neutral = counts.get(3.0, 0)
    agree = counts.get(4.0, 0) + counts.get(5.0, 0)
    
    results['Disagree'].append(disagree)
    results['Neutral'].append(neutral)
    results['Agree'].append(agree)
    ylabels.append(q_text)

fig2, ax = plt.subplots(figsize=(10, 4))
y = np.arange(len(ylabels))

ax.barh(y, results['Disagree'], color='#e74c3c', label='Disagree')
ax.barh(y, results['Neutral'], left=results['Disagree'], color='#95a5a6', label='Neutral')
ax.barh(y, results['Agree'], left=np.array(results['Disagree'])+np.array(results['Neutral']), color='#2ecc71', label='Agree')

ax.set_yticks(y)
ax.set_yticklabels(ylabels, fontweight='bold')
ax.set_xlabel('Percentage of Respondents (%)', fontweight='bold')
ax.set_title('Public Beliefs and Stigma Indicators', pad=15, fontweight='bold')
ax.legend(loc='upper center', bbox_to_anchor=(0.5, -0.15), ncol=3)

# Add value labels
for i in range(len(ylabels)):
    ax.text(results['Disagree'][i]/2, i, f"{results['Disagree'][i]:.1f}%", va='center', ha='center', color='white', fontweight='bold')
    ax.text(results['Disagree'][i] + results['Neutral'][i] + results['Agree'][i]/2, i, f"{results['Agree'][i]:.1f}%", va='center', ha='center', color='white', fontweight='bold')

plt.tight_layout()
plt.savefig('assets/fig2_stigma_spectrum.png', dpi=300, bbox_inches='tight')
plt.close()

# ---------------------------------------------------------
# Figure 3: Education Impact (Grouped Bar Chart)
# ---------------------------------------------------------
df['Edu_Group'] = np.where(df['Q4'] >= 4.0, 'University+', 'Below University')
safe_uni = (df[df['Edu_Group'] == 'University+']['Q6'] == 1.0).mean() * 100
safe_non = (df[df['Edu_Group'] == 'Below University']['Q6'] == 1.0).mean() * 100

accept_uni = (df[df['Edu_Group'] == 'University+']['Q7'] == 1.0).mean() * 100
accept_non = (df[df['Edu_Group'] == 'Below University']['Q7'] == 1.0).mean() * 100

labels = ['Perceive Meds as Safe', 'Acceptable like BP/Diabetes Meds']
uni_scores = [safe_uni, accept_uni]
non_scores = [safe_non, accept_non]

x = np.arange(len(labels))
width = 0.35

fig3, ax = plt.subplots(figsize=(8, 5))
rects1 = ax.bar(x - width/2, uni_scores, width, label='University+', color='#3498db')
rects2 = ax.bar(x + width/2, non_scores, width, label='Below University', color='#e67e22')

ax.set_ylabel('Percentage of Respondents (%)', fontweight='bold')
ax.set_title('Impact of Education on Public Acceptance', pad=15, fontweight='bold')
ax.set_xticks(x)
ax.set_xticklabels(labels, fontweight='bold')
ax.legend()
ax.set_ylim(0, max(uni_scores + non_scores) + 15)

for rect in rects1 + rects2:
    height = rect.get_height()
    ax.annotate(f'{height:.1f}%',
                xy=(rect.get_x() + rect.get_width() / 2, height),
                xytext=(0, 3), textcoords="offset points",
                ha='center', va='bottom', fontweight='bold')

plt.tight_layout()
plt.savefig('assets/fig3_education_impact.png', dpi=300, bbox_inches='tight')
plt.close()

# ---------------------------------------------------------
# Figure 4: User Experience (Horizontal Bar)
# ---------------------------------------------------------
users = df[df['Q31'] == 1.0]
if len(users) > 0:
    efficacy = (users['Q22'] == 1.0).mean() * 100
    side_effects = users['Q18'].isin([4.0, 5.0]).mean() * 100
    
    fig4, ax = plt.subplots(figsize=(8, 3))
    categories = ['Reported Clinical Improvement', 'Experienced Bothersome Side Effects']
    values = [efficacy, side_effects]
    colors = ['#27ae60', '#c0392b']
    
    bars = ax.barh(categories, values, color=colors)
    ax.set_xlabel('Percentage among Actual Users (%)', fontweight='bold')
    ax.set_title(f'User Experience Profile (n={len(users)})', pad=15, fontweight='bold')
    ax.set_xlim(0, 100)
    
    for bar in bars:
        ax.text(bar.get_width() - 5, bar.get_y() + bar.get_height()/2, 
                f'{bar.get_width():.1f}%', 
                va='center', ha='right', color='white', fontweight='bold')

    plt.tight_layout()
    plt.savefig('assets/fig4_user_experience.png', dpi=300, bbox_inches='tight')
    plt.close()

print("✅ Visualization Complete! Check the 'assets' folder for 4 high-quality charts.")

