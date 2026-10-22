"""Technology detection for repository analysis with evidence-backed findings."""

from __future__ import annotations

from app.services.evidence_collector import EvidenceCollector


class TechnologyDetector:
    """Identify technologies, libraries, and infrastructure using repository evidence."""

    def detect_technologies(self, tree: list[dict], file_contents: dict[str, str] | None = None) -> list[dict]:
        """Return a list of evidence-backed technology findings."""
        file_contents = file_contents or {}
        file_paths = {item.get("path", "") for item in tree if isinstance(item, dict)}
        normalized_paths = {path for path in file_paths if path}
        combined_text = "\n".join(file_contents.values()).lower()

        findings: list[dict] = []

        python_manifests = {"requirements.txt", "pyproject.toml", "Pipfile", "setup.py"}
        if normalized_paths & python_manifests or any(path.endswith(".py") for path in normalized_paths):
            python_evidence = EvidenceCollector.collect_manifest_matches(normalized_paths, python_manifests)
            python_text_matches = EvidenceCollector.collect_matches(
                normalized_paths,
                file_contents,
                {
                    "FastAPI": "fastapi",
                    "Django": "django",
                    "Flask": "flask",
                },
            )
            python_evidence.extend(python_text_matches)
            if python_evidence:
                findings.append(
                    {
                        "technology": "Python",
                        "category": "language",
                        "confidence": "high",
                        "evidence": python_evidence[:10],
                    }
                )

            if "fastapi" in combined_text or "FastAPI" in combined_text:
                findings.append(
                    {
                        "technology": "FastAPI",
                        "category": "backend_framework",
                        "confidence": "high",
                        "evidence": EvidenceCollector.collect_matches(
                            normalized_paths,
                            file_contents,
                            {"FastAPI import": "fastapi", "FastAPI app": "FastAPI"},
                        )[:10],
                    }
                )
            if "django" in combined_text:
                findings.append(
                    {
                        "technology": "Django",
                        "category": "backend_framework",
                        "confidence": "high",
                        "evidence": EvidenceCollector.collect_matches(
                            normalized_paths,
                            file_contents,
                            {"Django config": "django"},
                        )[:10],
                    }
                )
            if "flask" in combined_text:
                findings.append(
                    {
                        "technology": "Flask",
                        "category": "backend_framework",
                        "confidence": "high",
                        "evidence": EvidenceCollector.collect_matches(
                            normalized_paths,
                            file_contents,
                            {"Flask import": "flask"},
                        )[:10],
                    }
                )

        java_manifests = {"pom.xml", "build.gradle", "build.gradle.kts"}
        if normalized_paths & java_manifests or any("src/main/java" in path for path in normalized_paths):
            java_evidence = EvidenceCollector.collect_manifest_matches(normalized_paths, java_manifests)
            java_evidence.extend(
                EvidenceCollector.collect_matches(
                    normalized_paths,
                    file_contents,
                    {
                        "Spring Boot": "@SpringBootApplication",
                        "Spring Boot": "spring-boot",
                        "Spring MVC": "@RestController",
                        "Spring MVC": "@GetMapping",
                        "Spring MVC": "@PostMapping",
                    },
                )
            )
            if java_evidence:
                findings.append(
                    {
                        "technology": "Java",
                        "category": "language",
                        "confidence": "medium",
                        "evidence": java_evidence[:10],
                    }
                )
                if "@springbootapplication" in combined_text or "spring-boot" in combined_text:
                    findings.append(
                        {
                            "technology": "Spring Boot",
                            "category": "backend_framework",
                            "confidence": "high",
                            "evidence": EvidenceCollector.collect_matches(
                                normalized_paths,
                                file_contents,
                                {"Spring Boot app": "@SpringBootApplication", "Spring Boot app": "spring-boot"},
                            )[:10],
                        }
                    )

        dotnet_manifests = {".csproj", ".sln"}
        if any(path.endswith(tuple(dotnet_manifests)) for path in normalized_paths) or any(path.endswith(".cs") for path in normalized_paths):
            dotnet_evidence = [
                {"file": path, "reason": "C# project manifest indicates .NET usage."}
                for path in sorted(normalized_paths)
                if path.endswith(tuple(dotnet_manifests))
            ]
            dotnet_evidence.extend(
                EvidenceCollector.collect_matches(
                    normalized_paths,
                    file_contents,
                    {
                        "ASP.NET Core": "WebApplication",
                        "ASP.NET Core": "MapGet",
                        "ASP.NET Core": "UseRouting",
                        "ASP.NET Core": "Startup",
                    },
                )
            )
            if dotnet_evidence:
                findings.append(
                    {
                        "technology": ".NET",
                        "category": "backend_framework",
                        "confidence": "medium",
                        "evidence": dotnet_evidence[:10],
                    }
                )

        js_manifests = {"package.json", "package-lock.json", "pnpm-lock.yaml", "vite.config.js", "vite.config.ts"}
        if normalized_paths & js_manifests or any(path.endswith((".js", ".jsx", ".ts", ".tsx")) for path in normalized_paths):
            js_evidence = EvidenceCollector.collect_manifest_matches(normalized_paths, js_manifests)
            js_evidence.extend(
                EvidenceCollector.collect_matches(
                    normalized_paths,
                    file_contents,
                    {
                        "React": "react",
                        "Angular": "@angular",
                        "Vue": "vue",
                        "Express": "express",
                        "NestJS": "@nestjs",
                        "Vite": "vite",
                    },
                )
            )
            if js_evidence:
                findings.append(
                    {
                        "technology": "JavaScript/TypeScript",
                        "category": "language",
                        "confidence": "high",
                        "evidence": js_evidence[:10],
                    }
                )
                if "react" in combined_text:
                    findings.append(
                        {
                            "technology": "React",
                            "category": "frontend_framework",
                            "confidence": "high",
                            "evidence": EvidenceCollector.collect_matches(
                                normalized_paths,
                                file_contents,
                                {"React": "react"},
                            )[:10],
                        }
                    )
                if "express" in combined_text:
                    findings.append(
                        {
                            "technology": "Express",
                            "category": "backend_framework",
                            "confidence": "high",
                            "evidence": EvidenceCollector.collect_matches(
                                normalized_paths,
                                file_contents,
                                {"Express": "express"},
                            )[:10],
                        }
                    )

        infra_paths = {"Dockerfile", "docker-compose.yml", "docker-compose.yaml", ".github/workflows"}
        if normalized_paths & {"Dockerfile", "docker-compose.yml", "docker-compose.yaml"} or any(path.startswith(".github/") for path in normalized_paths):
            infra_evidence = [
                {"file": path, "reason": "Infrastructure or deployment file found."}
                for path in sorted(normalized_paths)
                if path in {"Dockerfile", "docker-compose.yml", "docker-compose.yaml"} or path.startswith(".github/")
            ]
            if infra_evidence:
                findings.append(
                    {
                        "technology": "Docker / CI-CD",
                        "category": "infrastructure",
                        "confidence": "medium",
                        "evidence": infra_evidence[:10],
                    }
                )

        database_signals = {
            "PostgreSQL": "postgresql",
            "MySQL": "mysql",
            "MongoDB": "mongodb",
            "Redis": "redis",
            "Kafka": "kafka",
            "RabbitMQ": "rabbitmq",
        }
        database_matches = EvidenceCollector.collect_matches(normalized_paths, file_contents, database_signals)
        if database_matches:
            for tech_name, signal_text in database_signals.items():
                if any(match["file"] for match in database_matches if tech_name.lower() in signal_text.lower()):
                    pass

            findings.append(
                {
                    "technology": "Database / Messaging Signals",
                    "category": "data_integration",
                    "confidence": "medium",
                    "evidence": database_matches[:10],
                }
            )

        return findings
