import json
import pytest
import respx

from football_news.fetchers.guardian_fetcher import GuardianFetcher
from dotenv import load_dotenv

load_dotenv()
with open("tests/data/guardian_sample.json") as f:
    fixture_json = json.load(f)


@pytest.mark.asyncio
@respx.mock
async def test_guardian(monkeypatch):
    monkeypatch.setenv("GUARDIAN_KEY", "dummy")  # Set environment variable for test
    cfg = {
        "name": "guardian",
        "endpoint": "https://content.guardianapis.com/search?section=football&show-fields=body&api-key={api_key}",  # Changed to {api_key}
        "quota_day": 500,
        "quota_sec": 1,
    }

    respx.get("https://content.guardianapis.com/search").respond(200, json=fixture_json)
    n = await GuardianFetcher(cfg).fetch()
    assert n == len(fixture_json["response"]["results"])
