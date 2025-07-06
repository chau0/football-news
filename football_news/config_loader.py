from pathlib import Path
import os
import yaml
from typing import List, Dict, Any


def load_json_cfg(path: str | Path = "config/json.yml") -> List[Dict[str, Any]]:
    path = Path(path)
    with path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}
    sources = raw.get("json_sources", [])
    for s in sources:
        if isinstance(s.get("endpoint"), str):
            s["endpoint"] = os.path.expandvars(s["endpoint"])
        # Also expand environment variables in api_key field
        if isinstance(s.get("api_key"), str):
            s["api_key"] = os.path.expandvars(s["api_key"])
    return sources


def load_html_cfg(path: str | Path = "config/html.yml") -> List[Dict[str, Any]]:
    path = Path(path)
    with path.open("r", encoding="utf-8") as f:
        raw = yaml.safe_load(f) or {}
    return raw.get("html_sources", [])
