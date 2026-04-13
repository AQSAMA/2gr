import pandas as pd
import numpy as np
import json

# 1. Load the dataset
file_name = "survey_Psychiatric_Medication_Use_and_Public_Acceptance_in_Iraq.xlsx"
df = pd.read_excel(file_name)

# 2. Extract and save question labels (Professional Metadata Backup)
question_labels = df.iloc[0].to_dict()
with open("question_labels.json", "w", encoding="utf-8") as f:
    json.dump(question_labels, f, ensure_ascii=False, indent=4)

# Drop row 0 to keep only the actual respondent data
df = df.drop(0).reset_index(drop=True)

# 3. ADVANCED CLEANING PIPELINE
# Remove invisible formatting characters
df = df.replace(r'\xa0|\u200f|\u200e|\u200c', '', regex=True)

# Normalize spaces and handle nulls safely
for col in df.columns:
    if df[col].dtype == 'object' or pd.api.types.is_string_dtype(df[col]):
        # Replace multiple spaces with a single space, and strip edges
        df[col] = df[col].astype(str).str.replace(r'\s+', ' ', regex=True).str.strip()
        # Convert string representations of nulls back to actual NaN
        df[col] = df[col].replace({'nan': np.nan, 'None': np.nan, '': np.nan})

# 4. COMPREHENSIVE MAPPING DICTIONARIES (Extended Context)
age_mapping = {"18-25": 1, "26-35": 2, "36-45": 3, "46-60": 4, ">60": 5}
gender_mapping = {"ذكر": 1, "انثى": 2, "أنثى": 2}

education_mapping = {
    "ابتدائي": 1, "إبتدائي": 1,
    "متوسط": 2, "متوسطة": 2,
    "اعدادي": 3, "إعدادي": 3, "ثانوي": 3, "ثانوية": 3,
    "معهد": 3.5, "دبلوم": 3.5,
    "جامعي": 4, "بكالوريوس": 4,
    "دراسات عليا": 5, "ماجستير": 5, "دكتوراه": 5
}
marital_mapping = {"أعزب": 1, "اعزب": 1, "متزوج": 2, "مطلق": 3, "أرمل": 4, "ارمل": 4}

likert_mapping = {
    "أوافق بشدة": 5, "اوافق بشدة": 5,
    "أوافق": 4, "اوافق": 4,
    "محايد": 3,
    "لا أوافق": 2, "لا اوافق": 2,
    "لا أوافق بشدة": 1, "لا اوافق بشدة": 1
}

yes_no_mapping = {
    "نعم": 1,
    "لا": 0,
    "غير متأكد": 2, "غير متاكد": 2, "ربما": 2, "لا أعرف": 2, "لا اعرف": 2
}

# 5. COLUMN CATEGORIZATION
likert_cols = ['Q11', 'Q12', 'Q13', 'Q15', 'Q16', 'Q17', 'Q18', 'Q19', 'Q20']
yes_no_cols = ['Q6', 'Q7', 'Q8', 'Q9', 'Q31', 'Q22', 'Q23', 'Q24', 'Q25', 'Q26', 'Q27', 'Q28', 'Q29', 'Q30', 'Q31.1', 'Q32']

# 6. APPLY MAPPINGS SAFELY
mappings = {
    'Q1': age_mapping,
    'Q2': gender_mapping,
    'Q4': education_mapping,
    'Q5': marital_mapping
}

for col, mapping in mappings.items():
    if col in df.columns:
        df[col] = df[col].replace(mapping)

for col in likert_cols:
    if col in df.columns:
        df[col] = df[col].replace(likert_mapping)

for col in yes_no_cols:
    if col in df.columns:
        df[col] = df[col].replace(yes_no_mapping)

# 7. SMART NUMERIC CONVERSION
for col in df.columns:
    try:
        df[col] = pd.to_numeric(df[col])
    except (ValueError, TypeError):
        pass # Keep as string if it cannot be converted yet

# 8. THE SANITY CHECK (Detect Unmapped Data)
unmapped_warnings = {}
for col in df.columns:
    if df[col].dtype == 'object':
        # Get unique values, ignoring NaNs
        unique_vals = df[col].dropna().unique().tolist()
        if unique_vals:
            unmapped_warnings[col] = unique_vals

# 9. SAVE & REPORT
df.to_csv("encoded_survey_data.csv", index=False)

print("-" * 55)
print("✅ DATA CLEANING COMPLETE!")
print(f"Total valid responses processed: {len(df)}")
print("Files generated:")
print("  1. encoded_survey_data.csv (Clean numerical data)")
print("  2. question_labels.json    (Reference for Q mappings)")

if unmapped_warnings:
    print("\n⚠️  WARNING: The following columns still contain unmapped text:")
    for col, vals in unmapped_warnings.items():
        print(f"    -> Column '{col}': {vals}")
    print("   (Action: Add these words to the mapping dictionaries if they should be numbers)")
else:
    print("\n🎉 PERFECT RUN: All text successfully converted to numerical data!")
print("-" * 55)
