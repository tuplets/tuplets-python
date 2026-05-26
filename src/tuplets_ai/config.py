from __future__ import annotations

from ._version import __version__

DEFAULT_BASE_URL = "https://api.tuplets.ai"
DEFAULT_TIMEOUT_SECONDS = 60.0
DEFAULT_POLL_INTERVAL_SECONDS = 2.0
DEFAULT_USER_AGENT = f"tuplets-ai-python/{__version__}"


def normalize_base_url(base_url: str) -> str:
    return base_url.rstrip("/")
