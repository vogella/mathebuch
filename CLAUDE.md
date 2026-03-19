# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Mathebuch-Generator: a Python tool that generates a printable PDF math workbook for first-grade students. It reads YAML exercise definitions from `aufgaben/` and renders them via ReportLab into a full-color, illustrated PDF with title page, table of contents, chapters, and auto-generated solution pages.

## Commands

```bash
# Setup
python3 -m venv .venv && source .venv/bin/activate
pip install reportlab pyyaml

# Generate PDF (run from repo root)
cd generator && python3 main.py

# Custom output path (run from generator/)
python3 main.py --output ../output/custom.pdf
```

Default output: `output/mathebuch_klasse1.pdf`. No test framework — verify by generating the PDF and inspecting visually.

## Architecture

**Two-pass PDF rendering pipeline:**
1. `main.py` loads all `aufgaben/k*.yaml` files (alphabetical order = chapter order), runs a probe pass to calculate page numbers, then a final pass with correct TOC page references.
2. `aufgabentypen.py` contains ~20 `draw_*` functions, one per exercise type. Each renders a section on the canvas and returns the new Y position: `draw_TYPE(c, abschnitt, farb_key, start_y) → new_y`.
3. `layout.py` provides shared drawing primitives: page backgrounds, headers, answer boxes, color palette, A4 dimensions.
4. `loesungen.py` has a `SOLVER` registry mapping exercise types to solver functions that auto-calculate answers from YAML data, then renders compact solution pages at the end of the PDF.

**Adding a new exercise type requires changes in three places:**
1. A `draw_<type>` function in `aufgabentypen.py`
2. A solver function registered in the `SOLVER` dict in `loesungen.py`
3. A YAML file in `aufgaben/` using the new type

## YAML Content Format

Files in `aufgaben/` are named `k##_description.yaml`. Each file defines one chapter:

```yaml
kapitel:
  titel: "Chapter title"
  untertitel: "Subtitle"
  emoji: "🔢"
  farbe: "blau"          # blau|gruen|pink|orange|yellow|purple
  zahlenraum: 10         # 5, 10, or 20 — used for TOC grouping
  erklaerungsseite: false # true = explanation page (no stars, excluded from TOC details)

abschnitte:
  - typ: "lückenaufgaben"
    titel: "Section title"
    aufgaben: [...]       # Structure varies by type
```

## Branching Workflow

- Fetch the latest remote state before creating a branch: `git fetch origin`
- Create your new branch based on `origin/main`: `git checkout -b <branch-name> origin/main`

## Common Task Shortcuts

**"fix issue X"** means:
1. `git fetch origin`
2. Create a new local branch based on `origin/main`
3. Fix the issue
4. Commit, push, and create a new PR

**"check PR X"** means:
1. Fetch the PR branch locally (e.g., `gh pr checkout X`)
2. Review all new review comments/feedback on the PR
3. Evaluate each piece of feedback — apply changes that make sense
4. Commit and push the updates to the existing PR branch

## Key Conventions

- All user-facing text is in **German** (titles, descriptions, labels). Always write German content in YAML and UI strings.
- Exercise data uses `null` to mark blanks the student fills in (e.g., `[3, "+", null, 7]` means `3 + _ = 7`).
- Page layout: A4 (21×29.7cm), 4cm header area, automatic page breaks when content overflows.
- Color keys reference the palette in `layout.py` (`FARBEN` dict).
