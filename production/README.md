# Production Pipeline

This folder contains a self-contained production pipeline that keeps source research text unchanged and generates publication-ready outputs in multiple methods.

## Input sources used
- `/home/runner/work/2gr/2gr/content/*.md`
- `/home/runner/work/2gr/2gr/references.md`
- `/home/runner/work/2gr/2gr/figures/*.{md,png}`

## Outputs
- `assembled/comprehensive_research.md`
- `method_a_python/research_method_a.pdf`
- `method_a_python/research_method_a.docx`
- `method_a_python/research_method_a.tex`
- `method_b_hybrid/research_method_b.pdf`
- `method_b_hybrid/research_method_b.docx`
- `method_b_hybrid/research_method_b.tex`

## Run
```bash
cd /home/runner/work/2gr/2gr
python -m pip install -r production/requirements.txt
python production/src/build_production.py
```

## Operations (CI/CD)
The workflow in `.github/workflows/production.yml` runs on every `push` and `pull_request`, executes `python production/src/build_production.py`, and uploads the generated outputs as run artifacts in the Actions **Artifacts** panel.

When a tag push (for example `v1.0.0`) or a published GitHub Release event occurs, the same build runs again and DOCX/PDF/TEX/MD outputs are uploaded as Release assets on the matching tag/release page.

CI only builds and publishes artifacts/assets; it does not commit generated binary files back to the repository.

## Notes
- The pipeline does not modify any file in `content/`, `sources/`, `figures/`, or other repository paths.
- Page size/margins, Times New Roman style target, and line spacing are applied in generated outputs.
