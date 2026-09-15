"""CORE Part A, steps 3-6: the fix.

Same agent, same prompt style, but the resolve_request tool now loads
entitlement_policy.json and computes is_privileged(resource) in code
*before* the agent's proposed decision_owner is trusted at all. If the
resource is privileged, the code overrides decision_owner to "Human"
regardless of what the model said, writes the ticket, and -- separately,
in plain Python, not inside the tool -- pages the approver whenever the
logged ticket says Human.

Run:
    uv run python d20_access_desk/core/fixed_agent.py "add me to the Finance-Admins group"
    uv run python d20_access_desk/core/fixed_agent.py "reset my password"
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    TextBlock,
    ToolUseBlock,
    create_sdk_mcp_server,
    tool,
)

from common import append_audit_ticket, is_privileged, load_policy, page_approver, resource_enum

AUDIT_LOG = Path(__file__).parent / "audit_log_fixed.jsonl"

# The prompt no longer mentions a pager or "check with a human" -- the
# agent doesn't need to know the boundary exists. It just proposes.
SYSTEM_PROMPT = """You are an IT access-desk agent.
Resolve the employee's request and call resolve_request to record the outcome.
Propose a decision_owner of "Agent" for requests you believe are routine."""

# Resource is an enum pulled from entitlement_policy.json, not free text --
# the agent picks a name the code already knows how to classify, instead of
# describing the request in its own words.
_INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "requester": {"type": "string"},
        "resource": {"type": "string", "enum": resource_enum()},
        "action": {"type": "string"},
        "decision_owner": {"type": "string"},  # proposed -- not trusted as-is
    },
    "required": ["requester", "resource", "action", "decision_owner"],
}


@tool(
    "resolve_request",
    "Record the resolution of an access request in the audit log.",
    _INPUT_SCHEMA,
)
async def resolve_request(args: dict) -> dict:
    policy = load_policy()
    privileged = is_privileged(args["resource"], policy)

    ticket = dict(args)
    if privileged:
        # Code overrides the model's label. This line is the entire fix.
        ticket["decision_owner"] = "Human"

    ticket = append_audit_ticket(AUDIT_LOG, ticket)

    outcome = (
        "escalated to a human -- no access was granted"
        if ticket["decision_owner"] == "Human"
        else "resolved by the agent"
    )
    return {"content": [{"type": "text", "text": f"Ticket recorded, {outcome}: {ticket}"}]}


async def main(request_text: str) -> None:
    server = create_sdk_mcp_server("access_desk_fixed", tools=[resolve_request])
    options = ClaudeAgentOptions(
        system_prompt=SYSTEM_PROMPT,
        mcp_servers={"desk": server},
        allowed_tools=["mcp__desk__resolve_request"],
    )

    async with ClaudeSDKClient(options=options) as client:
        await client.query(
            f'Employee "alice" requests: "{request_text}". '
            "Resolve it and call resolve_request to record the outcome, using "
            "the resource enum value that best matches the request."
        )
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"[agent] {block.text}")
                    elif isinstance(block, ToolUseBlock):
                        print(f"[tool] {block.name}({block.input})")

    lines = AUDIT_LOG.read_text().splitlines()
    last_ticket_line = lines[-1] if lines else "(empty)"
    print(f"\n--- last audit row ({AUDIT_LOG.name}) ---")
    print(last_ticket_line)

    if lines:
        import json

        ticket = json.loads(last_ticket_line)
        # Plain code, run after the agent is done, pages a human based only
        # on the label in the ticket that was just read back off disk.
        result = page_approver(ticket)
        print(f"page_approver: {result}")


if __name__ == "__main__":
    text = sys.argv[1] if len(sys.argv) > 1 else "add me to the Finance-Admins group"
    asyncio.run(main(text))
