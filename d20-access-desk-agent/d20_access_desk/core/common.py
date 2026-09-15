"""Shared, plain-code helpers used by every tier of the access desk.

Nothing in this file is an agent tool description or a prompt. It is the
part of the system that an LLM cannot argue its way around: the policy
lookup, the audit write, and the page. Each tier's agent code calls into
this module instead of re-implementing the boundary.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())

POLICY_PATH = Path(__file__).parent / "entitlement_policy.json"
APPROVER_WEBHOOK_URL = os.environ.get("ESCALATION_WEBHOOK_URL", "")

# Testing/dev safety: don't hammer the real n8n webhook on every local run.
# Set PAGE_LIVE=1 in the environment to actually fire the HTTP POST.
PAGE_LIVE = os.environ.get("PAGE_LIVE", "0") == "1"


def load_policy() -> dict:
    return json.loads(POLICY_PATH.read_text())


def resource_enum(policy: dict | None = None) -> list[str]:
    """Every resource name a tool schema should accept -- pulled straight
    from the policy file so an agent can't invent a free-text resource
    description that the code can't classify."""
    policy = policy or load_policy()
    return sorted(policy.get("self_serve", []) + policy.get("privileged", []))


def is_privileged(resource: str, policy: dict | None = None) -> bool:
    """Fail closed: unlisted resources are treated as privileged.

    A resource is self-serve only if it is explicitly named in
    ``self_serve``. Anything else -- including a resource nobody has
    classified yet -- routes to a human.
    """
    policy = policy or load_policy()
    return resource not in set(policy.get("self_serve", []))


def append_audit_ticket(audit_log_path: Path, ticket: dict) -> dict:
    """Write one ticket to the audit log. This is the only place tickets
    are written to disk, and it is plain code, not an agent action."""
    ticket = dict(ticket)
    ticket["timestamp"] = datetime.now(timezone.utc).isoformat()
    audit_log_path.parent.mkdir(parents=True, exist_ok=True)
    with audit_log_path.open("a") as f:
        f.write(json.dumps(ticket) + "\n")
    return ticket


def page_approver(ticket: dict) -> str:
    """Page a human when, and only when, decision_owner == 'Human'.

    Called from plain Python after the ticket is written -- never from
    inside a tool the agent controls, and never decided by the model.
    """
    if ticket.get("decision_owner") != "Human":
        return "skipped (decision_owner != Human)"

    if not APPROVER_WEBHOOK_URL:
        return "skipped (no ESCALATION_WEBHOOK_URL configured)"

    if not PAGE_LIVE:
        return "dry-run (set PAGE_LIVE=1 to actually POST to the webhook)"

    resp = requests.post(APPROVER_WEBHOOK_URL, json=ticket, timeout=10)
    return f"paged (HTTP {resp.status_code})"


def read_last_ticket(audit_log_path: Path) -> dict | None:
    if not audit_log_path.exists():
        return None
    lines = [line for line in audit_log_path.read_text().splitlines() if line.strip()]
    if not lines:
        return None
    return json.loads(lines[-1])
