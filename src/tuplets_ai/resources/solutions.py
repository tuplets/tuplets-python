from __future__ import annotations

from typing import TYPE_CHECKING

from ..models import SolutionsInquiryRequest, SolutionsInquirySubmission

if TYPE_CHECKING:
    from ..async_client import AsyncTupletsClient
    from ..client import TupletsClient


class SolutionsResource:
    def __init__(self, client: "TupletsClient") -> None:
        self._client = client

    def create_inquiry(self, request: SolutionsInquiryRequest) -> SolutionsInquirySubmission:
        payload = self._client._request_json(
            "POST",
            "/solutions/inquiries",
            authenticated=False,
            json=request.as_json(),
        )
        return SolutionsInquirySubmission.from_dict(payload)


class AsyncSolutionsResource:
    def __init__(self, client: "AsyncTupletsClient") -> None:
        self._client = client

    async def create_inquiry(self, request: SolutionsInquiryRequest) -> SolutionsInquirySubmission:
        payload = await self._client._request_json(
            "POST",
            "/solutions/inquiries",
            authenticated=False,
            json=request.as_json(),
        )
        return SolutionsInquirySubmission.from_dict(payload)
