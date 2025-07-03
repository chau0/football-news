import pytest
import tempfile
import yaml
from pathlib import Path
from pydantic import ValidationError

from football_news.config import Feed, load_feeds


class TestLoadFeeds:
    def test_load_feeds_success(self):
        """Test successful loading of valid RSS feeds."""
        feeds_data = [
            {
                "name": "ESPN Football",
                "url": "https://www.espn.com/rss",
                "ttl_minutes": 15,
            },
            {
                "name": "BBC Sport",
                "url": "https://feeds.bbci.co.uk/sport/rss.xml",
                "ttl_minutes": 10,
            },
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            yaml.dump(feeds_data, f)
            temp_path = f.name

        try:
            feeds = load_feeds(temp_path)
            assert len(feeds) == 2
            assert feeds[0].name == "ESPN Football"
            assert str(feeds[0].url) == "https://www.espn.com/rss"
            assert feeds[0].ttl_minutes == 15
            assert feeds[1].name == "BBC Sport"
            assert feeds[1].ttl_minutes == 10
        finally:
            Path(temp_path).unlink()

    def test_load_feeds_with_defaults(self):
        """Test loading feeds with default ttl_minutes."""
        feeds_data = [{"name": "Test Feed", "url": "https://example.com/rss"}]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            yaml.dump(feeds_data, f)
            temp_path = f.name

        try:
            feeds = load_feeds(temp_path)
            assert len(feeds) == 1
            assert feeds[0].ttl_minutes == 15  # default value
        finally:
            Path(temp_path).unlink()

    def test_load_feeds_file_not_found(self):
        """Test error handling when configuration file doesn't exist."""
        with pytest.raises(FileNotFoundError, match="Configuration file not found"):
            load_feeds("nonexistent/path.yml")

    def test_load_feeds_invalid_url(self):
        """Test validation error for invalid URLs."""
        feeds_data = [
            {"name": "Invalid Feed", "url": "not-a-valid-url", "ttl_minutes": 15}
        ]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            yaml.dump(feeds_data, f)
            temp_path = f.name

        try:
            with pytest.raises(ValidationError):
                load_feeds(temp_path)
        finally:
            Path(temp_path).unlink()

    def test_load_feeds_missing_required_fields(self):
        """Test validation error for missing required fields."""
        feeds_data = [{"url": "https://example.com/rss"}]  # missing name

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            yaml.dump(feeds_data, f)
            temp_path = f.name

        try:
            with pytest.raises(ValidationError):
                load_feeds(temp_path)
        finally:
            Path(temp_path).unlink()

    def test_load_feeds_empty_list(self):
        """Test loading empty feed list."""
        feeds_data = []

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            yaml.dump(feeds_data, f)
            temp_path = f.name

        try:
            feeds = load_feeds(temp_path)
            assert len(feeds) == 0
        finally:
            Path(temp_path).unlink()

    def test_load_feeds_pathlib_path(self):
        """Test loading feeds using pathlib.Path object."""
        feeds_data = [{"name": "Test Feed", "url": "https://example.com/rss"}]

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
            yaml.dump(feeds_data, f)
            temp_path = Path(f.name)

        try:
            feeds = load_feeds(temp_path)
            assert len(feeds) == 1
            assert feeds[0].name == "Test Feed"
        finally:
            temp_path.unlink()


class TestFeedModel:
    def test_feed_model_validation(self):
        """Test Feed model validation."""
        feed = Feed(name="Test Feed", url="https://example.com/rss", ttl_minutes=30)
        assert feed.name == "Test Feed"
        assert str(feed.url) == "https://example.com/rss"
        assert feed.ttl_minutes == 30

    def test_feed_model_defaults(self):
        """Test Feed model with default values."""
        feed = Feed(name="Test Feed", url="https://example.com/rss")
        assert feed.ttl_minutes == 15

    def test_feed_model_invalid_url(self):
        """Test Feed model with invalid URL."""
        with pytest.raises(ValidationError):
            Feed(name="Test Feed", url="invalid-url")
