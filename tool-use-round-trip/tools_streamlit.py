"""
Day 12 - the tool_use round-trip, running live.

    uv run streamlit run tools_streamlit.py

This is an instrument panel, not a slideshow. Everything on screen is taken
from the real API response: stop_reason, the tool_use block, the ids, the
token counts, the timings, and the exact JSON sent over the wire.
"""

import os
import json
import time

import pandas as pd
import streamlit as st
from anthropic import Anthropic
from dotenv import load_dotenv

from sheet import TOOLS, TOOL_FUNCTIONS, run_tool
from sheet import read_tab as _read_tab
from sheet import tab_names as _tab_names


# The sheet does not change while we teach, so read each tab once.
@st.cache_data(ttl=300)
def read_tab(tab):
    return _read_tab(tab)


@st.cache_data(ttl=300)
def tab_names():
    return _tab_names()


HERE = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(HERE, ".env"))

MODEL = "claude-haiku-4-5-20251001"

SAMPLES = [
    ("Where is order ORD002?", "one tool"),
    ("Who ordered ORD002, and what did they buy?", "chains + parallel"),
    ("Has ORD005 been delivered?", "corrects the premise"),
    ("What is the status of ORD999?", "the tool errors"),
]

st.set_page_config(page_title="tool_use — the round-trip", page_icon="🔧",
                   layout="wide", initial_sidebar_state="expanded")

C1, C2, C3, C4 = "#c0562a", "#b07d20", "#8a7a1c", "#3f7d42"
STEP = {
    1: (C1, "CLAUDE", "asks for a tool"),
    2: (C2, "YOUR CODE", "runs the function"),
    3: (C3, "YOUR CODE", "returns the result"),
    4: (C4, "CLAUDE", "continues"),
}

st.markdown("""
<style>
  .stepcard  { border-left:5px solid var(--c); background:#faf8f5;
               border-radius:6px; padding:.5rem .9rem; margin:.1rem 0 .4rem; }
  .stepnum   { display:inline-block; width:1.4rem; height:1.4rem; line-height:1.4rem;
               text-align:center; border-radius:50%; background:var(--c);
               color:#fff; font-weight:700; font-size:.78rem; margin-right:.5rem; }
  .steptitle { font-weight:800; font-size:1.02rem; color:#141414; }
  .who       { float:right; font-size:.68rem; letter-spacing:.09em;
               color:var(--c); font-weight:800; padding-top:.3rem; }
  .field     { font-family:ui-monospace,monospace; font-size:.82rem;
               font-weight:600; color:#7a3b18;
               background:#efeae2; border-radius:4px; padding:.1rem .4rem; }
  .note      { color:#3d3d3d; font-size:.88rem; font-weight:500;
               line-height:1.5; margin-top:.35rem; }

  /* global: darker, slightly heavier body text than Streamlit's default */
  section.main p, section.main li,
  [data-testid="stMarkdownContainer"] p { color:#1f1f1f; font-weight:450; }
  [data-testid="stCaptionContainer"], .stCaption,
  [data-testid="stCaptionContainer"] p { color:#4a4a4a !important;
                                         font-weight:500 !important; }
  section[data-testid="stSidebar"] p,
  section[data-testid="stSidebar"] li { color:#1f1f1f; font-weight:500; }
  [data-testid="stMetricValue"] { font-weight:800 !important; }
  [data-testid="stMetricLabel"] { font-weight:600 !important; color:#4a4a4a; }
  h1,h2,h3,h4,h5 { font-weight:800 !important; color:#141414 !important; }
  .stTabs [data-baseweb="tab"] { font-weight:700; font-size:.95rem; }
  .idchip    { font-family:ui-monospace,monospace; font-size:.74rem;
               background:#f6e4d9; border:1px solid #d9a184; color:#7a3b18;
               border-radius:4px; padding:.1rem .35rem; margin-right:.25rem; }
  /* the four-step strip in the header */
  .flow      { display:flex; align-items:center; justify-content:flex-end;
               flex-wrap:wrap; gap:.3rem; }
  .fstep     { font-size:.72rem; font-weight:700; letter-spacing:.02em;
               color:#fff; background:var(--c);
               border-radius:11px; padding:.2rem .6rem; white-space:nowrap; }
  .farrow    { color:#b9b2a8; font-size:.8rem; }
  /* tool names in the sidebar, readable on any theme */
  .toolchip  { display:inline-block; font-family:ui-monospace,monospace;
               font-size:.8rem; color:#7a3b18; background:#f6e4d9;
               border:1px solid #e0bda6; border-radius:4px;
               padding:.12rem .45rem; margin:.12rem .2rem .12rem 0; }
  [data-testid="stSidebarCollapseButton"] button { opacity:1 !important; }
  [data-testid="stSidebarCollapseButton"] svg    { width:1.4rem; height:1.4rem; }
</style>
""", unsafe_allow_html=True)


def step_header(n):
    colour, who, title = STEP[n]
    st.markdown(
        f'<div class="stepcard" style="--c:{colour}">'
        f'<span class="who">{who}</span>'
        f'<span class="stepnum">{n}</span>'
        f'<span class="steptitle">{title}</span></div>',
        unsafe_allow_html=True)


def note(html):
    st.markdown(f'<div class="note">{html}</div>', unsafe_allow_html=True)


def blocks_to_json(content):
    """Turn Claude's response blocks into plain JSON we can display."""
    out = []
    for b in content:
        if b.type == "text":
            out.append({"type": "text", "text": b.text})
        elif b.type == "tool_use":
            out.append({"type": "tool_use", "id": b.id,
                        "name": b.name, "input": b.input})
    return out


# ---------------------------------------------------------------- state
api_key = os.getenv("ANTHROPIC_API_KEY")
if api_key and "client" not in st.session_state:
    st.session_state.client = Anthropic(api_key=api_key)

st.session_state.setdefault("messages", [])   # the real API messages list
st.session_state.setdefault("chat", [])
st.session_state.setdefault("trace", [])
st.session_state.setdefault("calls", [])      # raw request/response log
st.session_state.setdefault("error", None)


# ============================================================================
# The round-trip. Every API call is timed and logged as it happens.
# ============================================================================

def ask_claude(label):
    """One call to client.messages.create, timed and recorded."""
    started = time.time()
    response = st.session_state.client.messages.create(
        model=MODEL,
        max_tokens=1024,
        tools=TOOLS,
        messages=st.session_state.messages,
    )
    elapsed = time.time() - started

    st.session_state.calls.append({
        "label": label,
        "seconds": round(elapsed, 2),
        "messages_sent": len(st.session_state.messages),
        "stop_reason": response.stop_reason,
        "in_tokens": response.usage.input_tokens,
        "out_tokens": response.usage.output_tokens,
        "response": blocks_to_json(response.content),
    })
    return response, elapsed


def run_round_trip(question):
    st.session_state.error = None
    st.session_state.trace = []
    st.session_state.calls = []
    st.session_state.chat.append(("user", question))
    st.session_state.messages.append({"role": "user", "content": question})

    try:
        # ---- STEP 1: Claude asks ---------------------------------------
        response, elapsed = ask_claude("initial request")

        st.session_state.trace.append({
            "step": 1,
            "stop_reason": response.stop_reason,
            "seconds": round(elapsed, 2),
            "usage": (response.usage.input_tokens, response.usage.output_tokens),
            # Claude often writes a sentence BEFORE the tool_use block.
            "said": "".join(b.text for b in response.content if b.type == "text"),
            "tool_uses": [{"type": "tool_use", "id": b.id, "name": b.name,
                           "input": b.input}
                          for b in response.content if b.type == "tool_use"],
        })

        while response.stop_reason == "tool_use":
            calls = [b for b in response.content if b.type == "tool_use"]

            # ---- STEP 2: our code runs ---------------------------------
            results = []
            for c in calls:
                t0 = time.time()
                out = run_tool(c.name, c.input)
                results.append((c, out, round(time.time() - t0, 2)))

            st.session_state.trace.append({
                "step": 2,
                "calls": [{"name": c.name, "input": c.input,
                           "result": r, "seconds": secs}
                          for c, r, secs in results],
            })

            # ---- STEP 3: we return the results -------------------------
            # BOTH appends matter. Drop the assistant turn and history breaks.
            tool_result_message = {
                "role": "user",
                "content": [{"type": "tool_result",
                             "tool_use_id": c.id,
                             "content": r} for c, r, _ in results],
            }
            st.session_state.messages.append(
                {"role": "assistant", "content": response.content})
            st.session_state.messages.append(tool_result_message)

            st.session_state.trace.append({
                "step": 3,
                "sent": tool_result_message,
                "asked_ids": [c.id for c, _, _ in results],
            })

            # ---- STEP 4: Claude continues ------------------------------
            response, elapsed = ask_claude("after tool_result")

            st.session_state.trace.append({
                "step": 4,
                "stop_reason": response.stop_reason,
                "seconds": round(elapsed, 2),
                "usage": (response.usage.input_tokens, response.usage.output_tokens),
                "answer": "".join(b.text for b in response.content if b.type == "text"),
            })

        answer = "".join(b.text for b in response.content if b.type == "text")
        st.session_state.messages.append({"role": "assistant", "content": answer})
        st.session_state.chat.append(("assistant", answer))

    except Exception as e:
        st.session_state.error = f"{type(e).__name__}: {e}"


# ============================================================================
# SIDEBAR - what is on the table right now
# ============================================================================
with st.sidebar:
    st.markdown("### What is wired up")
    st.caption("Collapse this panel with the « arrow.")

    st.markdown(f"**Model**")
    st.code(MODEL, language="text")

    st.markdown(f"**{len(TOOLS)} client tools**")
    st.markdown(
        "".join(f'<span class="toolchip">{t["name"]}</span>' for t in TOOLS),
        unsafe_allow_html=True)
    note("Client tools: the functions live in <span class='field'>sheet.py</span> "
         "and run on this machine. Claude can only ask for them by name.")

    st.divider()
    st.markdown("**The loop**")
    st.code('while stop_reason == "tool_use":\n'
            '    run the tool\n'
            '    append the result\n'
            '    call again', language="python")

    if st.session_state.calls:
        st.divider()
        st.markdown("**This question cost**")
        total_s = sum(c["seconds"] for c in st.session_state.calls)
        tin = sum(c["in_tokens"] for c in st.session_state.calls)
        tout = sum(c["out_tokens"] for c in st.session_state.calls)
        st.metric("API calls", len(st.session_state.calls))
        st.metric("Seconds", f"{total_s:.2f}")
        st.metric("Tokens in / out", f"{tin} / {tout}")


# ============================================================================
# MAIN
# ============================================================================
head_l, head_r = st.columns([3, 2], vertical_alignment="center")
with head_l:
    st.markdown("## `tool_use` — the round-trip")
    st.caption("Claude asks · your code runs · you return the result · Claude continues")
with head_r:
    st.markdown(
        '<div class="flow">'
        f'<span class="fstep" style="--c:{C1}">1 Claude asks</span>'
        '<span class="farrow">→</span>'
        f'<span class="fstep" style="--c:{C2}">2 you run</span>'
        '<span class="farrow">→</span>'
        f'<span class="fstep" style="--c:{C3}">3 you return</span>'
        '<span class="farrow">→</span>'
        f'<span class="fstep" style="--c:{C4}">4 Claude continues</span>'
        '</div>', unsafe_allow_html=True)

st.divider()

if not api_key:
    st.error("`ANTHROPIC_API_KEY` is not set. Copy `.env.example` to `.env`.")
    st.stop()

run_tab, wire_tab, msg_tab, schema_tab, sheet_tab = st.tabs(
    ["Run it", "Raw API calls", "The messages list", "What Claude sees", "The sheet"])

# ------------------------------------------------------------- run it
with run_tab:
    left, right = st.columns([5, 6], gap="large")

    with left:
        st.markdown("##### Conversation")
        st.caption("All the user ever sees.")

        for role, text in st.session_state.chat:
            with st.chat_message(role):
                st.write(text)

        typed = st.chat_input("Ask about an order, customer or product…")
        if typed:
            with st.spinner("Running…"):
                run_round_trip(typed)
            st.rerun()

        cols = st.columns(2)
        for i, (q, why) in enumerate(SAMPLES):
            with cols[i % 2]:
                if st.button(q, use_container_width=True, key=f"s{i}"):
                    with st.spinner("Running…"):
                        run_round_trip(q)
                    st.rerun()
                st.caption(why)

        if st.session_state.chat and st.button("Clear", use_container_width=True):
            st.session_state.chat, st.session_state.trace = [], []
            st.session_state.messages, st.session_state.calls = [], []
            st.session_state.error = None
            st.rerun()

    with right:
        st.markdown("##### Behind the scenes")
        st.caption("Read straight off the API response.")

        if st.session_state.error:
            st.error(st.session_state.error)

        if not st.session_state.trace and not st.session_state.error:
            st.info("Ask a question on the left. Every step below is filled in "
                    "from the real API response as it arrives.")
            for n in (1, 2, 3, 4):
                step_header(n)
                colour, who, title = STEP[n]
                note({
                    1: "Claude replies with <span class='field'>stop_reason: "
                       "tool_use</span> and a <span class='field'>tool_use</span> "
                       "block naming the tool and its arguments. Then it waits.",
                    2: "We call the real python function. The Sheets API fires. "
                       "This is the only step where anything happens in the world.",
                    3: "We append a <span class='field'>tool_result</span> carrying "
                       "the <b>same id</b> Claude sent. Wrong id, request rejected.",
                    4: "Claude reads the result and either answers "
                       "(<span class='field'>end_turn</span>) or asks for another "
                       "tool (<span class='field'>tool_use</span>, loop again).",
                }[n])

        for c in st.session_state.trace:
            n = c["step"]

            if n == 1:
                step_header(1)
                a, b = st.columns(2)
                a.metric("stop_reason", c["stop_reason"])
                b.metric("took", f'{c["seconds"]}s')
                note(f'tokens in/out: {c["usage"][0]} / {c["usage"][1]}')
                if c["said"]:
                    note(f'Claude wrote text <i>before</i> the tool call: '
                         f'“{c["said"]}” — so we scan every block, not '
                         f'<span class="field">content[0]</span>.')
                if len(c["tool_uses"]) > 1:
                    st.warning(f'{len(c["tool_uses"])} tool_use blocks in ONE '
                               f'response — parallel tool use.')
                for tu in c["tool_uses"]:
                    st.json(tu, expanded=True)

            elif n == 2:
                step_header(2)
                note("Claude is paused. This is our python, on this laptop, "
                     "hitting the Sheets API.")
                for call in c["calls"]:
                    st.code(f'{call["name"]}({json.dumps(call["input"])})'
                            f'   # {call["seconds"]}s', language="python")
                    st.success(call["result"])

            elif n == 3:
                step_header(3)
                chips = "".join(f'<span class="idchip">{i}</span>'
                                for i in c["asked_ids"])
                note(f"Every id from step 1 gets exactly one result:<br>{chips}")
                st.caption("This is the literal message appended to the list:")
                st.json(c["sent"], expanded=True)

            elif n == 4:
                step_header(4)
                a, b = st.columns(2)
                a.metric("stop_reason", c["stop_reason"])
                b.metric("took", f'{c["seconds"]}s')
                note(f'tokens in/out: {c["usage"][0]} / {c["usage"][1]}')
                if c["stop_reason"] == "tool_use":
                    st.warning("Still `tool_use` — Claude wants another tool. "
                               "The loop repeats; watch step 2 again below.")
                else:
                    st.success("`end_turn` — the loop exits here.")
                if c["answer"]:
                    st.write(c["answer"])

# -------------------------------------------------------- raw API calls
with wire_tab:
    st.markdown("##### Every call to `client.messages.create`")
    st.caption("One row per API call. A question with N tool calls makes N+1 of them.")

    if not st.session_state.calls:
        st.info("Ask something on the first tab.")
    else:
        st.dataframe(pd.DataFrame([{
            "#": i + 1,
            "when": c["label"],
            "messages sent": c["messages_sent"],
            "stop_reason": c["stop_reason"],
            "tokens in": c["in_tokens"],
            "tokens out": c["out_tokens"],
            "seconds": c["seconds"],
        } for i, c in enumerate(st.session_state.calls)]),
            use_container_width=True, hide_index=True)

        note("Watch <b>messages sent</b> grow by two each time — the assistant's "
             "tool_use turn, and our tool_result. That growth is the memory. "
             "It is also why a long tool loop gets more expensive per call: "
             "the whole history is re-sent every time.")

        st.divider()
        for i, c in enumerate(st.session_state.calls):
            with st.expander(f'Call {i+1} — {c["label"]} — '
                             f'stop_reason: {c["stop_reason"]}'):
                st.caption("What came back in `response.content`:")
                st.json(c["response"])

# ------------------------------------------------------ messages list
with msg_tab:
    st.markdown("##### The messages list is the memory")
    st.caption("The actual list handed to the API on the most recent call.")

    if not st.session_state.messages:
        st.info("Ask something on the first tab.")
    else:
        rows = []
        for m in st.session_state.messages:
            content = m["content"]
            if isinstance(content, str):
                summary = content
            else:
                parts = []
                for blk in content:
                    btype = blk["type"] if isinstance(blk, dict) else blk.type
                    if btype == "tool_use":
                        nm = blk["name"] if isinstance(blk, dict) else blk.name
                        parts.append(f"tool_use -> {nm}(…)")
                    elif btype == "tool_result":
                        parts.append("tool_result <- same id")
                    elif btype == "text":
                        txt = blk["text"] if isinstance(blk, dict) else blk.text
                        if txt.strip():
                            parts.append(txt.strip())
                summary = "   +   ".join(parts)
            rows.append({"role": m["role"], "content": summary})

        st.dataframe(pd.DataFrame(rows), use_container_width=True)
        note("user asks · assistant calls the tool · user carries the result · "
             "assistant answers. Note the <b>tool_result rides in a user "
             "message</b> — you are speaking back to Claude.")

# ------------------------------------------------------ what Claude sees
with schema_tab:
    st.markdown("##### What Claude actually receives")
    st.caption("Not the code — only this. Claude picks a tool by reading the "
               "description, which is why the wording decides the behaviour.")

    st.code(f"""client.messages.create(
    model="{MODEL}",
    max_tokens=1024,
    tools=TOOLS,        # <- the {len(TOOLS)} schemas below
    messages=messages,
)""", language="python")

    for t in TOOLS:
        with st.expander(f'{t["name"]}  —  {t["description"][:64]}…'):
            st.json(t)
            fn = TOOL_FUNCTIONS[t["name"]]
            st.caption(f"Behind it: `sheet.{fn.__name__}()` — ordinary python "
                       "that Claude has never seen.")

    st.info("Try it: ask *“where is ORD002”* and Claude picks `get_shipping`, "
            "not `get_order` — because “where is it” matches the shipping "
            "description. Change the wording in `sheet.py` and the choice changes.")

# -------------------------------------------------------------- sheet
with sheet_tab:
    st.markdown("##### The live spreadsheet")
    st.caption("Show this first — it proves the data is real, and the shared "
               "ids explain why Claude has to chain tools.")

    try:
        names = tab_names()
        for tab, sub in zip(st.tabs(names), names):
            with tab:
                headers, rows = read_tab(sub)
                if headers:
                    padded = [r + [""] * (len(headers) - len(r)) for r in rows]
                    st.dataframe(pd.DataFrame(padded, columns=headers),
                                 use_container_width=True, hide_index=True)
                    st.caption(f"{len(rows)} rows · tools match on **{headers[0]}**")
                else:
                    st.warning("This tab is empty.")

        st.info("**Orders** holds `customer_id` and `product_id` but not the names. "
                "So *“who ordered ORD002 and what did they buy?”* cannot be "
                "answered by one tool — Claude must call `get_order`, read the "
                "ids out of the result, then call `get_customer` and "
                "`get_product`. That is the loop running more than once.")
    except Exception as e:
        st.error(f"Could not read the sheet: {e}")
        st.caption("Most likely the sheet is not shared with the service-account "
                   "email in `service-account.json`.")
