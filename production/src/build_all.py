#!/usr/bin/env python3
from __future__ import annotations

import shutil
import sys
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

import build_production  # noqa: E402
import build_typst  # noqa: E402
import build_typst_content  # noqa: E402


def warn_missing_tool(name: str, purpose: str) -> None:
    if shutil.which(name) is None:
        print(f"WARNING: {name} is not installed; {purpose}")


def main() -> None:
    warn_missing_tool("pandoc", "Pandoc-dependent conversions are unavailable, but the Python Method A path will still run.")
    warn_missing_tool("typst", "Typst PDFs will be skipped after the Markdown/Method A build completes.")

    print("Step 1/3: Building assembled Markdown and Method A outputs.")
    build_production.ensure_dirs()
    build_production.copy_figure_assets()
    md_path = build_production.assemble_markdown()
    build_production.run_method_a(md_path)
    print(f"Method A outputs: {build_production.METHOD_A_DIR}")

    print("Step 2/3: Building Method B Typst outputs.")
    build_typst.run_method_b(md_path)

    print("Step 3/3: Building editable typst_content source and companion outputs.")
    build_typst_content.run_typst_content(md_path)
    print("All available production paths completed.")


if __name__ == "__main__":
    main()
