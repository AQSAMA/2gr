import json
import re
from pathlib import Path

import numpy as np
import pandas as pd


BASE_DIR = Path(__file__).resolve().parents[1]
RAW_XLSX = BASE_DIR / "survey_Psychiatric_Medication_Use_and_Public_Acceptance_in_Iraq.xlsx"
OUTPUT_DIR = BASE_DIR / "analysis_pipeline" / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CLEAN_CSV_UTF8 = OUTPUT_DIR / "cleaned_survey_data_utf8.csv"
CLEAN_CSV_UTF8_SIG = OUTPUT_DIR / "cleaned_survey_data_utf8_sig.csv"
QUESTION_LABELS_JSON = OUTPUT_DIR / "question_labels.json"
VALUE_LABELS_JSON = OUTPUT_DIR / "value_labels.json"
CLEANING_REPORT_MD = OUTPUT_DIR / "cleaning_report.md"


def normalize_text(value):
    if pd.isna(value):
        return np.nan
    text = str(value)
    text = re.sub(r"[\u200f\u200e\u200c\xa0]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    if text in {"", "nan", "None", "null", "NULL"}:
        return np.nan
    return text


def main():
    raw_df = pd.read_excel(RAW_XLSX, dtype=object)
    raw_df = raw_df.rename(columns=lambda c: str(c).replace(".", "_"))
    question_labels = raw_df.iloc[0].to_dict()
    df = raw_df.drop(index=0).reset_index(drop=True)

    for col in df.columns:
        df[col] = df[col].map(normalize_text)

    demographic_maps = {
        "Q1": {"18-25": 1, "26-35": 2, "36-45": 3, "46-60": 4, ">60": 5},
        "Q2": {"ذكر": 1, "انثى": 2, "أنثى": 2},
        "Q4": {"ابتدائي": 1, "متوسط": 2, "ثانوي": 3, "معهد": 4, "دبلوم": 4, "جامعي": 5, "دراسات عليا": 6},
        "Q5": {"أعزب": 1, "اعزب": 1, "متزوج": 2, "مطلق": 3, "أرمل": 4, "ارمل": 4},
    }

    likert_map = {
        "أوافق بشدة": 5,
        "اوافق بشدة": 5,
        "أوافق": 4,
        "اوافق": 4,
        "محايد": 3,
        "لا أوافق": 2,
        "لا اوافق": 2,
        "لا أوافق بشدة": 1,
        "لا اوافق بشدة": 1,
    }

    yes_no_unsure_map = {
        "نعم": 1,
        "لا": 0,
        "غير متأكد": 2,
        "غير متاكد": 2,
        "ربما": 2,
        "لا أعرف": 2,
        "لا اعرف": 2,
    }

    yes_no_map = {"نعم": 1, "لا": 0}

    likert_cols = ["Q11", "Q12", "Q13", "Q15", "Q16", "Q17", "Q18", "Q19", "Q20"]
    yes_no_unsure_cols = ["Q6", "Q7", "Q8", "Q9"]
    yes_no_cols = ["Q31", "Q22", "Q23", "Q24", "Q25", "Q26", "Q27", "Q28", "Q29", "Q30", "Q31_1", "Q32"]

    for col, mapping in demographic_maps.items():
        if col in df.columns:
            df[col] = df[col].replace(mapping)

    for col in likert_cols:
        if col in df.columns:
            df[col] = df[col].replace(likert_map)

    for col in yes_no_unsure_cols:
        if col in df.columns:
            df[col] = df[col].replace(yes_no_unsure_map)

    for col in yes_no_cols:
        if col in df.columns:
            df[col] = df[col].replace(yes_no_map)

    for col in df.columns:
        try:
            df[col] = pd.to_numeric(df[col], errors="raise")
        except Exception:
            pass

    unmapped = {}
    for col in df.columns:
        non_null = df[col].dropna()
        if non_null.dtype == object:
            unique_values = sorted(non_null.unique().tolist())
            if unique_values:
                unmapped[col] = unique_values

    with open(QUESTION_LABELS_JSON, "w", encoding="utf-8") as f:
        json.dump(question_labels, f, ensure_ascii=False, indent=2)

    value_labels = {
        "Q1": {"1": "18-25", "2": "26-35", "3": "36-45", "4": "46-60", "5": ">60"},
        "Q2": {"1": "Male", "2": "Female"},
        "Q4": {"1": "Primary", "2": "Middle School", "3": "High School", "4": "Institute/Diploma", "5": "University", "6": "Postgraduate"},
        "Q5": {"1": "Single", "2": "Married", "3": "Divorced", "4": "Widowed"},
        "LIKERT": {"1": "Strongly disagree", "2": "Disagree", "3": "Neutral", "4": "Agree", "5": "Strongly agree"},
        "YES_NO_UNSURE": {"0": "No", "1": "Yes", "2": "Not sure"},
        "YES_NO": {"0": "No", "1": "Yes"},
    }
    with open(VALUE_LABELS_JSON, "w", encoding="utf-8") as f:
        json.dump(value_labels, f, ensure_ascii=False, indent=2)

    df.to_csv(CLEAN_CSV_UTF8, index=False, encoding="utf-8")
    df.to_csv(CLEAN_CSV_UTF8_SIG, index=False, encoding="utf-8-sig")

    missing_table = pd.DataFrame(
        {
            "question_code": df.columns,
            "non_missing_n": [int(df[c].notna().sum()) for c in df.columns],
            "missing_n": [int(df[c].isna().sum()) for c in df.columns],
        }
    )
    missing_table["missing_pct"] = (missing_table["missing_n"] / len(df) * 100).round(1)

    report_lines = []
    report_lines.append("# Cleaning Report")
    report_lines.append("")
    report_lines.append(f"- Raw rows in Excel (including label row): {len(raw_df)}")
    report_lines.append(f"- Respondent rows after removing label row: {len(df)}")
    report_lines.append(f"- Number of variables: {len(df.columns)}")
    report_lines.append(f"- UTF-8 output: `{CLEAN_CSV_UTF8}`")
    report_lines.append(f"- UTF-8 with BOM output: `{CLEAN_CSV_UTF8_SIG}`")
    report_lines.append("")
    report_lines.append("## Missingness by Variable")
    report_lines.append("")
    report_lines.append("| Variable | Non-missing n | Missing n | Missing % |")
    report_lines.append("|---|---:|---:|---:|")
    for _, row in missing_table.iterrows():
        report_lines.append(
            f"| {row['question_code']} | {int(row['non_missing_n'])} | {int(row['missing_n'])} | {row['missing_pct']:.1f} |"
        )

    report_lines.append("")
    report_lines.append("## Unmapped Text Values")
    report_lines.append("")
    if unmapped:
        for col, values in unmapped.items():
            report_lines.append(f"- {col}: {values}")
    else:
        report_lines.append("- None. All mapped fields are numeric.")
    report_lines.append("- Instrument note: Q28 and Q29 have duplicate Arabic wording in the source questionnaire header row.")

    CLEANING_REPORT_MD.write_text("\n".join(report_lines), encoding="utf-8")

    print("Cleaning complete.")
    print(f"Rows processed: {len(df)}")
    print(f"Unmapped columns: {len(unmapped)}")


if __name__ == "__main__":
    main()
