"""Request models for repository analysis inputs."""

from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, field_validator


class RepositoryAnalysisRequest(BaseModel):
    """Request payload for repository analysis."""

    repository_url: str

    model_config = ConfigDict(extra="forbid")

    @field_validator("repository_url")
    @classmethod
    def validate_repository_url(cls, value: str) -> str:
        """Ensure the input is a valid public GitHub repository URL."""
        parsed = urlparse(value)

        if parsed.scheme not in {"http", "https"}:
            raise ValueError("Repository URL must use http or https.")

        if parsed.netloc.lower().replace("www.", "") not in {"github.com"}:
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

        return value
