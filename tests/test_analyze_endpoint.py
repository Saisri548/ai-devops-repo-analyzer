"""Tests for the analyze endpoint."""

from fastapi.testclient import TestClient

from app.main import app
from app.services.repository_scanner import RepositoryScanner

client = TestClient(app)


def test_analyze_endpoint_returns_repository_summary(monkeypatch) -> None:
    """The analyze endpoint should validate the request and return a repository summary."""

    async def fake_analyze(self, repository_url: str) -> dict:
        return {
            "owner": "octo",
            "repository": "demo",
            "default_branch": "main",
            "metadata": {"full_name": "octo/demo", "private": False},
            "tree": [{"path": "README.md", "type": "blob"}],
        }

    monkeypatch.setattr(RepositoryScanner, "analyze_repository", fake_analyze)

    response = client.post(
        "/analyze",
        json={"repository_url": "https://github.com/octo/demo"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "success"
    assert response.json()["result"]["owner"] == "octo"


def test_analyze_endpoint_rejects_invalid_repository_url() -> None:
    """Invalid GitHub URLs should return a 400 response."""
    response = client.post(
        "/analyze",
        json={"repository_url": "https://example.com/octo/demo"},
    )

    assert response.status_code == 400
    assert "Only public GitHub URLs are supported" in response.json()["detail"]
