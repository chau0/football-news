import json
import pytest
import respx

from football_news.fetchers.guardian_fetcher import GuardianFetcher

fixture_json = json.load(open("tests/data/guardian_sample.json"))


@pytest.mark.asyncio
@respx.mock
async def test_guardian(monkeypatch):
    monkeypatch.setenv("GUARDIAN_KEY", "dummy")
    cfg = {
        "name": "guardian",
        "endpoint": "https://content.guardianapis.com/search?section=football&show-fields=body&api-key=${GUARDIAN_KEY}",
        "quota_day": 500,
        "quota_sec": 1,
    }

    respx.get("https://content.guardianapis.com/").respond(200, json=fixture_json)
    n = await GuardianFetcher(cfg).fetch()
    assert n == len(fixture_json["response"]["results"])
