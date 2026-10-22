"""GitHub API client used to fetch repository metadata and tree data."""

from __future__ import annotations

from urllib.parse import urlparse

import httpx


class GitHubAPIError(RuntimeError):
    """Raised when the GitHub API is unavailable or returns an error."""


class GitHubClient:
    """Thin wrapper around the GitHub REST API."""

    def __init__(self, token: str | None = None, timeout: float = 15.0):
        self.timeout = timeout
        self.token = token
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github+json",
            "User-Agent": "ai-devops-repo-analyzer",
        }
        if token:
            self.headers["Authorization"] = f"Bearer {token}"

    @staticmethod
    def validate_repository_url(repository_url: str) -> tuple[str, str]:
        """Parse and validate a repository URL, returning (owner, repo)."""
        parsed = urlparse(repository_url)

        if parsed.scheme not in {"http", "https"}:
            raise ValueError("Repository URL must use http or https.")

        if parsed.netloc.lower().replace("www.", "") != "github.com":
            raise ValueError("Only public GitHub URLs are supported.")

        path = parsed.path.strip("/")
        if not path:
            raise ValueError("Repository URL must include an owner and repository name.")

        segments = [segment for segment in path.split("/") if segment]
        if len(segments) != 2:
            raise ValueError(
                "Repository URL must follow the format https://github.com/owner/repository"
            )

        owner, repo_name = segments
        repo_name = repo_name.removesuffix(".git")

        if not owner or not repo_name:
            raise ValueError("Repository URL must include a valid owner and repository name.")

        return owner, repo_name

    async def get_repository(self, owner: str, repo_name: str) -> dict:
        """Return repository metadata for a given owner and repository."""
        url = f"{self.base_url}/repos/{owner}/{repo_name}"
        return await self._request("GET", url)

    async def get_repository_tree(self, owner: str, repo_name: str, branch: str) -> list[dict]:
        """Return the recursive file tree for a repository branch."""
        url = f"{self.base_url}/repos/{owner}/{repo_name}/git/trees/{branch}?recursive=1"
        payload = await self._request("GET", url)
        return payload.get("tree", [])

    async def _request(self, method: str, url: str) -> dict:
        """Perform a GitHub REST request with simple error handling."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request(method, url, headers=self.headers)
        except httpx.RequestError as exc:  # pragma: no cover - network failure path
            raise GitHubAPIError(f"Failed to reach GitHub API: {exc}") from exc

        if response.status_code == 404:
            raise GitHubAPIError("Repository not found or is inaccessible.")
        if response.status_code == 403:
            raise GitHubAPIError("GitHub API rate limit or access issue.")
        if response.status_code >= 400:
            raise GitHubAPIError(f"GitHub API request failed with status {response.status_code}.")

        return response.json()
