"""Analysis routines for the cleaned TMDB dataset."""
from __future__ import annotations

import pandas as pd

from .logger_config import configure_logger

logger = configure_logger(__name__)


def rank_movies(df: pd.DataFrame, metric: str, ascending: bool = False) -> pd.DataFrame:
    """Return a ranked dataframe for a metric."""
    if metric not in df.columns:
        if metric == "profit_musd" and "revenue_musd" in df.columns and "budget_musd" in df.columns:
            df = df.copy()
            df["profit_musd"] = df["revenue_musd"] - df["budget_musd"]
        elif metric == "roi" and "revenue_musd" in df.columns and "budget_musd" in df.columns:
            df = df.copy()
            df["roi"] = df["revenue_musd"] / df["budget_musd"].replace(0, pd.NA)
        else:
            raise KeyError(f"Metric '{metric}' not found in dataframe")
    return df.sort_values(by=metric, ascending=ascending).head(10).reset_index(drop=True)


def build_rankings(df: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """Create a dictionary of common rankings."""
    logger.info("Building rankings")
    budget_mask = df["budget_musd"].notna() if "budget_musd" in df.columns else pd.Series([False] * len(df), index=df.index)
    vote_mask = df["vote_count"].notna() if "vote_count" in df.columns else pd.Series([False] * len(df), index=df.index)
    return {
        "highest_revenue": rank_movies(df, "revenue_musd", ascending=False),
        "highest_budget": rank_movies(df, "budget_musd", ascending=False),
        "highest_profit": rank_movies(df, "profit_musd", ascending=False),
        "lowest_profit": rank_movies(df, "profit_musd", ascending=True),
        "highest_roi": rank_movies(df.loc[budget_mask & (df["budget_musd"] >= 10)], "roi", ascending=False),
        "lowest_roi": rank_movies(df.loc[budget_mask & (df["budget_musd"] >= 10)], "roi", ascending=True),
        "most_voted": rank_movies(df, "vote_count", ascending=False),
        "highest_rated": rank_movies(df.loc[vote_mask & (df["vote_count"] >= 10)], "vote_average", ascending=False),
        "lowest_rated": rank_movies(df.loc[vote_mask & (df["vote_count"] >= 10)], "vote_average", ascending=True),
        "most_popular": rank_movies(df, "popularity", ascending=False),
    }


def search_sci_fi_action_bruce_willis(df: pd.DataFrame) -> pd.DataFrame:
    """Search for Sci-Fi Action movies starring Bruce Willis, sorted by rating."""
    if not all(col in df.columns for col in ["genres", "cast", "vote_average"]):
        raise KeyError("Required columns for search are missing")
    return df.loc[
        df["genres"].str.contains("Science Fiction", na=False)
        & df["genres"].str.contains("Action", na=False)
        & df["cast"].str.contains("Bruce Willis", na=False)
    ].sort_values(by="vote_average", ascending=False).reset_index(drop=True)


def search_uma_thurman_quentin_tarantino(df: pd.DataFrame) -> pd.DataFrame:
    """Search for movies starring Uma Thurman, directed by Quentin Tarantino, sorted by runtime."""
    if not all(col in df.columns for col in ["cast", "director", "runtime"]):
        raise KeyError("Required columns for search are missing")
    return df.loc[
        df["cast"].str.contains("Uma Thurman", na=False)
        & (df["director"] == "Quentin Tarantino")
    ].sort_values(by="runtime", ascending=True).reset_index(drop=True)


def summarize_franchise_performance(df: pd.DataFrame) -> pd.DataFrame:
    """Summarize franchise metrics."""
    return (
        df.groupby("belongs_to_collection", dropna=False)
        .agg(
            movie_count=("id", "size"),
            total_budget=("budget_musd", "sum"),
            mean_budget=("budget_musd", "mean"),
            total_revenue=("revenue_musd", "sum"),
            mean_revenue=("revenue_musd", "mean"),
            mean_rating=("vote_average", "mean"),
        )
        .reset_index().sort_values(by="mean_rating", ascending=False)
    )


def summarize_director_performance(df: pd.DataFrame) -> pd.DataFrame:
    """Summarize director metrics."""
    return (
        df.groupby("director", dropna=False)
        .agg(
            movie_count=("id", "size"),
            total_revenue=("revenue_musd", "sum"),
            mean_rating=("vote_average", "mean"),
        )
        .reset_index()
    )
