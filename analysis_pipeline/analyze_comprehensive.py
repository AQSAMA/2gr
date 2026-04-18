import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy.stats import chi2_contingency, mannwhitneyu
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler


BASE_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = BASE_DIR / "analysis_pipeline" / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CLEAN_CSV = OUTPUT_DIR / "cleaned_survey_data_utf8.csv"
QUESTION_LABELS_JSON = OUTPUT_DIR / "question_labels.json"
VALUE_LABELS_JSON = OUTPUT_DIR / "value_labels.json"
ANALYSIS_MD = OUTPUT_DIR / "survey_data_results_comprehensive.md"
ROOT_ANALYSIS_MD = BASE_DIR / "survey_data_results.md"
ANALYSIS_JSON = OUTPUT_DIR / "analysis_results.json"
KMEANS_N_INIT = 50
KMEANS_RANDOM_STATE = 42
DEMOGRAPHIC_QUESTION_IDS = ("Q1", "Q2", "Q4", "Q5")
# Exploratory profile search is intentionally bounded to small k values for interpretability with Q11-Q13.
CLUSTER_RANGE = [2, 3, 4]
# English render labels are used only for report text so final outputs remain English-only.
# Source Arabic labels are preserved in question_labels.json from the raw survey header row.
# Translation mapping here follows direct item-level wording from that source header.
ENGLISH_QUESTION_LABELS = {
    "Q1": "Age",
    "Q2": "Gender",
    "Q4": "Educational level",
    "Q5": "Marital status",
    "Q6": "Do you think psychiatric medications are safe?",
    "Q7": "Do you see their use as acceptable like hypertension and diabetes medications?",
    "Q8": "Would you recommend psychiatric medications to someone close if needed?",
    "Q9": "Do you have concerns about interacting with a person taking psychiatric medications?",
    "Q11": "Doctors prescribe medications more than necessary",
    "Q12": "Most medications cause psychological or physical dependence",
    "Q13": "Modern medications are safer than older ones",
    "Q15": "I believe psychiatric medications are necessary for my health",
    "Q16": "Psychiatric medications keep me stable",
    "Q17": "Without psychiatric medications, my condition would worsen",
    "Q18": "Psychiatric medications cause bothersome side effects",
    "Q19": "I worry about habituation or addiction to psychiatric medications",
    "Q20": "Psychiatric medications may harm my health in the long term",
    "Q22": "I feel better when using psychiatric medications",
    "Q23": "Medications make me lose control of my life",
    "Q24": "Medications help me be more normal",
    "Q25": "Medications cause problems for me",
    "Q26": "Medications make me confident in my ability to recover",
    "Q27": "Using medications makes me feel afraid",
    "Q28": "Psychiatric medications help me be in a better state",
    "Q29": "Psychiatric medications help me be in a better state (duplicate wording in source item)",
    "Q30": "Medications make my life worse",
    "Q31": "Do you currently use or have you ever used a psychiatric medication?",
    "Q31_1": "I feel psychiatric medications are necessary for me",
    "Q32": "Medications cause me worry about their effects",
}


def fmt_p(p):
    if p is None or pd.isna(p):
        return "NA"
    return "<0.0001" if p < 0.0001 else f"{p:.4f}"


def fmt_or(or_val, ci_low, ci_high):
    if any(pd.isna(v) for v in [or_val, ci_low, ci_high]):
        return "NA"
    if any(np.isinf(v) for v in [or_val, ci_low, ci_high]):
        return "NA"
    if any(v <= 0 for v in [or_val, ci_low, ci_high]):
        return "NA"
    if any(v > 1e4 for v in [or_val, ci_low, ci_high]):
        return "NA"
    return f"{or_val:.3f} ({ci_low:.3f} to {ci_high:.3f})"


def safe_exp(x, clip=20):
    if pd.isna(x):
        return np.nan
    x = float(np.clip(x, -clip, clip))
    return float(np.exp(x))


def has_arabic(text):
    if text is None:
        return False
    return bool(re.search(r"[\u0600-\u06FF]", str(text)))


def english_question_label(col, qlabels):
    if col in ENGLISH_QUESTION_LABELS:
        return ENGLISH_QUESTION_LABELS[col]
    raw = qlabels.get(col, "")
    if has_arabic(raw):
        return ""
    return str(raw)


def numeric_code_label_map(value_labels, question_id):
    """Convert JSON string-coded value labels to integer-keyed mappings for coded survey columns."""
    return {
        int(code): label
        for code, label in value_labels.get(question_id, {}).items()
        if str(code).lstrip("-").isdigit()
    }


def cramers_v_from_ct(ct: pd.DataFrame):
    if ct.shape[0] < 2 or ct.shape[1] < 2:
        return np.nan
    chi2, _, _, _ = chi2_contingency(ct)
    n = ct.values.sum()
    if n == 0:
        return np.nan
    return np.sqrt(chi2 / (n * (min(ct.shape) - 1)))


def cliffs_delta(x, y):
    x = np.asarray(x)
    y = np.asarray(y)
    if len(x) == 0 or len(y) == 0:
        return np.nan
    gt = 0
    lt = 0
    for xv in x:
        gt += np.sum(xv > y)
        lt += np.sum(xv < y)
    return (gt - lt) / (len(x) * len(y))


def as_binary(series, yes=1, no=0):
    return np.where(series == yes, 1, np.where(series == no, 0, np.nan))


def add_binary_demographics(df):
    d = df.copy()
    d["Age_Binary"] = np.where(d["Q1"] == 1, 1, np.where(d["Q1"] > 1, 0, np.nan))
    d["Edu_Binary"] = np.where(d["Q4"] >= 5, 1, np.where(d["Q4"] < 5, 0, np.nan))
    d["Married_Binary"] = np.where(d["Q5"] >= 2, 1, np.where(d["Q5"] == 1, 0, np.nan))
    d["Gender_Binary"] = np.where(d["Q2"] == 2, 1, np.where(d["Q2"] == 1, 0, np.nan))
    return d


def safe_logit_fit(formula, data, maxiter=500):
    mle_model = smf.logit(formula, data=data).fit(disp=0, maxiter=maxiter)
    return mle_model, "mle"


def safe_mnlogit_fit(y, X, maxiter=500):
    mle_model = sm.MNLogit(y, X).fit(disp=0, maxiter=maxiter)
    return mle_model, "mle"


def extract_multinomial_ci(conf, outcome_col, term):
    if conf is None:
        return np.nan, np.nan
    if isinstance(conf.index, pd.MultiIndex):
        for key in (outcome_col, str(outcome_col)):
            try:
                ci_row = conf.loc[(key, term)]
                return ci_row.get("lower", np.nan), ci_row.get("upper", np.nan)
            except KeyError:
                continue
        return np.nan, np.nan
    ci_row = conf.loc[term]
    if hasattr(ci_row, "get"):
        low = ci_row.get("lower", np.nan)
        high = ci_row.get("upper", np.nan)
    else:
        low = ci_row[0] if len(ci_row) > 0 else np.nan
        high = ci_row[1] if len(ci_row) > 1 else np.nan
    return low, high


def to_builtin(value):
    if isinstance(value, dict):
        return {str(k): to_builtin(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [to_builtin(v) for v in value]
    if isinstance(value, np.ndarray):
        return [to_builtin(v) for v in value.tolist()]
    if isinstance(value, pd.Series):
        return [to_builtin(v) for v in value.tolist()]
    if isinstance(value, pd.DataFrame):
        return [to_builtin(row) for row in value.to_dict(orient="records")]
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating, float)):
        if pd.isna(value) or np.isinf(value):
            return None
        return float(value)
    if isinstance(value, (np.bool_,)):
        return bool(value)
    return value


def summarize_logit(model):
    params = model.params
    try:
        conf = model.conf_int()
    except Exception:
        conf = pd.DataFrame({0: params - np.nan, 1: params + np.nan})
    try:
        pvals = model.pvalues
    except Exception:
        pvals = pd.Series(np.nan, index=params.index)
    rows = []
    for term in params.index:
        low_beta = np.nan
        high_beta = np.nan
        if term in conf.index and conf.shape[1] >= 2:
            ci_row = conf.loc[term]
            low_beta = ci_row.iloc[0]
            high_beta = ci_row.iloc[1]
        or_val = safe_exp(params[term])
        low = safe_exp(low_beta)
        high = safe_exp(high_beta)
        p = float(pvals[term]) if term in pvals.index else np.nan
        rows.append((term, or_val, low, high, p))
    return rows


def fit_hierarchical_models(df):
    work = add_binary_demographics(df.copy())
    work["Recommend_Binary"] = as_binary(work["Q8"], yes=1, no=0)
    work["PriorUse_Binary"] = as_binary(work["Q31"], yes=1, no=0)
    work["Fear_Binary"] = as_binary(work["Q9"], yes=1, no=0)

    # Primary model set avoids proximal tautology with Q6/Q7.
    base_cols = [
        "Recommend_Binary",
        "Age_Binary",
        "Gender_Binary",
        "Edu_Binary",
        "Married_Binary",
        "PriorUse_Binary",
        "Q11",
        "Q12",
        "Q13",
        "Fear_Binary",
    ]
    d = work[base_cols].dropna().copy()

    formulas = [
        "Recommend_Binary ~ Age_Binary + Gender_Binary + Edu_Binary + Married_Binary",
        "Recommend_Binary ~ Age_Binary + Gender_Binary + Edu_Binary + Married_Binary + PriorUse_Binary",
        "Recommend_Binary ~ Age_Binary + Gender_Binary + Edu_Binary + Married_Binary + PriorUse_Binary + Q11 + Q12 + Q13 + Fear_Binary",
    ]

    fitted = []
    for i, f in enumerate(formulas, start=1):
        model, fit_type = safe_logit_fit(f, d, maxiter=500)
        fitted.append((f"Block {i}", model, f, fit_type))

    # Sensitivity model with proximal beliefs Q6/Q7 added.
    work["Safe_Binary"] = as_binary(work["Q6"], yes=1, no=0)
    work["Acceptable_Binary"] = as_binary(work["Q7"], yes=1, no=0)
    sens_cols = [
        "Recommend_Binary",
        "Age_Binary",
        "Gender_Binary",
        "Edu_Binary",
        "Married_Binary",
        "PriorUse_Binary",
        "Q11",
        "Q12",
        "Q13",
        "Fear_Binary",
        "Safe_Binary",
        "Acceptable_Binary",
    ]
    ds = work[sens_cols].dropna().copy()
    sens_formula = (
        "Recommend_Binary ~ Age_Binary + Gender_Binary + Edu_Binary + Married_Binary + PriorUse_Binary + "
        "Q11 + Q12 + Q13 + Fear_Binary + Safe_Binary + Acceptable_Binary"
    )
    sens_model, sens_fit_type = safe_logit_fit(sens_formula, ds, maxiter=500)

    return d, fitted, ds, sens_model, sens_fit_type


def fit_multinomial_q8(df):
    work = add_binary_demographics(df.copy())
    work["PriorUse_Binary"] = as_binary(work["Q31"], yes=1, no=0)
    cols = ["Q8", "Age_Binary", "Gender_Binary", "Edu_Binary", "Married_Binary", "PriorUse_Binary", "Q11", "Q12", "Q13"]
    d = work[cols].dropna().copy()
    d = d[d["Q8"].isin([0, 1, 2])]

    X = d[["Age_Binary", "Gender_Binary", "Edu_Binary", "Married_Binary", "PriorUse_Binary", "Q11", "Q12", "Q13"]].astype(float)
    X = sm.add_constant(X, has_constant="add")
    X = X.astype(float)
    y = d["Q8"].astype(int)

    model, fit_type = safe_mnlogit_fit(y, X, maxiter=500)
    return d, model, fit_type


def contact_hypothesis(df):
    users = df[df["Q31"] == 1].copy()
    non_users = df[df["Q31"] == 0].copy()

    results = []
    for col in ["Q11", "Q12", "Q13"]:
        d = df[["Q31", col]].dropna().copy()
        uvals = d[d["Q31"] == 1][col]
        nvals = d[d["Q31"] == 0][col]

        if len(uvals) == 0 or len(nvals) == 0:
            results.append((col, np.nan, np.nan, np.nan, np.nan, np.nan, int(len(d)), np.nan, np.nan))
            continue

        u_stat, p_u = mannwhitneyu(uvals, nvals, alternative="two-sided")
        delta = cliffs_delta(uvals.values, nvals.values)

        ct = pd.crosstab(d["Q31"], d[col])
        chi2, p_c, _, _ = chi2_contingency(ct)
        cv = cramers_v_from_ct(ct)
        results.append((col, float(u_stat), float(p_u), float(delta), float(p_c), float(cv), int(len(d)), float(uvals.median()), float(nvals.median())))

    return users, non_users, results


def profile_clustering(df):
    features = ["Q11", "Q12", "Q13"]
    d = df[features].dropna().copy()
    x = d.values.astype(float)

    scaler = StandardScaler()
    xs = scaler.fit_transform(x)

    scores = []
    models = {}
    for k in CLUSTER_RANGE:
        km = KMeans(n_clusters=k, n_init=KMEANS_N_INIT, random_state=KMEANS_RANDOM_STATE)
        labels = km.fit_predict(xs)
        sil = silhouette_score(xs, labels)
        scores.append((k, float(sil)))
        models[k] = (km, labels)

    best_k = max(scores, key=lambda t: t[1])[0]
    _, labels = models[best_k]
    d = d.copy()
    d["Profile"] = labels

    profile_table = (
        d.groupby("Profile")[features]
        .mean()
        .round(3)
        .reset_index()
        .sort_values("Profile")
    )
    sizes = d["Profile"].value_counts().sort_index()

    return d, scores, best_k, profile_table, sizes


def main():
    if not CLEAN_CSV.exists():
        raise FileNotFoundError(f"Cleaned CSV not found: {CLEAN_CSV}")

    df = pd.read_csv(CLEAN_CSV)
    with open(QUESTION_LABELS_JSON, "r", encoding="utf-8") as f:
        qlabels = json.load(f)
    with open(VALUE_LABELS_JSON, "r", encoding="utf-8") as f:
        value_labels = json.load(f)

    n_total = len(df)
    export_data = {
        "meta": {
            "n_total": int(n_total),
        },
        "inferential": {},
        "descriptive": {},
    }

    lines = []
    lines.append(f"# Psychiatric Medication Use and Public Acceptance in Iraq — Unified Survey Analysis (N={n_total})")
    lines.append("")
    lines.append("This script now provides a single unified output with main/clean models and clearly labeled exploratory analyses.")
    lines.append("")
    lines.append("## Main/Clean Analysis (Publication-Ready)")
    lines.append("")

    # 1) Hierarchical block logistic regression
    lines.append("## 1) Hierarchical Block Logistic Regression (Outcome: Q8 Yes vs No)")
    lines.append("")
    d_block, blocks, d_sens, sens_model, sens_fit_type = fit_hierarchical_models(df)
    lines.append(f"- Complete-case n (primary hierarchical models): **{len(d_block)}**")
    lines.append("")
    lines.append("| Model block | Formula summary | McFadden pseudo R² | LLR p-value |")
    lines.append("|---|---|---:|---:|")
    for name, m, formula, fit_type in blocks:
        prsquared = getattr(m, "prsquared", np.nan)
        llr_pvalue = getattr(m, "llr_pvalue", np.nan)
        lines.append(f"| {name} ({fit_type}) | `{formula}` | {prsquared:.4f} | {fmt_p(llr_pvalue)} |")
    export_data["inferential"]["hierarchical"] = {
        "complete_case_n": int(len(d_block)),
        "blocks": [
            {
                "block": name,
                "formula": formula,
                "fit_type": fit_type,
                "mcfadden_pseudo_r2": getattr(m, "prsquared", np.nan),
                "llr_pvalue": getattr(m, "llr_pvalue", np.nan),
            }
            for name, m, formula, fit_type in blocks
        ],
    }

    lines.append("")
    lines.append("### Final Primary Block (Block 3) — Adjusted Odds Ratios")
    lines.append("")
    lines.append("| Predictor | Adjusted OR (95% CI) | p-value |")
    lines.append("|---|---:|---:|")
    primary_or_rows = summarize_logit(blocks[-1][1])
    for term, or_val, low, high, p in primary_or_rows:
        lines.append(f"| {term} | {fmt_or(or_val, low, high)} | {fmt_p(p)} |")
    export_data["inferential"]["primary_or"] = [
        {
            "predictor": term,
            "adjusted_or": or_val,
            "ci_low": low,
            "ci_high": high,
            "p_value": p,
        }
        for term, or_val, low, high, p in primary_or_rows
    ]

    lines.append("")
    lines.append("### Sensitivity Model Adding Proximal Beliefs (Q6/Q7)")
    lines.append("")
    lines.append(f"- Complete-case n (sensitivity model): **{len(d_sens)}**")
    sens_pr2 = getattr(sens_model, "prsquared", np.nan)
    lines.append(f"- McFadden pseudo R²: **{sens_pr2:.4f}**")
    lines.append(f"- Fit type: **{sens_fit_type}**")
    lines.append("- This sensitivity model is reported separately because Q6 and Q7 are conceptually close to Q8 and can dominate explanatory variance.")
    export_data["inferential"]["sensitivity_model"] = {
        "complete_case_n": int(len(d_sens)),
        "fit_type": sens_fit_type,
        "mcfadden_pseudo_r2": sens_pr2,
        "formula": sens_model.model.formula if hasattr(sens_model.model, "formula") else None,
        "adjusted_or": [
            {
                "predictor": term,
                "adjusted_or": or_val,
                "ci_low": low,
                "ci_high": high,
                "p_value": p,
            }
            for term, or_val, low, high, p in summarize_logit(sens_model)
        ],
    }

    # 2) Multinomial logistic retaining Not sure
    lines.append("")
    lines.append("## 2) Multinomial Logistic Regression Preserving Hesitation (Q8 = No / Yes / Not sure)")
    lines.append("")
    d_mn, mn_model, mn_fit_type = fit_multinomial_q8(df)
    mn_categories = sorted(d_mn["Q8"].astype(int).unique().tolist())
    non_ref_categories = mn_categories[1:]
    expected_mapping = len(mn_model.params.columns) == len(non_ref_categories)
    lines.append(f"- Complete-case n: **{len(d_mn)}**")
    lines.append(f"- Model log-likelihood: **{mn_model.llf:.3f}**")
    lines.append(f"- Fit type: **{mn_fit_type}**")
    lines.append("")
    lines.append("Reference outcome in statsmodels is the lowest coded category; coefficients are shown for non-reference outcome equations.")
    lines.append("")
    lines.append("| Outcome equation | Predictor | Relative risk ratio (95% CI) | p-value |")
    lines.append("|---|---|---:|---:|")
    try:
        conf = mn_model.conf_int()
    except Exception:
        conf = None
    multinomial_rows = []
    for equation_idx, outcome_col in enumerate(mn_model.params.columns):
        mapped_outcome = non_ref_categories[equation_idx] if expected_mapping else outcome_col
        for term in mn_model.params.index:
            beta = mn_model.params.loc[term, outcome_col]
            p = mn_model.pvalues.loc[term, outcome_col]
            ci_low, ci_high = extract_multinomial_ci(conf, mapped_outcome, term)
            rrr = safe_exp(beta)
            low = safe_exp(ci_low)
            high = safe_exp(ci_high)
            lines.append(f"| Q8={mapped_outcome} vs ref | {term} | {fmt_or(rrr, low, high)} | {fmt_p(float(p))} |")
            multinomial_rows.append(
                {
                    "outcome": int(mapped_outcome) if isinstance(mapped_outcome, (int, np.integer)) else mapped_outcome,
                    "outcome_column": int(outcome_col) if isinstance(outcome_col, (int, np.integer)) else outcome_col,
                    "predictor": term,
                    "beta": beta,
                    "rrr": rrr,
                    "ci_low": low,
                    "ci_high": high,
                    "p_value": float(p),
                }
            )
    export_data["inferential"]["multinomial"] = {
        "complete_case_n": int(len(d_mn)),
        "fit_type": mn_fit_type,
        "log_likelihood": float(mn_model.llf),
        "categories": [int(c) for c in mn_categories],
        "reference_category": int(mn_categories[0]) if mn_categories else None,
        "rows": multinomial_rows,
    }

    lines.append("")
    lines.append("## Exploratory Analysis (Clearly Labeled)")
    lines.append("")

    # 3) Contact hypothesis
    lines.append("")
    lines.append("## 3) Contact Hypothesis: Users vs Non-Users on Core Beliefs (Q11-Q13)")
    lines.append("")
    users_df, non_users_df, contact = contact_hypothesis(df)
    lines.append(f"- Users (Q31=1): **{len(users_df)}**")
    lines.append(f"- Non-users (Q31=0): **{len(non_users_df)}**")
    lines.append("")
    lines.append("| Item | User median | Non-user median | Mann-Whitney U p-value | Cliff's delta | Chi-square p-value | Cramer's V | N used |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|")
    for col, u_stat, p_u, delta, p_c, cv, n_used, med_u, med_n in contact:
        lines.append(
            f"| {col} ({english_question_label(col, qlabels)}) | {med_u:.2f} | {med_n:.2f} | {fmt_p(p_u)} | {delta:.3f} | {fmt_p(p_c)} | {cv:.3f} | {n_used} |"
        )
    export_data["inferential"]["contact_hypothesis"] = {
        "users_n": int(len(users_df)),
        "non_users_n": int(len(non_users_df)),
        "items": [
            {
                "item": col,
                "user_median": med_u,
                "non_user_median": med_n,
                "mann_whitney_u_stat": u_stat,
                "mann_whitney_u_pvalue": p_u,
                "cliffs_delta": delta,
                "chi_square_pvalue": p_c,
                "cramers_v": cv,
                "n_used": int(n_used),
            }
            for col, u_stat, p_u, delta, p_c, cv, n_used, med_u, med_n in contact
        ],
    }

    # 4) Exploratory stigma profiles
    lines.append("")
    lines.append("## 4) Exploratory Stigma Phenotypes (K-Means on Standardized Q11-Q13)")
    lines.append("")
    cluster_df, cluster_scores, best_k, profile_table, sizes = profile_clustering(df)
    lines.append("| k | Silhouette score |")
    lines.append("|---:|---:|")
    for k, sil in cluster_scores:
        lines.append(f"| {k} | {sil:.3f} |")
    lines.append("")
    lines.append(f"- Selected k by maximum silhouette: **{best_k}**")
    lines.append("")
    lines.append("| Profile | Size n | Q11 mean | Q12 mean | Q13 mean |")
    lines.append("|---:|---:|---:|---:|---:|")
    for _, row in profile_table.iterrows():
        p = int(row["Profile"])
        lines.append(f"| {p} | {int(sizes[p])} | {row['Q11']:.3f} | {row['Q12']:.3f} | {row['Q13']:.3f} |")
    profile_means_unrounded = (
        cluster_df.groupby("Profile")[["Q11", "Q12", "Q13"]]
        .mean()
        .reset_index()
        .sort_values("Profile")
    )
    export_data["inferential"]["kmeans"] = {
        "features": ["Q11", "Q12", "Q13"],
        "cluster_range": [int(k) for k in CLUSTER_RANGE],
        "scores": [{"k": int(k), "silhouette_score": sil} for k, sil in cluster_scores],
        "best_k": int(best_k),
        "profiles": [
            {
                "profile": int(row["Profile"]),
                "size_n": int(sizes[int(row["Profile"])]),
                "Q11_mean": row["Q11"],
                "Q12_mean": row["Q12"],
                "Q13_mean": row["Q13"],
            }
            for _, row in profile_means_unrounded.iterrows()
        ],
    }

    lines.append("")
    lines.append("## 5) Notes for Manuscript Positioning")
    lines.append("")
    lines.append("- Hierarchical and multinomial modeling are suitable main-text analyses because they preserve response structure and clarify incremental explanatory value.")
    lines.append("- K-means profiling should be presented as an exploratory secondary analysis.")
    lines.append("- For stronger latent construct validation in future work, ordinal EFA/CFA with polychoric correlations is recommended on appropriately scoped item blocks.")

    # 6) Descriptive statistics appendices (added without modifying existing inferential analyses)
    lines.append("")
    lines.append('<div style="page-break-after: always;"></div>')
    lines.append("")
    lines.append("## Demographics Summary")
    lines.append("")
    lines.append("| Variable | Category | Count | Percentage |")
    lines.append("|---|---|---:|---:|")
    demographics_value_labels = {q: numeric_code_label_map(value_labels, q) for q in DEMOGRAPHIC_QUESTION_IDS}
    demographic_specs = [
        ("Gender", "Q2", demographics_value_labels.get("Q2", {})),
        ("Age", "Q1", demographics_value_labels.get("Q1", {})),
        ("Educational level", "Q4", demographics_value_labels.get("Q4", {})),
        ("Marital status", "Q5", demographics_value_labels.get("Q5", {})),
    ]
    demographics_export = []
    for var_label, col, categories in demographic_specs:
        valid = df[col].dropna()
        denom = len(valid)
        for code, cat_label in categories.items():
            count = int((valid == code).sum())
            pct = (count / denom * 100.0) if denom else np.nan
            lines.append(f"| {var_label} | {cat_label} | {count} | {pct:.2f}% |")
            demographics_export.append(
                {
                    "variable": var_label,
                    "question_id": col,
                    "category_code": int(code),
                    "category_label": cat_label,
                    "count": count,
                    "percentage": pct,
                    "denominator": int(denom),
                }
            )
    export_data["descriptive"]["demographics"] = demographics_export

    lines.append("")
    lines.append("## Core Beliefs Likert Distribution")
    lines.append("")
    lines.append("| Question | Disagree % | Neutral % | Agree % |")
    lines.append("|---|---:|---:|---:|")
    likert_export = []
    for qcol in ["Q11", "Q12", "Q13"]:
        valid = df[qcol].dropna()
        denom = len(valid)
        disagree_pct = (valid.isin([1, 2]).sum() / denom * 100.0) if denom else np.nan
        neutral_pct = ((valid == 3).sum() / denom * 100.0) if denom else np.nan
        agree_pct = (valid.isin([4, 5]).sum() / denom * 100.0) if denom else np.nan
        lines.append(f"| {qcol} | {disagree_pct:.2f}% | {neutral_pct:.2f}% | {agree_pct:.2f}% |")
        likert_export.append(
            {
                "question_id": qcol,
                "disagree_pct": disagree_pct,
                "neutral_pct": neutral_pct,
                "agree_pct": agree_pct,
                "denominator": int(denom),
            }
        )
    export_data["descriptive"]["likert"] = likert_export

    lines.append("")
    lines.append("## Correlation Matrix: Primary Beliefs")
    lines.append("")
    lines.append("| Variable | Q11 | Q12 | Q13 | Concern | Acceptance | Recommend |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|")
    corr_cols = {
        "Q11": "Q11",
        "Q12": "Q12",
        "Q13": "Q13",
        "Concern": "Q9",
        "Acceptance": "Q7",
        "Recommend": "Q8",
    }
    corr_df = df[list(corr_cols.values())].apply(pd.to_numeric, errors="coerce")
    corr = corr_df.corr(method="pearson")
    corr_order = ["Q11", "Q12", "Q13", "Concern", "Acceptance", "Recommend"]
    for row_name in corr_order:
        row_col = corr_cols[row_name]
        row_vals = [f"{corr.loc[row_col, corr_cols[col_name]]:.3f}" for col_name in corr_order]
        lines.append(f"| {row_name} | " + " | ".join(row_vals) + " |")
    export_data["descriptive"]["correlations"] = {
        "method": "pearson",
        "variables": corr_order,
        "matrix": [
            [corr.loc[corr_cols[row_name], corr_cols[col_name]] for col_name in corr_order]
            for row_name in corr_order
        ],
    }

    lines.append("")
    lines.append("## Acceptance by Prior Use")
    lines.append("")
    lines.append("| Prior Use | Recommend Yes % | Sample n |")
    lines.append("|---|---:|---:|")
    prior_use_specs = [("Yes", 1), ("No", 0)]
    acceptance_by_prior_use_export = []
    for label, code in prior_use_specs:
        subgroup = df[(df["Q31"] == code) & (df["Q8"].isin([0, 1, 2]))]
        denom = len(subgroup)
        recommend_yes_pct = ((subgroup["Q8"] == 1).sum() / denom * 100.0) if denom else np.nan
        lines.append(f"| {label} | {recommend_yes_pct:.2f}% | {denom} |")
        acceptance_by_prior_use_export.append(
            {
                "prior_use_label": label,
                "prior_use_code": int(code),
                "recommend_yes_pct": recommend_yes_pct,
                "sample_n": int(denom),
            }
        )
    export_data["descriptive"]["acceptance_by_prior_use"] = acceptance_by_prior_use_export

    lines.append("")
    lines.append("## General Attitudes Distribution")
    lines.append("")
    lines.append("| Question | Yes n | Yes % | Not sure n | Not sure % | No n | No % |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|")
    attitude_specs = [
        ("Safety perception", "Q6"),
        ("Acceptability", "Q7"),
        ("Recommendation willingness", "Q8"),
        ("Social concerns", "Q9"),
    ]
    attitudes_export = []
    for label, col in attitude_specs:
        valid = df[df[col].isin([0, 1, 2])][col]
        denom = len(valid)
        yes_n = int((valid == 1).sum())
        unsure_n = int((valid == 2).sum())
        no_n = int((valid == 0).sum())
        yes_pct = (yes_n / denom * 100.0) if denom else np.nan
        unsure_pct = (unsure_n / denom * 100.0) if denom else np.nan
        no_pct = (no_n / denom * 100.0) if denom else np.nan
        lines.append(f"| {label} | {yes_n} | {yes_pct:.2f}% | {unsure_n} | {unsure_pct:.2f}% | {no_n} | {no_pct:.2f}% |")
        attitudes_export.append(
            {
                "question_label": label,
                "question_id": col,
                "yes_n": yes_n,
                "yes_pct": yes_pct,
                "not_sure_n": unsure_n,
                "not_sure_pct": unsure_pct,
                "no_n": no_n,
                "no_pct": no_pct,
                "sample_n": int(denom),
            }
        )
    export_data["descriptive"]["attitudes"] = attitudes_export

    lines.append("")
    lines.append("## Recommendation by Gender")
    lines.append("")
    lines.append("| Gender | Yes n | Yes % | Not sure n | Not sure % | No n | No % | Sample n |")
    lines.append("|---|---:|---:|---:|---:|---:|---:|---:|")
    gender_label_map = numeric_code_label_map(value_labels, "Q2")
    gender_specs = [
        ("Male", 1),
        ("Female", 2),
    ]
    gender_crosstabs_export = []
    for fallback_label, gender_code in gender_specs:
        gender_label = gender_label_map.get(gender_code, fallback_label)
        subgroup = df[(df["Q2"] == gender_code) & (df["Q8"].isin([0, 1, 2]))]["Q8"]
        denom = len(subgroup)
        yes_n = int((subgroup == 1).sum())
        unsure_n = int((subgroup == 2).sum())
        no_n = int((subgroup == 0).sum())
        yes_pct = (yes_n / denom * 100.0) if denom else np.nan
        unsure_pct = (unsure_n / denom * 100.0) if denom else np.nan
        no_pct = (no_n / denom * 100.0) if denom else np.nan
        lines.append(
            f"| {gender_label} | {yes_n} | {yes_pct:.2f}% | {unsure_n} | {unsure_pct:.2f}% | {no_n} | {no_pct:.2f}% | {denom} |"
        )
        gender_crosstabs_export.append(
            {
                "gender_label": gender_label,
                "gender_code": int(gender_code),
                "yes_n": yes_n,
                "yes_pct": yes_pct,
                "not_sure_n": unsure_n,
                "not_sure_pct": unsure_pct,
                "no_n": no_n,
                "no_pct": no_pct,
                "sample_n": int(denom),
            }
        )
    export_data["descriptive"]["gender_crosstabs"] = gender_crosstabs_export

    output_text = "\n".join(lines) + "\n"
    ANALYSIS_MD.write_text(output_text, encoding="utf-8")
    ROOT_ANALYSIS_MD.write_text(output_text, encoding="utf-8")
    ANALYSIS_JSON.write_text(json.dumps(to_builtin(export_data), ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(f"Unified analysis written to: {ANALYSIS_MD}")
    print(f"Root analysis file updated: {ROOT_ANALYSIS_MD}")
    print(f"Structured analysis JSON written to: {ANALYSIS_JSON}")


if __name__ == "__main__":
    main()
