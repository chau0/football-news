from pydantic import BaseModel
from pathlib import Path
import yaml
from typing import List, Union


class Feed(BaseModel):
    name: str
    url: str
    ttl_minutes: int = 15


def load_feeds(path: Union[str, Path] = "config/rss.yml") -> List[Feed]:
    """Load RSS feeds from YAML configuration file."""
    config_path = Path(path)

    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path, "r", encoding="utf-8") as file:
        data = yaml.safe_load(file)

    # Handle both nested structure (feeds: [...]) and flat structure ([...])
    if isinstance(data, dict) and "feeds" in data:
        feeds_data = data["feeds"]
    elif isinstance(data, list):
        feeds_data = data
    else:
        raise ValueError(
            "Configuration file must contain either a list of feeds or a 'feeds' key with a list of feeds"
        )

    if not isinstance(feeds_data, list):
        raise ValueError("Feeds data must be a list")

    return [Feed(**feed) for feed in feeds_data]
