"""Pattern-based guard for common secret/PII material in bundle source inputs."""

import re
from pathlib import Path

from build_bundle import ROOT, inputs

PATTERNS = {
    "private-key PEM": re.compile(rb"-----BEGIN(?: [A-Z]+)? PRIVATE KEY-----"),
    "AWS access key": re.compile(rb"\bAKIA[0-9A-Z]{16}\b"),
    "bearer-like token": re.compile(rb"\bsk-[A-Za-z0-9]{20,}\b"),
    "email address": re.compile(rb"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
}


def main() -> None:
    failures: list[str] = []
    for relative in inputs():
        path = ROOT / Path(relative)
        data = path.read_bytes()
        for label, pattern in PATTERNS.items():
            if pattern.search(data):
                failures.append(f"{relative}: {label}")
    if failures:
        raise SystemExit("Sensitive-pattern scan failed:\n" + "\n".join(failures))
    print(f"Sensitive-pattern scan passed: {len(inputs())} source files")


if __name__ == "__main__":
    main()
