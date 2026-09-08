from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_DIRECTORY = PROJECT_ROOT / "data" / "raw"

PROCESSED_DIRECTORY = PROJECT_ROOT / "data" / "processed"
PROCESSED_INDEX = PROCESSED_DIRECTORY / "index.pkl"

DATASETS_DIRECTORY = PROJECT_ROOT / "data" / "datasets"
OUTPUT_DIRECTORY = PROJECT_ROOT / "data" / "output"


BM25_K1 = 1.5
BM25_B = 0.75
