"""STRETCH: the access desk built from the spec.

One router applies the entitlement policy and decides Agent-vs-Human. Two
read-only subagents verify identity and look up entitlements. One write
subagent records the audit ticket -- the only agent ever handed a write
tool. The router itself is never handed any desk tool at all: its base
tool set is restricted to just "Agent" (subagent delegation), so it is
architecturally incapable of writing a ticket or reading HR data directly,
regardless of what its prompt says.

Run:
    uv run python d20_access_desk/stretch/access_desk.py
"""

from __future__ import annotations

import asyncio
from pathlib import Path

from claude_agent_sdk import (
    AgentDefinition,
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    TextBlock,
    ToolUseBlock,
    create_sdk_mcp_server,
)

from tools import append_audit_ticket, get_employee, get_entitlement

AUDIT_LOG = Path(__file__).parent / "audit_log.jsonl"

ROUTER_PROMPT = """You are the IT access-desk router. You have no tools except Agent
(subagent delegation) -- you cannot look up HR data or record a ticket yourself.

For every employee request:
1. Delegate to identity_reader to verify the requester exists (pass their employee_id).
   If unknown, stop and report that instead of guessing.
2. Delegate to entitlement_reader to look up what that employee's role may self-serve.
3. Decide decision_owner: "Agent" only if the requested resource is explicitly in that
   role's self-serve list; "Human" for anything privileged, unrecognized, or that is
   really a request to talk to a human (use resource "manager_escalation" for those).
4. Delegate to ticket_writer exactly once, at the end, passing requester, resource,
   action, and your decision_owner.
Then give the employee a short, plain reply."""


def build_options() -> ClaudeAgentOptions:
    server = create_sdk_mcp_server(
        "desk", tools=[get_employee, get_entitlement, append_audit_ticket]
    )
    agents = {
        "identity_reader": AgentDefinition(
            description="Looks up an employee's identity, department, and manager. Read-only.",
            prompt="Call get_employee with the given employee_id and report exactly what "
            "it returns, including an honest 'unknown' for an unrecognized id.",
            tools=["mcp__desk__get_employee"],
            mcpServers=["desk"],
        ),
        "entitlement_reader": AgentDefinition(
            description="Looks up what a role may self-serve. Read-only.",
            prompt="Call get_entitlement with the given role and report exactly what it returns.",
            tools=["mcp__desk__get_entitlement"],
            mcpServers=["desk"],
        ),
        "ticket_writer": AgentDefinition(
            description="Records one audit ticket. The only agent that can write.",
            prompt="Call append_audit_ticket exactly once with the requester, resource, "
            "action, and decision_owner you were given, unchanged. Report what was recorded.",
            tools=["mcp__desk__append_audit_ticket"],
            mcpServers=["desk"],
        ),
    }
    return ClaudeAgentOptions(
        system_prompt=ROUTER_PROMPT,
        mcp_servers={"desk": server},
        agents=agents,
        tools=["Agent"],  # the router's entire built-in tool set is "delegate"
        allowed_tools=["Agent"],
    )


async def run_case(request: str) -> None:
    print(f"\n=== request: {request} ===")
    async with ClaudeSDKClient(options=build_options()) as client:
        await client.query(request)
        async for message in client.receive_response():
            if isinstance(message, AssistantMessage):
                for block in message.content:
                    if isinstance(block, TextBlock):
                        print(f"[router] {block.text}")
                    elif isinstance(block, ToolUseBlock):
                        print(f"[tool] {block.name}({block.input})")


async def main() -> None:
    AUDIT_LOG.unlink(missing_ok=True)
    await run_case('Employee "alice" requests: "unlock my account, I got locked out."')
    await run_case('Employee "alice" requests: "add me to the Finance-Admins group."')
    await run_case('Employee "alice" requests: "let me talk to my manager about my access."')

    print(f"\n--- audit log ({AUDIT_LOG.name}) ---")
    print(AUDIT_LOG.read_text())


if __name__ == "__main__":
    asyncio.run(main())
