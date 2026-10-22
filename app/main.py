"""Main application entry point."""

from fastapi import FastAPI

from app.api.routes import router

app = FastAPI(
    title="AI DevOps Repo Analyzer",
    version="0.1.0",
    description="A repository analyzer for GitHub repositories.",
)

app.include_router(router)

