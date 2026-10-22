"""Tests for GitHub URL validation and mocked GitHub client behavior."""

from __future__ import annotations

import asyncio

import httpx

from app.services.github_client import GitHubAPIError, GitHubClient
from app.services.repository_scanner import RepositoryScanner


class FakeResponse:
    """Minimal response object for mocked API calls."""

    def __init__(self, payload: dict, status_code: int = 200):
        self._payload = payload
        self.status_code = status_code

    def json(self) -> dict:
        return self._payload

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise httpx.HTTPStatusError(
                "Request failed",
                request=httpx.Request("GET", "https://api.github.com"),
                response=httpx.Response(self.status_code, request=httpx.Request("GET", "https://api.github.com")),
            )


class FakeAsyncClient:
    """Fake HTTP client used to simulate GitHub API responses."""

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc, tb):
        return False

    async def request(self, method: str, url: str, headers: dict | None = None):
        if url.endswith("/repos/octo/demo"):
            return FakeResponse(
                {
                    "full_name": "octo/demo",
                    "default_branch": "main",
                    "private": False,
                }
            )

        if url.endswith("/repos/octo/demo/git/trees/main?recursive=1"):
            return FakeResponse({
                "tree": [
                    {"path": "README.md", "type": "blob"},
                    {"path": "app/main.py", "type": "blob"},
                ]
            })

        if url.endswith("/repos/missing/repo"):
            return FakeResponse({"message": "Not Found"}, status_code=404)

        if url.endswith("/repos/rate-limited/repo"):
            return FakeResponse({"message": "API rate limit exceeded"}, status_code=403)

        return FakeResponse({"message": "ok"})


def test_valid_github_urls_are_accepted() -> None:
    valid_urls = [
        "https://github.com/octo/demo",
        "http://github.com/octo/demo",
        "https://github.com/octo/demo.git",
    ]

    for value in valid_urls:
        owner, repo = GitHubClient.validate_repository_url(value)
        assert owner == "octo"
        assert repo == "demo"


def test_invalid_github_urls_raise_value_error() -> None:
    invalid_urls = [
        "https://example.com/octo/demo",
        "https://github.com/octo",
        "not-a-url",
        "https://github.com/octo/demo/extra",
    ]

    for value in invalid_urls:
        try:
            GitHubClient.validate_repository_url(value)
            raise AssertionError(f"Expected validation to fail for {value!r}")
        except ValueError:
            pass


def test_repository_scanner_fetches_metadata_and_tree(monkeypatch) -> None:
    monkeypatch.setattr("app.services.github_client.httpx.AsyncClient", FakeAsyncClient)

    async def run_scanner() -> dict:
        scanner = RepositoryScanner()
        return await scanner.analyze_repository("https://github.com/octo/demo")

    result = asyncio.run(run_scanner())

    assert result["owner"] == "octo"
    assert result["repository"] == "demo"
    assert result["default_branch"] == "main"
    assert result["tree"][0]["path"] == "README.md"


def test_github_client_raises_for_missing_and_rate_limited_repositories(monkeypatch) -> None:
    monkeypatch.setattr("app.services.github_client.httpx.AsyncClient", FakeAsyncClient)
    client = GitHubClient()

    async def run_missing() -> None:
        await client.get_repository("missing", "repo")

    async def run_limited() -> None:
        await client.get_repository("rate-limited", "repo")

    try:
        asyncio.run(run_missing())
        raise AssertionError("Expected missing repository to raise GitHubAPIError")
    except GitHubAPIError:
        pass

    try:
        asyncio.run(run_limited())
        raise AssertionError("Expected rate-limited request to raise GitHubAPIError")
    except GitHubAPIError:
        pass
