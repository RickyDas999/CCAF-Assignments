# -*- coding: utf-8 -*-
"""
streamlit_caching_chat.py  —  a chat that caches itself, and shows the bill.

WHAT THE LEARNER SEES
    A normal chat, plus a panel that makes prompt caching VISIBLE:
      - a turn counter
      - each turn labelled WRITE (rebuild the cache) or READ (90% off)
      - the running cost, cached vs. what it WOULD have cost uncached
    A toggle turns caching ON/OFF so you can compare.

WHAT WE CACHE  (this is the important teaching point)
    We cache the WHOLE stable prefix — system prompt AND the frozen
    conversation history — not just the system prompt. We do this by putting a
    cache_control breakpoint on the LAST message each turn. As the chat grows,
    the growing history reads at 10%, so the saving gets BIGGER with length.

    A single breakpoint on only the system prompt is the classic trap: the
    system prompt is small, while history + output dominate, so the blended
    saving looks tiny. Caching the history is what makes it dramatic.

THE "REBUILD EVERY 5" RHYTHM  (a teaching simulation on top of the real thing)
    We count USER turns. When caching is ON:
        Turn 1  -> WRITE   (pay to store the prefix)
        Turns 2-5 -> READ  (ride the cache, 90% off)
        Turn 6  -> WRITE (rebuild), 7-10 READ, 11 WRITE ...
    The cost shown is driven by the REAL usage the API reports, so the numbers
    are honest; the WRITE/READ label is our countable story on top.

RUN IT
    uv run streamlit run streamlit_caching_chat.py
"""

import os

import streamlit as st
from anthropic import Anthropic
from dotenv import load_dotenv

import pricing

load_dotenv()

# ----------------------------------------------------------------------------
# The stable SYSTEM context. Big enough to be worth caching on its own.
# ----------------------------------------------------------------------------
SYSTEM_CONTEXT = (
    "You are GrowwStacks' friendly AI assistant. You help prospects understand "
    "how AI automation can save their team time. Keep answers short, warm, and "
    "concrete. GrowwStacks builds custom Claude-powered agents, MCP integrations, "
    "and workflow automations for businesses. Ask about the prospect's biggest "
    "time sinks, suggest one concrete automation, and keep a helpful, no-hype tone."
)
# NOTE: no padding. This is a real, short system prompt. Early turns won't clear
# the model's cache floor (1,024 tokens for Sonnet), so they simply won't cache —
# and the panel says so. As the conversation grows, the prefix crosses the floor
# and caching kicks in on its own. Honest, and the exact behaviour to teach.

REBUILD_EVERY = 5  # rebuild (WRITE) the cache once every N user turns

# ----------------------------------------------------------------------------
# Page setup
# ----------------------------------------------------------------------------
st.set_page_config(page_title="Caching Chat · GrowwStacks", page_icon="💬", layout="wide")

st.markdown(
    """
    <style>
      /* readable, never-clipped cost tiles */
      .cost-card {
        background: #F0EEE6; border: 1px solid #E3DFD3; border-radius: 10px;
        padding: 12px 10px; text-align: center; margin-bottom: 8px;
      }
      .cost-card .lbl {
        font-size: 0.70rem; letter-spacing: .03em; text-transform: uppercase;
        color: #6b6b63; margin-bottom: 4px;
      }
      .cost-card .val {
        font-size: 1.1rem; font-weight: 700; color: #1A1A17;
        font-variant-numeric: tabular-nums; white-space: nowrap;
      }
      .cost-card.saved .val { color: #2e7d32; }
      .cost-card.write .val { color: #C0562F; }

      /* the chat scrolls inside its own box; min-height keeps it from
         collapsing, but it grows with content instead of showing a big
         empty rectangle when the chat is short. */
      .chat-scroll {
        min-height: 120px; max-height: 68vh; overflow-y: auto;
        padding: 8px 14px;
      }

      /* FREEZE the right-hand cost panel: make the 2nd column stick to the
         top of the viewport so it stays put while the page/chat scrolls. */
      div[data-testid="stHorizontalBlock"] > div[data-testid="column"]:last-child {
        position: sticky;
        top: 4.5rem;
        align-self: flex-start;
        max-height: calc(100vh - 5rem);
        overflow-y: auto;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- session state ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "turn" not in st.session_state:
    st.session_state.turn = 0
if "ledger" not in st.session_state:
    st.session_state.ledger = []


def turn_kind(turn_number: int, caching_on: bool) -> str:
    """WRITE on turn 1, 6, 11, ...  READ otherwise.  OFF = no caching at all."""
    if not caching_on:
        return "OFF"
    return "WRITE" if (turn_number - 1) % REBUILD_EVERY == 0 else "READ"


def build_request(caching_on: bool, ttl: str, history):
    """
    Build (system, messages) for the call.

    KEY FIX: the cache breakpoint goes on the SYSTEM prompt AND on the last
    ASSISTANT message — the frozen tail of the history. NOT on the new user
    message. Why: the cache only reuses a prefix that is *identical* to a prior
    call. The newest user message has never been seen, so marking it just
    writes a throwaway entry that never gets read. The last assistant turn, by
    contrast, is stable — it's the same bytes the previous call already cached —
    so the whole prefix (system + settled turns) reads at 10%.
    """
    system = [{"type": "text", "text": SYSTEM_CONTEXT}]
    if caching_on:
        system[0]["cache_control"] = {"type": "ephemeral", "ttl": ttl}

    messages = [{"role": m["role"], "content": m["content"]} for m in history]

    if caching_on:
        # find the LAST assistant message and mark it — that's the frozen tail
        for i in range(len(messages) - 1, -1, -1):
            if messages[i]["role"] == "assistant":
                messages[i]["content"] = [
                    {
                        "type": "text",
                        "text": messages[i]["content"],
                        "cache_control": {"type": "ephemeral", "ttl": ttl},
                    }
                ]
                break
    return system, messages


def cost_card(label: str, value: str, kind: str = "") -> str:
    cls = f"cost-card {kind}".strip()
    return f"<div class='{cls}'><div class='lbl'>{label}</div><div class='val'>{value}</div></div>"


# ----------------------------------------------------------------------------
# SIDEBAR
# ----------------------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Settings")

    model = st.selectbox(
        "Model",
        options=list(pricing.MODELS.keys()),
        format_func=lambda k: pricing.MODELS[k]["label"],
    )

    caching_on = st.toggle(
        "Prompt caching",
        value=True,
        help="ON: cache the system prompt AND the conversation history "
             "(WRITE once, then READ at 90% off). OFF: pay full input price "
             "every turn — the baseline.",
    )

    ttl_label = st.radio(
        "Cache duration (TTL)",
        options=["5 minutes (1.25x write)", "1 hour (2x write)"],
        help="How long a cached prefix stays warm. Longer TTL costs more to write.",
        disabled=not caching_on,
    )
    ttl_choice = "1h" if ttl_label.startswith("1 hour") else "5m"

    st.divider()
    _min = pricing.MODELS[model]["cache_min_tokens"]
    if caching_on:
        st.caption(
            f"**Rhythm:** rebuild every **{REBUILD_EVERY}** turns — "
            f"1 WRITE + {REBUILD_EVERY - 1} READs per block.\n\n"
            "We cache the **system prompt + history** (breakpoint on the last "
            "assistant turn), so the longer the chat, the bigger the saving.\n\n"
            f"ℹ️ {pricing.MODELS[model]['label']} only caches a prefix of "
            f"**{_min:,}+ tokens** — shorter prefixes silently don't cache."
        )
    else:
        st.caption("**Caching OFF.** Every turn pays full input price.")

    if st.button("🔄 Reset conversation"):
        st.session_state.messages = []
        st.session_state.turn = 0
        st.session_state.ledger = []
        st.rerun()

# ----------------------------------------------------------------------------
# HEADER
# ----------------------------------------------------------------------------
st.title("💬 The self-costing chat")
st.caption("Prompt caching, made visible. Every turn shows whether it wrote or read the cache — and what it cost.")

if not os.getenv("ANTHROPIC_API_KEY"):
    st.error(
        "No API key found. Create a file named **.env** in this folder "
        "containing `ANTHROPIC_API_KEY=sk-ant-...your-key...`, then click "
        "**Rerun**. If you only edited `.env.example`, copy it to `.env` first."
    )
    st.stop()

client = Anthropic()

# ----------------------------------------------------------------------------
# LAYOUT
# ----------------------------------------------------------------------------
chat_col, panel_col = st.columns([3, 2.4], gap="large")

# --- process a new message FIRST (so the panel below reflects this turn) ----
prompt = st.chat_input("Ask about GrowwStacks automation...")
if prompt:
    st.session_state.turn += 1
    this_turn = st.session_state.turn
    kind = turn_kind(this_turn, caching_on)

    st.session_state.messages.append({"role": "user", "content": prompt})

    system, api_messages = build_request(
        caching_on, ttl_choice, st.session_state.messages
    )
    with st.spinner("Thinking..."):
        resp = client.messages.create(
            model=model, max_tokens=400, system=system, messages=api_messages,
        )
    answer = pricing.first_text(resp)
    st.session_state.messages.append({"role": "assistant", "content": answer})

    # ---- REAL receipt ----
    u = resp.usage
    real_write = getattr(u, "cache_creation_input_tokens", 0) or 0
    real_read = getattr(u, "cache_read_input_tokens", 0) or 0
    fresh_in = u.input_tokens          # NEW/dynamic input tokens (not from cache)
    out = u.output_tokens

    # ---- COST, broken into its real pieces so nothing is a black box ----
    # cached-eligible tokens this call (the stable prefix): read OR write.
    cached_now = real_read + real_write

    # piece 1: the cached prefix
    if caching_on and real_write > 0:          # this call WROTE the cache
        prefix_cost = pricing.cache_write_cost(model, real_write, ttl_choice)
        prefix_label = "cache write (1.25x)" if ttl_choice == "5m" else "cache write (2x)"
    elif caching_on and real_read > 0:         # this call READ the cache
        prefix_cost = pricing.cache_read_cost(model, real_read)
        prefix_label = "cache read (0.10x)"
    else:                                      # nothing cached (under floor / off)
        prefix_cost = pricing.input_cost(model, cached_now)
        prefix_label = "full price (not cached)"

    # piece 2: the new/dynamic input (your latest message) — always full price
    dynamic_cost = pricing.input_cost(model, fresh_in)
    # piece 3: the output — always full price, caching never touches it
    out_cost = pricing.output_cost(model, out)

    actual = prefix_cost + dynamic_cost + out_cost

    # the honest baseline: SAME tokens, but everything at full input price
    total_input = fresh_in + cached_now
    uncached = pricing.input_cost(model, total_input) + out_cost

    st.session_state.ledger.append(
        {
            "turn": this_turn, "kind": kind,
            "cached_tokens": cached_now, "fresh_in": fresh_in, "out": out,
            "actual": actual, "uncached": uncached, "saved": uncached - actual,
            "real_write": real_write, "real_read": real_read,
            # breakdown pieces:
            "prefix_cost": prefix_cost, "prefix_label": prefix_label,
            "dynamic_cost": dynamic_cost, "out_cost": out_cost,
            "total_input": total_input,
        }
    )

# --- LEFT: the conversation, inside a fixed-height scroll box ----------------
with chat_col:
    st.markdown("<div class='chat-scroll'>", unsafe_allow_html=True)
    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])
    st.markdown("</div>", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# RIGHT: the cost panel (pinned) — readable, in cents
# ----------------------------------------------------------------------------
with panel_col:
    st.subheader("📊 The bill, live")
    st.caption("Costs in **cents** (¢) — per-call amounts are fractions of a cent.")

    if not st.session_state.ledger:
        st.info("Send a message to see the caching rhythm and cost appear here.")
    else:
        latest = st.session_state.ledger[-1]

        if latest["kind"] == "WRITE":
            st.markdown(f"#### Turn {latest['turn']} · 🟠 CACHE WRITE")
            st.caption("Rebuilding the cache — we pay a little more to store the prefix.")
        elif latest["kind"] == "READ":
            st.markdown(f"#### Turn {latest['turn']} · 🟢 CACHE READ — 90% off")
            st.caption("Riding the cache — system + history cost 10% of normal.")
        else:
            st.markdown(f"#### Turn {latest['turn']} · ⚪ NO CACHING")
            st.caption("Full input price this turn — the baseline.")

        # Honest note: caching ON but nothing actually cached yet.
        if latest["kind"] in ("WRITE", "READ") and latest["cached_tokens"] == 0:
            _min = pricing.MODELS[model]["cache_min_tokens"]
            st.warning(
                f"Prefix still under {_min:,} tokens, so {pricing.MODELS[model]['label']} "
                "hasn't cached it yet — that's why saving is 0. Keep chatting; once the "
                "system prompt + history clears the threshold, reads kick in and the "
                "saving jumps."
            )

        write_flag = "write" if latest["kind"] == "WRITE" else ""
        a, b, c = st.columns(3)
        a.markdown(cost_card("This turn", pricing.cents(latest["actual"]), write_flag),
                   unsafe_allow_html=True)
        b.markdown(cost_card("If uncached", pricing.cents(latest["uncached"])),
                   unsafe_allow_html=True)
        c.markdown(cost_card("Saved", pricing.cents(latest["saved"]), "saved"),
                   unsafe_allow_html=True)

        tot_actual = sum(r["actual"] for r in st.session_state.ledger)
        tot_uncached = sum(r["uncached"] for r in st.session_state.ledger)
        tot_saved = tot_uncached - tot_actual
        pct = (tot_saved / tot_uncached * 100) if tot_uncached else 0

        st.markdown("**Running total**")
        d, e, f = st.columns(3)
        d.markdown(cost_card("Paid so far", pricing.cents(tot_actual)),
                   unsafe_allow_html=True)
        e.markdown(cost_card("Uncached", pricing.cents(tot_uncached)),
                   unsafe_allow_html=True)
        f.markdown(cost_card(f"Saved · {pct:.0f}%", pricing.cents(tot_saved), "saved"),
                   unsafe_allow_html=True)

        st.markdown("**Every turn so far**")
        icon = {"WRITE": "🟠 WRITE", "READ": "🟢 READ", "OFF": "⚪ none"}
        table = [
            {
                "Turn": r["turn"], "Cache": icon[r["kind"]],
                "Cached tok": f"{r['cached_tokens']:,}",
                "Paid": pricing.cents(r["actual"]), "Saved": pricing.cents(r["saved"]),
            }
            for r in st.session_state.ledger
        ]
        st.dataframe(table, hide_index=True, use_container_width=True)

        # ============ THE BREAKDOWN — where every token & cent goes ============
        st.markdown("---")
        st.markdown("### 🔬 Where the cost actually goes")
        L = latest

        # 1) plain-English sentence
        if L["real_read"] > 0:
            st.markdown(
                f"This turn sent **{L['total_input']:,} input tokens**. "
                f"**{L['real_read']:,}** came straight from cache at 10% price, "
                f"and only **{L['fresh_in']:,}** were new tokens processed fresh. "
                f"Output was **{L['out']:,}** tokens (never cached)."
            )
        elif L["real_write"] > 0:
            st.markdown(
                f"This turn sent **{L['total_input']:,} input tokens**. "
                f"**{L['real_write']:,}** were written into the cache (paid once, "
                f"at 1.25x) so future turns can reuse them. "
                f"**{L['fresh_in']:,}** were new; output was **{L['out']:,}**."
            )
        else:
            _min = pricing.MODELS[model]["cache_min_tokens"]
            st.markdown(
                f"This turn sent **{L['total_input']:,} input tokens**, all at full "
                f"price — **nothing cached**. The stable prefix is still under "
                f"**{_min:,} tokens** (this model's floor), so caching hasn't "
                f"engaged yet. Keep chatting; once the prefix crosses the floor, "
                f"reads kick in."
            )

        # 2) token split
        st.markdown("**Tokens this turn**")
        tok_rows = [
            {"Part": "🟢 Cached prefix (read)", "Tokens": f"{L['real_read']:,}",
             "What it is": "stable system + frozen history, reused"},
            {"Part": "🟠 Prefix write (stored)", "Tokens": f"{L['real_write']:,}",
             "What it is": "prefix stored this turn for reuse"},
            {"Part": "🔵 New input (dynamic)", "Tokens": f"{L['fresh_in']:,}",
             "What it is": "your latest message — always fresh"},
            {"Part": "⚪ Output (generated)", "Tokens": f"{L['out']:,}",
             "What it is": "Claude's reply — never cached"},
        ]
        st.dataframe(tok_rows, hide_index=True, use_container_width=True)

        # 3) cost breakup — piece by piece, then totals
        st.markdown("**Cost breakup**")
        cost_rows = [
            {"Line": f"Prefix — {L['prefix_label']}", "Cost": pricing.cents(L["prefix_cost"])},
            {"Line": "New input — full price", "Cost": pricing.cents(L["dynamic_cost"])},
            {"Line": "Output — full price", "Cost": pricing.cents(L["out_cost"])},
            {"Line": "= TOTAL you paid", "Cost": pricing.cents(L["actual"])},
            {"Line": "vs. if NO caching", "Cost": pricing.cents(L["uncached"])},
            {"Line": "→ Saved this turn", "Cost": pricing.cents(L["saved"])},
        ]
        st.dataframe(cost_rows, hide_index=True, use_container_width=True)

        # 4) the raw API usage, folded away for the curious
        with st.expander("Raw API usage (the exact fields)"):
            st.json(
                {
                    "cache_creation_input_tokens": L["real_write"],
                    "cache_read_input_tokens": L["real_read"],
                    "input_tokens (new/dynamic)": L["fresh_in"],
                    "output_tokens": L["out"],
                    "model": model, "ttl": ttl_choice,
                    "caching": "on" if caching_on else "off",
                }
            )
