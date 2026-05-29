import os
import sys
from pathlib import Path

# Ensure the project root and src are on sys.path for all tests
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

# Set a safe default for BASE_DATA_DIR during tests
os.environ.setdefault("BASE_DATA_DIR", str(ROOT / "tests" / "tmp_data"))
