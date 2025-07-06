from fastapi.testclient import TestClient
from football_news.api.main import app

client = TestClient(app)


def test_list_endpoint():
    r = client.get("/v1/news?limit=1")
    assert r.status_code == 200
    assert isinstance(r.json(), list)
