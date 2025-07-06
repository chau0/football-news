from pydantic import BaseModel
from pathlib import Path
import yaml
from typing import List, Union
from football_news.utils.logger import logger


class Feed(BaseModel):
    name: str
    url: str
    ttl_minutes: int = 15


def load_feeds(path: Union[str, Path] = "config/rss.yml") -> List[Feed]:
    """Load RSS feeds from YAML configuration file."""
    config_path = Path(path)

    logger.debug(f"Loading feeds configuration from: {config_path}")

    if not config_path.exists():
        logger.error(f"Configuration file not found: {config_path}")
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    try:
        with open(config_path, "r", encoding="utf-8") as file:
            data = yaml.safe_load(file)
        logger.debug("Successfully loaded YAML configuration")
    except yaml.YAMLError as e:
        logger.error(f"Invalid YAML in configuration file: {e}")
        raise
    except Exception as e:
        logger.error(f"Error reading configuration file: {e}")
        raise

    # Handle both nested structure (feeds: [...]) and flat structure ([...])
    if isinstance(data, dict) and "feeds" in data:
        feeds_data = data["feeds"]
    elif isinstance(data, list):
        feeds_data = data
    else:
        logger.error(
            "Configuration file must contain either a list of feeds or a 'feeds' key with a list of feeds"
        )
        raise ValueError(
            "Configuration file must contain either a list of feeds or a 'feeds' key with a list of feeds"
        )

    if not isinstance(feeds_data, list):
        logger.error("Feeds data must be a list")
        raise ValueError("Feeds data must be a list")

    try:
        feeds = [Feed(**feed) for feed in feeds_data]
        logger.info(f"Successfully loaded {len(feeds)} feed configurations")
        return feeds
    except Exception as e:
        logger.error(f"Error validating feed configurations: {e}")
        raise
