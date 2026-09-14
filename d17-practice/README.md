# Day 17 — CORE + APPLIED

Two single-tool agents on the Claude Agent SDK. The SDK runs the agentic loop;
the rules live in a Skill, not in the system prompt.

- **CORE** (`agent.py`) — order-support agent; the exercise is finding why a
  named Skill silently never loads.
- **APPLIED** (`applied_agent.py`) — a personal diet-tracking agent, the same
  pattern on a real task. [Jump to APPLIED](#day-17-applied--personal-diet-tracker).

---

# Day 17 CORE — Fix the Agent That Guesses

A single-tool order-support agent built on the Claude Agent SDK. The SDK runs the
agentic loop; the rules live in a Skill, not in the system prompt.

## Files

| Path | Role |
|---|---|
| `agent.py` | The tool (`get_order_status`), fake order data, the `ClaudeAgentOptions` block, and the message-stream reader |
| `.claude/skills/order-support/SKILL.md` | The behaviour rules: always look up, never guess, admit not-found, keep it short |

## Run

```bash
uv run python agent.py "What's the status of order A1002?"
uv run python agent.py "Where is order Z9999?"      # not in the data — must say so, not invent
```

Auth comes from the logged-in `claude` CLI — no `ANTHROPIC_API_KEY` / `.env` needed.

Real order IDs in the fake data: `A1001` (delivered), `A1002` (in transit), `A1003` (processing).

## The bug this exercise is about

`skills=["order-support"]` only *names* the Skill. The SDK spawns the `claude`
CLI as a subprocess, and that subprocess has to **find `SKILL.md` on disk** and
inject it into the system prompt before the first model call. Two options make
that possible, and the assignment's starter block had neither:

```python
cwd=os.path.dirname(os.path.abspath(__file__)),  # where the CLI looks for .claude/skills/
setting_sources=["project"],                     # permission to read project config
```

Without `cwd`, the CLI looks relative to wherever you launched the process, not
where the script lives. A filter (`skills=[...]`) that matches zero discovered
skills is **not an error** — so the agent starts fine and just answers without
its rules. The only signal is line 1 of output: `Skill 'order-support' loaded: False`.

> Version note: in `claude-agent-sdk` 0.2.152, a non-empty `skills=[...]` list
> auto-defaults `setting_sources=["user","project"]`, so the still-live half of
> the bug is `cwd`. Both lines are kept — correct and version-proof.

## Success criteria

- Startup prints `Skill 'order-support' loaded: True`
- A real order returns its real status/carrier/ETA, with a `[tool]` line proving the tool was called
- A fake order ID produces an honest "not found", not an invented order

---

## Part B — Self-Test

**1. An agent runs with no errors but keeps inventing data its Skill forbids.
What single line of output tells you the Skill didn't load, and what two options
fix it?**

The startup line `Skill '<name>' loaded: False`. It means the Skill was named but
never discovered so a current working directory needs to be set (cwd) with the skill location and setting_sources=['project] to give Claude the permission to read the skill within the project directory. 

**2. Why is a silent failure (wrong answer, no error) more dangerous in
production than a loud one (a crash)?**

A silent failure in production does not tell anyone that it is ocurring so it may be duplicated for very long until somebody directly looks for it. A loud crash will immediately page an engineer and disallow further issues that may occur in a production setting. 

---

# Day 17 APPLIED — Personal Diet Tracker

**One job:** *answer questions about my diet by looking up my daily goals and
what I've eaten so far.* Same SDK pattern as CORE, one tool, fake data.

## Files

| Path | Role |
|---|---|
| `applied_agent.py` | The tool (`get_diet_status`), fake `GOALS` / `LOG` / `REFERENCE_PER_100G` data, the options block, the stream reader |
| `.claude/skills/diet-coach/SKILL.md` | Rules: always look up, never guess goals/log/totals, convert to grams using the tool's reference table, admit when a food or date is missing |

## Run

```bash
uv run python applied_agent.py "How am I tracking on calories today?"
uv run python applied_agent.py "How many grams of chicken breast should I eat to hit my protein goal for the rest of today?"
uv run python applied_agent.py "How many grams of salmon should I eat for dinner?"   # not in reference — must admit it
```

The one tool `get_diet_status(date)` returns, for a given day (default today):
the calorie/protein goals, every logged meal, consumed totals, what remains, and
reference macros per 100 g for chicken breast / rice / egg / almonds. The model
does the arithmetic and the food conversion; it never sources the numbers
itself.

Logged days in the fake data: `2026-09-08` (today, partial) and `2026-09-07` (full).

## Test run — observed behaviour

| Question | Result |
|---|---|
| *How many grams of chicken breast to hit my protein goal for the rest of today?* | `loaded: True`, `[tool]` line, then **345 g** — 107 g protein remaining ÷ 31 g per 100 g, reference stated |
| *How am I tracking on calories today?* | `[tool]` line, then "650 of 2200 logged, 1550 remaining" — grounded in the log |
| *How many grams of salmon should I eat?* (no reference macros) | calls the tool, then "I don't have macro values for salmon" — **no invented numbers** |
| *What did I eat on 2026-08-30?* (no log) | calls the tool, then "No diet log found for that date" |

## Success criteria — met

- Startup prints `Skill 'diet-coach' loaded: True`.
- Both real questions produce a `[tool]` line and a grounded answer.
- The salmon question produces an honest "I don't have that", no invention.
- A teammate can read `diet-coach/SKILL.md` and know exactly what the agent does.

## Part B — Self-Test (about this agent)

**1. Which parts of your agent did the SDK run for you, and which did you have to
declare yourself?**

The SDK ran the whole loop: send the prompt to the model, detect the tool-use
request, dispatch it to `get_diet_status`, feed the result back, decide when to
stop (`max_turns` / no more tool calls), enforce `permission_mode` and the
allow-list, discover the Skill and inject it into the system prompt, and carry
the MCP messages back and forth. I declared: the tool function and its schema +
description, the fake data, the `SKILL.md` rules, the `ClaudeAgentOptions` block
(model + fallback, `mcp_servers`, `skills`, allow-list, `cwd`, `setting_sources`,
`permission_mode`, `max_turns`), and the message-stream reader that prints the
startup line, the `[tool]` lines, and `terminal_reason`.

**2. If your teammate's agent started guessing, what is the first line of output
you'd tell them to check, and why?**

`Skill '<name>' loaded:`. If it says `False`, the Skill was named in `skills=[...]`
but never discovered, so its "always look up / never guess" rules never reached
the model — and nothing errored, because a skill filter that matches nothing is
a normal outcome. Tell them to set `cwd` to the script's own directory and add
`setting_sources=["project"]`.