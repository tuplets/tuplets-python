from __future__ import annotations

import asyncio
import mimetypes
import time


def bool_to_api(value: bool) -> str:
    return "true" if value else "false"


def guess_content_type(filename: str, default: str = "application/octet-stream") -> str:
    guessed, _ = mimetypes.guess_type(filename)
    return guessed or default


def sleep(seconds: float) -> None:
    time.sleep(seconds)


async def async_sleep(seconds: float) -> None:
    await asyncio.sleep(seconds)
