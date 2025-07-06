import json
import pytest
import respx

from football_news.fetchers.guardian_fetcher import GuardianFetcher

with open("tests/data/guardian_sample.json") as f:
    fixture_json = json.load(f)


@pytest.mark.asyncio
@respx.mock
async def test_guardian(monkeypatch, caplog):
    monkeypatch.setenv("GUARDIAN_KEY", "dummy")
    cfg = {
        "name": "guardian",
        "endpoint": "https://content.guardianapis.com/search?section=football&show-fields=body&api-key=${GUARDIAN_KEY}",
        "quota_day": 500,
        "quota_sec": 1,
    }

    # Use pattern matching for more robust mocking
    respx.get(
        url__regex=r"https://content\.guardianapis\.com/search.*api-key=dummy.*"
    ).respond(200, json=fixture_json)

    print(f"Expected results: {len(fixture_json['response']['results'])}")
    n = await GuardianFetcher(cfg).fetch()
    print(f"Actual results: {n}")

    # Print any captured logs to debug the error
    for record in caplog.records:
        print(f"Log: {record.levelname} - {record.message}")

    assert n == len(fixture_json["response"]["results"])
