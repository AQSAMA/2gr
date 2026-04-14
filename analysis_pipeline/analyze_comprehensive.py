import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from matplotlib import pyplot as plt
from scipy.stats import chi2_contingency, mannwhitneyu
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler


BASE_DIR = Path(__file__).resolve().parents[1]
OUTPUT_DIR = BASE_DIR / "analysis_pipeline" / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

CLEAN_CSV = OUTPUT_DIR / "cleaned_survey_data_utf8.csv"
QUESTION_LABELS_JSON = OUTPUT_DIR / "question_labels.json"
ANALYSIS_MD = OUTPUT_DIR / "survey_data_results_comprehensive.md"
ROOT_ANALYSIS_MD = BASE_DIR / "survey_data_results.md"
RADAR_PNG = OUTPUT_DIR / "user_experience_radar.png"
RADAR_REPORT_PATH = "analysis_pipeline/output/user_experience_radar.png"
# Absolute log-odds values above this threshold are treated as unstable for this survey model pipeline.
MAX_LOGIT_PARAM_ABS = 8
KMEANS_N_INIT = 50
KMEANS_RANDOM_STATE = 42
# Exploratory profile search is intentionally bounded to small k values for interpretability with Q11-Q13.
CLUSTER_RANGE = [2, 3, 4]
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
    "Q29": "Psychiatric medications help me be in a better state",
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


def add_grouped_demographics(df):
    d = df.copy()
    d["Age_Group3"] = np.select(
        [d["Q1"].isin([1, 2]), d["Q1"].isin([3, 4]), d["Q1"] == 5],
        [1, 2, 3],
        default=np.nan,
    )
    d["Edu_Group3"] = np.select(
        [d["Q4"].isin([1, 2, 3]), d["Q4"] == 4, d["Q4"].isin([5, 6])],
        [1, 2, 3],
        default=np.nan,
    )
    d["Marital_Group2"] = np.select(
        [d["Q5"] == 1, d["Q5"].isin([2, 3, 4])],
        [1, 2],
        default=np.nan,
    )
    return d


def collapse_sparse_levels(df, col, min_n=15):
    """Collapse sparse category levels to sentinel -1 to stabilize regression estimation."""
    d = df.copy()
    counts = d[col].value_counts(dropna=True)
    rare_levels = counts[counts < min_n].index
    if len(rare_levels) > 0:
        d[col] = d[col].where(~d[col].isin(rare_levels), -1)
    return d


def safe_logit_fit(formula, data, maxiter=500):
    """Fit logit with MLE first, then fall back to regularized fit when unstable."""
    try:
        mle_model = smf.logit(formula, data=data).fit(disp=0, maxiter=maxiter)
        params = getattr(mle_model, "params", pd.Series(dtype=float))
        pr2 = getattr(mle_model, "prsquared", np.nan)
        converged = getattr(mle_model, "mle_retvals", {}).get("converged", True)
        unstable = (
            params.empty
            or (not np.isfinite(params).all())
            or (float(np.max(np.abs(params))) > MAX_LOGIT_PARAM_ABS)
            or pd.isna(pr2)
            or (not np.isfinite(pr2))
            or (not converged)
        )
        if not unstable:
            return mle_model, "mle"
    except Exception:
        pass
    return smf.logit(formula, data=data).fit_regularized(disp=0), "regularized"


def safe_mnlogit_fit(y, X, maxiter=500):
    try:
        mle_model = sm.MNLogit(y, X).fit(disp=0, maxiter=maxiter)
        params = getattr(mle_model, "params", pd.DataFrame())
        llf = getattr(mle_model, "llf", np.nan)
        unstable = (
            params.empty
            or (not np.isfinite(params.to_numpy()).all())
            or (float(np.max(np.abs(params.to_numpy()))) > MAX_LOGIT_PARAM_ABS)
            or pd.isna(llf)
            or (not np.isfinite(llf))
        )
        if not unstable:
            return mle_model, "mle"
    except Exception:
        pass
    return sm.MNLogit(y, X).fit_regularized(disp=0), "regularized"


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
        or_val = safe_exp(params[term])
        low = safe_exp(conf.loc[term, 0]) if term in conf.index else np.nan
        high = safe_exp(conf.loc[term, 1]) if term in conf.index else np.nan
        p = float(pvals[term]) if term in pvals.index else np.nan
        rows.append((term, or_val, low, high, p))
    return rows


def fit_hierarchical_models(df):
    work = add_grouped_demographics(df.copy())
    work["Recommend_Binary"] = as_binary(work["Q8"], yes=1, no=0)
    work["PriorUse_Binary"] = as_binary(work["Q31"], yes=1, no=0)
    work["Fear_Binary"] = as_binary(work["Q9"], yes=1, no=0)

    # Primary model set avoids proximal tautology with Q6/Q7.
    base_cols = [
        "Recommend_Binary",
        "Age_Group3",
        "Q2",
        "Edu_Group3",
        "Marital_Group2",
        "PriorUse_Binary",
        "Q11",
        "Q12",
        "Q13",
        "Fear_Binary",
    ]
    d = work[base_cols].dropna().copy()
    for c in ["Age_Group3", "Edu_Group3", "Marital_Group2"]:
        d = collapse_sparse_levels(d, c, min_n=15)

    formulas = [
        "Recommend_Binary ~ C(Age_Group3) + C(Q2) + C(Edu_Group3) + C(Marital_Group2)",
        "Recommend_Binary ~ C(Age_Group3) + C(Q2) + C(Edu_Group3) + C(Marital_Group2) + PriorUse_Binary",
        "Recommend_Binary ~ C(Age_Group3) + C(Q2) + C(Edu_Group3) + C(Marital_Group2) + PriorUse_Binary + Q11 + Q12 + Q13 + Fear_Binary",
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
        "Age_Group3",
        "Q2",
        "Edu_Group3",
        "Marital_Group2",
        "PriorUse_Binary",
        "Q11",
        "Q12",
        "Q13",
        "Fear_Binary",
        "Safe_Binary",
        "Acceptable_Binary",
    ]
    ds = work[sens_cols].dropna().copy()
    for c in ["Age_Group3", "Edu_Group3", "Marital_Group2"]:
        ds = collapse_sparse_levels(ds, c, min_n=15)
    sens_formula = (
        "Recommend_Binary ~ C(Age_Group3) + C(Q2) + C(Edu_Group3) + C(Marital_Group2) + PriorUse_Binary + "
        "Q11 + Q12 + Q13 + Fear_Binary + Safe_Binary + Acceptable_Binary"
    )
    sens_model, sens_fit_type = safe_logit_fit(sens_formula, ds, maxiter=500)

    return d, fitted, ds, sens_model, sens_fit_type


def fit_multinomial_q8(df):
    work = add_grouped_demographics(df.copy())
    cols = ["Q8", "Age_Group3", "Q2", "Edu_Group3", "Marital_Group2", "Q31", "Q11", "Q12", "Q13"]
    d = work[cols].dropna().copy()
    d = d[d["Q8"].isin([0, 1, 2])]

    for c in ["Age_Group3", "Edu_Group3", "Marital_Group2"]:
        d = collapse_sparse_levels(d, c, min_n=15)
    X = pd.get_dummies(
        d[["Age_Group3", "Q2", "Edu_Group3", "Marital_Group2", "Q31"]].astype(int).astype(str),
        drop_first=True,
        dtype=float,
    )
    X[["Q11", "Q12", "Q13"]] = d[["Q11", "Q12", "Q13"]].astype(float)
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


def mediation_bootstrap(df, n_boot=1500, seed=42):
    rng = np.random.default_rng(seed)

    work = add_grouped_demographics(df.copy())
    work["X_prior_use"] = as_binary(work["Q31"], yes=1, no=0)
    work["M_safe"] = as_binary(work["Q6"], yes=1, no=0)
    work["Y_recommend"] = as_binary(work["Q8"], yes=1, no=0)

    cols = ["X_prior_use", "M_safe", "Y_recommend", "Age_Group3", "Q2", "Edu_Group3", "Marital_Group2"]
    d = work[cols].dropna().copy()

    f_a = "M_safe ~ X_prior_use + C(Age_Group3) + C(Q2) + C(Edu_Group3) + C(Marital_Group2)"
    f_b = "Y_recommend ~ X_prior_use + M_safe + C(Age_Group3) + C(Q2) + C(Edu_Group3) + C(Marital_Group2)"
    f_c = "Y_recommend ~ X_prior_use + C(Age_Group3) + C(Q2) + C(Edu_Group3) + C(Marital_Group2)"

    d = collapse_sparse_levels(d, "Age_Group3", min_n=15)
    d = collapse_sparse_levels(d, "Edu_Group3", min_n=15)
    d = collapse_sparse_levels(d, "Marital_Group2", min_n=15)

    m_a, _ = safe_logit_fit(f_a, d, maxiter=500)
    m_b, _ = safe_logit_fit(f_b, d, maxiter=500)
    m_c, _ = safe_logit_fit(f_c, d, maxiter=500)

    a_hat = float(m_a.params["X_prior_use"])
    b_hat = float(m_b.params["M_safe"])
    cprime_hat = float(m_b.params["X_prior_use"])
    c_hat = float(m_c.params["X_prior_use"])
    indirect_hat = a_hat * b_hat

    boot_vals = []
    idx = np.arange(len(d))
    for _ in range(n_boot):
        sample_idx = rng.choice(idx, size=len(idx), replace=True)
        bdf = d.iloc[sample_idx]
        try:
            ba, _ = safe_logit_fit(f_a, bdf, maxiter=300)
            bb, _ = safe_logit_fit(f_b, bdf, maxiter=300)
            boot_vals.append(float(ba.params["X_prior_use"] * bb.params["M_safe"]))
        except Exception:
            continue

    if len(boot_vals) < 50:
        ci_low, ci_high = np.nan, np.nan
    else:
        ci_low = float(np.percentile(boot_vals, 2.5))
        ci_high = float(np.percentile(boot_vals, 97.5))

    return {
        "n": int(len(d)),
        "a": a_hat,
        "b": b_hat,
        "c_prime": cprime_hat,
        "c_total": c_hat,
        "indirect": indirect_hat,
        "indirect_ci_low": ci_low,
        "indirect_ci_high": ci_high,
        "boot_kept": int(len(boot_vals)),
    }


def make_user_radar(users):
    cols = ["Q15", "Q16", "Q17", "Q18", "Q19", "Q20"]
    d = users[cols].dropna(how="all")
    means = d.mean(skipna=True)

    labels = [
        "Necessary",
        "Stability",
        "Worse w/o meds",
        "Side effects",
        "Dependence worry",
        "Long-term harm worry",
    ]

    vals = means.values.astype(float)
    if len(vals) == 0 or np.all(np.isnan(vals)):
        return None

    vals = np.nan_to_num(vals, nan=np.nanmean(vals))
    vals_pct = (vals - 1) / 4 * 100

    angles = np.linspace(0, 2 * np.pi, len(vals_pct), endpoint=False)
    vals_cycle = np.r_[vals_pct, vals_pct[0]]
    angles_cycle = np.r_[angles, angles[0]]

    fig, ax = plt.subplots(figsize=(7, 7), subplot_kw=dict(polar=True))
    ax.plot(angles_cycle, vals_cycle, linewidth=2)
    ax.fill(angles_cycle, vals_cycle, alpha=0.25)
    ax.set_xticks(angles)
    ax.set_xticklabels(labels)
    ax.set_ylim(0, 100)
    ax.set_yticks([20, 40, 60, 80, 100])
    ax.set_title("User Experience Profile (Q15-Q20, normalized 0-100)")
    fig.tight_layout()
    fig.savefig(RADAR_PNG, dpi=220)
    plt.close(fig)
    return means


def main():
    if not CLEAN_CSV.exists():
        raise FileNotFoundError(f"Cleaned CSV not found: {CLEAN_CSV}")

    df = pd.read_csv(CLEAN_CSV)
    with open(QUESTION_LABELS_JSON, "r", encoding="utf-8") as f:
        qlabels = json.load(f)

    n_total = len(df)
    users = df[df["Q31"] == 1].copy()
    non_users = df[df["Q31"] == 0].copy()

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

    lines.append("")
    lines.append("### Final Primary Block (Block 3) — Adjusted Odds Ratios")
    lines.append("")
    lines.append("| Predictor | Adjusted OR (95% CI) | p-value |")
    lines.append("|---|---:|---:|")
    for term, or_val, low, high, p in summarize_logit(blocks[-1][1]):
        lines.append(f"| {term} | {fmt_or(or_val, low, high)} | {fmt_p(p)} |")

    lines.append("")
    lines.append("### Sensitivity Model Adding Proximal Beliefs (Q6/Q7)")
    lines.append("")
    lines.append(f"- Complete-case n (sensitivity model): **{len(d_sens)}**")
    sens_pr2 = getattr(sens_model, "prsquared", np.nan)
    lines.append(f"- McFadden pseudo R²: **{sens_pr2:.4f}**")
    lines.append(f"- Fit type: **{sens_fit_type}**")
    lines.append("- This sensitivity model is reported separately because Q6 and Q7 are conceptually close to Q8 and can dominate explanatory variance.")

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
    for equation_idx, outcome_col in enumerate(mn_model.params.columns):
        mapped_outcome = non_ref_categories[equation_idx] if expected_mapping else outcome_col
        for term in mn_model.params.index:
            beta = mn_model.params.loc[term, outcome_col]
            p = mn_model.pvalues.loc[term, outcome_col]
            ci_low, ci_high = extract_multinomial_ci(conf, outcome_col, term)
            rrr = safe_exp(beta)
            low = safe_exp(ci_low)
            high = safe_exp(ci_high)
            lines.append(f"| Q8={mapped_outcome} vs ref | {term} | {fmt_or(rrr, low, high)} | {fmt_p(float(p))} |")

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

    # 5) Mediation bootstrap
    lines.append("")
    lines.append("## 5) Exploratory Mediation (Associational): Q31 -> Q6 -> Q8")
    lines.append("")
    med = mediation_bootstrap(df)
    lines.append(f"- Analysis sample (Q31/Q6/Q8 coded as binary Yes/No only): **n={med['n']}**")
    lines.append(f"- a-path (Q31 -> Q6) log-odds coefficient: **{med['a']:.4f}**")
    lines.append(f"- b-path (Q6 -> Q8, adjusted for Q31) log-odds coefficient: **{med['b']:.4f}**")
    lines.append(f"- Direct effect c' (Q31 -> Q8 controlling mediator): **{med['c_prime']:.4f}**")
    lines.append(f"- Total effect c (Q31 -> Q8 without mediator): **{med['c_total']:.4f}**")
    lines.append(f"- Indirect effect a*b (log-odds scale): **{med['indirect']:.4f}**")
    if np.isnan(med["indirect_ci_low"]):
        lines.append("- Bootstrap CI for indirect effect: **not estimable** (too many failed resamples).")
    else:
        lines.append(
            f"- Bootstrap 95% CI for indirect effect: **{med['indirect_ci_low']:.4f} to {med['indirect_ci_high']:.4f}** "
            f"(successful resamples={med['boot_kept']})"
        )
    lines.append("- Interpretation note: this cross-sectional mediation is exploratory and should not be interpreted as causal.")

    # 6) Radar chart
    lines.append("")
    lines.append("## 6) User-Subset Visual Profile")
    lines.append("")
    means = make_user_radar(users)
    if means is None:
        lines.append("- Radar chart was not generated because user subset had insufficient data.")
    else:
        lines.append(f"- Radar chart saved to: `{RADAR_REPORT_PATH}`")
        lines.append("- Mean raw item values used for radar chart:")
        lines.append("")
        lines.append("| Item | Mean (1-5) |")
        lines.append("|---|---:|")
        for col, val in means.items():
            lines.append(f"| {col} ({english_question_label(col, qlabels)}) | {val:.3f} |")

    lines.append("")
    lines.append("## 7) Notes for Manuscript Positioning")
    lines.append("")
    lines.append("- Hierarchical and multinomial modeling are suitable main-text analyses because they preserve response structure and clarify incremental explanatory value.")
    lines.append("- K-means profiling and mediation should be presented as exploratory secondary analyses.")
    lines.append("- For stronger latent construct validation in future work, ordinal EFA/CFA with polychoric correlations is recommended on appropriately scoped item blocks.")

    output_text = "\n".join(lines) + "\n"
    ANALYSIS_MD.write_text(output_text, encoding="utf-8")
    ROOT_ANALYSIS_MD.write_text(output_text, encoding="utf-8")
    print(f"Unified analysis written to: {ANALYSIS_MD}")
    print(f"Root analysis file updated: {ROOT_ANALYSIS_MD}")
    if RADAR_PNG.exists():
        print(f"Radar figure written to: {RADAR_PNG}")


if __name__ == "__main__":
    main()
