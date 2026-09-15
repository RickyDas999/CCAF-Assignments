"""The access desk's three tools: two read-only, one write.

Capability, not instruction: a reader is only ever handed the read tools
below, and only ticket_writer is ever handed append_audit_ticket. See
access_desk.py for how each subagent's allow-list enforces that split.
"""

from __future__ import annotations

import sys
from pathlib import Path

from claude_agent_sdk import tool

from fake_data import EMPLOYEES, ROLE_ENTITLEMENTS

sys.path.insert(0, str(Path(__file__).parent.parent / "core"))
from common import append_audit_ticket as _append_audit_ticket  # noqa: E402
from common import is_privileged, load_policy, page_approver, resource_enum  # noqa: E402

AUDIT_LOG = Path(__file__).parent / "audit_log.jsonl"

# Resources the writer will accept, plus a catch-all for requests that
# don't map to a named resource at all (e.g. "let me talk to my manager").
# Anything outside the policy's self_serve list -- including this catch-all
# -- is privileged by the same fail-closed rule as CORE.
_RESOURCE_ENUM = resource_enum() + ["manager_escalation"]


@tool("get_employee", "Look up an employee's identity, department, and manager.", {"employee_id": str})
async def get_employee(args: dict) -> dict:
    record = EMPLOYEES.get(args["employee_id"], {"status": "unknown"})
    return {"content": [{"type": "text", "text": str(record)}]}


@tool("get_entitlement", "Look up what a role may self-serve.", {"role": str})
async def get_entitlement(args: dict) -> dict:
    self_serve = ROLE_ENTITLEMENTS.get(args["role"])
    record = {"role": args["role"], "self_serve": self_serve} if self_serve is not None else {"status": "unknown"}
    return {"content": [{"type": "text", "text": str(record)}]}


@tool(
    "append_audit_ticket",
    "Record one audit ticket for a resolved access request. The only tool that writes.",
    {
        "type": "object",
        "properties": {
            "requester": {"type": "string"},
            "resource": {"type": "string", "enum": _RESOURCE_ENUM},
            "action": {"type": "string"},
            "decision_owner": {"type": "string"},  # proposed by the router -- not trusted as-is
        },
        "required": ["requester", "resource", "action", "decision_owner"],
    },
)
async def append_audit_ticket(args: dict) -> dict:
    policy = load_policy()
    ticket = dict(args)
    if is_privileged(ticket["resource"], policy):
        # Same override as CORE's fix, now living at the one place that
        # can ever write a ticket instead of inside a router-owned tool.
        ticket["decision_owner"] = "Human"

    ticket = _append_audit_ticket(AUDIT_LOG, ticket)
    page_result = page_approver(ticket)
    return {"content": [{"type": "text", "text": f"Recorded: {ticket} | page_approver: {page_result}"}]}
