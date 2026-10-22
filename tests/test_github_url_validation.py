"""Repository scanner for Stage 2 analysis flow."""

from __future__ import annotations

from app.services.github_client import GitHubAPIError, GitHubClient


class RepositoryScanner:
    """Coordinate repository-level metadata fetches for analysis."""

    def __init__(self, github_client: GitHubClient | None = None):
        self.github_client = github_client or GitHubClient()

    async def analyze_repository(self, repository_url: str) -> dict:
        """Fetch metadata and tree for a repository URL."""
        owner, repo_name = GitHubClient.validate_repository_url(repository_url)
        metadata = await self.github_client.get_repository(owner, repo_name)
        default_branch = metadata.get("default_branch", "main")
        tree = await self.github_client.get_repository_tree(owner, repo_name, default_branch)

        return {
            "owner": owner,
            "repository": repo_name,
            "default_branch": default_branch,
            "metadata": metadata,
            "tree": tree,
        }

    async def get_repository_summary(self, repository_url: str) -> dict:
        """Convenience wrapper for scanner calls."""
        try:
            return await self.analyze_repository(repository_url)
        except GitHubAPIError as exc:
            raise ValueError(str(exc)) from exc
