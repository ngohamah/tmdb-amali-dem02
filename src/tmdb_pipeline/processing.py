"""Data cleaning and transformation utilities for TMDB movie data."""
from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from .config import FINAL_COLUMNS, JSON_COLUMNS, IRRELEVANT_COLUMNS
from .logger_config import configure_logger

logger = configure_logger(__name__)


def flatten_json_field(series: pd.Series) -> pd.Series:
    """Convert JSON-like values to a pipe-separated string."""

    def _normalize(value: Any) -> str:
        if isinstance(value, str):
            return value
        if value is None:
            return np.nan
        if isinstance(value, (list, tuple, set)):
            items = [
                item.get("name") if isinstance(item, dict) and "name" in item else str(item)
                for item in value
            ]
            return "|".join(item for item in items if item)
        if isinstance(value, dict):
            return value.get("name") or ""
        try:
            if pd.isna(value):
                return np.nan
        except TypeError:
            return str(value)
        return str(value) # Fallback for any other type

    return series.apply(_normalize)


def clean_movie_data(payloads: list[dict[str, Any]]) -> pd.DataFrame:
    """Create and clean a movie dataframe from raw payloads."""
    logger.info("Starting data cleaning for %d records", len(payloads))
    df = pd.DataFrame(payloads)

    try:
        df = df.drop(columns=[col for col in IRRELEVANT_COLUMNS if col in df.columns], errors="ignore")
        for column in JSON_COLUMNS:
            if column in df.columns:
                df[column] = flatten_json_field(df[column])

        df["budget"] = pd.to_numeric(df.get("budget"), errors="coerce")
        df["id"] = pd.to_numeric(df.get("id"), errors="coerce")
        df["popularity"] = pd.to_numeric(df.get("popularity"), errors="coerce")
        df["release_date"] = pd.to_datetime(df.get("release_date"), errors="coerce")
        df["revenue"] = pd.to_numeric(df.get("revenue"), errors="coerce")
        df["runtime"] = pd.to_numeric(df.get("runtime"), errors="coerce")
        df["vote_count"] = pd.to_numeric(df.get("vote_count"), errors="coerce")
        df["vote_average"] = pd.to_numeric(df.get("vote_average"), errors="coerce")

        df["budget"] = df["budget"].replace(0, np.nan) # business logic: 0 budget is likely missing data, not a real value
        df["revenue"] = df["revenue"].replace(0, np.nan)
        df["runtime"] = df["runtime"].replace(0, np.nan)
        df["overview"] = df["overview"].replace({"No Data": np.nan, "": np.nan})
        df["tagline"] = df["tagline"].replace({"No Data": np.nan, "": np.nan})

        df["budget_musd"] = df["budget"] / 1_000_000
        df["revenue_musd"] = df["revenue"] / 1_000_000
        df["profit_musd"] = df["revenue_musd"] - df["budget_musd"]
        df["roi"] = df["revenue_musd"] / df["budget_musd"].replace(0, np.nan)

        df = df.drop_duplicates(subset=["id"]).copy()
        df = df.dropna(subset=["id", "title"], how="any")
        df = df.loc[df.isna().sum(axis=1) <= (len(df.columns) - 10)]
        status_series = df["status"] if "status" in df.columns else pd.Series(["Released"] * len(df), index=df.index)
        df = df.loc[status_series == "Released"].copy()    # copy() SettingWithCopyWarning avoidance 
        df = df.drop(columns=["status"], errors="ignore")

        df["cast"] = df.get("cast", pd.Series([np.nan] * len(df), index=df.index))
        df["cast_size"] = df.get("cast_size", pd.Series([np.nan] * len(df), index=df.index))
        df["director"] = df.get("director", pd.Series([np.nan] * len(df), index=df.index))
        df["crew_size"] = df.get("crew_size", pd.Series([np.nan] * len(df), index=df.index))

        columns = [col for col in FINAL_COLUMNS if col in df.columns]
        df = df.loc[:, columns]
        df = df.reset_index(drop=True)
        
        logger.info("Cleaning completed with %d rows", len(df))
        return df
    except Exception:
        logger.exception("Cleaning failed")
        raise
