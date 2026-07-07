"""Smoke test: the smallest possible check that the app is not broken.

A "smoke test" comes from electronics - you power on a new board and see if it
smokes. Here we boot the app and hit the health endpoint. If this passes, the
app imports, starts, and responds - so nothing is catastrophically broken.
"""

from fastapi.testclient import TestClient

from app.main import app

# TestClient lets us call our API in-process, without starting a real server.
client = TestClient(app)


def test_health_check_returns_ok():
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
