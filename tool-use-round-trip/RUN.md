# Day 12 — the `tool_use` round-trip

One client tool, `get_order`, reading the live **CCAF-Demo** Google Sheet.
Two ways to run it; both import the same tool from `sheet.py`.

## Setup — one command

```bash
uv sync
```

That reads `uv.lock` and builds the exact same environment on any machine.
Then add your key:

```bash
cp .env.example .env      # paste a real ANTHROPIC_API_KEY
```

`service-account.json` ships with the folder and the sheet is already shared
with `ccaf-sheet-bot@booming-monitor-457114-g8.iam.gserviceaccount.com`.

## Run

```bash
uv run streamlit run tools_streamlit.py    # the UI  → http://localhost:8501
uv run python tools.py                     # the terminal walk-through
uv run python tools.py "Has ORD005 shipped?"
```

No `activate`, no `pip install`. `uv run` resolves the environment itself.

## The five tabs

| Tab | What you show |
|---|---|
| ① Round-trip | Ask on the left, four colour-coded step cards build on the right |
| ② Three kinds of tool | client user-defined · client Anthropic-schema · server (slides 5–6) |
| ③ stop_reason | All six values, and the `while` loop that becomes an agent (slide 8) |
| ④ The messages list | The live four-line table — the memory (slide 13) |
| ⑤ The sheet | The real rows, so nobody thinks the data is faked |

Teaching order that works: **⑤ → ① → ② → ③ → ④.**
Show the real data first, run one question, then explain what they just saw.

## Sample questions

| Question | What the class sees |
|---|---|
| `Where is order ORD002?` | Shipped, 2026-07-18 — one clean round-trip |
| `Has ORD005 been delivered?` | Cancelled — Claude corrects the premise |
| `What is the status of ORD999?` | Miss — the tool returns an error string, Claude explains it |
| `Compare ORD001 and ORD003` | Two `tool_use` blocks — parallel tool use, loop runs twice |

Real IDs are `ORD001`–`ORD010`.

## The files

| File | What it is |
|---|---|
| `sheet.py` | The tool: `get_order`, its schema, the Sheets call. Both demos import this. |
| `tools.py` | The round-trip in the terminal, printing each step as it happens. |
| `tools_streamlit.py` | The round-trip in the browser, plus the four teaching tabs. |
| `pyproject.toml` + `uv.lock` | The pinned environment. `uv sync` reproduces it exactly. |

## The four steps (slide 7)

1. **Claude asks** — `stop_reason: "tool_use"`, plus a `tool_use` block carrying `id`, `name`, `input`.
2. **Your code runs** — `run_tool()` calls `get_order()`. Claude is paused; nothing moves until you reply.
3. **You return** — a `tool_result` carrying the **same `tool_use_id`**. Mismatch and the API rejects it.
4. **Claude continues** — `stop_reason: "end_turn"` and the sentence the user reads.

## Points to land

- A tool is a **labelled button**. Claude never presses it — it asks, your code presses.
- Key the loop off **`stop_reason`**, never off the prose.
- The **id is the claim ticket** — it pairs result to request.
- Append **both** messages in step 3: Claude's `tool_use` turn *and* your `tool_result`.
- Iterate `response.content` — Claude often writes a sentence before the `tool_use` block.
- The `tool_result` travels in a **user** message. You are speaking back to Claude.
