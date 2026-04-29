from __future__ import annotations

from fastapi import BackgroundTasks, FastAPI, HTTPException

from app.engine import execute_workflow_run
from app.models import RunCreateRequest, RunRecord, WorkflowCreateRequest, WorkflowDefinition
from app.store import InMemoryStore

app = FastAPI(
    title="Workflow Automation Agent MVP",
    description="A minimal runnable workflow automation service for demo and application evidence.",
    version="0.1.0",
)
store = InMemoryStore()


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/workflows", response_model=WorkflowDefinition)
def create_workflow(payload: WorkflowCreateRequest) -> WorkflowDefinition:
    return store.create_workflow(payload)


@app.get("/workflows", response_model=list[WorkflowDefinition])
def list_workflows() -> list[WorkflowDefinition]:
    return store.list_workflows()


@app.get("/workflows/{workflow_id}", response_model=WorkflowDefinition)
def get_workflow(workflow_id: str) -> WorkflowDefinition:
    workflow = store.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found.")
    return workflow


@app.post("/workflows/{workflow_id}/runs", response_model=RunRecord)
def create_run(
    workflow_id: str,
    payload: RunCreateRequest,
    background_tasks: BackgroundTasks,
) -> RunRecord:
    workflow = store.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found.")

    run = store.create_run(workflow_id=workflow_id, context=payload.initial_context)
    if payload.run_in_background:
        background_tasks.add_task(execute_workflow_run, workflow, run.id, store)
        return run

    return execute_workflow_run(workflow, run.id, store)


@app.get("/runs/{run_id}", response_model=RunRecord)
def get_run(run_id: str) -> RunRecord:
    run = store.get_run(run_id)
    if not run:
        raise HTTPException(status_code=404, detail="Run not found.")
    return run


@app.get("/workflows/{workflow_id}/runs", response_model=list[RunRecord])
def list_workflow_runs(workflow_id: str) -> list[RunRecord]:
    workflow = store.get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found.")
    return store.list_runs_by_workflow(workflow_id)
