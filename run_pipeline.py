"""Run the TMDB movie analysis pipeline."""
from __future__ import annotations

from src.tmdb_pipeline.analysis import (
    build_rankings,
    summarize_director_performance,
    summarize_franchise_performance,
)
from src.tmdb_pipeline.api_utils import fetch_movie_batch
from src.tmdb_pipeline.config import (
    CLEAN_DATA_PATH,
    PLOTS_DIR,
    RAW_DATA_PATH,
    REPORT_PATH,
)
from src.tmdb_pipeline.logger_config import configure_logger
from src.tmdb_pipeline.processing import clean_movie_data
from src.tmdb_pipeline.visualization import save_plots

logger = configure_logger("run_pipeline")


def main() -> None:
    """Executing the full end-to-end pipeline."""
    try:
        payloads = fetch_movie_batch()
        RAW_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
        RAW_DATA_PATH.write_text(str(payloads), encoding="utf-8")
        logger.info("Stored raw payloads at %s", RAW_DATA_PATH)

        clean_df = clean_movie_data(payloads)
        CLEAN_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
        clean_df.to_csv(CLEAN_DATA_PATH, index=False)
        logger.info("Stored cleaned data at %s", CLEAN_DATA_PATH)

        rankings = build_rankings(clean_df)
        franchise_summary = summarize_franchise_performance(clean_df)
        director_summary = summarize_director_performance(clean_df)

        save_plots(clean_df, PLOTS_DIR)

        report_lines = [
            "# TMDB Movie Data Analysis Report",
            "",
            "## Summary",
            "- Extracted and cleaned TMDB movie data.",
            "- Generated rankings and performance summaries.",
            "",
            "## Top Rankings",
        ]
        for name, frame in rankings.items():
            report_lines.append(f"### {name}")
            report_lines.append(frame.head(5).to_string(index=False))
            report_lines.append("")

        report_lines.extend([
            "## Franchise Summary",
            franchise_summary.head(10).to_string(index=False),
            "",
            "## Director Summary",
            director_summary.head(10).to_string(index=False),
        ])

        REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
        REPORT_PATH.write_text("\n".join(report_lines), encoding="utf-8")
        logger.info("Wrote report to %s", REPORT_PATH)
    except Exception:
        logger.exception("Pipeline execution failed")
        raise


if __name__ == "__main__":
    main()
