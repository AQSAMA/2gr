# Method B: Typst Pipeline

## English

Method B is the Typst production path for the thesis. It uses the same assembled Markdown manuscript as Method A and produces five PDF designs from one synchronized source.

The scientific source remains `content/*.md`. Do not edit `generated/body.typ` to change scientific text, survey results, figures, citations, or chapter order. That file is generated automatically from `production/assembled/comprehensive_research.md` by `production/src/build_typst.py`.

Directory roles are simple. `templates/` contains editable Typst design files. `generated/` contains automatic Typst files and design entry points. `output/` contains final PDF files. `main.typ` is a default entry point for compiling the classic design after the generated body exists.

To run locally from the repository root:

```bash
python -m pip install -r production/requirements.txt
python production/src/build_all.py
```

If Typst is installed, the build produces these files in `production/method_b_typst/output/`:

```text
design_01_classic.pdf
design_02_modern_navy.pdf
design_03_minimal_journal.pdf
design_04_elegant_frontmatter.pdf
design_05_defense_copy.pdf
```

To modify a design, edit the matching file in `templates/`, then rerun `python production/src/build_all.py`. For example, edit `templates/design_02_modern_navy.typ` to change the navy design only. Do not manually edit `generated/body.typ`, because the next build will overwrite it.

## Related Editable Typst Source

The separate `typst_content/research.typ` file is the preferred single-file Typst source for manual editing. This Method B directory remains the multi-design production path, while `typst_content/` provides one clean thesis-style version with front matter, borders, Roman preliminary numbering, Arabic main numbering, and companion PDF/DOCX outputs in CI.
