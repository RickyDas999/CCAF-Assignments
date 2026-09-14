"""Day 17 CORE — order-support agent.

The SDK runs the agentic loop. Our rules live in .claude/skills/order-support/SKILL.md.
One tool: get_order_status.

Run:  uv run python agent.py "What's the status of order A1002?"
"""

import sys
import os

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    SystemMessage,
    TextBlock,
    ToolUseBlock,
    create_sdk_mcp_server,
    query,
    tool,
)
from dotenv import load_dotenv

load_dotenv()

MODEL = "claude-sonnet-4-5"
MAX_TURNS = 6

# --- fake data -------------------------------------------------------------
ORDERS = {
    "A1001": {"status": "delivered", "carrier": "UPS", "eta": "2026-09-01 (delivered)"},
    "A1002": {"status": "in transit", "carrier": "FedEx", "eta": "2026-09-10"},
    "A1003": {"status": "processing", "carrier": "not yet assigned", "eta": "2026-09-14"},
}


# --- the one tool ---------------------------------------------------------
@tool(
    "get_order_status",
    "Look up the live status, carrier, and ETA of a customer order by its order "
    "ID (e.g. 'A1002'). Call this for every question about a specific order; it "
    "is the only source of truth for order facts.",
    {"order_id": str},
)
async def get_order_status(args):
    order_id = str(args["order_id"]).strip().upper()
    record = ORDERS.get(order_id)
    if record is None:
        text = f"NOT FOUND: no order with ID {order_id!r} exists in the system."
    else:
        text = (
            f"Order {order_id}: status={record['status']}, "
            f"carrier={record['carrier']}, eta={record['eta']}."
        )
    return {"content": [{"type": "text", "text": text}]}


orders_server = create_sdk_mcp_server(
    name="orders", version="1.0.0", tools=[get_order_status]
)

# --- options (BROKEN — see the assignment) ------------------------------
# Missing two lines. Read the first line of output before you touch anything.
options = ClaudeAgentOptions(
    model=MODEL,
    fallback_model=MODEL,
    system_prompt="You are a concise order-support agent.",
    mcp_servers={"orders": orders_server},
    skills=["order-support"],  # names the Skill...
    allowed_tools=["mcp__orders__get_order_status", "Skill"],
    permission_mode="dontAsk",
    max_turns=MAX_TURNS,
    cwd=os.path.dirname(os.path.abspath(__file__)),
    setting_sources=["project"]
)


def _skill_loaded(init_data: dict) -> bool:
    """True if the 'order-support' skill made it into the model's context."""
    skills = init_data.get("skills")
    blob = repr(skills) if skills is not None else repr(init_data)
    return "order-support" in blob


async def main() -> None:
    prompt = sys.argv[1] if len(sys.argv) > 1 else "What's the status of order A1002?"
    print(f"> {prompt}\n")

    async for message in query(prompt=prompt, options=options):
        if isinstance(message, SystemMessage) and message.subtype == "init":
            loaded = _skill_loaded(message.data)
            print(f"Skill 'order-support' loaded: {loaded}")
            if not loaded:
                # show what the CLI reported, so the failure isn't silent
                print(f"   (init skills payload: {message.data.get('skills')!r})")
            print()
        elif isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)
                elif isinstance(block, ToolUseBlock):
                    # Only show our tool and the Skill invocation; hide SDK-internal
                    # plumbing like ToolSearch.
                    if block.name.startswith("mcp__") or block.name == "Skill":
                        print(f"[tool] {block.name}({block.input})")
        elif isinstance(message, ResultMessage):
            print(f"\nterminal_reason: {message.terminal_reason}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
