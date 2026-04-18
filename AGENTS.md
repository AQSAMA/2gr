# AGENTS.md Governance Baseline

## 1) Canonical policy file
`AGENTS.md` is the canonical governance file for writing instructions in this repository. Any reference to `agents.md` or other casing means this same file.

## 2) Single source of truth model
Use this governance stack in order:
1. `AGENTS.md` (policy and process rules)
2. `outline.md` (section architecture and scope)
3. Section draft file under `content/` (execution of the mapped section only)

If instructions conflict, follow the highest item in this order.

## 3) Section-level evidence rules
- **Results:** All numeric findings (counts, percentages, model outputs, p-values, ORs, CIs) must come from `survey_data_results.md` only.
- **Introduction and Discussion:** Use mapped literature from `sources/` with in-text citations that match `references.md`.
- **Methods:** Describe this study workflow and analysis process for the current cross-sectional dataset. Do not use narrative-review search-method framing (no database search strategy, no inclusion/exclusion flow for literature screening).

## 4) Analysis reporting boundaries
- Keep **main/primary analyses** separate from **sensitivity analyses** and **exploratory analyses**.
- Do not label exploratory outputs as confirmatory.
- Keep interpretation proportional to analysis type.

## 5) Lightweight pre-draft QA checklist
Before drafting any section, confirm all four checks:
1. **Provenance:** Every claim has the correct source type (`survey_data_results.md` vs `sources/`).
2. **Scope:** Content matches the assigned section purpose in `outline.md`.
3. **Section identity:** Headings and numbering match `outline.md`.
4. **Figure existence:** Any referenced figure/table exists in repository files before mention.

## 6) Practical writing style
- Use clear scientific English and direct sentences.
- Prefer active voice.
- Avoid inflated or decorative wording.
- Keep paragraphs focused on one claim chain: evidence -> interpretation -> implication.
- In body text, write full paragraphs instead of bullet-list argument fragments.
