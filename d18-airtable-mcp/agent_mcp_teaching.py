"""
agent_mcp_teaching.py -- Day 18: the Agent SDK + MCP, pointed at a REAL Airtable base.

THE ONE IDEA
    The tools this agent uses are NOT ours. They live on Airtable's MCP server.
    We wrote none of them -- we only connect, and the server hands over its catalogue.

THE FOUR STEPS (all inside the MCP SETUP block below)
    1. CONNECT   -- a URL + a token, keyed by the nickname "airtable"
    2. RESTRICT  -- an allow-list of the few READ tools we permit
    3. BRIEF     -- a system prompt telling the agent what base to look at
    4. RUN       -- one `async for`. The SDK owns the loop.

PROOF
    - The FIRST printed line reports how many Airtable tools were DISCOVERED.
      We never listed them; the server did.
    - A real question prints a [tool] line, then an answer from an actual row.

Run:
    cd d18_airtable
    uv run agent_mcp_teaching.py                       # default read question
    uv run agent_mcp_teaching.py "your question here"  # ask your own
    uv run agent_mcp_teaching.py --blocked             # STRETCH: prove a write is denied
"""

import asyncio
import os
import sys

from dotenv import load_dotenv

# THE RENAME TRAP: the package is claude_agent_sdk, NOT anthropic.
from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    SystemMessage,
    TextBlock,
    ToolResultBlock,
    ToolUseBlock,
    UserMessage,
    query,
)

HERE = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(HERE, ".env"))

MODEL = "claude-haiku-4-5-20251001"
MAX_TURNS = 8


#  ======================================================================
#  === MCP SETUP : START ================================================

# --- 1. CONNECT ------------------------------------------------------------
# Everything comes from .env, never hard-coded. Point AIRTABLE_MCP_URL at a
# different MCP server and this same agent has different powers.
AIRTABLE_MCP_URL = os.environ["AIRTABLE_MCP_URL"]
AIRTABLE_TOKEN = os.environ["AIRTABLE_MCP_TOKEN"]

# THE FOUR LINES THAT ADD THE WHOLE AIRTABLE TOOLSET.
# "airtable" is our local nickname -> tools arrive as mcp__airtable__<tool>.
# "type": "http" is the transport (a remote server). A local server would be
# "type": "stdio" -- same protocol, different pipe.
MCP_SERVERS = {
    "airtable": {
        "type": "http",
        "url": AIRTABLE_MCP_URL,
        "headers": {"Authorization": f"Bearer {AIRTABLE_TOKEN}"},
    }
}

# --- 2. RESTRICT ---------------------------------------------------------
# The server exposes ~46 tools, including create/update/delete. MCP tools are
# DENIED by default; connecting makes them POSSIBLE, this allow-list makes them
# PERMITTED. We permit READ tools only -- no wildcard mcp__airtable__* (that
# would grant every tool, including delete_table).
READ_TOOLS = [
    "search_records",
    "list_records_for_table",
    "get_table_schema", 
]
ALLOWED_TOOLS = [f"mcp__airtable__{name}" for name in READ_TOOLS]

# --- 3. BRIEF ----------------------------------------------------------
# Pinned IDs from .env so the agent does not burn turns discovering the base.
BASE_ID = os.environ["AIRTABLE_BASE_ID"]
TABLE_ID = os.environ["AIRTABLE_TABLE_ID"]

SYSTEM_PROMPT = f"""You answer questions about a real Airtable base by calling the
Airtable MCP tools. Never guess -- every answer must come from a record you
actually retrieved with a tool call.

Use these IDs directly. Do NOT call search_bases, list_bases, or list_tables:
    baseId  = {BASE_ID}
    tableId = {TABLE_ID}

The table is a small order tracker. Each row has:
    - an order name, e.g. "Order 1002"
    - a Status: one of "To do", "In progress", "Done"
    - an item name, e.g. "Item 2"

Prefer a single search_records call (query = the order number) and answer from
what comes back. If a record is not found, say so plainly.
Keep answers to one or two sentences.
"""

# STRETCH demo only: a prompt that TELLS the agent to write, so it actually
# attempts update_records_for_table -- and the allow-list, not the prompt, is
# what stops the call.
BLOCKED_DEMO_PROMPT = f"""You maintain a real Airtable order tracker.
baseId = {BASE_ID}, tableId = {TABLE_ID}.
When asked to change a record, find it with search_records, then update it with
mcp__airtable__update_records_for_table. Do it directly; do not ask permission.
"""


# --- 4. OPTIONS ------------------------------------------------------------
def build_options(system_prompt: str = SYSTEM_PROMPT) -> ClaudeAgentOptions:
    return ClaudeAgentOptions(
        model=MODEL,
        fallback_model=MODEL,
        system_prompt=system_prompt,
        mcp_servers=MCP_SERVERS,          # <<< the MCP line
        allowed_tools=ALLOWED_TOOLS,
        # Deny the built-ins by name so the agent can reach Airtable and nothing
        # else. NOT `tools=[]` -- that would kill the MCP tools too.
        disallowed_tools=[
            "Bash", "Write", "Edit", "Read", "Glob", "Grep",
            "WebSearch", "WebFetch", "Task",
        ],
        # "default": tools on ALLOWED_TOOLS run with no prompt; anything else is
        # auto-DENIED (the run does not hang, and the denial shows up on the
        # ResultMessage). This is what makes the allow-list a real boundary.
        #
        # NOTE: the handout says "bypassPermissions" here. In this SDK version
        # (claude-agent-sdk 0.2.144) bypassPermissions auto-approves EVERYTHING,
        # so an un-allowed write would still go through -- the allow-list stops
        # being the boundary. "default" is the correct choice for a script that
        # must not touch anything outside its allow-list.
        permission_mode="default",
        max_turns=MAX_TURNS,
        cwd=HERE,
    )


#  === MCP SETUP : END ==================================================
#  ======================================================================


async def run(question: str, system_prompt: str = SYSTEM_PROMPT) -> None:
    print(f"Question: {question}\n")
    async for message in query(prompt=question, options=build_options(system_prompt)):
        if isinstance(message, SystemMessage) and message.subtype == "init":
            tools = [t for t in (message.data or {}).get("tools", []) if "airtable" in t]
            print(f"Connected. Airtable tools discovered: {len(tools)}")
            print(f"Permission mode: {(message.data or {}).get('permissionMode')}\n")

        elif isinstance(message, (AssistantMessage, UserMessage)):
            if isinstance(message.content, str):
                continue
            for block in message.content or []:
                if isinstance(block, ToolUseBlock):
                    print(f"    [tool] {block.name.split('__')[-1]}({block.input})")
                elif isinstance(block, ToolResultBlock):
                    text = str(block.content)[:200].replace("\n", " ")
                    print(f"    [result] {text}")
                elif isinstance(block, TextBlock) and block.text.strip():
                    print(f"\nClaude: {block.text.strip()}")

        elif isinstance(message, ResultMessage):
            denials = message.permission_denials or []
            print(
                f"\nFinished in {message.num_turns} turn(s). "
                f"denied tool calls: {len(denials)} "
                f"cost: ${message.total_cost_usd or 0:.4f}"
            )
            for d in denials:
                print(f"    denied: {d.get('tool_name')}")


if __name__ == "__main__":
    args = sys.argv[1:]
    if args and args[0] == "--blocked":
        asyncio.run(run("Mark Order 1002 as Done.", BLOCKED_DEMO_PROMPT))
    elif args:
        asyncio.run(run(" ".join(args)))
    else:
        asyncio.run(run("What is the status of Order 1002, and what item is on it?"))
