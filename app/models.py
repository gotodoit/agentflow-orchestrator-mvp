from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field

StepAction = Literal["set_context", "template", "wait", "notify_mock"]
RunStatus = Literal["queued", "running", "succeeded", "failed"]


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class WorkflowStep(BaseModel):
    name: str = Field(..., description="Step display name")
    action: StepAction = Field(..., description="Action type for this step")
    params: dict[str, Any] = Field(default_factory=dict, description="Action parameters")


class WorkflowCreateRequest(BaseModel):
    name: str
    description: str = ""
    steps: list[WorkflowStep] = Field(..., min_length=1)


class WorkflowDefinition(BaseModel):
    id: str
    name: str
    description: str
    steps: list[WorkflowStep]
    created_at: str = Field(default_factory=utc_now_iso)


class RunCreateRequest(BaseModel):
    initial_context: dict[str, Any] = Field(default_factory=dict)
    run_in_background: bool = True


class RunRecord(BaseModel):
    id: str
    workflow_id: str
    status: RunStatus = "queued"
    started_at: str | None = None
    finished_at: str | None = None
    context: dict[str, Any] = Field(default_factory=dict)
    logs: list[str] = Field(default_factory=list)
    error: str | None = None
