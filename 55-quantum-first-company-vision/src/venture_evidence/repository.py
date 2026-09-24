"""Local data boundary. No remote retrieval or cross-project state at runtime."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

from venture_evidence.models import Corpus, Protocol

ROOT = Path(os.getenv("VENTURE_ROOT", Path(__file__).resolve().parents[2])).resolve()


def load_corpus(root: Path = ROOT) -> Corpus:
    return Corpus.model_validate_json((root / "data/evidence/corpus.v1.json").read_text(encoding="utf-8"))


def load_protocol(root: Path = ROOT) -> Protocol:
    return Protocol.model_validate_json((root / "data/opportunities/protocol.v1.json").read_text(encoding="utf-8"))


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
