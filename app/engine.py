from __future__ import annotations

import re
import time
from typing import Any

from app.models import RunRecord, WorkflowDefinition, utc_now_iso
from app.store import InMemoryStore

PLACEHOLDER_RE = re.compile(r"\{([a-zA-Z0-9_]+)\}")


def render_template(template: str, context: dict[str, Any]) -> str:
    def _replace(match: re.Match[str]) -> str:
        key = match.group(1)
        return str(context.get(key, f"{{{key}}}"))

    return PLACEHOLDER_RE.sub(_replace, template)


def execute_workflow_run(
    workflow: WorkflowDefinition,
    run_id: str,
    store: InMemoryStore,
) -> RunRecord:
    run = store.get_run(run_id)
    if not run:
        raise ValueError(f"Run '{run_id}' not found.")

    run.status = "running"
    run.started_at = utc_now_iso()
    run.logs.append(f"Run started for workflow: {workflow.name}")
    store.update_run(run)

    try:
        for index, step in enumerate(workflow.steps, start=1):
            run.logs.append(f"Step {index}: {step.name} ({step.action})")
            _execute_step(step.action, step.params, run)
            store.update_run(run)

        run.status = "succeeded"
        run.logs.append("Run completed successfully.")
    except Exception as exc:  # noqa: BLE001 - keep API payload readable
        run.status = "failed"
        run.error = str(exc)
        run.logs.append(f"Run failed: {exc}")
    finally:
        run.finished_at = utc_now_iso()

    return store.update_run(run)


def _execute_step(action: str, params: dict[str, Any], run: RunRecord) -> None:
    if action == "set_context":
        values = params.get("values", {})
        if not isinstance(values, dict):
            raise ValueError("'values' must be an object for set_context.")
        run.context.update(values)
        return

    if action == "template":
        template = params.get("template")
        output_key = params.get("output_key")
        if not template or not output_key:
            raise ValueError("'template' and 'output_key' are required for template action.")
        run.context[output_key] = render_template(str(template), run.context)
        return

    if action == "wait":
        seconds = float(params.get("seconds", 0))
        # Keep demo runs quick while still simulating orchestration wait time.
        seconds = max(0.0, min(seconds, 2.0))
        time.sleep(seconds)
        run.logs.append(f"Waited {seconds:.1f}s")
        return

    if action == "notify_mock":
        channel = str(params.get("channel", "console"))
        message = str(params.get("message", ""))
        rendered = render_template(message, run.context)
        run.logs.append(f"[notify:{channel}] {rendered}")
        return

    raise ValueError(f"Unsupported step action: {action}")
