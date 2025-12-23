# PythonApps

PythonApps is a collection of Python applications built to demonstrate practical programming, modular architecture, and real-world functionality. The main purpose of this repository is to serve as a technical portfolio that increases your market value as a Python developer by showcasing skills in data processing, automation, scraping, graphical interfaces, and media manipulation.

---

**Purpose**

- Demonstrate software engineering practices with small, independent projects.
- Expose relevant technical skills to employers and clients (data processing, analysis, visualization, automation and GUI).
- Keep each application modular to facilitate evolution, testing and code reuse.

---

**Available Applications**

- **EcomReport** (EcomReport/): desktop tool that processes sales CSVs, validates data, generates statistics (total revenue, orders, AOV) and produces visualizations (bars, lines, donuts) with export to PDF. UI in Tkinter, processing with Pandas and graphics with Matplotlib.
- **EliteCritics** (EliteCritics/): scraping and analysis engine to recalculate critical scores (Tomatometer-like). It scrapes pages, stores information in SQLite and calculates metrics weighted by the critic's experience/genre.
- **VideoTools** (VideoTools/): utilities for batch video processing: cut and concatenate (`SmartVideoCutter.py`), totalize timelines (`TimelineTotalizer.py`), inspect resolutions (`MultiVideoInspector.py`) and extract frames (`MultiVideoToFrames.py`) using `moviepy` and `tqdm`.
- **GhostMouse** (GhostMouse/): mouse event recorder and player for automating repetitive tasks. Uses `pynput` for capture and `pyautogui` for replay with preserved delays and fail-safe mechanism.
- **Counter** (Counter/): simple widget in Qt (PySide6) — minimalist counter, always on top, with circular, draggable UI and support for copying value to clipboard.
- **clean_csv** (clean_csv/): utility scripts for cleaning CSVs, removing nulls, and normalizing fields to prepare data for analysis.
- **TableScripts** (TableScripts/): scripts for creating and altering tables (e.g.: `CreateTables.py`, `AlterTables.py`) used to manage simple database schemas.
- **Junkcode**: small experiments and various utilities (ad-hoc analyses, transformations) used as a laboratory for ideas.

Each application includes a local README with usage instructions, dependencies and execution examples. Examples of test CSVs and assets are present in the corresponding folders where applicable.

---

**Technologies & Libraries**

- **Python 3.8+**: main language used in all projects.
- **Pandas**: manipulation and cleaning of tabular data.
- **Matplotlib**: creation of graphs and visualizations.
- **Pillow**: image composition and report generation support (PDF from image).
- **Tkinter** / **PySide6 (Qt)**: graphical interfaces (simple desktop apps and widgets).
- **moviepy, tqdm, numpy**: video processing and iteration.
- **pynput, pyautogui**: capture and replay mouse events for automation.
- **SQLite**: lightweight local storage (used by `EliteCritics`).
- **Requests / BeautifulSoup / Selenium** (when necessary): HTML scraping and parsing (depending on the project).

These technologies were chosen for their robustness and broad market adoption, facilitating practical demonstrations of tools and workflows valued by engineering teams and recruiters.

---

### Contributing

Contributions are welcome! You can:
- Improve existing apps with new features or bug fixes.
- Submit issues or pull requests via GitHub.

---

### License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.