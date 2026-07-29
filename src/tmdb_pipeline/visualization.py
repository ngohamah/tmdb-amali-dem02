"""Visualization helpers for the TMDB analysis."""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from .logger_config import configure_logger

logger = configure_logger(__name__)

'''
#TODO: improve visualization (X)
label encoding for genres and production companies to make plots more readable
Proper scaling rating.

ANALYSIS:
The dataset is small and due to piping some genres combination occur more times than 
others. If we use the primary genre, then our analysis might be faulty b/c tmdb does not weight the genres
to indicate which is primary or more prevalent in the movie. Therefore color encoding based on genre is problematic.

#TODO: Color code based on the original movie title. (X)

ANALYSIS:
This is only recommended b/c the dataset is small. For larger datasets, it might be better to encode based on the production company.

#TODO: Color code based on the production company. (Best practice!)
'''

def save_plots(df: pd.DataFrame, output_dir: Path) -> list[Path]:
    """Create plots and save them to disk."""
    output_dir.mkdir(parents=True, exist_ok=True)
    saved_paths: list[Path] = []

    plot_df = df.copy()
    if "roi" not in plot_df.columns:
        plot_df["roi"] = plot_df["revenue_musd"] / plot_df["budget_musd"].replace(0, pd.NA)
    plot_df = plot_df.dropna(subset=["budget_musd", "revenue_musd", "roi"])

    primary_studio = plot_df["production_companies"].fillna("Unknown").str.split("|").str[0]
    studio_codes, studio_labels = pd.factorize(primary_studio)

    try:
        fig, ax = plt.subplots(figsize=(12, 9))
        scatter = ax.scatter(
            plot_df["budget_musd"], plot_df["revenue_musd"],
            c=studio_codes, cmap="tab20", alpha=0.7,
        )
        ax.set_title("Revenue vs Budget")
        ax.set_xlabel("Budget (M USD)")
        ax.set_ylabel("Revenue (M USD)")
        handles, _ = scatter.legend_elements(num=len(studio_labels))
        ax.legend(handles, studio_labels, title="Production Company", bbox_to_anchor=(1.02, 1), loc="upper left", fontsize="small")
        path = output_dir / "revenue_vs_budget.png"
        fig.tight_layout()
        fig.savefig(path, bbox_inches="tight")
        plt.close(fig)
        saved_paths.append(path)

        fig, ax = plt.subplots(figsize=(25, 15))
        plot_df.boxplot(column="roi", by="genres", ax=ax)
        ax.set_title("ROI Distribution by Genre")
        ax.set_ylabel("ROI (x)")
        ax.set_xticklabels(ax.get_xticklabels(), rotation=90)
        path = output_dir / "roi_by_genre.png"
        fig.tight_layout()
        fig.savefig(path)
        plt.close(fig)
        saved_paths.append(path)

        fig, ax = plt.subplots(figsize=(12, 9))
        scatter = ax.scatter(
            plot_df["popularity"], plot_df["vote_average"],
            c=studio_codes, cmap="tab20", alpha=0.7,
        )
        ax.set_title("Popularity vs Rating")
        ax.set_xlabel("Popularity (/100)")
        ax.set_ylabel("Vote Average (/10)")
        handles, _ = scatter.legend_elements(num=len(studio_labels))
        ax.legend(handles, studio_labels, title="Production Company", bbox_to_anchor=(1.02, 1), loc="upper left", fontsize="small")
        path = output_dir / "popularity_vs_rating.png"
        fig.tight_layout()
        fig.savefig(path, bbox_inches="tight")
        plt.close(fig)
        saved_paths.append(path)

        logger.info("Saved %d plots", len(saved_paths))
        return saved_paths
    except Exception:
        logger.exception("Plot generation failed")
        raise
