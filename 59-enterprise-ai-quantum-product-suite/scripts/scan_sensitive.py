from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = (
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"(?i)(?:api[_-]?key|client[_-]?secret)\s*[:=]\s*['\"][^'\"]+"),
)
EXCLUDED = {".git", ".venv", "node_modules", ".next", "test-results", "playwright-report"}


def main() -> None:
    findings: list[str] = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or any(part in EXCLUDED for part in path.parts):
            continue
        if path.suffix.lower() not in {".py", ".ts", ".tsx", ".json", ".md", ".yaml", ".yml", ".ps1"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        if any(pattern.search(text) for pattern in PATTERNS):
            findings.append(str(path.relative_to(ROOT)))
    if findings:
        raise SystemExit(f"sensitive material patterns found: {findings}")
    print({"files_scanned": sum(1 for path in ROOT.rglob("*") if path.is_file()), "findings": 0})


if __name__ == "__main__":
    main()
