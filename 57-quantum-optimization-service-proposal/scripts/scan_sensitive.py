from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = {
    "private_key": re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    "aws_access_key": re.compile(r"AKIA[0-9A-Z]{16}"),
    "generic_secret": re.compile(r"(?i)(?:api[_-]?key|client[_-]?secret|password)\s*[:=]\s*['\"][^'\"]{8,}"),
}
SKIP = {".git", ".venv", "node_modules", ".next", "test-results"}
files = [
    path
    for path in ROOT.rglob("*")
    if path.is_file()
    and not set(path.relative_to(ROOT).parts) & SKIP
    and path.suffix.lower() not in {".png", ".zip", ".pyc"}
]
failures: list[str] = []
for path in files:
    text = path.read_text(encoding="utf-8", errors="ignore")
    for label, pattern in PATTERNS.items():
        if pattern.search(text):
            failures.append(f"{path.relative_to(ROOT).as_posix()}: {label}")
if failures:
    raise SystemExit("Sensitive-pattern scan failed:\n" + "\n".join(failures))
print(f"Sensitive-pattern scan passed: {len(files)} source files")
