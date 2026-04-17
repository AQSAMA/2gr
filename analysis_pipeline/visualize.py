from __future__ import annotations

import csv
import math
import re
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

import matplotlib.pyplot as plt
import numpy as np


BASE_DIR = Path(__file__).resolve().parents[1]
INPUT_MD = BASE_DIR / "survey_data_results.md"
INPUT_CSV = BASE_DIR / "survey_psychiatric_medication_use_public_acceptance_iraq_cleaned_english.csv"
OUTPUT_DIR = BASE_DIR / "output"
SUMMARY_MD = OUTPUT_DIR / "chart_summary.md"
# Floor value prevents log10(0) errors while preserving significance ranking for very small p-values.
MIN_PVALUE = 1e-12
# Ratio of chart height used to offset text labels above bars.
TEXT_LABEL_OFFSET_RATIO = 0.03
EXPECTED_CHART_COUNT = 31
MIN_CORRELATION_SAMPLE_SIZE = 3


plt.style.use("seaborn-v0_8-whitegrid")


@dataclass
class MarkdownTable:
    heading: str
    headers: list[str]
    rows: list[dict[str, str]]


@dataclass
class ChartOutput:
    filename: str
    title: str
    caption: str
    analysis: str


def _split_row(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def _is_separator(line: str) -> bool:
    cells = _split_row(line)
    if not cells:
        return False
    return all(re.fullmatch(r":?-{3,}:?", cell or "") for cell in cells)


def parse_tables(markdown_text: str) -> list[MarkdownTable]:
    lines = markdown_text.splitlines()
    tables: list[MarkdownTable] = []
    current_heading = ""
    i = 0

    while i < len(lines):
        line = lines[i].strip()
        if line.startswith("#"):
            current_heading = line.lstrip("#").strip()

        if i + 1 < len(lines) and "|" in lines[i] and _is_separator(lines[i + 1].strip()):
            headers = _split_row(lines[i])
            rows: list[dict[str, str]] = []
            j = i + 2
            while j < len(lines):
                row_line = lines[j].rstrip()
                if not row_line.strip().startswith("|"):
                    break
                cells = _split_row(row_line)
                if len(cells) == len(headers):
                    rows.append(dict(zip(headers, cells)))
                j += 1
            tables.append(MarkdownTable(heading=current_heading, headers=headers, rows=rows))
            i = j
            continue

        i += 1

    return tables


def find_table(tables: list[MarkdownTable], heading_keyword: str, required_headers: list[str]) -> MarkdownTable:
    for table in tables:
        if heading_keyword.lower() not in table.heading.lower():
            continue
        if all(h in table.headers for h in required_headers):
            return table
    raise ValueError(
        f"Could not find table for heading keyword '{heading_keyword}' with headers {required_headers}."
    )


def parse_number(value: str) -> float:
    cleaned = value.replace("**", "").replace(",", "").strip()
    cleaned = cleaned.replace("−", "-")
    return float(cleaned)


def parse_pvalue(value: str) -> float:
    cleaned = value.strip()
    if cleaned.startswith("<"):
        return float(cleaned[1:])
    return parse_number(cleaned)


def parse_or_ci(value: str) -> tuple[float, float, float]:
    match = re.search(r"([0-9.]+)\s*\(([-0-9.]+)\s*to\s*([-0-9.]+)\)", value)
    if not match:
        raise ValueError(
            f"Unable to parse OR/CI value: '{value}'. Expected format: 'number (number to number)'."
        )
    return float(match.group(1)), float(match.group(2)), float(match.group(3))


def parse_total_n(markdown_text: str) -> int:
    match = re.search(r"N=(\d+)", markdown_text)
    if not match:
        raise ValueError("Unable to parse total sample size from survey_data_results.md")
    return int(match.group(1))


def save_chart(path: Path, draw_fn: Callable[[], None]) -> None:
    fig = plt.figure(figsize=(10, 6), dpi=300)
    try:
        draw_fn()
        plt.tight_layout()
        fig.savefig(path, dpi=300, bbox_inches="tight")
    finally:
        plt.close(fig)


def load_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return [{k: (v or "").strip() for k, v in row.items()} for row in csv.DictReader(handle)]


def ordered_counts(rows: list[dict[str, str]], column: str, order: list[str] | None = None) -> tuple[list[str], list[int]]:
    counts = Counter(row.get(column, "") for row in rows if row.get(column, ""))
    if order:
        labels = [label for label in order if label in counts]
        labels.extend([label for label in counts if label not in labels])
    else:
        labels = [label for label, _ in counts.most_common()]
    return labels, [counts[label] for label in labels]


def to_pct(values: list[int]) -> list[float]:
    total = sum(values)
    if total == 0:
        return [0.0 for _ in values]
    return [(100.0 * value) / total for value in values]


def map_likert(value: str) -> float | None:
    mapping = {
        "Strongly disagree": 1.0,
        "Disagree": 2.0,
        "Neutral": 3.0,
        "Agree": 4.0,
        "Strongly agree": 5.0,
    }
    return mapping.get(value)


def map_yes_no_unsure(value: str) -> float | None:
    mapping = {"No": 1.0, "Not sure": 2.0, "Yes": 3.0}
    return mapping.get(value)


def safe_corr(a: np.ndarray, b: np.ndarray) -> float:
    mask = ~np.isnan(a) & ~np.isnan(b)
    if np.sum(mask) < MIN_CORRELATION_SAMPLE_SIZE:
        return np.nan
    return float(np.corrcoef(a[mask], b[mask])[0, 1])


def draw_donut(ax: plt.Axes, labels: list[str], counts: list[int], title: str, colors: list[str]) -> None:
    wedges, _, autotexts = ax.pie(
        counts,
        labels=labels,
        autopct="%1.1f%%",
        startangle=90,
        colors=colors[: len(labels)],
        wedgeprops={"width": 0.42, "edgecolor": "white"},
        textprops={"fontsize": 8},
    )
    for txt in autotexts:
        txt.set_fontsize(8)
    ax.set_title(title, fontsize=10)
    ax.axis("equal")


def draw_waffle(ax: plt.Axes, percent_value: float, title: str, positive_label: str = "Yes", negative_label: str = "Other") -> None:
    total_cells = 100
    positive_cells = int(round(max(0.0, min(100.0, percent_value))))
    indices = np.arange(total_cells)
    x = indices % 10
    y = 9 - (indices // 10)
    colors = np.array(["#E0E0E0"] * total_cells, dtype=object)
    colors[:positive_cells] = "#59A14F"
    ax.scatter(x, y, c=colors, marker="s", s=185, edgecolors="white", linewidths=0.8)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlim(-0.7, 9.7)
    ax.set_ylim(-0.7, 9.7)
    ax.set_title(title)
    ax.text(0, -1.5, f"{positive_label}: {percent_value:.1f}% | {negative_label}: {100.0 - percent_value:.1f}%", fontsize=9)
    for spine in ax.spines.values():
        spine.set_visible(False)


def main() -> None:
    if not INPUT_MD.exists():
        raise FileNotFoundError(f"Input markdown not found: {INPUT_MD}")
    if not INPUT_CSV.exists():
        raise FileNotFoundError(f"Input CSV not found: {INPUT_CSV}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    text = INPUT_MD.read_text(encoding="utf-8")
    survey_rows = load_csv_rows(INPUT_CSV)
    tables = parse_tables(text)
    n_total = parse_total_n(text)

    block_table = find_table(
        tables,
        "Hierarchical Block Logistic Regression",
        ["Model block", "McFadden pseudo R²", "LLR p-value"],
    )
    primary_or_table = find_table(
        tables,
        "Final Primary Block",
        ["Predictor", "Adjusted OR (95% CI)", "p-value"],
    )
    multinomial_table = find_table(
        tables,
        "Multinomial Logistic Regression",
        ["Outcome equation", "Predictor", "Relative risk ratio (95% CI)", "p-value"],
    )
    contact_table = find_table(
        tables,
        "Contact Hypothesis",
        ["Item", "User median", "Non-user median", "Mann-Whitney U p-value", "Cliff's delta", "Chi-square p-value", "Cramer's V"],
    )
    silhouette_table = find_table(
        tables,
        "Exploratory Stigma Phenotypes",
        ["k", "Silhouette score"],
    )
    profile_table = find_table(
        tables,
        "Exploratory Stigma Phenotypes",
        ["Profile", "Size n", "Q11 mean", "Q12 mean", "Q13 mean"],
    )

    chart_outputs: list[ChartOutput] = []

    # Shared parsed structures
    block_names = [row["Model block"].split("(")[0].strip() for row in block_table.rows]
    block_r2 = [parse_number(row["McFadden pseudo R²"]) for row in block_table.rows]
    block_p = [parse_pvalue(row["LLR p-value"]) for row in block_table.rows]

    primary_rows = [row for row in primary_or_table.rows if row["Predictor"].lower() != "intercept"]
    predictors = [row["Predictor"] for row in primary_rows]
    primary_or_vals = [parse_or_ci(row["Adjusted OR (95% CI)"]) for row in primary_rows]
    primary_pvals = [parse_pvalue(row["p-value"]) for row in primary_rows]

    mn_yes = [row for row in multinomial_table.rows if row["Outcome equation"].startswith("Q8=1") and row["Predictor"] != "const"]
    mn_unsure = [row for row in multinomial_table.rows if row["Outcome equation"].startswith("Q8=2") and row["Predictor"] != "const"]

    contact_items = [row["Item"].split("(")[0].strip() for row in contact_table.rows]
    user_median = [parse_number(row["User median"]) for row in contact_table.rows]
    non_median = [parse_number(row["Non-user median"]) for row in contact_table.rows]
    cliff_delta = [parse_number(row["Cliff's delta"]) for row in contact_table.rows]
    cramer_v = [parse_number(row["Cramer's V"]) for row in contact_table.rows]
    mw_p = [parse_pvalue(row["Mann-Whitney U p-value"]) for row in contact_table.rows]
    chi_p = [parse_pvalue(row["Chi-square p-value"]) for row in contact_table.rows]

    k_values = [int(parse_number(row["k"])) for row in silhouette_table.rows]
    silhouette_scores = [parse_number(row["Silhouette score"]) for row in silhouette_table.rows]

    profiles = [int(parse_number(row["Profile"])) for row in profile_table.rows]
    profile_sizes = [int(parse_number(row["Size n"])) for row in profile_table.rows]
    profile_q11 = [parse_number(row["Q11 mean"]) for row in profile_table.rows]
    profile_q12 = [parse_number(row["Q12 mean"]) for row in profile_table.rows]
    profile_q13 = [parse_number(row["Q13 mean"]) for row in profile_table.rows]

    age_col = "Age"
    gender_col = "Gender"
    edu_col = "Educational level"
    marital_col = "Marital status"
    recommendation_col = "Would you recommend psychiatric medications to someone close if needed?"
    acceptance_col = "Do you see their use as acceptable like hypertension and diabetes medications?"
    concerns_col = "Do you have concerns about interacting with a person taking psychiatric medications?"
    prior_use_col = "Do you currently use or have you ever used a psychiatric medication?"
    q11_col = "Doctors prescribe medications more than necessary"
    q12_col = "Most medications cause psychological or physical dependence"
    q13_col = "Modern medications are safer than older ones"
    safety_col = "Do you think psychiatric medications are safe?"

    age_labels, age_counts = ordered_counts(survey_rows, age_col, ["18-25", "26-35", "36-45", "46-60", ">60"])
    gender_labels, gender_counts = ordered_counts(survey_rows, gender_col, ["Female", "Male"])
    edu_labels, edu_counts = ordered_counts(survey_rows, edu_col, ["Primary", "High school", "University", "Postgraduate"])
    marital_labels, marital_counts = ordered_counts(survey_rows, marital_col, ["Single", "Married", "Divorced", "Widowed"])
    recommend_labels, recommend_counts = ordered_counts(survey_rows, recommendation_col, ["Yes", "Not sure", "No"])
    acceptance_labels, acceptance_counts = ordered_counts(survey_rows, acceptance_col, ["Yes", "Not sure", "No"])
    safety_labels, safety_counts = ordered_counts(survey_rows, safety_col, ["Yes", "Not sure", "No"])
    concerns_labels, concerns_counts = ordered_counts(survey_rows, concerns_col, ["Yes", "Not sure", "No"])
    safety_count_map = dict(zip(safety_labels, safety_counts))
    acceptance_count_map = dict(zip(acceptance_labels, acceptance_counts))
    recommend_count_map = dict(zip(recommend_labels, recommend_counts))

    likert_questions = [q11_col, q12_col, q13_col]
    likert_short_labels = ["Q11", "Q12", "Q13"]
    likert_groups: dict[str, list[float]] = {"Disagree": [], "Neutral": [], "Agree": []}
    for question in likert_questions:
        counts = Counter(row.get(question, "") for row in survey_rows if row.get(question, ""))
        total = sum(counts.values())
        disagree = counts.get("Strongly disagree", 0) + counts.get("Disagree", 0)
        neutral = counts.get("Neutral", 0)
        agree = counts.get("Agree", 0) + counts.get("Strongly agree", 0)
        if total == 0:
            likert_groups["Disagree"].append(0.0)
            likert_groups["Neutral"].append(0.0)
            likert_groups["Agree"].append(0.0)
        else:
            likert_groups["Disagree"].append((100.0 * disagree) / total)
            likert_groups["Neutral"].append((100.0 * neutral) / total)
            likert_groups["Agree"].append((100.0 * agree) / total)

    corr_columns = [q11_col, q12_col, q13_col, concerns_col, acceptance_col, recommendation_col]
    corr_labels = ["Q11", "Q12", "Q13", "Concern", "Acceptance", "Recommend"]
    corr_vectors: list[np.ndarray] = []
    for column in corr_columns:
        mapped: list[float] = []
        for row in survey_rows:
            raw = row.get(column, "")
            value = map_likert(raw)
            if value is None:
                value = map_yes_no_unsure(raw)
            mapped.append(np.nan if value is None else value)
        corr_vectors.append(np.array(mapped, dtype=float))
    corr_matrix = np.zeros((len(corr_vectors), len(corr_vectors)))
    for i, vec_i in enumerate(corr_vectors):
        for j, vec_j in enumerate(corr_vectors):
            corr_matrix[i, j] = safe_corr(vec_i, vec_j)

    prior_groups = ["Yes", "No"]
    prior_recommend_pct: list[float] = []
    prior_n: list[int] = []
    for prior_value in prior_groups:
        subgroup = [row for row in survey_rows if row.get(prior_use_col, "") == prior_value and row.get(recommendation_col, "")]
        denom = len(subgroup)
        numer = sum(1 for row in subgroup if row.get(recommendation_col, "") == "Yes")
        prior_n.append(denom)
        prior_recommend_pct.append((100.0 * numer / denom) if denom else 0.0)

    safety_yes = safety_count_map.get("Yes", 0)
    safety_no = safety_count_map.get("No", 0)
    safety_decisive_total = safety_yes + safety_no
    safety_yes_share_decisive = (100.0 * safety_yes / safety_decisive_total) if safety_decisive_total else 0.0
    safety_no_share_decisive = (100.0 * safety_no / safety_decisive_total) if safety_decisive_total else 0.0

    gender_groups = [group for group in ["Female", "Male"] if group in set(gender_labels)]
    gender_recommend_categories = ["Yes", "Not sure", "No"]
    gender_recommend_pct: dict[str, list[float]] = {}
    for gender in gender_groups:
        subgroup = [row for row in survey_rows if row.get(gender_col, "") == gender and row.get(recommendation_col, "")]
        subgroup_counts = Counter(row.get(recommendation_col, "") for row in subgroup)
        total = sum(subgroup_counts.get(cat, 0) for cat in gender_recommend_categories)
        if total == 0:
            gender_recommend_pct[gender] = [0.0, 0.0, 0.0]
        else:
            gender_recommend_pct[gender] = [(100.0 * subgroup_counts.get(cat, 0)) / total for cat in gender_recommend_categories]

    # 01
    filename = "01_hierarchical_pseudo_r2.png"

    def draw_01() -> None:
        bars = plt.bar(block_names, block_r2, color=["#4E79A7", "#59A14F", "#E15759"])
        plt.title("Hierarchical Model Fit Improvement")
        plt.ylabel("McFadden pseudo R²")
        max_height = max(block_r2)
        plt.ylim(0, max_height * 1.25)
        label_offset = max_height * TEXT_LABEL_OFFSET_RATIO
        for bar, val in zip(bars, block_r2):
            plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + label_offset, f"{val:.3f}", ha="center", va="bottom", fontsize=9)

    save_chart(OUTPUT_DIR / filename, draw_01)
    chart_outputs.append(
        ChartOutput(
            filename=filename,
            title="Hierarchical model pseudo R² by block",
            caption="Block-wise McFadden pseudo R² from the hierarchical logistic regression.",
            analysis="Block 3 shows the largest increase in pseudo R², indicating the most substantial improvement in model fit.",
        )
    )

    # 02
    filename = "02_hierarchical_llr_significance.png"

    def draw_02() -> None:
        transformed = [-math.log10(max(p, MIN_PVALUE)) for p in block_p]
        transformed_max = max(transformed) if transformed else 0.0
        label_offset = transformed_max * TEXT_LABEL_OFFSET_RATIO
        bars = plt.bar(block_names, transformed, color=["#A0CBE8", "#8CD17D", "#F28E2B"])
        threshold = -math.log10(0.05)
        plt.axhline(threshold, linestyle="--", color="#444444", linewidth=1.2, label="p = 0.05")
        plt.title("Likelihood-Ratio Test Significance by Model Block")
        plt.ylabel("-log10(LLR p-value)")
        plt.legend(frameon=False)
        for bar, raw in zip(bars, block_p):
            plt.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + label_offset,
                f"p={raw:.4f}",
                ha="center",
                va="bottom",
                fontsize=8,
            )

    save_chart(OUTPUT_DIR / filename, draw_02)
    chart_outputs.append(
        ChartOutput(
            filename=filename,
            title="LLR significance by hierarchical block",
            caption="Transformed LLR p-values for each hierarchical block.",
            analysis="Block 3 achieves statistical significance (p < 0.05), while Blocks 1 and 2 do not reach the conventional threshold.",
        )
    )

    # 03
    filename = "03_primary_adjusted_or_forest.png"

    def draw_03() -> None:
        or_vals = np.array([x[0] for x in primary_or_vals])
        low = np.array([x[1] for x in primary_or_vals])
        high = np.array([x[2] for x in primary_or_vals])
        y = np.arange(len(predictors))
        err_left = or_vals - low
        err_right = high - or_vals
        plt.errorbar(or_vals, y, xerr=[err_left, err_right], fmt="o", color="#4E79A7", ecolor="#4E79A7", capsize=4)
        plt.axvline(1.0, color="#333333", linestyle="--", linewidth=1)
        plt.yticks(y, predictors)
        plt.xscale("log")
        plt.xlabel("Adjusted OR (log scale)")
        plt.title("Primary Model Predictors: Adjusted Odds Ratios")

    save_chart(OUTPUT_DIR / filename, draw_03)
    n_sig_primary = sum(1 for p in primary_pvals if p < 0.05)
    chart_outputs.append(
        ChartOutput(
            filename=filename,
            title="Primary adjusted OR forest plot",
            caption="Adjusted odds ratios with 95% confidence intervals for Block 3 predictors.",
            analysis=f"{n_sig_primary} predictors are statistically significant at p<0.05, with clear protective and risk-direction effects.",
        )
    )

    # 04
    filename = "04_primary_effect_direction_log2or.png"

    def draw_04() -> None:
        log2_or = np.log2(np.array([x[0] for x in primary_or_vals]))
        colors = ["#59A14F" if v > 0 else "#E15759" for v in log2_or]
        bars = plt.barh(predictors, log2_or, color=colors)
        plt.axvline(0, color="#333333", linestyle="--", linewidth=1)
        plt.title("Direction and Magnitude of Primary Predictor Effects")
        plt.xlabel("log2(Adjusted OR)")
        for bar, val in zip(bars, log2_or):
            xpos = bar.get_width() + (0.03 if val >= 0 else -0.03)
            align = "left" if val >= 0 else "right"
            plt.text(xpos, bar.get_y() + bar.get_height() / 2, f"{val:.2f}", va="center", ha=align, fontsize=8)

    save_chart(OUTPUT_DIR / filename, draw_04)
    chart_outputs.append(
        ChartOutput(
            filename=filename,
            title="Primary effect direction chart",
            caption="log2-transformed adjusted odds ratios to show effect direction around zero.",
            analysis="Positive values indicate higher odds of recommending medication, while negative values indicate lower odds.",
        )
    )

    # 05
    filename = "05_primary_predictor_significance.png"

    def draw_05() -> None:
        scores = [-math.log10(max(p, MIN_PVALUE)) for p in primary_pvals]
        colors = ["#4E79A7" if p < 0.05 else "#BAB0AC" for p in primary_pvals]
        plt.barh(predictors, scores, color=colors)
        plt.axvline(-math.log10(0.05), color="#333333", linestyle="--", linewidth=1)
        plt.xlabel("-log10(p-value)")
        plt.title("Primary Predictors Ranked by Statistical Strength")

    save_chart(OUTPUT_DIR / filename, draw_05)
    chart_outputs.append(
        ChartOutput(
            filename=filename,
            title="Primary predictor significance ranking",
            caption="Predictor-level p-value strength for the primary logistic model.",
            analysis="Q13 and Fear_Binary exhibit the lowest p-values among adjusted predictors, indicating the most robust statistical associations.",
        )
    )

    # 06
    filename = "06_multinomial_q8yes_rrr_forest.png"

    def draw_06() -> None:
        labels = [row["Predictor"] for row in mn_yes]
        vals = [parse_or_ci(row["Relative risk ratio (95% CI)"]) for row in mn_yes]
        rrr = np.array([x[0] for x in vals])
        low = np.array([x[1] for x in vals])
        high = np.array([x[2] for x in vals])
        y = np.arange(len(labels))
        plt.errorbar(rrr, y, xerr=[rrr - low, high - rrr], fmt="o", color="#4E79A7", ecolor="#4E79A7", capsize=4)
        plt.axvline(1.0, color="#333333", linestyle="--", linewidth=1)
        plt.yticks(y, labels)
        plt.xscale("log")
        plt.xlabel("Relative risk ratio (log scale)")
        plt.title("Multinomial Model: Q8=Yes vs Reference")

    save_chart(OUTPUT_DIR / filename, draw_06)
    chart_outputs.append(
        ChartOutput(
            filename=filename,
            title="Multinomial forest plot (Q8=Yes)",
            caption="Relative risk ratios for the Q8=Yes outcome equation.",
            analysis="Gender, Q12, and Q13 are the clearest differentiators in the Yes-vs-reference contrast.",
        )
    )

    # 07
    filename = "07_multinomial_q8unsure_rrr_forest.png"

    def draw_07() -> None:
        labels = [row["Predictor"] for row in mn_unsure]
        vals = [parse_or_ci(row["Relative risk ratio (95% CI)"]) for row in mn_unsure]
        rrr = np.array([x[0] for x in vals])
        low = np.array([x[1] for x in vals])
        high = np.array([x[2] for x in vals])
        y = np.arange(len(labels))
        plt.errorbar(rrr, y, xerr=[rrr - low, high - rrr], fmt="o", color="#F28E2B", ecolor="#F28E2B", capsize=4)
        plt.axvline(1.0, color="#333333", linestyle="--", linewidth=1)
        plt.yticks(y, labels)
        plt.xscale("log")
        plt.xlabel("Relative risk ratio (log scale)")
        plt.title("Multinomial Model: Q8=Not Sure vs Reference")

    save_chart(OUTPUT_DIR / filename, draw_07)
    chart_outputs.append(
        ChartOutput(
            filename=filename,
            title="Multinomial forest plot (Q8=Not sure)",
            caption="Relative risk ratios for the Q8=Not sure outcome equation.",
            analysis="Gender remains the main significant factor in the hesitation profile.",
        )
    )

    # 08
    filename = "08_multinomial_key_predictor_comparison.png"

    def draw_08() -> None:
        keys = ["Gender_Binary", "Q11", "Q12", "Q13"]
        yes_map = {row["Predictor"]: parse_or_ci(row["Relative risk ratio (95% CI)"])[0] for row in mn_yes}
        unsure_map = {row["Predictor"]: parse_or_ci(row["Relative risk ratio (95% CI)"])[0] for row in mn_unsure}
        yes_vals = [yes_map[k] for k in keys]
        unsure_vals = [unsure_map[k] for k in keys]
        x = np.arange(len(keys))
        w = 0.38
        plt.bar(x - w / 2, yes_vals, width=w, color="#4E79A7", label="Q8=Yes")
        plt.bar(x + w / 2, unsure_vals, width=w, color="#F28E2B", label="Q8=Not sure")
        plt.axhline(1.0, linestyle="--", color="#333333", linewidth=1)
        plt.xticks(x, keys)
        plt.ylabel("Relative risk ratio")
        plt.title("Multinomial Key Predictors Across Response Profiles")
        plt.legend(frameon=False)

    save_chart(OUTPUT_DIR / filename, draw_08)
    chart_outputs.append(
        ChartOutput(
            filename=filename,
            title="Multinomial key predictor comparison",
            caption="Side-by-side RRR values for key predictors across Yes and Not sure outcomes.",
            analysis="Q13 shows a larger relative risk ratio for Yes responses, whereas Q11 and Q12 have relative risk ratios closer to 1.0 in the Not sure equation.",
        )
    )

    # 09
    filename = "09_multinomial_pvalue_heatmap.png"

    def draw_09() -> None:
        labels = [row["Predictor"] for row in mn_yes]
        yes_p = [parse_pvalue(row["p-value"]) for row in mn_yes]
        unsure_p = [parse_pvalue(row["p-value"]) for row in mn_unsure]
        mat = np.array([[-math.log10(max(v, MIN_PVALUE)) for v in yes_p], [-math.log10(max(v, MIN_PVALUE)) for v in unsure_p]])
        im = plt.imshow(mat, cmap="Blues", aspect="auto")
        plt.yticks([0, 1], ["Q8=Yes", "Q8=Not sure"])
        plt.xticks(np.arange(len(labels)), labels, rotation=35, ha="right")
        plt.title("Multinomial Predictor Significance Heatmap")
        cbar = plt.colorbar(im)
        cbar.set_label("-log10(p-value)")

    save_chart(OUTPUT_DIR / filename, draw_09)
    chart_outputs.append(
        ChartOutput(
            filename=filename,
            title="Multinomial significance heatmap",
            caption="Heatmap of predictor significance across multinomial outcome equations.",
            analysis="Darker cells identify where evidence is strongest, especially for Q13 in the Yes equation.",
        )
    )

    # 10
    filename = "10_contact_group_medians.png"

    def draw_10() -> None:
        x = np.arange(len(contact_items))
        w = 0.36
        plt.bar(x - w / 2, user_median, width=w, color="#59A14F", label="Users")
        plt.bar(x + w / 2, non_median, width=w, color="#4E79A7", label="Non-users")
        plt.xticks(x, contact_items)
        plt.ylim(0, 5)
        plt.ylabel("Median score")
        plt.title("Contact Hypothesis: Median Belief Scores")
        plt.legend(frameon=False)

    save_chart(OUTPUT_DIR / filename, draw_10)
    chart_outputs.append(
        ChartOutput(
            filename=filename,
            title="Contact hypothesis median comparison",
            caption="Users vs non-users median responses for Q11–Q13.",
            analysis="Users show lower skepticism on Q11 and higher confidence on Q13 compared with non-users.",
        )
    )

    # 11
    filename = "11_contact_effect_sizes.png"

    def draw_11() -> None:
        x = np.arange(len(contact_items))
        w = 0.36
        plt.bar(x - w / 2, cliff_delta, width=w, color="#E15759", label="Cliff's delta")
        plt.bar(x + w / 2, cramer_v, width=w, color="#76B7B2", label="Cramer's V")
        plt.axhline(0, color="#333333", linewidth=1)
        plt.xticks(x, contact_items)
        plt.ylabel("Effect size")
        plt.title("Effect Size Profile for Contact Hypothesis")
        plt.legend(frameon=False)

    save_chart(OUTPUT_DIR / filename, draw_11)
    chart_outputs.append(
        ChartOutput(
            filename=filename,
            title="Contact effect sizes",
            caption="Effect-size metrics for group differences in Q11–Q13.",
            analysis="Effects are small but consistent, with Q13 showing the strongest directional separation.",
        )
    )

    # 12
    filename = "12_contact_pvalue_strength.png"

    def draw_12() -> None:
        x = np.arange(len(contact_items))
        w = 0.36
        mw_strength = [-math.log10(max(v, MIN_PVALUE)) for v in mw_p]
        chi_strength = [-math.log10(max(v, MIN_PVALUE)) for v in chi_p]
        plt.bar(x - w / 2, mw_strength, width=w, color="#4E79A7", label="Mann-Whitney")
        plt.bar(x + w / 2, chi_strength, width=w, color="#F28E2B", label="Chi-square")
        plt.axhline(-math.log10(0.05), linestyle="--", color="#333333", linewidth=1)
        plt.xticks(x, contact_items)
        plt.ylabel("-log10(p-value)")
        plt.title("Contact Hypothesis Test Strength")
        plt.legend(frameon=False)

    save_chart(OUTPUT_DIR / filename, draw_12)
    chart_outputs.append(
        ChartOutput(
            filename=filename,
            title="Contact p-value strength",
            caption="Statistical strength of Mann-Whitney and Chi-square tests for Q11–Q13.",
            analysis="Q13 has the strongest evidence of group separation across both statistical tests.",
        )
    )

    # 13
    filename = "13_silhouette_by_k.png"

    def draw_13() -> None:
        plt.plot(k_values, silhouette_scores, marker="o", color="#4E79A7", linewidth=2)
        best_idx = int(np.argmax(silhouette_scores))
        plt.scatter([k_values[best_idx]], [silhouette_scores[best_idx]], color="#E15759", zorder=3)
        plt.xticks(k_values)
        plt.xlabel("Number of clusters (k)")
        plt.ylabel("Silhouette score")
        plt.title("K-Means Cluster Quality Across k Values")

    save_chart(OUTPUT_DIR / filename, draw_13)
    best_k = k_values[int(np.argmax(silhouette_scores))]
    chart_outputs.append(
        ChartOutput(
            filename=filename,
            title="Silhouette score trend",
            caption="Silhouette scores for candidate k values in exploratory profile clustering.",
            analysis=f"k={best_k} gives the best separation, matching the final model choice.",
        )
    )

    # 14
    filename = "14_profile_means_heatmap.png"

    def draw_14() -> None:
        matrix = np.array([profile_q11, profile_q12, profile_q13]).T
        im = plt.imshow(matrix, cmap="YlGnBu", aspect="auto", vmin=1, vmax=5)
        plt.xticks([0, 1, 2], ["Q11 mean", "Q12 mean", "Q13 mean"])
        plt.yticks(np.arange(len(profiles)), [f"Profile {p}" for p in profiles])
        plt.title("Belief Structure Across Stigma Profiles")
        cbar = plt.colorbar(im)
        cbar.set_label("Mean score")

    save_chart(OUTPUT_DIR / filename, draw_14)
    chart_outputs.append(
        ChartOutput(
            filename=filename,
            title="Profile means heatmap",
            caption="Heatmap of profile-level means across Q11, Q12, and Q13.",
            analysis="Profiles show distinct belief combinations, especially around confidence in newer medications (Q13).",
        )
    )

    # 15
    filename = "15_profile_size_distribution.png"

    def draw_15() -> None:
        labels = [f"Profile {p}" for p in profiles]
        colors = ["#4E79A7", "#59A14F", "#F28E2B", "#E15759"]
        plt.pie(profile_sizes, labels=labels, autopct="%1.1f%%", startangle=90, colors=colors[: len(labels)], wedgeprops={"linewidth": 1, "edgecolor": "white"})
        plt.title("Distribution of Respondents Across Stigma Profiles")

    save_chart(OUTPUT_DIR / filename, draw_15)
    largest_profile = profiles[int(np.argmax(profile_sizes))]
    chart_outputs.append(
        ChartOutput(
            filename=filename,
            title="Profile size distribution",
            caption=f"Share of respondents (N={n_total}) in each exploratory stigma profile.",
            analysis=f"Profile {largest_profile} is the largest segment, but the distribution remains relatively balanced overall.",
        )
    )

    # 16
    filename = "16_demographics_gender_distribution.png"

    def draw_16() -> None:
        pct = to_pct(gender_counts)
        bars = plt.bar(gender_labels, pct, color=["#B07AA1", "#4E79A7"][: len(gender_labels)])
        plt.ylabel("Percent of respondents")
        plt.title("Sample Composition by Gender")
        plt.ylim(0, max(pct) * 1.2 if pct else 1)
        for bar, val in zip(bars, pct):
            plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.8, f"{val:.1f}%", ha="center", va="bottom", fontsize=8)

    save_chart(OUTPUT_DIR / filename, draw_16)
    chart_outputs.append(
        ChartOutput(
            filename=filename,
            title="Gender distribution",
            caption=f"Gender composition of the survey sample (N={n_total}).",
            analysis="The sample is predominantly female, which should be considered when interpreting attitude prevalence estimates.",
        )
    )

    # 17
    filename = "17_demographics_age_distribution.png"

    def draw_17() -> None:
        pct = to_pct(age_counts)
        bars = plt.bar(age_labels, pct, color="#59A14F")
        plt.ylabel("Percent of respondents")
        plt.title("Sample Composition by Age Group")
        plt.ylim(0, max(pct) * 1.2 if pct else 1)
        for bar, val in zip(bars, pct):
            plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5, f"{val:.1f}%", ha="center", va="bottom", fontsize=8)

    save_chart(OUTPUT_DIR / filename, draw_17)
    chart_outputs.append(
        ChartOutput(
            filename=filename,
            title="Age-group distribution",
            caption=f"Age-group distribution of respondents (N={n_total}).",
            analysis="Most respondents are in the 18–25 group, so results mainly reflect younger public attitudes.",
        )
    )

    # 18
    filename = "18_demographics_education_distribution.png"

    def draw_18() -> None:
        pct = to_pct(edu_counts)
        bars = plt.bar(edu_labels, pct, color="#EDC948")
        plt.ylabel("Percent of respondents")
        plt.title("Sample Composition by Education Level")
        plt.ylim(0, max(pct) * 1.2 if pct else 1)
        for bar, val in zip(bars, pct):
            plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5, f"{val:.1f}%", ha="center", va="bottom", fontsize=8)

    save_chart(OUTPUT_DIR / filename, draw_18)
    chart_outputs.append(
        ChartOutput(
            filename=filename,
            title="Education-level distribution",
            caption=f"Education-level distribution among respondents (N={n_total}).",
            analysis="University-level education is the largest category in this sample.",
        )
    )

    # 19
    filename = "19_likert_diverging_q11_q13.png"

    def draw_19() -> None:
        y = np.arange(len(likert_short_labels))
        disagree = np.array(likert_groups["Disagree"])
        neutral = np.array(likert_groups["Neutral"])
        agree = np.array(likert_groups["Agree"])
        plt.barh(y, -disagree, color="#E15759", label="Disagree")
        plt.barh(y, neutral, color="#BAB0AC", label="Neutral")
        plt.barh(y, agree, left=neutral, color="#59A14F", label="Agree")
        plt.axvline(0, color="#333333", linewidth=1)
        plt.yticks(y, likert_short_labels)
        plt.xlabel("Percent of respondents")
        plt.title("Diverging Likert Profile for Core Stigma Questions")
        plt.xlim(-100, 100)
        plt.legend(frameon=False, loc="lower right")

    save_chart(OUTPUT_DIR / filename, draw_19)
    chart_outputs.append(
        ChartOutput(
            filename=filename,
            title="Diverging Likert chart (Q11–Q13)",
            caption="Disagree/Neutral/Agree percentages for Q11, Q12, and Q13.",
            analysis="Q11 and Q12 lean toward agreement with concern-focused statements, while Q13 shows stronger positive confidence in newer medications.",
        )
    )

    # 20
    filename = "20_correlation_matrix_primary_beliefs.png"

    def draw_20() -> None:
        im = plt.imshow(corr_matrix, cmap="coolwarm", vmin=-1, vmax=1)
        plt.xticks(np.arange(len(corr_labels)), corr_labels, rotation=35, ha="right")
        plt.yticks(np.arange(len(corr_labels)), corr_labels)
        plt.title("Correlation Matrix: Core Beliefs and Acceptance Indicators")
        cbar = plt.colorbar(im)
        cbar.set_label("Pearson correlation")
        for i in range(corr_matrix.shape[0]):
            for j in range(corr_matrix.shape[1]):
                value = corr_matrix[i, j]
                if np.isnan(value):
                    label = "NA"
                else:
                    label = f"{value:.2f}"
                plt.text(j, i, label, ha="center", va="center", fontsize=7, color="#111111")

    save_chart(OUTPUT_DIR / filename, draw_20)
    chart_outputs.append(
        ChartOutput(
            filename=filename,
            title="Correlation matrix heatmap",
            caption="Pearson correlations among core belief items and acceptance/recommendation indicators.",
            analysis="The matrix provides a quick view of how stigma-related beliefs move together and where overlap may influence multivariable modeling.",
        )
    )

    # 21
    filename = "21_acceptance_by_prior_use.png"

    def draw_21() -> None:
        bars = plt.bar(prior_groups, prior_recommend_pct, color=["#4E79A7", "#F28E2B"])
        plt.ylabel("Recommend 'Yes' rate (%)")
        plt.title("Recommendation Acceptance by Prior Medication Use")
        plt.ylim(0, 100)
        for bar, pct, count in zip(bars, prior_recommend_pct, prior_n):
            plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1.2, f"{pct:.1f}% (n={count})", ha="center", va="bottom", fontsize=8)

    save_chart(OUTPUT_DIR / filename, draw_21)
    chart_outputs.append(
        ChartOutput(
            filename=filename,
            title="Acceptance by prior-use subgroup",
            caption="Recommendation acceptance rate among respondents with and without prior psychiatric medication use.",
            analysis="The cleaned dataset does not include a direct trusted-source variable, so prior medication exposure is used as the closest subgroup context for acceptance differences.",
        )
    )

    # 22
    filename = "22_demographics_marital_distribution.png"

    def draw_22() -> None:
        pct = to_pct(marital_counts)
        bars = plt.bar(marital_labels, pct, color="#76B7B2")
        plt.ylabel("Percent of respondents")
        plt.title("Sample Composition by Marital Status")
        plt.ylim(0, max(pct) * 1.2 if pct else 1)
        for bar, val in zip(bars, pct):
            plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5, f"{val:.1f}%", ha="center", va="bottom", fontsize=8)

    save_chart(OUTPUT_DIR / filename, draw_22)
    chart_outputs.append(
        ChartOutput(
            filename=filename,
            title="Marital-status distribution",
            caption=f"Marital-status profile of participants (N={n_total}).",
            analysis="Most participants are single, which aligns with the young age structure of the sample.",
        )
    )

    # 23
    filename = "23_safety_perception_distribution.png"

    def draw_23() -> None:
        pct = to_pct(safety_counts)
        bars = plt.bar(safety_labels, pct, color=["#59A14F", "#BAB0AC", "#E15759"][: len(safety_labels)])
        plt.ylabel("Percent of respondents")
        plt.title("Perceived Safety of Psychiatric Medications")
        plt.ylim(0, max(pct) * 1.2 if pct else 1)
        for bar, val in zip(bars, pct):
            plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.6, f"{val:.1f}%", ha="center", va="bottom", fontsize=8)

    save_chart(OUTPUT_DIR / filename, draw_23)
    chart_outputs.append(
        ChartOutput(
            filename=filename,
            title="Safety-perception distribution",
            caption="Distribution of responses to whether psychiatric medications are safe.",
            analysis="Safety perception is mixed, with a substantial uncertain segment that may be responsive to targeted counseling.",
        )
    )

    # 24
    filename = "24_acceptability_distribution.png"

    def draw_24() -> None:
        pct = to_pct(acceptance_counts)
        bars = plt.bar(acceptance_labels, pct, color=["#59A14F", "#BAB0AC", "#E15759"][: len(acceptance_labels)])
        plt.ylabel("Percent of respondents")
        plt.title("Public Acceptability of Psychiatric Medication Use")
        plt.ylim(0, max(pct) * 1.2 if pct else 1)
        for bar, val in zip(bars, pct):
            plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.6, f"{val:.1f}%", ha="center", va="bottom", fontsize=8)

    save_chart(OUTPUT_DIR / filename, draw_24)
    chart_outputs.append(
        ChartOutput(
            filename=filename,
            title="Acceptability distribution",
            caption="Distribution of responses about accepting psychiatric medications like chronic-disease treatment.",
            analysis="Negative and uncertain acceptability responses remain prominent, which complements the modeled hesitation findings.",
        )
    )

    # 25
    filename = "25_recommendation_distribution.png"

    def draw_25() -> None:
        pct = to_pct(recommend_counts)
        bars = plt.bar(recommend_labels, pct, color=["#59A14F", "#BAB0AC", "#E15759"][: len(recommend_labels)])
        plt.ylabel("Percent of respondents")
        plt.title("Recommendation Willingness Distribution")
        plt.ylim(0, max(pct) * 1.2 if pct else 1)
        for bar, val in zip(bars, pct):
            plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.6, f"{val:.1f}%", ha="center", va="bottom", fontsize=8)

    save_chart(OUTPUT_DIR / filename, draw_25)
    chart_outputs.append(
        ChartOutput(
            filename=filename,
            title="Recommendation response distribution",
            caption="Distribution of responses to recommending psychiatric medications to someone close.",
            analysis="A majority report willingness to recommend, but a notable minority still declines or remains unsure.",
        )
    )

    # 26
    filename = "26_social_concern_distribution.png"

    def draw_26() -> None:
        pct = to_pct(concerns_counts)
        bars = plt.bar(concerns_labels, pct, color=["#E15759", "#BAB0AC", "#59A14F"][: len(concerns_labels)])
        plt.ylabel("Percent of respondents")
        plt.title("Concerns About Interacting With Medication Users")
        plt.ylim(0, max(pct) * 1.2 if pct else 1)
        for bar, val in zip(bars, pct):
            plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.6, f"{val:.1f}%", ha="center", va="bottom", fontsize=8)

    save_chart(OUTPUT_DIR / filename, draw_26)
    chart_outputs.append(
        ChartOutput(
            filename=filename,
            title="Social-interaction concern distribution",
            caption="Distribution of concern about interacting with people using psychiatric medications.",
            analysis="Social-contact concern remains common enough to signal persistent stigma in everyday interactions.",
        )
    )

    # 27
    filename = "27_donut_main_questions.png"

    def draw_27() -> None:
        axes = [plt.subplot(1, 3, idx + 1) for idx in range(3)]
        draw_donut(
            axes[0],
            ["Yes", "Not sure", "No"],
            [safety_count_map.get("Yes", 0), safety_count_map.get("Not sure", 0), safety_count_map.get("No", 0)],
            "Safety",
            ["#59A14F", "#BAB0AC", "#E15759"],
        )
        draw_donut(
            axes[1],
            ["Yes", "Not sure", "No"],
            [acceptance_count_map.get("Yes", 0), acceptance_count_map.get("Not sure", 0), acceptance_count_map.get("No", 0)],
            "Acceptability",
            ["#59A14F", "#BAB0AC", "#E15759"],
        )
        draw_donut(
            axes[2],
            ["Yes", "Not sure", "No"],
            [recommend_count_map.get("Yes", 0), recommend_count_map.get("Not sure", 0), recommend_count_map.get("No", 0)],
            "Recommendation",
            ["#59A14F", "#BAB0AC", "#E15759"],
        )
        plt.suptitle("Main Public Opinion Questions (Donut View)", fontsize=14)

    save_chart(OUTPUT_DIR / filename, draw_27)
    chart_outputs.append(
        ChartOutput(
            filename=filename,
            title="Donut charts for main questions",
            caption="Donut infographic view for safety, acceptability, and recommendation responses.",
            analysis="This compact format gives a quick social-media-style snapshot of the three core public opinion outcomes.",
        )
    )

    # 28
    filename = "28_waffle_safety_yes_share.png"

    def draw_28() -> None:
        draw_waffle(
            plt.gca(),
            safety_count_map.get("Yes", 0) * 100.0 / max(sum(safety_counts), 1),
            "Waffle Chart: Safety 'Yes' Share (Per 100 Respondents)",
            positive_label="Safety Yes",
            negative_label="Not Yes",
        )

    save_chart(OUTPUT_DIR / filename, draw_28)
    chart_outputs.append(
        ChartOutput(
            filename=filename,
            title="Safety waffle chart",
            caption="100-cell waffle chart showing the share answering Yes on safety.",
            analysis="The grid format translates percentages into an intuitive 'out of 100 people' visual.",
        )
    )

    # 29
    filename = "29_safety_yes_no_decisive.png"

    def draw_29() -> None:
        labels = ["Yes", "No"]
        values = [safety_yes_share_decisive, safety_no_share_decisive]
        bars = plt.bar(labels, values, color=["#59A14F", "#E15759"])
        plt.ylabel("Percent among decisive responses")
        plt.title("Safety Debate: Yes vs No (Excluding Not Sure)")
        plt.ylim(0, 100)
        for bar, val in zip(bars, values):
            plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1, f"{val:.1f}%", ha="center", va="bottom", fontsize=9)

    save_chart(OUTPUT_DIR / filename, draw_29)
    chart_outputs.append(
        ChartOutput(
            filename=filename,
            title="Safety yes-vs-no chart",
            caption="Direct Yes versus No comparison for safety among decisive responses.",
            analysis="This focuses the safety debate on respondents with a clear position.",
        )
    )

    # 30
    filename = "30_experience_gap_recommendation.png"

    def draw_30() -> None:
        bars = plt.bar(prior_groups, prior_recommend_pct, color=["#4E79A7", "#F28E2B"])
        plt.ylabel("Recommend 'Yes' rate (%)")
        plt.title("Experience Gap: Recommendation by Prior Medication Use")
        plt.ylim(0, 100)
        for bar, pct, count in zip(bars, prior_recommend_pct, prior_n):
            plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1, f"{pct:.1f}% (n={count})", ha="center", va="bottom", fontsize=8)

    save_chart(OUTPUT_DIR / filename, draw_30)
    chart_outputs.append(
        ChartOutput(
            filename=filename,
            title="Experience-gap chart",
            caption="Recommendation acceptance rates among respondents with and without prior medication experience.",
            analysis="A clear gap between experienced and non-experienced respondents highlights the role of personal exposure.",
        )
    )

    # 31
    filename = "31_gender_recommendation_breakdown.png"

    def draw_31() -> None:
        x = np.arange(len(gender_groups))
        width = 0.24
        yes_vals = [gender_recommend_pct[group][0] for group in gender_groups]
        unsure_vals = [gender_recommend_pct[group][1] for group in gender_groups]
        no_vals = [gender_recommend_pct[group][2] for group in gender_groups]
        b1 = plt.bar(x - width, yes_vals, width=width, color="#59A14F", label="Yes")
        b2 = plt.bar(x, unsure_vals, width=width, color="#BAB0AC", label="Not sure")
        b3 = plt.bar(x + width, no_vals, width=width, color="#E15759", label="No")
        plt.xticks(x, gender_groups)
        plt.ylim(0, 100)
        plt.ylabel("Percent within gender")
        plt.title("Recommendation Opinions by Gender")
        plt.legend(frameon=False)
        for bars in [b1, b2, b3]:
            for bar in bars:
                val = bar.get_height()
                plt.text(bar.get_x() + bar.get_width() / 2, val + 0.8, f"{val:.1f}%", ha="center", va="bottom", fontsize=7)

    save_chart(OUTPUT_DIR / filename, draw_31)
    chart_outputs.append(
        ChartOutput(
            filename=filename,
            title="Gender breakdown of recommendation opinions",
            caption="Within-gender distribution of Yes/Not sure/No responses for recommendation.",
            analysis="The side-by-side format highlights how recommendation sentiment differs between women and men.",
        )
    )

    expected_prefixes = [f"{idx:02d}_" for idx in range(1, EXPECTED_CHART_COUNT + 1)]
    generated_files = [chart.filename for chart in chart_outputs]
    missing_prefixes = [prefix for prefix in expected_prefixes if not any(name.startswith(prefix) for name in generated_files)]

    if len(chart_outputs) != EXPECTED_CHART_COUNT or missing_prefixes:
        raise RuntimeError(
            "Chart generation incomplete. "
            f"Expected {EXPECTED_CHART_COUNT} charts with prefixes 01_..{EXPECTED_CHART_COUNT:02d}_, generated {len(chart_outputs)} charts. "
            f"Missing prefixes: {missing_prefixes}."
        )

    summary_lines: list[str] = []
    summary_lines.append("# Survey Visualization Summary")
    summary_lines.append("")
    summary_lines.append("This is an auto-generated chart summary created by `analysis_pipeline/visualize.py` from `survey_data_results.md`.")
    summary_lines.append(f"Generated at: {datetime.now(timezone.utc).isoformat()}")
    summary_lines.append("")

    for idx, chart in enumerate(chart_outputs, start=1):
        description_path = OUTPUT_DIR / f"{Path(chart.filename).stem}.md"
        description_lines = [
            f"# {chart.title}",
            "",
            "This chart is part of the survey analysis for *Psychiatric Medication Use and Public Acceptance in Iraq*.",
            "",
            f"![{chart.title}]({chart.filename})",
            "",
            f"**Caption:** {chart.caption}",
            "",
            f"**Quick analysis:** {chart.analysis}",
            "",
        ]
        description_path.write_text("\n".join(description_lines), encoding="utf-8")

        summary_lines.append(f"## Chart {idx:02d}: {chart.title}")
        summary_lines.append("")
        summary_lines.append(f"![{chart.title}]({chart.filename})")
        summary_lines.append("")
        summary_lines.append(f"**Caption:** {chart.caption}")
        summary_lines.append("")
        summary_lines.append(f"**Quick analysis:** {chart.analysis}")
        summary_lines.append("")

    SUMMARY_MD.write_text("\n".join(summary_lines).strip() + "\n", encoding="utf-8")

    print(f"Created {len(chart_outputs)} charts in: {OUTPUT_DIR}")
    print(f"Summary markdown written to: {SUMMARY_MD}")


if __name__ == "__main__":
    main()
