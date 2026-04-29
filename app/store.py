from __future__ import annotations

from copy import deepcopy
from threading import Lock
from uuid import uuid4

from app.models import RunRecord, WorkflowCreateRequest, WorkflowDefinition


class InMemoryStore:
    def __init__(self) -> None:
        self._workflows: dict[str, WorkflowDefinition] = {}
        self._runs: dict[str, RunRecord] = {}
        self._lock = Lock()

    def create_workflow(self, payload: WorkflowCreateRequest) -> WorkflowDefinition:
        workflow = WorkflowDefinition(id=str(uuid4()), **payload.model_dump())
        with self._lock:
            self._workflows[workflow.id] = workflow
        return deepcopy(workflow)

    def list_workflows(self) -> list[WorkflowDefinition]:
        with self._lock:
            return [deepcopy(item) for item in self._workflows.values()]

    def get_workflow(self, workflow_id: str) -> WorkflowDefinition | None:
        with self._lock:
            workflow = self._workflows.get(workflow_id)
            return deepcopy(workflow) if workflow else None

    def create_run(self, workflow_id: str, context: dict) -> RunRecord:
        run = RunRecord(id=str(uuid4()), workflow_id=workflow_id, context=context)
        with self._lock:
            self._runs[run.id] = run
        return deepcopy(run)

    def update_run(self, run: RunRecord) -> RunRecord:
        with self._lock:
            self._runs[run.id] = deepcopy(run)
            return deepcopy(self._runs[run.id])

    def get_run(self, run_id: str) -> RunRecord | None:
        with self._lock:
            run = self._runs.get(run_id)
            return deepcopy(run) if run else None

    def list_runs_by_workflow(self, workflow_id: str) -> list[RunRecord]:
        with self._lock:
            runs = [run for run in self._runs.values() if run.workflow_id == workflow_id]
            return [deepcopy(run) for run in runs]
