# Caching & Batching — Code Pack

Two cost levers for the Anthropic API, each as a runnable demo.

## Setup (once)
```bash
uv add anthropic python-dotenv streamlit    # or: pip install -r requirements.txt
cp .env.example .env                         # then paste your real key into .env
```

## Files

| File | What it teaches | How to run |
|------|-----------------|-----------|
| `pricing.py` | The one source of truth for all cost math. Edit rates here. | `python pricing.py` (prints sample math) |
| `01_caching_basics.py` | Smallest honest caching example: WRITE then READ, proven by `usage`. | `python 01_caching_basics.py` |
| `streamlit_caching_chat.py` | **The main demo.** A chat that caches itself, rebuilds every 5 turns, shows the bill live in USD. | `uv run streamlit run streamlit_caching_chat.py` |
| `02_batch_emails.py` | Batch API submit: 5 GrowwStacks prospects → one batch, saves the id, exits. | `python 02_batch_emails.py` |
| `streamlit_batch_app.py` | **The batch demo (visual).** 5-prospect email batch: submit, check status, collect, with a 50% cost breakdown. | `uv run streamlit run streamlit_batch_app.py` |
| `03_batch_check.py` | Batch API collect: checks status, gathers the emails when ready, shows 50% saving. | `python 03_batch_check.py` |

## The two levers, one question
- **Caching** — for real-time, repeated context. ~90% off the reused prefix. → the chat app.
- **Batching** — for bulk work, no one waiting. 50% off everything, within 24h. → the emails script.
- The tell: **"Is anyone waiting for this answer right now?"** Yes → cache. No → batch.

## Notes
- **Rolling history caching:** the chat caches the system prompt AND the conversation
  history (a cache_control breakpoint on the last message each turn). This is why the
  saving GROWS as the chat gets longer. Caching only the system prompt is the classic
  trap — the system prompt is small, so history + output dominate and the saving looks tiny.
- Model IDs: `claude-sonnet-5`, `claude-haiku-4-5-20251001`.
- Cache read = 10% of base input; 5m write = 1.25×, 1h write = 2×.
- The chat's "rebuild every 5 turns" is a teaching simulation of the real 5-minute
  window — the real `cache_control` marker is sent on every call, and the actual API
  usage is shown in the "Behind the scenes" expander.
- If `streamlit` says "command not found", use `uv run streamlit run ...`.
