from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from .._utils import guess_content_type
from ..models import BrowserUploadTarget

if TYPE_CHECKING:
    from ..async_client import AsyncTupletsClient
    from ..client import TupletsClient


class UploadsResource:
    def __init__(self, client: "TupletsClient") -> None:
        self._client = client

    def create_target(self, *, filename: str, size: int, content_type: str | None = None) -> BrowserUploadTarget:
        payload = self._client._request_json(
            "POST",
            "/jobs/upload-target",
            json={
                "filename": filename,
                "size": size,
                "content_type": content_type,
            },
        )
        return BrowserUploadTarget.from_dict(payload)

    def upload_file(
        self,
        upload: BrowserUploadTarget,
        file_path: str | Path,
        *,
        content_type: str | None = None,
    ) -> None:
        resolved = Path(file_path)
        self.upload_bytes(
            upload,
            data=resolved.read_bytes(),
            content_type=content_type or guess_content_type(resolved.name),
        )

    def upload_bytes(
        self,
        upload: BrowserUploadTarget,
        *,
        data: bytes,
        content_type: str | None = None,
    ) -> None:
        headers = dict(upload.upload_headers)
        if content_type and "Content-Type" not in headers:
            headers["Content-Type"] = content_type
        self._client._request(
            upload.upload_method,
            upload.upload_url,
            authenticated=False,
            accept_json=False,
            headers=headers,
            content=data,
        )


class AsyncUploadsResource:
    def __init__(self, client: "AsyncTupletsClient") -> None:
        self._client = client

    async def create_target(self, *, filename: str, size: int, content_type: str | None = None) -> BrowserUploadTarget:
        payload = await self._client._request_json(
            "POST",
            "/jobs/upload-target",
            json={
                "filename": filename,
                "size": size,
                "content_type": content_type,
            },
        )
        return BrowserUploadTarget.from_dict(payload)

    async def upload_file(
        self,
        upload: BrowserUploadTarget,
        file_path: str | Path,
        *,
        content_type: str | None = None,
    ) -> None:
        resolved = Path(file_path)
        await self.upload_bytes(
            upload,
            data=resolved.read_bytes(),
            content_type=content_type or guess_content_type(resolved.name),
        )

    async def upload_bytes(
        self,
        upload: BrowserUploadTarget,
        *,
        data: bytes,
        content_type: str | None = None,
    ) -> None:
        headers = dict(upload.upload_headers)
        if content_type and "Content-Type" not in headers:
            headers["Content-Type"] = content_type
        await self._client._request(
            upload.upload_method,
            upload.upload_url,
            authenticated=False,
            accept_json=False,
            headers=headers,
            content=data,
        )
