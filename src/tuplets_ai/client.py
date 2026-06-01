from __future__ import annotations

from typing import Any, cast

import httpx

from .config import DEFAULT_BASE_URL, DEFAULT_TIMEOUT_SECONDS, DEFAULT_USER_AGENT, normalize_base_url
from .errors import raise_for_response
from .resources.jobs import JobsResource
from .resources.uploads import UploadsResource


class TupletsClient:
    def __init__(
        self,
        *,
        api_key: str,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
        http_client: httpx.Client | None = None,
    ) -> None:
        self.api_key = api_key
        self.base_url = normalize_base_url(base_url)
        self._owns_http_client = http_client is None
        self._http_client = http_client or httpx.Client(base_url=self.base_url, timeout=timeout)

        self.jobs = JobsResource(self)
        self.uploads = UploadsResource(self)

    def __enter__(self) -> "TupletsClient":
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        self.close()

    def close(self) -> None:
        if self._owns_http_client:
            self._http_client.close()

    def _request(
        self,
        method: str,
        path: str,
        *,
        authenticated: bool = True,
        accept_json: bool = True,
        **kwargs: Any,
    ) -> httpx.Response:
        headers = dict(kwargs.pop("headers", {}) or {})
        headers.setdefault("User-Agent", DEFAULT_USER_AGENT)
        if accept_json:
            headers.setdefault("Accept", "application/json")
        if authenticated:
            headers.setdefault("Authorization", f"Bearer {self.api_key}")

        response = self._http_client.request(method, path, headers=headers, **kwargs)
        raise_for_response(response)
        return response

    def _request_json(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        response = self._request(method, path, **kwargs)
        return cast(dict[str, Any], response.json())

    def _request_void(self, method: str, path: str, **kwargs: Any) -> None:
        self._request(method, path, **kwargs)
