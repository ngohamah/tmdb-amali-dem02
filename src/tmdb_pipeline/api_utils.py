"""Utilities for reading TMDB data from the API."""
import json
from pathlib import Path
from typing import Any

import requests

from .config import (
    MOVIE_IDS,
    RAW_PAYLOAD_PATH,
    SAMPLE_PAYLOAD_PATH,
    TMDB_API_KEY,
    TMDB_API_URL,
)
from .logger_config import configure_logger

logger = configure_logger(__name__)

def load_cached_payloads(path: Path | None = None) -> list[dict[str, Any]]:
    """Load payloads from disk if available."""
    payload_path = path or RAW_PAYLOAD_PATH
    if payload_path.exists():
        logger.info("Using cached payloads from %s", payload_path)
        return json.loads(payload_path.read_text(encoding="utf-8"))
    return []


def fetch_movie_payload(session: requests.Session, movie_id: int) -> dict[str, Any]:
    """Fetch one movie payload from the TMDB API."""
    if not TMDB_API_KEY or TMDB_API_KEY == "YOUR_TMDB_API_KEY":
        logger.warning("TMDB API key is not configured; falling back to cached sample data")
        raise ValueError("TMDB API key is not configured")

    url = TMDB_API_URL.format(movie_id=movie_id)
    params = {"api_key": TMDB_API_KEY, "language": "en-US"}

    try:
        response = session.get(url, params=params, timeout=30)
        response.raise_for_status()
        payload = response.json()
        logger.info("Fetched movie %s from TMDB", movie_id)
        return payload
    except requests.RequestException:
        logger.exception("Failed to fetch movie %s", movie_id)
        raise


def fetch_movie_batch(movie_ids: list[int] | None = None) -> list[dict[str, Any]]:
    """Fetch a batch of movie payloads once and return them."""
    ids = movie_ids or MOVIE_IDS
    cached_payloads = load_cached_payloads(RAW_PAYLOAD_PATH)
    if cached_payloads:
        logger.info("Returning cached payloads for %d movies", len(cached_payloads))
        return cached_payloads

    results: list[dict[str, Any]] = []
    with requests.Session() as session:
        for movie_id in ids:
            if movie_id <= 0:
                logger.info("Skipping invalid movie id %s", movie_id)
                continue
            try:
                payload = fetch_movie_payload(session, movie_id)
            except ValueError:
                logger.info("Error Returning %d movies", movie_id)
                return json.loads(SAMPLE_PAYLOAD_PATH.read_text(encoding="utf-8"))
            except requests.RequestException:
                logger.info("Error Returning %d movies", movie_id)
                return json.loads(SAMPLE_PAYLOAD_PATH.read_text(encoding="utf-8"))
            results.append(payload)

    RAW_PAYLOAD_PATH.parent.mkdir(parents=True, exist_ok=True)
    RAW_PAYLOAD_PATH.write_text(json.dumps(results, indent=2), encoding="utf-8")
    logger.info("Completed batch fetch for %d movies", len(results))
    return results
