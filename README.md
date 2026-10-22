# AI DevOps Repo Analyzer

AI DevOps Repo Analyzer is a Python FastAPI project that inspects public GitHub repositories, identifies obvious technology stacks, and prepares the groundwork for later architecture and DevOps analysis.

## Project goal

This project accepts a public GitHub repository URL, validates it, and prepares to analyze repository structure, files, configuration, and evidence. The initial stage focuses on a working API skeleton and a passing health check.

## Tech stack

- Python 3.11+
- FastAPI
- Uvicorn
- Pydantic
- HTTPX
- Pytest

## Repository structure

```text
ai-devops-repo-analyzer/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── services/
│   │   └── __init__.py
│   └── models/
│       └── __init__.py
├── tests/
│   └── test_health.py
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
└── .venv/
```

## Windows PowerShell setup

```powershell
cd path\to\ai-devops-repo-analyzer
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## Run the app

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Then open:

- http://localhost:8000/health

## Run tests

```powershell
pytest
```

## Example health response

```json
{
  "status": "ok",
  "service": "ai-devops-repo-analyzer",
  "message": "API is running"
}
```

## Notes

- This is Stage 1 only.
- The project is intentionally simple and modular.
- Later stages will add GitHub validation, repository scanning, technology detection, and report generation.
