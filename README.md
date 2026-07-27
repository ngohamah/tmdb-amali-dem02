# TMDB Movie Data Analysis Pipeline

An end-to-end Python pipeline that fetches movie data from [The Movie Database (TMDB)](https://www.themoviedb.org/) API, cleans and transforms it with Pandas, computes rankings and performance KPIs (top/worst movies, franchise vs. standalone comparisons, director performance), and produces a Markdown report with supporting charts.

## What it does

Running the pipeline (`run_pipeline.py`) performs these steps in order:

1. **Fetch** — Requests a fixed batch of movies (by TMDB ID, see `src/tmdb_pipeline/config.py`) from the TMDB API. If no API key is configured or the request fails, it automatically falls back to the bundled sample payloads (`data/sample_payloads.json`) so the pipeline still runs end-to-end offline. Raw responses are cached to `data/raw_payloads.json` and a snapshot is written to `data/raw_movies.json`.
2. **Clean** — Drops irrelevant columns, flattens JSON-like fields (genres, production companies/countries, spoken languages, collections) into pipe-separated strings, fixes data types, treats zero budget/revenue/runtime as missing, converts budget/revenue to million-USD units, derives `profit_musd` and `roi`, removes duplicates/incomplete rows, and keeps only `Released` movies. The result is saved to `data/clean_movies.csv`.
3. **Analyze** — Builds top-10 rankings (highest revenue, budget, profit, ROI, votes, rating, popularity, etc.), and summarizes franchise (`belongs_to_collection`) and director performance.
4. **Visualize** — Saves charts to `reports/plots/`: Revenue vs. Budget, ROI Distribution by Genre, and Popularity vs. Rating.
5. **Report** — Writes a combined Markdown summary to `reports/movie_analysis_report.md`.

All steps log progress and errors to `logs/pipeline.log`.

## Project structure

```
run_pipeline.py                 Entry point — runs the full pipeline
src/tmdb_pipeline/
  config.py                     Paths, TMDB API settings, movie ID list, column definitions
  api_utils.py                  TMDB API fetching + cached/sample payload fallback
  processing.py                 Data cleaning & transformation
  analysis.py                   Rankings, searches, franchise/director summaries
  visualization.py              Chart generation (matplotlib)
  logger_config.py              Shared file-based logging setup
data/                           Raw and cleaned datasets (generated + sample data)
reports/                        Generated report and plots
logs/                           Pipeline log output
requirements.txt                Python dependencies
```

## Prerequisites

- Python 3.11+ (developed with Python 3.14)
- A [TMDB API key](https://www.themoviedb.org/settings/api) — optional. Without one, the pipeline uses the bundled sample data automatically.

## Installation

1. Clone the repository and move into it:
   ```bash
   git clone <repo-url>
   cd DEM02
   ```
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate      # Windows: .venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration (optional)

To fetch live data instead of using the sample payloads, set your TMDB API key in `src/tmdb_pipeline/config.py`:

```python
TMDB_API_KEY = "YOUR_TMDB_API_KEY"
```

Replace the placeholder with your real key. If it's left as-is, or a request fails, the pipeline logs a warning and transparently falls back to `data/sample_payloads.json`.

> Note: `data/raw_payloads.json`, if present, is treated as a cache and will be reused instead of hitting the API again. Delete it to force a fresh fetch.

## Running the pipeline

From the project root, with the virtual environment activated:

```bash
python run_pipeline.py
```

This generates/updates:
- `data/clean_movies.csv` — cleaned dataset
- `reports/movie_analysis_report.md` — rankings and summary report
- `reports/plots/*.png` — generated charts
- `logs/pipeline.log` — execution log

## Linting

The project uses [Ruff](https://docs.astral.sh/ruff/) for linting:

```bash
ruff check .
```
