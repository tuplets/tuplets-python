from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Literal, Mapping

from ._utils import bool_to_api

TranscriptionModel = Literal["standard", "premium"]
JobState = Literal["queued", "running", "completed", "failed"]
TranscriptPayload = dict[str, Any]


@dataclass(slots=True)
class JobCreateParams:
    """Parameters for job submission.

    When ``diarization`` is ``True``, speaker attribution is treated as a
    required outcome. Jobs can finish as failed if usable diarization cannot
    be produced.
    """

    language: str = "auto"
    transcription_model: TranscriptionModel = "standard"
    diarization: bool = False
    pii_processing: bool = False
    analytics: Mapping[str, Any] | None = None

    def as_form_fields(self) -> dict[str, str]:
        fields = {
            "language": self.language,
            "transcription_model": self.transcription_model,
            "diarization": bool_to_api(self.diarization),
            "pii_processing": bool_to_api(self.pii_processing),
        }
        if self.analytics is not None:
            fields["analytics"] = json.dumps(dict(self.analytics))
        return fields


@dataclass(slots=True)
class UploadedAudioReference:
    object_key: str
    upload_token: str


@dataclass(slots=True)
class JobAccepted:
    status: Literal["accepted"]
    id: str
    status_url: str
    cancel_url: str
    cancel_token: str

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "JobAccepted":
        return cls(
            status="accepted",
            id=str(payload["id"]),
            status_url=str(payload["status_url"]),
            cancel_url=str(payload["cancel_url"]),
            cancel_token=str(payload["cancel_token"]),
        )


@dataclass(slots=True)
class BrowserUploadTarget:
    upload_url: str
    upload_method: Literal["PUT"]
    upload_headers: dict[str, str]
    object_key: str
    upload_token: str
    expires_in_seconds: int

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "BrowserUploadTarget":
        return cls(
            upload_url=str(payload["upload_url"]),
            upload_method="PUT",
            upload_headers=dict(payload.get("upload_headers") or {}),
            object_key=str(payload["object_key"]),
            upload_token=str(payload["upload_token"]),
            expires_in_seconds=int(payload["expires_in_seconds"]),
        )


@dataclass(slots=True)
class JobStatus:
    """Normalized job status returned by the API.

    ``result`` is populated only for completed jobs. When ``diarization`` is
    enabled, failed speaker attribution leaves ``result`` as ``None`` and
    surfaces the failure detail through ``error_message``.
    """

    id: str
    status: JobState
    result: TranscriptPayload | None
    error_message: str | None
    audio_duration_seconds: float | None
    transcription_model: TranscriptionModel
    diarization: bool
    pii_processing: bool
    analytics: dict[str, Any] | None
    estimated_cost_usd: float | None
    billed_cost_usd: float | None
    billing_status: str | None
    source_type: str | None
    result_download_available: bool
    source_audio_available: bool
    progress_percent: float | None
    estimated_seconds_remaining: int | None
    cancel_token: str | None
    created_at: str
    started_at: str | None
    completed_at: str | None
    runtime_ms: int | None

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "JobStatus":
        return cls(
            id=str(payload["id"]),
            status=str(payload["status"]),
            result=dict(payload["result"]) if isinstance(payload.get("result"), dict) else None,
            error_message=payload.get("error_message"),
            audio_duration_seconds=float(payload["audio_duration_seconds"]) if payload.get("audio_duration_seconds") is not None else None,
            transcription_model=str(payload.get("transcription_model", "standard")),
            diarization=bool(payload.get("diarization", False)),
            pii_processing=bool(payload.get("pii_processing", False)),
            analytics=dict(payload["analytics"]) if isinstance(payload.get("analytics"), dict) else None,
            estimated_cost_usd=float(payload["estimated_cost_usd"]) if payload.get("estimated_cost_usd") is not None else None,
            billed_cost_usd=float(payload["billed_cost_usd"]) if payload.get("billed_cost_usd") is not None else None,
            billing_status=payload.get("billing_status"),
            source_type=payload.get("source_type"),
            result_download_available=bool(payload.get("result_download_available", False)),
            source_audio_available=bool(payload.get("source_audio_available", False)),
            progress_percent=float(payload["progress_percent"]) if payload.get("progress_percent") is not None else None,
            estimated_seconds_remaining=int(payload["estimated_seconds_remaining"]) if payload.get("estimated_seconds_remaining") is not None else None,
            cancel_token=payload.get("cancel_token"),
            created_at=str(payload["created_at"]),
            started_at=payload.get("started_at"),
            completed_at=payload.get("completed_at"),
            runtime_ms=int(payload["runtime_ms"]) if payload.get("runtime_ms") is not None else None,
        )


@dataclass(slots=True)
class JobList:
    items: list[JobStatus]
    total_items: int
    status_filter: str | None

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "JobList":
        return cls(
            items=[JobStatus.from_dict(item) for item in payload.get("items", [])],
            total_items=int(payload.get("total_items", 0)),
            status_filter=payload.get("status_filter"),
        )


@dataclass(slots=True)
class SolutionsInquiryRequest:
    company_name: str
    contact_email: str
    role: str
    project_type: str
    budget_range: str
    audio_hours_of_processing: str
    requirements: str

    def as_json(self) -> dict[str, str]:
        return {
            "company_name": self.company_name,
            "contact_email": self.contact_email,
            "role": self.role,
            "project_type": self.project_type,
            "budget_range": self.budget_range,
            "audio_hours_of_processing": self.audio_hours_of_processing,
            "requirements": self.requirements,
        }


@dataclass(slots=True)
class SolutionsInquirySubmission:
    status: str
    message: str
    inquiry_id: str
    submitted_at: str

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "SolutionsInquirySubmission":
        return cls(
            status=str(payload["status"]),
            message=str(payload["message"]),
            inquiry_id=str(payload["inquiry_id"]),
            submitted_at=str(payload["submitted_at"]),
        )
