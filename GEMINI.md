# 📚 Mathebuch-Generator – Klasse 1

A professional Python tool for generating high-quality, printable PDF math workbooks for first-grade students. It transforms YAML-defined exercises into a structured, colorful PDF with a title page, table of contents, themed chapters, and automated solution pages.

## 🏗️ Project Overview

- **Purpose:** Automated generation of math exercise books in German.
- **Tech Stack:** Python 3, [ReportLab](https://www.reportlab.com/) (PDF rendering), [PyYAML](https://pyyaml.org/) (Data parsing).
- **Output:** A4 PDF with dynamic layout, automatic page breaks, and color-coded chapters.

### 🧩 Architecture

1.  **Orchestration (`generator/main.py`):**
    - Executes a **two-pass rendering pipeline**:
        - **Pass 1 (Probe):** Renders the document to a buffer to calculate exact page numbers for each chapter.
        - **Pass 2 (Final):** Renders the final PDF with a correct Table of Contents (TOC) and solution references.
    - Manages global state: page backgrounds, chapter separators (Trennseiten), and TOC grouping by "Zahlenraum" (5, 10, 20).

2.  **Exercise Rendering (`generator/aufgabentypen.py`):**
    - Contains over 25 `draw_<type>` functions (e.g., `draw_lückenaufgaben`, `draw_rechenmauer`, `draw_magisches_quadrat`).
    - Each function calculates its own Y-offset and handles element positioning within a section.

3.  **Visual Primitives (`generator/layout.py`):**
    - Defines the central color palette (`FARBEN`).
    - Provides reusable components: `draw_header`, `draw_answer_box`, `draw_page_bg`.

4.  **Auto-Solver (`generator/loesungen.py`):**
    - A registry of solver functions that programmatically derive answers from the exercise data.
    - Renders ultra-compact solution pages at the end of the book.

5.  **Content (`aufgaben/`):**
    - YAML files named `kXX_description.yaml`.
    - Alphabetical order of filenames determines the chapter sequence.

## 🚀 Building and Running

### Setup
```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install reportlab pyyaml
```

### Execution
```bash
# Generate the default workbook (from root)
cd generator
python3 main.py

# Optional: Specify custom output path
python3 main.py --output ../output/mein_mathebuch.pdf

# Optional: Run layout audit (Verify content fits on pages)
cd generator && python3 main.py --audit-layout
```

## 🛠️ Development Conventions

### Content Standards
- **Language:** All user-facing text (titles, descriptions, labels) MUST be in **German**.
- **Data Format:** Use `null` in YAML to indicate a blank field (Lücke) for the student to fill in.
- **Chapter Colors:** Use keys from `layout.py` (`blau`, `gruen`, `pink`, `orange`, `yellow`, `purple`).

### Adding a New Exercise Type
1.  **Implement Renderer:** Add `draw_<new_type>` in `aufgabentypen.py`.
2.  **Register Renderer:** Add the mapping to the `TYPEN` dict in `main.py`.
3.  **Implement Solver:** Add `_solve_<new_type>` in `loesungen.py`.
4.  **Register Solver:** Add the mapping to the `SOLVER` dict in `loesungen.py`.
5.  **Test:** Create a new YAML file in `aufgaben/` using the type and verify the visual output.

### Layout Constants
- **Page Size:** A4 (21cm x 29.7cm).
- **Safe Zone:** Content should respect `MIN_Y` (2.5 cm) to avoid overlapping the page number footer.
- **Header:** Reserved area at the top (~4cm) for titles and emojis.

## 🧪 Layout Verification Workflow

To run the layout audit independently using a git worktree:
1. `git worktree add ../mathebuch-audit <branch-name>`
2. `cd ../mathebuch-audit && python3 -m venv .venv && source .venv/bin/activate`
3. `pip install reportlab pyyaml`
4. `cd generator && python3 main.py --audit-layout`
5. Cleanup: Return to your original repository directory and run `git worktree remove ../mathebuch-audit`
