from __future__ import annotations

from typing import Any

import httpx


def DefaultHttpxClient(**kwargs: Any) -> httpx.Client:
    return httpx.Client(**kwargs)


def DefaultAsyncHttpxClient(**kwargs: Any) -> httpx.AsyncClient:
    return httpx.AsyncClient(**kwargs)