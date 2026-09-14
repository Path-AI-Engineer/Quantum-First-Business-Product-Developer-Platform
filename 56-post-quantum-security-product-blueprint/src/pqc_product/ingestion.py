"""Bounded offline importers. Imported records are observations, never active scans."""

import csv
import hashlib
import io
import json
import re
from datetime import UTC, datetime
from typing import Any

from pqc_product.domain import Evidence

MAX_BYTES = 64_000
ALLOWED = frozenset({"cbom", "cyclonedx", "tls_csv", "sarif", "kms_json", "vendor_csv", "vendor_json", "manual"})
FORBIDDEN_KEYS = frozenset({"privatekey", "secret", "password", "accesstoken", "certificatepem", "keymaterial"})
KNOWLEDGE = frozenset({"verified", "inferred", "declared_by_vendor", "conflicting", "unknown", "stale"})
ALGORITHMS = frozenset(
    {"RSA-2048", "ECDSA-P256", "ECDH-P256", "DH-2048", "ML-KEM", "ML-DSA", "SLH-DSA", "AES-256-GCM", "unidentified"}
)
FUNCTIONS = frozenset({"signature", "key_exchange", "key_encapsulation", "encryption", "hashing", "unspecified"})


class ImportRejected(ValueError):
    pass


def _reject_sensitive(value: Any) -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            if re.sub(r"[^a-z0-9]", "", str(key).lower()) in FORBIDDEN_KEYS:
                raise ImportRejected("secret-bearing field is not accepted")
            _reject_sensitive(child)
    elif isinstance(value, list):
        for child in value:
            _reject_sensitive(child)


def _records(source_type: str, payload: bytes) -> list[dict[str, Any]]:
    if source_type not in ALLOWED:
        raise ImportRejected("unsupported source type")
    if not payload or len(payload) > MAX_BYTES:
        raise ImportRejected("empty or oversized import")
    if b"-----BEGIN" in payload.upper() or b"PRIVATE KEY" in payload.upper():
        raise ImportRejected("cryptographic material is not accepted")
    try:
        text = payload.decode("utf-8", errors="strict")
        if source_type.endswith("csv"):
            rows = list(csv.DictReader(io.StringIO(text, newline="")))
            if not rows or len(rows) > 250:
                raise ImportRejected("CSV must contain 1-250 records")
            _reject_sensitive(rows)
            return rows
        parsed = json.loads(text)
    except (UnicodeError, json.JSONDecodeError, csv.Error) as exc:
        raise ImportRejected("malformed import") from exc
    _reject_sensitive(parsed)
    if source_type == "cyclonedx":
        if not isinstance(parsed, dict) or parsed.get("bomFormat") != "CycloneDX":
            raise ImportRejected("invalid CycloneDX marker")
        records = parsed.get("components")
    elif source_type == "sarif":
        if not isinstance(parsed, dict) or parsed.get("version") != "2.1.0":
            raise ImportRejected("invalid SARIF version")
        runs = parsed.get("runs")
        if not isinstance(runs, list) or len(runs) != 1 or not isinstance(runs[0], dict):
            raise ImportRejected("SARIF requires one run")
        records = runs[0].get("results")
    elif isinstance(parsed, dict):
        records = parsed.get("observations")
    else:
        records = None
    if not isinstance(records, list) or not 1 <= len(records) <= 250 or not all(isinstance(x, dict) for x in records):
        raise ImportRejected("invalid observation collection")
    return records


def parse_import(
    tenant_id: str,
    source_type: str,
    payload: bytes,
    known_assets: frozenset[str],
    *,
    observed_at: str | None = None,
) -> tuple[Evidence, ...]:
    """Validate all rows before returning any; caller commits the tuple atomically."""
    records = _records(source_type, payload)
    timestamp = observed_at or datetime.now(UTC).isoformat()
    output: list[Evidence] = []
    for index, row in enumerate(records):
        asset_id = row.get("asset_id") or row.get("assetId")
        if not isinstance(asset_id, str) or asset_id not in known_assets:
            raise ImportRejected("unknown asset or cross-tenant asset")
        algorithm = row.get("algorithm")
        if source_type == "cyclonedx" and not algorithm:
            properties = row.get("properties")
            if isinstance(properties, list):
                algorithm = next(
                    (p.get("value") for p in properties if isinstance(p, dict) and p.get("name") == "crypto:algorithm"),
                    None,
                )
        if source_type == "sarif" and not algorithm:
            properties = row.get("properties")
            algorithm = properties.get("algorithm") if isinstance(properties, dict) else None
        if not isinstance(algorithm, str) or not algorithm.strip() or len(algorithm) > 80:
            raise ImportRejected("missing or invalid algorithm")
        if algorithm not in ALGORITHMS:
            raise ImportRejected("algorithm is outside the synthetic fixture vocabulary")
        knowledge = row.get("knowledge", "declared_by_vendor" if source_type.startswith("vendor") else "inferred")
        if knowledge not in KNOWLEDGE:
            raise ImportRejected("invalid knowledge state")
        function = row.get("function", "unspecified")
        if not isinstance(function, str) or len(function) > 80:
            raise ImportRejected("invalid cryptographic function")
        if function not in FUNCTIONS:
            raise ImportRejected("function is outside the synthetic fixture vocabulary")
        raw = json.dumps(row, sort_keys=True, separators=(",", ":")).encode()
        digest = hashlib.sha256(raw).hexdigest()
        output.append(
            Evidence(
                id=f"import-{tenant_id}-{digest[:16]}-{index}",
                tenant_id=tenant_id,
                asset_id=asset_id,
                source_type=source_type,
                source_id=f"offline-import/{digest[:16]}/{index}",
                observed_at=timestamp,
                scope="tenant-owned offline fixture",
                parser_version="pqc-import.v1",
                sha256=digest,
                confidence=0.8 if knowledge == "verified" else 0.5,
                knowledge=knowledge,
                algorithm=algorithm,
                function=function,
                note="Imported metadata only; no key material accepted",
            )
        )
    return tuple(output)
