"""Content-addressed local storage for generated synthetic reports only."""

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

MAX_REPORT_BYTES = 2_000_000


class ObjectStore:
    def __init__(self, root: Path) -> None:
        self.root = root.resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def put_report(self, report: dict[str, Any]) -> str:
        if report.get("synthetic") is not True:
            raise ValueError("only synthetic reports can be stored")
        data = (json.dumps(report, sort_keys=True, separators=(",", ":")) + "\n").encode()
        if len(data) > MAX_REPORT_BYTES:
            raise ValueError("report is oversized")
        digest = hashlib.sha256(data).hexdigest()
        destination = self.root / f"{digest}.json"
        if not destination.exists():
            with tempfile.NamedTemporaryFile(mode="wb", dir=self.root, prefix="candidate-", delete=False) as stream:
                temporary = Path(stream.name)
                stream.write(data)
            try:
                os.replace(temporary, destination)
            finally:
                temporary.unlink(missing_ok=True)
        return digest

    def read_report(self, digest: str) -> dict[str, Any]:
        if len(digest) != 64 or any(character not in "0123456789abcdef" for character in digest):
            raise ValueError("invalid object digest")
        data = (self.root / f"{digest}.json").read_bytes()
        if hashlib.sha256(data).hexdigest() != digest:
            raise ValueError("object digest mismatch")
        result = json.loads(data)
        if not isinstance(result, dict) or result.get("synthetic") is not True:
            raise ValueError("invalid report object")
        return result
