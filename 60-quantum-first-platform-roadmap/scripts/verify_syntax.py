from __future__ import annotations

import ast
from pathlib import Path


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    files = sorted((*root.joinpath("src").rglob("*.py"), *root.joinpath("scripts").rglob("*.py"), *root.joinpath("tests").rglob("*.py")))
    for path in files:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    print({"python_files_compiled": len(files), "mode": "in_memory"})


if __name__ == "__main__":
    main()
