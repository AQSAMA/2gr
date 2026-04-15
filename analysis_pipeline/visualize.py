from __future__ import annotations

import math
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

import matplotlib.pyplot as plt
import numpy as np


BASE_DIR = Path(__file__).resolve().parents[1]
INPUT_MD = BASE_DIR / "survey_data_results.md"
OUTPUT_DIR = BASE_DIR / "output"
SUMMARY_MD = OUTPUT_DIR / "chart_summary.md"
# Floor for p-values before log10 transforms to avoid undefined log10(0).
MIN_PVALUE = 1e-12
TEXT_LABEL_OFFSET_RATIO = 0.03
EXPECTED_CHART_COUNT = 15


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


def main() -> None:
    if not INPUT_MD.exists():
        raise FileNotFoundError(f"Input markdown not found: {INPUT_MD}")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    text = INPUT_MD.read_text(encoding="utf-8")
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

    expected_prefixes = [f"{idx:02d}_" for idx in range(1, EXPECTED_CHART_COUNT + 1)]
    generated_files = [chart.filename for chart in chart_outputs]
    missing_prefixes = [prefix for prefix in expected_prefixes if not any(name.startswith(prefix) for name in generated_files)]

    if len(chart_outputs) != EXPECTED_CHART_COUNT or missing_prefixes:
        raise RuntimeError(
            "Chart generation incomplete. "
            f"Expected {EXPECTED_CHART_COUNT} charts with prefixes 01_..{EXPECTED_CHART_COUNT:02d}_, generated {len(chart_outputs)} charts. "
            f"Missing prefixes: {missing_prefixes}. Generated files: {generated_files}"
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
