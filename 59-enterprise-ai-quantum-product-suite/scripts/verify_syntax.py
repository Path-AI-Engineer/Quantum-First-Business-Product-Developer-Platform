from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
files = [path for path in ROOT.rglob("*.py") if ".venv" not in path.parts]
for file in files:
    ast.parse(file.read_text(encoding="utf-8"), filename=str(file))
print({"python_files_compiled": len(files), "mode": "in_memory"})
