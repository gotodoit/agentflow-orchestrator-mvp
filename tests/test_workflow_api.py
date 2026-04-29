from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_create_and_run_workflow_sync() -> None:
    workflow_payload = {
        "name": "Lead Follow-up Automation",
        "description": "Auto-generate and send a follow-up message.",
        "steps": [
            {
                "name": "Load lead profile",
                "action": "set_context",
                "params": {"values": {"user_name": "Alice", "product": "AI Copilot"}},
            },
            {
                "name": "Generate message",
                "action": "template",
                "params": {
                    "template": "Hi {user_name}, welcome to {product}.",
                    "output_key": "message",
                },
            },
            {
                "name": "Notify sales channel",
                "action": "notify_mock",
                "params": {"channel": "slack", "message": "{message}"},
            },
        ],
    }

    create_workflow_resp = client.post("/workflows", json=workflow_payload)
    assert create_workflow_resp.status_code == 200
    workflow_id = create_workflow_resp.json()["id"]

    run_resp = client.post(
        f"/workflows/{workflow_id}/runs",
        json={"initial_context": {"region": "APAC"}, "run_in_background": False},
    )
    assert run_resp.status_code == 200
    run = run_resp.json()
    assert run["status"] == "succeeded"
    assert run["context"]["message"] == "Hi Alice, welcome to AI Copilot."
    assert any("notify:slack" in log for log in run["logs"])


def test_get_nonexistent_workflow_returns_404() -> None:
    response = client.get("/workflows/not-exist")
    assert response.status_code == 404
