"""
Day 12 - the tool_use round-trip, in the terminal.

    python tools.py                       # runs the sample query
    python tools.py "Where is A-1044?"    # runs your own query
"""

import os
import sys
import json

from dotenv import load_dotenv
from anthropic import Anthropic

from sheet import TOOLS, run_tool

load_dotenv()

# Claude's answers can contain characters the Windows console cannot print in
# its default codepage (the rupee sign, em dashes). Print as UTF-8 instead.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

MODEL = "claude-haiku-4-5-20251001"
SAMPLE_QUERY = "Who ordered ORD002, and what did they buy?"


def main():
    question = sys.argv[1] if len(sys.argv) > 1 else SAMPLE_QUERY

    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("ANTHROPIC_API_KEY missing. Copy .env.example to .env and fill it in.")
        return

    client = Anthropic(api_key=api_key)

    # The messages list IS the memory. Every step below appends to it.
    messages = [{"role": "user", "content": question}]
    print(f"\nUser: {question}")

    turn = 0
    while True:
        # STEP 1 / STEP 4 - Claude asks for a tool, or answers.
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            tools=TOOLS,               # <- handing Claude the buttons
            messages=messages,
        )
        print(f"\nstop_reason = {response.stop_reason}")

        # Claude often writes a sentence BEFORE the tool_use block,
        # so we iterate the content list instead of assuming content[0].
        for block in response.content:
            if block.type == "text" and block.text.strip():
                print(f'Claude also said: "{block.text.strip()}"')
            elif block.type == "tool_use":
                print(json.dumps({"type": block.type, "id": block.id,
                                  "name": block.name, "input": block.input}, indent=2))

        if response.stop_reason != "tool_use":
            break
        turn += 1

        # STEP 2 - our code runs. Claude may ask for SEVERAL tools in one
        # response (parallel tool use), so we collect them all. Returning a
        # result for only the first is the classic error:
        # "tool_use ids were found without tool_result".
        tool_uses = [b for b in response.content if b.type == "tool_use"]
        results = []
        for tool_use in tool_uses:
            print(f"Calling  {tool_use.name}({tool_use.input!r})")
            results.append(run_tool(tool_use.name, tool_use.input))
            print(f"  {results[-1]}")

        # STEP 3 - we return the results. Both appends matter:
        # skipping the assistant turn breaks history.
        messages.append({"role": "assistant", "content": response.content})
        messages.append({
            "role": "user",
            "content": [
                {
                    "type": "tool_result",
                    "tool_use_id": tool_use.id,   # <- same id Claude sent us
                    "content": result,
                }
                for tool_use, result in zip(tool_uses, results)
            ],
        })

    answer = "".join(b.text for b in response.content if b.type == "text")
    print(f"\nClaude: {answer}")
    print(f"{turn} tool call(s).\n")


if __name__ == "__main__":
    main()
