from __future__ import annotations

import time
from pathlib import Path
from typing import TYPE_CHECKING, Any

from .._utils import async_sleep, guess_content_type, sleep
from ..config import DEFAULT_POLL_INTERVAL_SECONDS
from ..errors import WaitTimeoutError
from ..models import JobAccepted, JobCreateParams, JobList, JobStatus

if TYPE_CHECKING:
    from ..async_client import AsyncTupletsClient
    from ..client import TupletsClient


class JobsResource:
    def __init__(self, client: "TupletsClient") -> None:
        self._client = client

    def create_from_file(
        self,
        file_path: str | Path,
        *,
        params: JobCreateParams | None = None,
        content_type: str | None = None,
    ) -> JobAccepted:
        resolved = Path(file_path)
        with resolved.open("rb") as handle:
            payload = self._client._request_json(
                "POST",
                "/jobs",
                data=(params or JobCreateParams()).as_form_fields(),
                files={
                    "audio_file": (
                        resolved.name,
                        handle,
                        content_type or guess_content_type(resolved.name),
                    )
                },
            )
        return JobAccepted.from_dict(payload)

    def create_from_bytes(
        self,
        *,
        filename: str,
        data: bytes,
        params: JobCreateParams | None = None,
        content_type: str | None = None,
    ) -> JobAccepted:
        payload = self._client._request_json(
            "POST",
            "/jobs",
            data=(params or JobCreateParams()).as_form_fields(),
            files={
                "audio_file": (
                    filename,
                    data,
                    content_type or guess_content_type(filename),
                )
            },
        )
        return JobAccepted.from_dict(payload)

    def create_from_url(self, remote_url: str, *, params: JobCreateParams | None = None) -> JobAccepted:
        form_fields = (params or JobCreateParams()).as_form_fields()
        form_fields["remote_url"] = remote_url
        payload = self._client._request_json("POST", "/jobs", data=form_fields)
        return JobAccepted.from_dict(payload)

    def create_from_uploaded_audio(
        self,
        *,
        object_key: str,
        upload_token: str,
        params: JobCreateParams | None = None,
    ) -> JobAccepted:
        form_fields = (params or JobCreateParams()).as_form_fields()
        form_fields["uploaded_audio_key"] = object_key
        form_fields["uploaded_audio_token"] = upload_token
        payload = self._client._request_json("POST", "/jobs", data=form_fields)
        return JobAccepted.from_dict(payload)

    def get(self, job_id: str) -> JobStatus:
        payload = self._client._request_json("GET", f"/jobs/{job_id}")
        return JobStatus.from_dict(payload)

    def list(self, *, status: str | None = None, limit: int = 20) -> JobList:
        params = {"limit": str(limit)}
        if status is not None:
            params["status"] = status
        payload = self._client._request_json("GET", "/jobs", params=params)
        return JobList.from_dict(payload)

    def cancel(self, job_id: str) -> None:
        self._client._request_void("DELETE", f"/jobs/{job_id}")

    def cancel_with_token(self, cancel_token: str) -> None:
        self._client._request_void("POST", "/jobs/cancel", json={"cancel_token": cancel_token})

    def download_result(self, job_id: str) -> dict[str, Any]:
        return self._client._request_json("GET", f"/jobs/{job_id}/download")

    def wait(
        self,
        job_id: str,
        *,
        poll_interval: float = DEFAULT_POLL_INTERVAL_SECONDS,
        timeout: float | None = None,
    ) -> JobStatus:
        deadline = time.monotonic() + timeout if timeout is not None else None

        while True:
            job = self.get(job_id)
            if job.status in {"completed", "failed"}:
                return job
            if deadline is not None and time.monotonic() >= deadline:
                raise WaitTimeoutError(f"Timed out waiting for job {job_id} to finish.")
            sleep(poll_interval)


class AsyncJobsResource:
    def __init__(self, client: "AsyncTupletsClient") -> None:
        self._client = client

    async def create_from_file(
        self,
        file_path: str | Path,
        *,
        params: JobCreateParams | None = None,
        content_type: str | None = None,
    ) -> JobAccepted:
        resolved = Path(file_path)
        data = resolved.read_bytes()
        return await self.create_from_bytes(
            filename=resolved.name,
            data=data,
            params=params,
            content_type=content_type or guess_content_type(resolved.name),
        )

    async def create_from_bytes(
        self,
        *,
        filename: str,
        data: bytes,
        params: JobCreateParams | None = None,
        content_type: str | None = None,
    ) -> JobAccepted:
        payload = await self._client._request_json(
            "POST",
            "/jobs",
            data=(params or JobCreateParams()).as_form_fields(),
            files={
                "audio_file": (
                    filename,
                    data,
                    content_type or guess_content_type(filename),
                )
            },
        )
        return JobAccepted.from_dict(payload)

    async def create_from_url(self, remote_url: str, *, params: JobCreateParams | None = None) -> JobAccepted:
        form_fields = (params or JobCreateParams()).as_form_fields()
        form_fields["remote_url"] = remote_url
        payload = await self._client._request_json("POST", "/jobs", data=form_fields)
        return JobAccepted.from_dict(payload)

    async def create_from_uploaded_audio(
        self,
        *,
        object_key: str,
        upload_token: str,
        params: JobCreateParams | None = None,
    ) -> JobAccepted:
        form_fields = (params or JobCreateParams()).as_form_fields()
        form_fields["uploaded_audio_key"] = object_key
        form_fields["uploaded_audio_token"] = upload_token
        payload = await self._client._request_json("POST", "/jobs", data=form_fields)
        return JobAccepted.from_dict(payload)

    async def get(self, job_id: str) -> JobStatus:
        payload = await self._client._request_json("GET", f"/jobs/{job_id}")
        return JobStatus.from_dict(payload)

    async def list(self, *, status: str | None = None, limit: int = 20) -> JobList:
        params = {"limit": str(limit)}
        if status is not None:
            params["status"] = status
        payload = await self._client._request_json("GET", "/jobs", params=params)
        return JobList.from_dict(payload)

    async def cancel(self, job_id: str) -> None:
        await self._client._request_void("DELETE", f"/jobs/{job_id}")

    async def cancel_with_token(self, cancel_token: str) -> None:
        await self._client._request_void("POST", "/jobs/cancel", json={"cancel_token": cancel_token})

    async def download_result(self, job_id: str) -> dict[str, Any]:
        return await self._client._request_json("GET", f"/jobs/{job_id}/download")

    async def wait(
        self,
        job_id: str,
        *,
        poll_interval: float = DEFAULT_POLL_INTERVAL_SECONDS,
        timeout: float | None = None,
    ) -> JobStatus:
        deadline = time.monotonic() + timeout if timeout is not None else None

        while True:
            job = await self.get(job_id)
            if job.status in {"completed", "failed"}:
                return job
            if deadline is not None and time.monotonic() >= deadline:
                raise WaitTimeoutError(f"Timed out waiting for job {job_id} to finish.")
            await async_sleep(poll_interval)
