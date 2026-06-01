from __future__ import annotations

import httpx

from tuplets_ai import DefaultHttpxClient, JobCreateParams, TupletsClient


def test_create_from_url_sends_bearer_auth_and_form_fields():
    seen: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen["authorization"] = request.headers.get("Authorization")
        seen["content_type"] = request.headers.get("Content-Type", "")
        seen["body"] = request.content.decode("utf-8")
        return httpx.Response(
            201,
            json={
                "status": "accepted",
                "id": "job_123",
                "status_url": "https://api.tuplets.ai/jobs/job_123",
                "cancel_url": "https://api.tuplets.ai/jobs/job_123",
                "cancel_token": "cancel_123",
            },
        )

    transport = httpx.MockTransport(handler)
    http_client = httpx.Client(transport=transport, base_url="https://api.tuplets.ai")
    client = TupletsClient(api_key="tb_test_key", http_client=http_client)

    job = client.jobs.create_from_url(
        "https://storage.example.com/call.wav",
        params=JobCreateParams(language="en", diarization=True, pii_processing=True),
    )

    assert job.id == "job_123"
    assert seen["authorization"] == "Bearer tb_test_key"
    assert seen["content_type"] == "application/x-www-form-urlencoded"
    assert "remote_url=https%3A%2F%2Fstorage.example.com%2Fcall.wav" in str(seen["body"])
    assert "diarization=true" in str(seen["body"])
    assert "true" in str(seen["body"])


def test_wait_polls_until_completion():
    responses = iter(
        [
            {
                "id": "job_123",
                "status": "queued",
                "result": None,
                "error_message": None,
                "audio_duration_seconds": 30.0,
                "transcription_model": "standard",
                "diarization": False,
                "pii_processing": False,
                "estimated_cost_usd": 0.1,
                "billed_cost_usd": None,
                "billing_status": "pending",
                "source_type": "upload",
                "result_download_available": False,
                "source_audio_available": True,
                "progress_percent": 5.0,
                "estimated_seconds_remaining": 6,
                "cancel_token": "cancel_123",
                "created_at": "2026-01-01T00:00:00+00:00",
                "started_at": None,
                "completed_at": None,
                "runtime_ms": None,
            },
            {
                "id": "job_123",
                "status": "completed",
                "result": {"text": "Finished"},
                "error_message": None,
                "audio_duration_seconds": 30.0,
                "transcription_model": "standard",
                "diarization": False,
                "pii_processing": False,
                "estimated_cost_usd": 0.1,
                "billed_cost_usd": 0.1,
                "billing_status": "billed",
                "source_type": "upload",
                "result_download_available": True,
                "source_audio_available": True,
                "progress_percent": 100.0,
                "estimated_seconds_remaining": 0,
                "cancel_token": None,
                "created_at": "2026-01-01T00:00:00+00:00",
                "started_at": "2026-01-01T00:00:02+00:00",
                "completed_at": "2026-01-01T00:00:04+00:00",
                "runtime_ms": 2200,
            },
        ]
    )

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=next(responses))

    transport = httpx.MockTransport(handler)
    http_client = httpx.Client(transport=transport, base_url="https://api.tuplets.ai")
    client = TupletsClient(api_key="tb_test_key", http_client=http_client)

    job = client.jobs.wait("job_123", poll_interval=0.0, timeout=1.0)

    assert job.status == "completed"
    assert job.result == {"text": "Finished"}


def test_upload_bytes_uses_signed_url_without_authorization_header():
    seen_headers: dict[str, str] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        seen_headers["authorization"] = request.headers.get("Authorization", "")
        seen_headers["content_type"] = request.headers.get("Content-Type", "")
        return httpx.Response(200, text="ok")

    transport = httpx.MockTransport(handler)
    http_client = httpx.Client(transport=transport, base_url="https://api.tuplets.ai")
    client = TupletsClient(api_key="tb_test_key", http_client=http_client)

    from tuplets_ai import BrowserUploadTarget

    client.uploads.upload_bytes(
        BrowserUploadTarget(
            upload_url="https://uploads.example.com/object",
            upload_method="PUT",
            upload_headers={"Content-Type": "audio/wav"},
            object_key="uploads/account/object.wav",
            upload_token="upload_token",
            expires_in_seconds=900,
        ),
        data=b"audio-bytes",
    )

    assert seen_headers["authorization"] == ""
    assert seen_headers["content_type"] == "audio/wav"


def test_default_httpx_client_can_be_configured_without_direct_httpx_client_import():
    seen_path = ""

    def handler(request: httpx.Request) -> httpx.Response:
        nonlocal seen_path
        seen_path = str(request.url)
        return httpx.Response(
            201,
            json={
                "status": "accepted",
                "id": "job_123",
                "status_url": "https://api.tuplets.ai/jobs/job_123",
                "cancel_url": "https://api.tuplets.ai/jobs/job_123",
                "cancel_token": "cancel_123",
            },
        )

    client = TupletsClient(
        api_key="tb_test_key",
        http_client=DefaultHttpxClient(
            transport=httpx.MockTransport(handler),
            base_url="https://api.tuplets.ai",
        ),
    )

    job = client.jobs.create_from_url("https://storage.example.com/call.wav")

    assert job.id == "job_123"
    assert seen_path == "https://api.tuplets.ai/jobs"