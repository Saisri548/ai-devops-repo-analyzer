"""API routes for the repository analyzer application."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health() -> dict[str, str]:
    """Return service health information."""
    return {
        "status": "ok",
        "service": "ai-devops-repo-analyzer",
        "message": "API is running",
    }
