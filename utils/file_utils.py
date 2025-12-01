# utils/file_utils.py
import json
from typing import Any
from pathlib import Path

def read_json_file(path: str) -> Any:
    """
    Read JSON using utf-8-sig to tolerate a BOM if present.
    Raises FileNotFoundError if missing.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Expected JSON file at {path} but not found.")
    # use utf-8-sig to silently strip BOM if it exists
    with p.open("r", encoding="utf-8-sig") as f:
        return json.load(f)

def write_json_file(path: str, data: Any) -> None:
    """
    Write JSON using utf-8 (no BOM). Ensures parent dir exists.
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
