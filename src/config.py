from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

RAW_DIRECTORY = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIRECTORY = PROJECT_ROOT / "data" / "processed"

DATASETS_DIRECTORY = PROJECT_ROOT / "data" / "datasets"
OUTPUT_DIRECTORY = PROJECT_ROOT / "data" / "output"
