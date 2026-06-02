# Tuplets Python SDK

Official Python client for the [Tuplets API](https://api.tuplets.ai) — transcribe audio, run speaker diarization, apply PII redaction, and request structured analytics from Python 3.10+.

- **Docs:** [tuplets.ai/docs](https://tuplets.ai/docs)
- **API reference:** [api.tuplets.ai](https://api.tuplets.ai)
- **Get an API key:** [tuplets.ai/settings/api-keys](https://tuplets.ai/settings/api-keys)

## Installation

```bash
pip install tuplets-ai
```

Requires Python **3.10+**. The only runtime dependency is [httpx](https://www.python-httpx.org/).

## Quick start

Transcribe a local file, wait for completion, and print the transcript:

```python
import os

from tuplets_ai import JobCreateParams, TupletsClient

client = TupletsClient(api_key=os.environ["TUPLETS_API_KEY"])

job = client.jobs.create_from_file(
    "interview.mp3",
    params=JobCreateParams(language="en"),
)

final_job = client.jobs.wait(job.id)

if final_job.status == "completed":
    transcript = client.jobs.download_result(job.id)
    print(transcript["text"])
elif final_job.status == "failed":
    print(final_job.error_message)
```

## Authentication

Create an API key in the Tuplets dashboard (prefix `tb_`) and pass it when constructing the client:

```python
client = TupletsClient(api_key="tb_your_api_key")
```

Every authenticated request sends `Authorization: Bearer tb_...`.

## Client configuration

```python
import httpx

from tuplets_ai import TupletsClient

# Custom base URL (defaults to https://api.tuplets.ai)
client = TupletsClient(
    api_key="tb_your_api_key",
    base_url="https://api.tuplets.ai",
    timeout=120.0,
)

# Reuse your own httpx client (connection pooling, proxies, retries, etc.)
http = httpx.Client(base_url="https://api.tuplets.ai", timeout=120.0)
client = TupletsClient(api_key="tb_your_api_key", http_client=http)

with client:
    ...
# or explicitly:
client.close()
```

Use `AsyncTupletsClient` the same way with `httpx.AsyncClient` and `async with`.

## Submitting transcription jobs

All job submission methods return a `JobAccepted` object with `id`, `status_url`, `cancel_url`, and `cancel_token`.

### From a local file

```python
job = client.jobs.create_from_file(
    "call.wav",
    params=JobCreateParams(language="en", transcription_model="premium"),
)
```

### From bytes (in memory)

```python
from pathlib import Path

audio = Path("call.wav").read_bytes()

job = client.jobs.create_from_bytes(
    filename="call.wav",
    data=audio,
    params=JobCreateParams(language="auto"),
)
```

### From a remote URL

Tuplets fetches the audio from a publicly reachable URL:

```python
job = client.jobs.create_from_url(
    "https://storage.example.com/recordings/call.mp3",
    params=JobCreateParams(language="en"),
)
```

### From a direct upload

For large files, upload to object storage first, then reference the upload when creating the job (see [Direct uploads](#direct-uploads)).

```python
job = client.jobs.create_from_uploaded_audio(
    object_key=upload.object_key,
    upload_token=upload.upload_token,
    params=JobCreateParams(language="en"),
)
```

## Job parameters

Pass options via `JobCreateParams`:

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `language` | `str` | `"auto"` | BCP-47 language code or `"auto"` for detection |
| `transcription_model` | `"standard"` \| `"premium"` | `"standard"` | Accuracy/latency tier |
| `diarization` | `bool` | `False` | Speaker attribution; when enabled, jobs **fail** if diarization cannot be produced |
| `pii_processing` | `bool` | `False` | Detect and redact personally identifiable information |
| `analytics` | `dict` | `None` | Structured post-transcription analytics (see below) |

```python
params = JobCreateParams(
    language="en",
    transcription_model="premium",
    diarization=True,
    pii_processing=True,
)
```

## Polling, waiting, and results

### Poll manually

```python
status = client.jobs.get(job.id)

print(status.status)                 # queued | running | completed | failed
print(status.progress_percent)       # 0–100 while running
print(status.estimated_seconds_remaining)
print(status.result)                 # inline preview when completed
print(status.error_message)          # set when status == "failed"
```

### Wait until finished

`wait()` polls until the job reaches `completed` or `failed`:

```python
final_job = client.jobs.wait(
    job.id,
    poll_interval=2.0,   # seconds between polls (default: 2)
    timeout=600.0,       # optional; raises WaitTimeoutError
)
```

### Download the full transcript

```python
transcript = client.jobs.download_result(job.id)
print(transcript["text"])
for segment in transcript.get("segments", []):
    print(segment["start"], segment["end"], segment["text"])
```

When `diarization=True`, segments include speaker labels. Completed jobs may also include an `analytics` object if analytics were requested.

Downloaded JSON includes `feature_execution.transcription_model_requested` and `feature_execution.transcription_model_applied` so archived result files record whether `standard` or `premium` transcription ran.

### List and cancel jobs

```python
recent = client.jobs.list(status="completed", limit=20)
for item in recent.items:
    print(item.id, item.status, item.created_at)

client.jobs.cancel(job.id)

# Cancel without storing the job id (uses token from JobAccepted)
client.jobs.cancel_with_token(job.cancel_token)
```

## Direct uploads

Upload large audio files to signed storage, then create a job from the upload reference:

```python
from pathlib import Path

from tuplets_ai import JobCreateParams, TupletsClient

client = TupletsClient(api_key="tb_your_api_key")
file_path = Path("large-audio.wav")

upload = client.uploads.create_target(
    filename=file_path.name,
    size=file_path.stat().st_size,
    content_type="audio/wav",
)

client.uploads.upload_file(upload, file_path)

job = client.jobs.create_from_uploaded_audio(
    object_key=upload.object_key,
    upload_token=upload.upload_token,
    params=JobCreateParams(language="en", transcription_model="premium"),
)
```

`create_target` returns a `BrowserUploadTarget` with a pre-signed `upload_url`, required `upload_headers`, and an expiry (`expires_in_seconds`). Upload with `upload_file` / `upload_bytes`, or PUT the bytes yourself using the signed URL.

## Analytics

Request generic and custom schema-bound analytics with `JobCreateParams.analytics`:

```python
job = client.jobs.create_from_file(
    "insurance-call.mp3",
    params=JobCreateParams(
        language="en",
        analytics={
            "profile": "full",
            "domain": "insurance",
            "schema": {
                "fields": [
                    {
                        "key": "call_reason",
                        "label": "Reason for call",
                        "type": "single_select",
                        "options": [
                            {"id": 1, "code": "CLAIM_STATUS", "label": "Claim status"},
                            {"id": 2, "code": "BILLING", "label": "Billing question"},
                        ],
                    }
                ]
            },
        },
    ),
)

final_job = client.jobs.wait(job.id)
if final_job.analytics:
    print(final_job.analytics["custom"]["fields"])
```

See [tuplets.ai/docs](https://tuplets.ai/docs) for supported profiles, domains, and schema field types.

## Async usage

The async client mirrors the sync API:

```python
from tuplets_ai import AsyncTupletsClient, JobCreateParams

async def main() -> None:
    async with AsyncTupletsClient(api_key="tb_your_api_key") as client:
        job = await client.jobs.create_from_url(
            "https://storage.example.com/call.mp3",
            params=JobCreateParams(language="en", pii_processing=True),
        )
        final_job = await client.jobs.wait(job.id)
        if final_job.status == "completed":
            transcript = await client.jobs.download_result(job.id)
            print(transcript["text"])
        elif final_job.status == "failed":
            print(final_job.error_message)
```

## Error handling

API failures raise typed exceptions with `status_code` and optional `response_body`:

| Exception | HTTP status |
|-----------|-------------|
| `ValidationError` | 400 |
| `AuthenticationError` | 401 |
| `PaymentRequiredError` | 402 |
| `PermissionDeniedError` | 403 |
| `NotFoundError` | 404 |
| `ConflictError` | 409 |
| `GoneError` | 410 |
| `RateLimitError` | 429 |
| `APIStatusError` | other 4xx/5xx |
| `WaitTimeoutError` | polling timeout (not an HTTP error) |

```python
from tuplets_ai import AuthenticationError, RateLimitError, TupletsClient

client = TupletsClient(api_key="tb_your_api_key")

try:
    client.jobs.get("job_unknown")
except AuthenticationError as exc:
    print(exc.status_code, exc.message)
except RateLimitError:
    ...
```

## API surface

| Resource | Methods |
|----------|---------|
| `client.jobs` | `create_from_file`, `create_from_bytes`, `create_from_url`, `create_from_uploaded_audio`, `get`, `list`, `wait`, `cancel`, `cancel_with_token`, `download_result` |
| `client.uploads` | `create_target`, `upload_file`, `upload_bytes` |
| `client.solutions` | `create_inquiry` (public enterprise inquiries; no API key required) |

### Exported types

`JobCreateParams`, `JobAccepted`, `JobStatus`, `JobList`, `BrowserUploadTarget`, `UploadedAudioReference`, `SolutionsInquiryRequest`, `SolutionsInquirySubmission`, and the exception classes above are exported from the top-level `tuplets_ai` package.

## Support

- Documentation: [tuplets.ai/docs](https://tuplets.ai/docs)
- Contact: [contact@tuplets.ai](mailto:contact@tuplets.ai)
