"""Configuration values for the TMDB pipeline."""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
LOG_DIR = BASE_DIR / "logs"
RAW_DATA_PATH = DATA_DIR / "raw_movies.json"
CLEAN_DATA_PATH = DATA_DIR / "clean_movies.csv"
REPORT_PATH = BASE_DIR / "reports" / "movie_analysis_report.md"
PLOTS_DIR = BASE_DIR / "reports" / "plots"
RAW_PAYLOAD_PATH = DATA_DIR / "raw_payloads.json"
SAMPLE_PAYLOAD_PATH = DATA_DIR / "sample_payloads.json"

TMDB_API_KEY = "YOUR_TMDB_API_KEY"
TMDB_API_URL = "https://api.themoviedb.org/3/movie/{movie_id}"

MOVIE_IDS = [
    0, 299534, 19995, 140607, 299536, 597, 135397,
    420818, 24428, 168259, 99861, 284054, 12445,
    181808, 330457, 351286, 109445, 321612, 260513,
]

IRRELEVANT_COLUMNS = [
    "adult", "imdb_id", "original_title", "video", "homepage",
]
JSON_COLUMNS = [
    "belongs_to_collection", "genres", "production_countries",
    "production_companies", "spoken_languages",
]
FINAL_COLUMNS = [
    "id", "title", "tagline", "release_date", "genres", "belongs_to_collection",
    "original_language", "budget_musd", "revenue_musd", "production_companies",
    "production_countries", "vote_count", "vote_average", "popularity", "runtime",
    "overview", "spoken_languages", "poster_path", "cast", "cast_size",
    "director", "crew_size",
]
