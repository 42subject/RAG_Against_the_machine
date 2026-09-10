from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_DIRECTORY = PROJECT_ROOT / "data" / "raw"

PROCESSED_DIRECTORY = PROJECT_ROOT / "data" / "processed"
INDEX_FILE = PROCESSED_DIRECTORY / "index.pkl"

DATASETS_DIRECTORY = PROJECT_ROOT / "data" / "datasets"
OUTPUT_DIRECTORY = PROJECT_ROOT / "data" / "output"

MODEL = "Qwen/Qwen3-0.6B"
MAX_NEW_TOKENS = 100

BM25_K1 = 1.5
BM25_B = 0.75

IOU_BORDER = 0.05
