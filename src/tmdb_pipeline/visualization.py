"""Visualization helpers for the TMDB analysis."""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from .logger_config import configure_logger

logger = configure_logger(__name__)


def save_plots(df: pd.DataFrame, output_dir: Path) -> list[Path]:
    """Create plots and save them to disk."""
    output_dir.mkdir(parents=True, exist_ok=True)
    saved_paths: list[Path] = []

    plot_df = df.copy()
    if "roi" not in plot_df.columns:
        plot_df["roi"] = plot_df["revenue_musd"] / plot_df["budget_musd"].replace(0, pd.NA)
    plot_df = plot_df.dropna(subset=["budget_musd", "revenue_musd", "roi"])

    try:
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.scatter(plot_df["budget_musd"], plot_df["revenue_musd"], alpha=0.7)
        ax.set_title("Revenue vs Budget")
        ax.set_xlabel("Budget (M USD)")
        ax.set_ylabel("Revenue (M USD)")
        path = output_dir / "revenue_vs_budget.png"
        fig.tight_layout()
        fig.savefig(path)
        plt.close(fig)
        saved_paths.append(path)

        fig, ax = plt.subplots(figsize=(25, 15))
        plot_df.boxplot(column="roi", by="genres", ax=ax)
        ax.set_title("ROI Distribution by Genre")
        ax.set_ylabel("ROI")
        ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
        path = output_dir / "roi_by_genre.png"
        fig.tight_layout()
        fig.savefig(path)
        plt.close(fig)
        saved_paths.append(path)

        fig, ax = plt.subplots(figsize=(8, 5))
        ax.scatter(plot_df["popularity"], plot_df["vote_average"], alpha=0.7)
        ax.set_title("Popularity vs Rating")
        ax.set_xlabel("Popularity")
        ax.set_ylabel("Vote Average")
        path = output_dir / "popularity_vs_rating.png"
        fig.tight_layout()
        fig.savefig(path)
        plt.close(fig)
        saved_paths.append(path)

        logger.info("Saved %d plots", len(saved_paths))
        return saved_paths
    except Exception:
        logger.exception("Plot generation failed")
        raise
