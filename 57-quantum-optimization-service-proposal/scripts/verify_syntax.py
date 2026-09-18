from __future__ import annotations

import ast
from pathlib import Path

root = Path(__file__).resolve().parents[1]
files = sorted((*root.joinpath("src").rglob("*.py"), *root.joinpath("scripts").glob("*.py")))
for file in files:
    ast.parse(file.read_text(encoding="utf-8"), filename=str(file))
print({"python_files_compiled": len(files), "mode": "in_memory"})
