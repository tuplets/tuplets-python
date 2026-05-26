from __future__ import annotations

from typing import Any

import httpx


class TupletsError(Exception):
    """Base SDK exception."""


class APIStatusError(TupletsError):
    def __init__(self, message: str, *, status_code: int, response_body: Any | None = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_body = response_body


class AuthenticationError(APIStatusError):
    pass


class PermissionDeniedError(APIStatusError):
    pass


class ValidationError(APIStatusError):
    pass


class PaymentRequiredError(APIStatusError):
    pass


class NotFoundError(APIStatusError):
    pass


class ConflictError(APIStatusError):
    pass


class GoneError(APIStatusError):
    pass


class RateLimitError(APIStatusError):
    pass


class WaitTimeoutError(TupletsError):
    pass


_STATUS_CODE_MAP: dict[int, type[APIStatusError]] = {
    400: ValidationError,
    401: AuthenticationError,
    402: PaymentRequiredError,
    403: PermissionDeniedError,
    404: NotFoundError,
    409: ConflictError,
    410: GoneError,
    429: RateLimitError,
}


def raise_for_response(response: httpx.Response) -> None:
    if response.is_success:
        return

    response_body: Any | None = None
    message = response.text.strip() or f"Tuplets API request failed with status {response.status_code}."

    try:
        response_body = response.json()
    except ValueError:
        response_body = None
    else:
        if isinstance(response_body, dict):
            detail = response_body.get("detail")
            if isinstance(detail, str) and detail.strip():
                message = detail.strip()

    error_cls = _STATUS_CODE_MAP.get(response.status_code, APIStatusError)
    raise error_cls(message, status_code=response.status_code, response_body=response_body)
