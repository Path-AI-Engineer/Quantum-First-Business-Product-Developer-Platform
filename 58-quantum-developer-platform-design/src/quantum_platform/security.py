"""Credential and webhook primitives with safe defaults."""

from __future__ import annotations

import hashlib
import hmac
import secrets
import time
from dataclasses import dataclass


def hash_secret(secret: str, salt: str) -> str:
    value = hashlib.pbkdf2_hmac("sha256", secret.encode(), salt.encode(), 120_000)
    return value.hex()


def verify_secret(secret: str, salt: str, expected: str) -> bool:
    return hmac.compare_digest(hash_secret(secret, salt), expected)


def new_api_secret(prefix: str) -> str:
    return f"{prefix}_{secrets.token_urlsafe(24)}"


def sign_webhook(secret: str, timestamp: int, delivery_id: str, body: bytes) -> str:
    payload = f"{timestamp}.{delivery_id}.".encode() + body
    return "v1=" + hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()


def verify_webhook(
    secret: str,
    timestamp: int,
    delivery_id: str,
    body: bytes,
    signature: str,
    *,
    now: int | None = None,
    tolerance_seconds: int = 300,
) -> bool:
    current = int(time.time()) if now is None else now
    if abs(current - timestamp) > tolerance_seconds:
        return False
    return hmac.compare_digest(sign_webhook(secret, timestamp, delivery_id, body), signature)


@dataclass(frozen=True)
class StoredSecret:
    prefix: str
    salt: str
    digest: str


def store_secret(secret: str, prefix: str) -> StoredSecret:
    salt = secrets.token_hex(16)
    return StoredSecret(prefix=prefix, salt=salt, digest=hash_secret(secret, salt))
