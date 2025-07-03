from pydantic import BaseModel, HttpUrl
from pathlib import Path
import yaml
from typing import List, Union


class Feed(BaseModel):
    name: str
    url: HttpUrl
    ttl_minutes: int = 15


def load_feeds(path: Union[str, Path] = "config/rss.yml") -> List[Feed]:
    """Load RSS feeds from YAML configuration file."""
    config_path = Path(path)

    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path, "r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    if not isinstance(data, list):
        raise ValueError("Configuration file must contain a list of feeds")

    return [Feed(**feed) for feed in data]
