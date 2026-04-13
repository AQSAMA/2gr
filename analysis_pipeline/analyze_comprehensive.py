import json
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import chi2_contingency, fisher_exact, mannwhitneyu, spearmanr
import statsmodels.formula.api as smf


BASE_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = BASE_DIR / "analysis_pipeline" / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CLEAN_CSV = OUTPUT_DIR / "cleaned_survey_data_utf8.csv"
QUESTION_LABELS_JSON = OUTPUT_DIR / "question_labels.json"
ANALYSIS_MD = OUTPUT_DIR / "survey_data_results_comprehensive.md"
ROOT_ANALYSIS_MD = BASE_DIR / "survey_data_results.md"


def cronbach_alpha(frame: pd.DataFrame):
    x = frame.dropna()
    if x.empty or x.shape[1] < 2:
        return np.nan, len(x)
    k = x.shape[1]
    variance_sum = x.var(axis=0, ddof=1).sum()
    total_var = x.sum(axis=1).var(ddof=1)
    if total_var == 0:
        return np.nan, len(x)
    alpha = (k / (k - 1)) * (1 - (variance_sum / total_var))
    return float(alpha), len(x)


def wilson_ci(k, n, z=1.96):
    if n == 0:
        return np.nan, np.nan
    p = k / n
    denom = 1 + z**2 / n
    center = (p + z**2 / (2 * n)) / denom
    half = z * np.sqrt((p * (1 - p) + z**2 / (4 * n)) / n) / denom
    return max(0, center - half), min(1, center + half)


def fmt_count_pct(k, n):
    if n == 0:
        return "0 (0.0%)"
    return f"{int(k)} ({100 * k / n:.1f}%)"


def yes_no_unsure_table(df, col):
    valid = df[col].dropna()
    n = len(valid)
    yes = int((valid == 1).sum())
    no = int((valid == 0).sum())
    unsure = int((valid == 2).sum())
    return n, fmt_count_pct(yes, n), fmt_count_pct(no, n), fmt_count_pct(unsure, n)


def yes_no_table(df, col):
    valid = df[col].dropna()
    n = len(valid)
    yes = int((valid == 1).sum())
    no = int((valid == 0).sum())
    return n, fmt_count_pct(yes, n), fmt_count_pct(no, n)


def likert_grouped(df, col):
    valid = df[col].dropna()
    n = len(valid)
    agree = int(valid.isin([4, 5]).sum())
    neutral = int((valid == 3).sum())
    disagree = int(valid.isin([1, 2]).sum())
    return n, fmt_count_pct(agree, n), fmt_count_pct(neutral, n), fmt_count_pct(disagree, n)


def likert_full_counts(df, col):
    valid = df[col].dropna()
    n = len(valid)
    out = {}
    for code in [1, 2, 3, 4, 5]:
        out[code] = fmt_count_pct(int((valid == code).sum()), n)
    return n, out


def cramers_v(ct):
    chi2, _, _, _ = chi2_contingency(ct)
    n = ct.to_numpy().sum()
    r, k = ct.shape
    if n == 0 or min(r, k) <= 1:
        return np.nan
    return np.sqrt(chi2 / (n * (min(r, k) - 1)))


def chi_square_result(df, x, y):
    d = df[[x, y]].dropna()
    if d.empty:
        return np.nan, np.nan, 0, np.nan
    ct = pd.crosstab(d[x], d[y])
    if ct.shape[0] < 2 or ct.shape[1] < 2:
        return np.nan, np.nan, len(d), np.nan
    chi2, p, _, _ = chi2_contingency(ct)
    cv = cramers_v(ct)
    return chi2, p, len(d), cv


def fisher_or_ci(df, exposure_col, outcome_col, exposure_yes=1, outcome_yes=1):
    d = df[[exposure_col, outcome_col]].dropna().copy()
    if d.empty:
        return np.nan, np.nan, np.nan, np.nan, 0
    d[exposure_col] = (d[exposure_col] == exposure_yes).astype(int)
    d[outcome_col] = (d[outcome_col] == outcome_yes).astype(int)
    ct = pd.crosstab(d[exposure_col], d[outcome_col])
    for i in [0, 1]:
        for j in [0, 1]:
            if i not in ct.index:
                ct.loc[i] = 0
            if j not in ct.columns:
                ct[j] = 0
    ct = ct.sort_index().reindex(columns=[0, 1])
    a = ct.loc[1, 1]
    b = ct.loc[1, 0]
    c = ct.loc[0, 1]
    d0 = ct.loc[0, 0]
    _, p = fisher_exact([[a, b], [c, d0]])

    aa, bb, cc, dd = a, b, c, d0
    if min(aa, bb, cc, dd) == 0:
        aa += 0.5
        bb += 0.5
        cc += 0.5
        dd += 0.5
    or_est = (aa * dd) / (bb * cc)
    se = np.sqrt(1 / aa + 1 / bb + 1 / cc + 1 / dd)
    lcl = np.exp(np.log(or_est) - 1.96 * se)
    ucl = np.exp(np.log(or_est) + 1.96 * se)
    return or_est, p, lcl, ucl, int(len(d))


def main():
    if not CLEAN_CSV.exists():
        raise FileNotFoundError(f"Cleaned CSV not found: {CLEAN_CSV}")

    df = pd.read_csv(CLEAN_CSV)
    with open(QUESTION_LABELS_JSON, "r", encoding="utf-8") as f:
        qlabels = json.load(f)

    n_total = len(df)
    users = df[df["Q31"] == 1].copy()
    non_users = df[df["Q31"] == 0].copy()

    yes_no_unsure_cols = ["Q6", "Q7", "Q8", "Q9"]
    likert_all = ["Q11", "Q12", "Q13"]
    likert_user = ["Q15", "Q16", "Q17", "Q18", "Q19", "Q20"]
    yes_no_user = ["Q22", "Q23", "Q24", "Q25", "Q26", "Q27", "Q28", "Q29", "Q30", "Q31_1", "Q32"]

    demographics_order = {
        "Q1": [1, 2, 3, 4, 5],
        "Q2": [1, 2],
        "Q4": [1, 2, 3, 4, 5, 6],
        "Q5": [1, 2, 3, 4],
    }
    demographics_labels = {
        "Q1": {1: "18-25", 2: "26-35", 3: "36-45", 4: "46-60", 5: ">60"},
        "Q2": {1: "Male", 2: "Female"},
        "Q4": {1: "Primary", 2: "Middle School", 3: "High School", 4: "Institute/Diploma", 5: "University", 6: "Postgraduate"},
        "Q5": {1: "Single", 2: "Married", 3: "Divorced", 4: "Widowed"},
    }

    lines = []
    lines.append(f"# Psychiatric Medication Use and Public Acceptance in Iraq — Comprehensive Survey Analysis (N={n_total})")
    lines.append("")
    lines.append("## 1) Data Integrity and Scope")
    lines.append("")
    lines.append(f"- Total respondents analyzed: **{n_total}**")
    lines.append(f"- Participants with prior/current psychiatric medication use (Q31=Yes): **{len(users)}**")
    lines.append(f"- Participants with no prior use (Q31=No): **{len(non_users)}**")
    lines.append("")
    lines.append("### Missingness Snapshot")
    lines.append("")
    lines.append("| Variable | Question (Arabic from source) | Non-missing n | Missing n | Missing % |")
    lines.append("|---|---|---:|---:|---:|")
    for c in df.columns:
        nn = int(df[c].notna().sum())
        miss = int(df[c].isna().sum())
        lines.append(f"| {c} | {qlabels.get(c, '')} | {nn} | {miss} | {100*miss/n_total:.1f} |")

    lines.append("")
    lines.append("## 2) Descriptive Results")
    lines.append("")
    lines.append("### 2.1 Sociodemographic Distribution")
    lines.append("")
    lines.append("| Variable | Category | n (%) |")
    lines.append("|---|---|---:|")
    for var in ["Q1", "Q2", "Q4", "Q5"]:
        valid = df[var].dropna()
        n_valid = len(valid)
        for code in demographics_order[var]:
            k = int((valid == code).sum())
            lines.append(f"| {var} | {demographics_labels[var][code]} | {fmt_count_pct(k, n_valid)} |")

    lines.append("")
    lines.append("### 2.2 Public Acceptance / Social Concern (Yes-No-Not Sure Questions)")
    lines.append("")
    lines.append("| Code | Question | Valid n | Yes | No | Not sure |")
    lines.append("|---|---|---:|---:|---:|---:|")
    for col in yes_no_unsure_cols:
        n, yes, no, unsure = yes_no_unsure_table(df, col)
        lines.append(f"| {col} | {qlabels.get(col, '')} | {n} | {yes} | {no} | {unsure} |")

    lines.append("")
    lines.append("### 2.3 Core Belief Items (Likert 1-5)")
    lines.append("")
    lines.append("| Code | Question | Valid n | Agree/Strongly Agree | Neutral | Disagree/Strongly Disagree |")
    lines.append("|---|---|---:|---:|---:|---:|")
    for col in likert_all:
        n, a, ne, d = likert_grouped(df, col)
        lines.append(f"| {col} | {qlabels.get(col, '')} | {n} | {a} | {ne} | {d} |")

    lines.append("")
    lines.append("### 2.4 User-Only Items (participants with Q31=Yes)")
    lines.append("")
    lines.append("| Code | Question | Valid n | Yes or Agree (%) | No or Disagree (%) | Neutral/Not sure (%) |")
    lines.append("|---|---|---:|---:|---:|---:|")
    for col in likert_user:
        n, a, ne, d = likert_grouped(users, col)
        lines.append(f"| {col} | {qlabels.get(col, '')} | {n} | {a} | {d} | {ne} |")
    for col in yes_no_user:
        n, y, no = yes_no_table(users, col)
        lines.append(f"| {col} | {qlabels.get(col, '')} | {n} | {y} | {no} | 0 (0.0%) |")

    lines.append("")
    lines.append("### 2.5 Full Response Distribution for Likert Items")
    lines.append("")
    lines.append("| Code | Valid n | 1 | 2 | 3 | 4 | 5 |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|")
    for col in likert_all + likert_user:
        n, counts = likert_full_counts(df if col in likert_all else users, col)
        lines.append(f"| {col} | {n} | {counts[1]} | {counts[2]} | {counts[3]} | {counts[4]} | {counts[5]} |")

    lines.append("")
    lines.append("## 3) Inferential Statistics and Effect Sizes")
    lines.append("")
    lines.append("### 3.1 Chi-square Association Tests")
    lines.append("")
    lines.append("| Predictor | Outcome | N used | Chi-square | p-value | Cramer's V |")
    lines.append("|---|---|---:|---:|---:|---:|")
    chi_pairs = [
        ("Q1", "Q7"),
        ("Q2", "Q9"),
        ("Q4", "Q6"),
        ("Q5", "Q8"),
        ("Q31", "Q8"),
        ("Q31", "Q9"),
    ]
    for x, y in chi_pairs:
        chi2, p, n_used, cv = chi_square_result(df, x, y)
        lines.append(
            f"| {x} ({qlabels.get(x, '')}) | {y} ({qlabels.get(y, '')}) | {n_used} | "
            f"{'NA' if pd.isna(chi2) else f'{chi2:.3f}'} | "
            f"{'NA' if pd.isna(p) else f'{p:.4f}'} | "
            f"{'NA' if pd.isna(cv) else f'{cv:.3f}'} |"
        )

    lines.append("")
    lines.append("### 3.2 Odds Ratios (Fisher exact, 95% CI)")
    lines.append("")
    lines.append("| Exposure (Yes=1) | Outcome (Yes=1) | N used | Odds ratio | 95% CI | p-value |")
    lines.append("|---|---|---:|---:|---:|---:|")
    or_specs = [
        ("Q31", "Q8"),  # prior use -> recommendation
        ("Q31", "Q9"),  # prior use -> fear
        ("Q6", "Q8"),   # believes safe -> recommendation
        ("Q7", "Q8"),   # medical equivalence -> recommendation
    ]
    for exp_col, out_col in or_specs:
        d = df[[exp_col, out_col]].dropna()
        if out_col in ["Q8", "Q9"]:
            d = d[d[out_col].isin([0, 1])]
        if exp_col in ["Q6", "Q7"]:
            d = d[d[exp_col].isin([0, 1])]
        or_est, p, lcl, ucl, n_used = fisher_or_ci(d, exp_col, out_col, 1, 1)
        lines.append(
            f"| {exp_col} ({qlabels.get(exp_col, '')}) | {out_col} ({qlabels.get(out_col, '')}) | {n_used} | "
            f"{'NA' if pd.isna(or_est) else f'{or_est:.3f}'} | "
            f"{'NA' if pd.isna(lcl) else f'{lcl:.3f} to {ucl:.3f}'} | "
            f"{'NA' if pd.isna(p) else f'{p:.4f}'} |"
        )

    lines.append("")
    lines.append("### 3.3 Correlation of Belief Items (Spearman)")
    lines.append("")
    lines.append("| Pair | N used | Spearman rho | p-value |")
    lines.append("|---|---:|---:|---:|")
    corr_items = ["Q11", "Q12", "Q13", "Q19", "Q20"]
    for a, b in combinations(corr_items, 2):
        d = df[[a, b]].dropna()
        if len(d) < 5:
            lines.append(f"| {a}-{b} | {len(d)} | NA | NA |")
            continue
        rho, p = spearmanr(d[a], d[b])
        lines.append(f"| {a}-{b} | {len(d)} | {rho:.3f} | {p:.4f} |")

    lines.append("")
    lines.append("### 3.4 Scale Reliability and Group Comparison")
    lines.append("")
    df["Risk_Belief_Score"] = df[["Q11", "Q12"]].mean(axis=1)
    alpha_general, alpha_n = cronbach_alpha(df[["Q11", "Q12"]])
    alpha_user, alpha_user_n = cronbach_alpha(users[["Q15", "Q16", "Q17", "Q18", "Q19", "Q20"]])
    lines.append(f"- Cronbach alpha (general risk belief scale: Q11+Q12): **{alpha_general:.3f}** (n={alpha_n})")
    lines.append(f"- Cronbach alpha (user-experience scale: Q15-Q20): **{alpha_user:.3f}** (n={alpha_user_n})")
    lines.append("")

    mw = df[["Q2", "Risk_Belief_Score"]].dropna()
    male = mw[mw["Q2"] == 1]["Risk_Belief_Score"]
    female = mw[mw["Q2"] == 2]["Risk_Belief_Score"]
    if len(male) > 0 and len(female) > 0:
        u_stat, p_mw = mannwhitneyu(male, female, alternative="two-sided")
        lines.append(f"- Mann-Whitney U test for gender difference in Risk_Belief_Score: U={u_stat:.1f}, p={p_mw:.4f}")
        lines.append(f"- Median score (male): {male.median():.2f}, median score (female): {female.median():.2f}")
    else:
        lines.append("- Mann-Whitney U test could not be computed because one group had no data.")

    lines.append("")
    lines.append("### 3.5 Multivariable Logistic Regression")
    lines.append("")
    reg_df = df.copy()
    reg_df["Recommend_Binary"] = np.where(reg_df["Q8"] == 1, 1, np.where(reg_df["Q8"].isin([0, 2]), 0, np.nan))
    reg_df["PriorUse_Binary"] = np.where(reg_df["Q31"] == 1, 1, np.where(reg_df["Q31"] == 0, 0, np.nan))
    reg_df["Safe_Binary"] = np.where(reg_df["Q6"] == 1, 1, np.where(reg_df["Q6"] == 0, 0, np.nan))
    reg_df["Acceptable_Binary"] = np.where(reg_df["Q7"] == 1, 1, np.where(reg_df["Q7"] == 0, 0, np.nan))
    reg_df["Fear_Binary"] = np.where(reg_df["Q9"] == 1, 1, np.where(reg_df["Q9"] == 0, 0, np.nan))

    reg_df["Married_Binary"] = np.where(reg_df["Q5"] == 2, 1, np.where(reg_df["Q5"].isin([1, 3, 4]), 0, np.nan))

    model_data = reg_df[
        [
            "Recommend_Binary",
            "Q1",
            "Q2",
            "Q4",
            "Married_Binary",
            "PriorUse_Binary",
            "Safe_Binary",
            "Acceptable_Binary",
            "Fear_Binary",
        ]
    ].dropna()
    lines.append(f"- Complete-case sample size for regression: **{len(model_data)}**")

    try:
        model = smf.logit(
            "Recommend_Binary ~ C(Q2) + Q1 + Q4 + Married_Binary + PriorUse_Binary + Safe_Binary + Acceptable_Binary + Fear_Binary",
            data=model_data,
        ).fit(disp=0, maxiter=200)
        params = model.params
        conf = model.conf_int()
        pvals = model.pvalues
        lines.append("")
        lines.append("| Predictor | Adjusted OR | 95% CI | p-value |")
        lines.append("|---|---:|---:|---:|")
        for term in params.index:
            or_val = np.exp(params[term])
            ci_low = np.exp(conf.loc[term, 0])
            ci_high = np.exp(conf.loc[term, 1])
            lines.append(f"| {term} | {or_val:.3f} | {ci_low:.3f} to {ci_high:.3f} | {pvals[term]:.4f} |")
        lines.append("")
        lines.append(f"- Model pseudo R² (McFadden): **{model.prsquared:.4f}**")
        lines.append(f"- Likelihood ratio test p-value: **{model.llr_pvalue:.4f}**")
    except Exception as e:
        lines.append(f"- Regression could not be fit: `{e}`")

    lines.append("")
    lines.append("## 4) Mathematical Details and Checks")
    lines.append("")
    lines.append("### 4.1 Key Proportions with 95% Wilson Confidence Intervals")
    lines.append("")
    lines.append("| Metric | Numerator/Denominator | Proportion | 95% CI |")
    lines.append("|---|---:|---:|---:|")
    ci_specs = [
        ("Believes psychiatric medications are safe (Q6=Yes)", int((df["Q6"] == 1).sum()), int(df["Q6"].isin([0, 1, 2]).sum())),
        ("Would recommend to a close person (Q8=Yes)", int((df["Q8"] == 1).sum()), int(df["Q8"].isin([0, 1, 2]).sum())),
        ("Fear of dealing with psychiatric medication users (Q9=Yes)", int((df["Q9"] == 1).sum()), int(df["Q9"].isin([0, 1, 2]).sum())),
        ("Among users: report improvement (Q22=Yes)", int((users["Q22"] == 1).sum()), int(users["Q22"].isin([0, 1]).sum())),
        ("Among users: report bothersome side effects (Q18 Agree/Strongly Agree)", int(users["Q18"].isin([4, 5]).sum()), int(users["Q18"].notna().sum())),
    ]
    for label, k, n in ci_specs:
        lcl, ucl = wilson_ci(k, n)
        p = (k / n) if n > 0 else np.nan
        lines.append(
            f"| {label} | {k}/{n} | {'NA' if n==0 else f'{100*p:.1f}%'} | {'NA' if n==0 else f'{100*lcl:.1f}% to {100*ucl:.1f}%'} |"
        )

    lines.append("")
    lines.append("### 4.2 Skip-Pattern and Instrument Consistency")
    lines.append("")
    user_section_cols = ["Q15", "Q16", "Q17", "Q18", "Q19", "Q20", "Q22", "Q23", "Q24", "Q25", "Q26", "Q27", "Q28", "Q29", "Q30", "Q31_1", "Q32"]
    non_user_non_missing = int(non_users[user_section_cols].notna().sum(axis=1).gt(0).sum())
    user_all_missing = int(users[user_section_cols].notna().sum(axis=1).eq(0).sum())
    lines.append(f"- Non-users with any user-section response filled: **{non_user_non_missing}**")
    lines.append(f"- Users with all user-section responses missing: **{user_all_missing}**")

    lines.append("")
    lines.append("## 5) Audit of Problems in Previous Analysis Attempts")
    lines.append("")
    lines.append("1. Some binary user variables (Q23, Q24, Q26, Q30, Q32) were summarized as Likert items in one prior script; this forced valid Yes/No values into the neutral column and produced incorrect tables.")
    lines.append("2. Q19 and Q20 were interpreted as full-sample items in prior outputs, while their valid denominator is user-only; this can mislead interpretation if denominator is not shown.")
    lines.append("3. One prior script contains `with open(\"analyze_v2.py\", \"w\")` which would overwrite the analysis script itself when executed.")
    lines.append("4. Prior education grouping merged categories inconsistently and omitted mapped code 2 and code 4 in some tables.")
    lines.append("5. Some p-values were reported without effect sizes or confidence intervals; this report adds Cramer's V, odds-ratio confidence intervals, and Wilson intervals.")

    lines.append("")
    lines.append("## 6) Practical Interpretation Summary")
    lines.append("")
    lines.append("The dataset shows a wide gap between willingness to recommend psychiatric medication and concerns about safety, dependence, and social fear. User subgroup data shows simultaneous benefit and burden: many users report clinical improvement while many also report side effects and anxiety. Multivariable analysis helps separate independent predictors of recommendation behavior from simple bivariate associations.")

    output_text = "\n".join(lines) + "\n"
    ANALYSIS_MD.write_text(output_text, encoding="utf-8")
    ROOT_ANALYSIS_MD.write_text(output_text, encoding="utf-8")

    print(f"Comprehensive analysis written to: {ANALYSIS_MD}")
    print(f"Root analysis file updated: {ROOT_ANALYSIS_MD}")


if __name__ == "__main__":
    main()
