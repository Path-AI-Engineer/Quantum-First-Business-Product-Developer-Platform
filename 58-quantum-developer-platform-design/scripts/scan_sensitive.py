import re
from pathlib import Path

root = Path(__file__).parents[1]
patterns = [
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"(?i)(?:password|secret|token)\s*=\s*['\"][^'\"]{12,}['\"]"),
]
files = [
    path
    for path in root.rglob("*")
    if path.is_file() and not any(part in {".venv", "node_modules", ".next", ".git"} for part in path.parts)
]
hits: list[str] = []
for path in files:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue
    if any(pattern.search(text) for pattern in patterns):
        hits.append(str(path.relative_to(root)))
if hits:
    raise SystemExit(f"Sensitive patterns found: {hits}")
print({"files_scanned": len(files), "sensitive_matches": 0})
