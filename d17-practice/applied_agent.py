"""Day 17 APPLIED — personal diet-tracking agent.

One job: answer questions about the user's diet by looking up their daily goals
and what they've logged so far. The SDK runs the agentic loop; the rules live in
.claude/skills/diet-coach/SKILL.md. One tool: get_diet_status.

Run:  uv run python applied_agent.py "How am I tracking on calories today?"
"""

import os
import sys

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
TODAY = "2026-09-08"

# --- fake data -----------------------------------------------------------
GOALS = {"calories": 2200, "protein_g": 165, "carbs_g": 220, "fat_g": 70}

LOG = {
    "2026-09-08": {
        "meals": [
            {"meal": "breakfast", "items": "oats 80g + whey scoop + banana",
             "calories": 520, "protein_g": 38},
            {"meal": "snack", "items": "greek yogurt 200g",
             "calories": 130, "protein_g": 20},
        ],
    },
    "2026-09-07": {
        "meals": [
            {"meal": "breakfast", "items": "3 eggs + toast", "calories": 440, "protein_g": 26},
            {"meal": "lunch", "items": "chicken rice bowl", "calories": 680, "protein_g": 52},
            {"meal": "dinner", "items": "salmon + potatoes + salad", "calories": 720, "protein_g": 46},
            {"meal": "snack", "items": "protein bar", "calories": 210, "protein_g": 20},
        ],
    },
}

REFERENCE_PER_100G = {
    "chicken breast": {"calories": 165, "protein_g": 31},
    "white rice (cooked)": {"calories": 130, "protein_g": 2.7},
    "egg": {"calories": 155, "protein_g": 13},
    "almonds": {"calories": 579, "protein_g": 21},
}


# --- the one tool ------------------------------------------------------
@tool(
    "get_diet_status",
    "Look up the user's diet for a given day (default today): their daily "
    "calorie/protein/carb/fat goals, every meal logged so far with totals, how "
    "much of each target remains, and reference macros per 100 g for a few "
    "common foods. Call this for every question about what or how much the user "
    "should eat or how they are tracking. It is the only source of truth for "
    "goals and logged intake.",
    {"date": str},
)
async def get_diet_status(args):
    date = str(args.get("date") or "today").strip().lower()
    if date in ("today", ""):
        date = TODAY

    day = LOG.get(date)
    if day is None:
        return {"content": [{"type": "text",
                             "text": f"NOT FOUND: no diet log for {date}."}]}

    consumed = {
        "calories": sum(m["calories"] for m in day["meals"]),
        "protein_g": sum(m["protein_g"] for m in day["meals"]),
    }
    remaining = {
        "calories": GOALS["calories"] - consumed["calories"],
        "protein_g": GOALS["protein_g"] - consumed["protein_g"],
    }
    meal_lines = "\n".join(
        f"  - {m['meal']}: {m['items']} ({m['calories']} kcal, {m['protein_g']} g protein)"
        for m in day["meals"]
    )
    ref_lines = "\n".join(
        f"  - {food}: {v['calories']} kcal, {v['protein_g']} g protein"
        for food, v in REFERENCE_PER_100G.items()
    )
    text = (
        f"Diet status for {date}\n"
        f"goals: {GOALS['calories']} kcal, {GOALS['protein_g']} g protein\n"
        f"logged:\n{meal_lines}\n"
        f"consumed so far: {consumed['calories']} kcal, {consumed['protein_g']} g protein\n"
        f"remaining: {remaining['calories']} kcal, {remaining['protein_g']} g protein\n"
        f"reference_per_100g:\n{ref_lines}"
    )
    return {"content": [{"type": "text", "text": text}]}


diet_server = create_sdk_mcp_server(
    name="diet", version="1.0.0", tools=[get_diet_status]
)

options = ClaudeAgentOptions(
    model=MODEL,
    fallback_model=MODEL,
    system_prompt="You are a concise personal diet-tracking assistant.",
    mcp_servers={"diet": diet_server},
    skills=["diet-coach"],
    allowed_tools=["mcp__diet__get_diet_status", "Skill"],
    permission_mode="dontAsk",
    max_turns=MAX_TURNS,
    cwd=os.path.dirname(os.path.abspath(__file__)),
    setting_sources=["project"],
)


def _skill_loaded(init_data: dict) -> bool:
    """True if the 'diet-coach' skill made it into the model's context."""
    skills = init_data.get("skills")
    blob = repr(skills) if skills is not None else repr(init_data)
    return "diet-coach" in blob


async def main() -> None:
    prompt = (
        sys.argv[1]
        if len(sys.argv) > 1
        else "How many grams of chicken breast should I eat to hit my protein goal for the rest of today?"
    )
    print(f"> {prompt}\n")

    async for message in query(prompt=prompt, options=options):
        if isinstance(message, SystemMessage) and message.subtype == "init":
            loaded = _skill_loaded(message.data)
            print(f"Skill 'diet-coach' loaded: {loaded}")
            if not loaded:
                print(f"   (init skills payload: {message.data.get('skills')!r})")
            print()
        elif isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)
                elif isinstance(block, ToolUseBlock):
                    if block.name.startswith("mcp__") or block.name == "Skill":
                        print(f"[tool] {block.name}({block.input})")
        elif isinstance(message, ResultMessage):
            print(f"\nterminal_reason: {message.terminal_reason}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
