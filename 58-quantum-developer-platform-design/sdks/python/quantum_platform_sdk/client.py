"""Small typed Python SDK layer over the generated contract resources."""

from __future__ import annotations

import time
from typing import Any

import httpx


class QuantumPlatformError(RuntimeError):
    def __init__(self, code: str, message: str, correlation_id: str) -> None:
        super().__init__(message)
        self.code = code
        self.correlation_id = correlation_id


class Client:
    def __init__(self, base_url: str, api_key: str, timeout: float = 10.0) -> None:
        self._client = httpx.Client(
            base_url=base_url.rstrip("/"),
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=timeout,
        )

    def capabilities(self) -> list[dict[str, Any]]:
        return list(self._request("GET", "/v1/capabilities"))

    def submit_job(self, project_id: str, request: dict[str, Any], idempotency_key: str) -> dict[str, Any]:
        if not idempotency_key:
            raise ValueError("idempotency_key is required for job creation")
        return dict(
            self._request(
                "POST",
                "/v1/jobs",
                params={"project_id": project_id},
                headers={"Idempotency-Key": idempotency_key},
                json=request,
            )
        )

    def wait(self, project_id: str, job_id: str, timeout: float = 30.0) -> dict[str, Any]:
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            job = dict(self._request("GET", f"/v1/jobs/{job_id}", params={"project_id": project_id}))
            if job["state"] in {"SUCCEEDED", "FAILED", "CANCELLED", "REJECTED", "EXPIRED"}:
                return job
            time.sleep(0.1)
        raise TimeoutError(f"job {job_id} did not finish within {timeout}s")

    def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        response = self._client.request(method, path, **kwargs)
        if response.is_error:
            body = response.json()
            raise QuantumPlatformError(
                body.get("code", "HTTP_ERROR"),
                body.get("detail", response.text),
                body.get("correlation_id", response.headers.get("X-Request-Id", "unknown")),
            )
        return response.json()
