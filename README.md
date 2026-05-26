# Tuplets Python SDK

Official Python SDK for the Tuplets API.

## Installation

```bash
pip install tuplets-ai
```

## Usage

```python
from tuplets_ai import JobCreateParams, TupletsClient

client = TupletsClient(api_key="tb_your_api_key")

job = client.jobs.create_from_file(
    "interview.mp3",
    params=JobCreateParams(language="en", diarization=True),
)

final_job = client.jobs.wait(job.id)

if final_job.status == "completed":
    transcript = client.jobs.download_result(job.id)
    print(transcript["text"])
```

## Direct Uploads

```python
from tuplets_ai import JobCreateParams, TupletsClient

client = TupletsClient(api_key="tb_your_api_key")

upload = client.uploads.create_target(
    filename="large-audio.wav",
    size=12_000_000,
    content_type="audio/wav",
)
client.uploads.upload_file(upload, "large-audio.wav")

job = client.jobs.create_from_uploaded_audio(
    object_key=upload.object_key,
    upload_token=upload.upload_token,
    params=JobCreateParams(language="en", transcription_model="premium"),
)
```

## Async Usage

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
```

## Supported Resources

- `client.jobs` for transcription job submission, polling, cancellation, and result download
- `client.uploads` for signed browser/direct upload targets
- `client.solutions` for public solutions inquiries
