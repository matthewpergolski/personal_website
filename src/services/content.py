import json
from pathlib import Path
from typing import Any, Dict, Optional


def load_experience(base: Path) -> Optional[Dict[str, Any]]:
    """Load experience data from data/experience.json, if present."""
    p = (base / "data" / "experience.json").resolve()
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text())
    except Exception:
        return None
