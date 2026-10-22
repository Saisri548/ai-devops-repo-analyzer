"""Simple evidence collection utilities for repository tech detection."""

from __future__ import annotations


class EvidenceCollector:
    """Collect evidence for repository findings from file paths and file contents."""

    @staticmethod
    def collect_matches(file_paths: set[str], file_contents: dict[str, str], signals: dict[str, str]) -> list[dict]:
        """Create evidence entries for file paths that match known signals."""
        findings: list[dict] = []

        for file_path in sorted(file_paths):
            text = file_contents.get(file_path, "")
            normalized_text = text.lower()
            for signal_name, signal_text in signals.items():
                lowered_signal = signal_text.lower()
                if lowered_signal in normalized_text:
                    findings.append(
                        {
                            "file": file_path,
                            "reason": f"{signal_name} is referenced in the file content.",
                        }
                    )

        return findings

    @staticmethod
    def collect_manifest_matches(file_paths: set[str], manifests: set[str]) -> list[dict]:
        """Collect evidence from any well-known file-level manifest names."""
        matches: list[dict] = []
        for manifest_name in sorted(manifests):
            if manifest_name in file_paths:
                matches.append(
                    {
                        "file": manifest_name,
                        "reason": "Manifest file indicates the technology stack.",
                    }
                )
        return matches
