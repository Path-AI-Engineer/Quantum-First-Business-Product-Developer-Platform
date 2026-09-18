from pathlib import Path

root = Path(__file__).parents[1]
files = sorted(
    [
        *root.glob("src/**/*.py"),
        *root.glob("tests/**/*.py"),
        *root.glob("scripts/**/*.py"),
        *root.glob("cli/**/*.py"),
        *root.glob("sdks/python/**/*.py"),
    ]
)
for file in files:
    compile(file.read_text(encoding="utf-8"), str(file), "exec")
print({"python_files_compiled": len(files), "mode": "in_memory"})
