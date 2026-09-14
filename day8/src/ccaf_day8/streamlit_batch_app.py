# -*- coding: utf-8 -*-
"""
streamlit_batch_app.py  —  the Batch API, made visible.

WHAT THE LEARNER SEES
    The mirror image of the caching app. Caching was for a LIVE chat where
    someone's waiting. This is BULK work where nobody is: five GrowwStacks
    prospects, each getting a personalized outreach email, sent as ONE batch
    at 50% off. You submit, watch the status, and collect when it's done.

    Same cost-breakup philosophy as the caching app: you see exactly what the
    batch cost, what it WOULD have cost one-by-one, and the saving.

THE FLOW (three buttons, matching the real lifecycle)
    1. Submit batch   → bundle 5 emails into one job, get a batch id
    2. Check status   → poll: in_progress → ended (this is the async part)
    3. Collect        → gather emails (matched by custom_id) + show the saving

RUN IT
    uv run streamlit run streamlit_batch_app.py
"""

import os
import time

import streamlit as st
from anthropic import Anthropic
from dotenv import load_dotenv

import pricing

load_dotenv()

MODEL = "claude-haiku-4-5-20251001"  # cheap + fast: ideal for bulk generation

# ----------------------------------------------------------------------------
# The 5 prospects. In real life this comes from your CRM / a spreadsheet.
# Each has a custom_id — how we match a result back, since batch results are
# returned UNORDERED.
# ----------------------------------------------------------------------------
PROSPECTS = [
    {"custom_id": "ravi-ecom", "name": "Ravi",
     "role": "Founder of a mid-size e-commerce furniture brand",
     "pain": "drowning in manual customer-support tickets"},
    {"custom_id": "meera-clinic", "name": "Dr. Meera",
     "role": "Owner of a chain of dental clinics",
     "pain": "no-shows and manual appointment reminders eating staff time"},
    {"custom_id": "sanjay-logistics", "name": "Sanjay",
     "role": "Ops head at a logistics company",
     "pain": "invoice data entry from hundreds of PDFs every week"},
    {"custom_id": "anita-saas", "name": "Anita",
     "role": "Head of Marketing at a B2B SaaS startup",
     "pain": "can't personalize outreach at scale"},
    {"custom_id": "farhan-realty", "name": "Farhan",
     "role": "Real-estate broker running a small team",
     "pain": "leads going cold because follow-ups are slow and manual"},
]

SYSTEM_BRIEF = (
    "You are a sales copywriter for GrowwStacks, an AI automation agency that "
    "builds custom Claude-powered agents and workflow automations. Write a "
    "short, warm, specific cold outreach email (max 120 words). Reference the "
    "prospect's exact pain point, propose one concrete GrowwStacks automation "
    "that solves it, and end with a soft call to book a 20-minute call. "
    "No pushy language, no buzzword soup."
)


def build_requests():
    """Turn each prospect into one batch request, keyed by custom_id."""
    reqs = []
    for p in PROSPECTS:
        user_msg = (
            f"Prospect name: {p['name']}\n"
            f"Role: {p['role']}\n"
            f"Pain point: {p['pain']}\n\n"
            "Write their personalized GrowwStacks outreach email."
        )
        reqs.append({
            "custom_id": p["custom_id"],
            "params": {
                "model": MODEL,
                "max_tokens": 400,
                "system": SYSTEM_BRIEF,
                "messages": [{"role": "user", "content": user_msg}],
            },
        })
    return reqs


# ----------------------------------------------------------------------------
# Page + state
# ----------------------------------------------------------------------------
st.set_page_config(page_title="Batch App · GrowwStacks", page_icon="📦", layout="wide")

if "batch_id" not in st.session_state:
    st.session_state.batch_id = None
if "status" not in st.session_state:
    st.session_state.status = None
if "results" not in st.session_state:
    st.session_state.results = None   # list of collected emails + tokens
# raw payloads captured for the "behind the scenes" visualization:
if "sent_requests" not in st.session_state:
    st.session_state.sent_requests = None   # the request list we submitted
if "status_payload" not in st.session_state:
    st.session_state.status_payload = None  # last status-check response
if "raw_result_sample" not in st.session_state:
    st.session_state.raw_result_sample = None  # one raw result object

NAMES = {p["custom_id"]: p["name"] for p in PROSPECTS}

st.title("📦 The batch outreach machine")
st.caption("The Batch API, made visible. Five personalized emails, one job, 50% off — "
           "because nobody's waiting on a cold email.")

if not os.getenv("ANTHROPIC_API_KEY"):
    st.error(
        "No API key found. Create a **.env** file next to this script with "
        "`ANTHROPIC_API_KEY=sk-ant-...`, then click **Rerun**."
    )
    st.stop()

client = Anthropic()

# ----------------------------------------------------------------------------
# LEFT: the flow.   RIGHT: what's happening / the prospects.
# ----------------------------------------------------------------------------
left, right = st.columns([3, 2], gap="large")

with right:
    st.subheader("The 5 prospects")
    st.caption("Each becomes one request in the batch, keyed by `custom_id`.")
    st.dataframe(
        [{"custom_id": p["custom_id"], "Name": p["name"], "Pain point": p["pain"]}
         for p in PROSPECTS],
        hide_index=True, use_container_width=True,
    )
    st.info("**Why batch, not live?** Nobody's waiting on these emails. Bundle "
            "them, pay half, feed the results to your outreach tool. The exact "
            "opposite of the caching chat, where a person waits on every turn.")

with left:
    # ---- STEP 1: SUBMIT ----
    st.markdown("### 1 · Submit the batch")
    st.caption("Bundle all 5 emails into ONE job and send it off.")

    # Preview the request structure BEFORE sending, so you see what goes out.
    _preview = build_requests()
    with st.expander("👀 See one request object (the structure you send ×5)", expanded=False):
        st.caption("Each prospect becomes ONE of these. `custom_id` is how you match "
                   "the answer back later; `params` is a normal Messages API call.")
        st.json(_preview[0])
        st.caption(f"The batch is a list of {len(_preview)} of these, sent in a single call: "
                   "`client.messages.batches.create(requests=[...])`")

    if st.button("📤 Submit batch", disabled=st.session_state.batch_id is not None):
        with st.spinner("Submitting..."):
            reqs = build_requests()
            batch = client.messages.batches.create(requests=reqs)
        st.session_state.batch_id = batch.id
        st.session_state.status = batch.processing_status
        st.session_state.results = None
        st.session_state.sent_requests = reqs  # keep for visualization
        st.rerun()

    if st.session_state.batch_id:
        st.success(f"Submitted. Batch id: `{st.session_state.batch_id}`")
        if st.session_state.sent_requests:
            with st.expander(f"📤 What we actually sent — all {len(st.session_state.sent_requests)} requests"):
                st.caption("The full list submitted in one call. Note the distinct `custom_id`s.")
                st.json(st.session_state.sent_requests)

    # ---- STEP 2: CHECK STATUS ----
    st.markdown("### 2 · Check status")
    st.caption("Batches finish within 24h (usually minutes). This is the async "
               "part — you check back, you don't hold the line.")
    c1, c2 = st.columns(2)
    if c1.button("🔄 Check status", disabled=st.session_state.batch_id is None):
        b = client.messages.batches.retrieve(st.session_state.batch_id)
        st.session_state.status = b.processing_status
        # capture the raw status payload for the visualization
        st.session_state.status_payload = b.model_dump(mode="json")
        st.rerun()
    if c2.button("⏳ Auto-wait (poll)", disabled=st.session_state.batch_id is None):
        with st.spinner("Polling until ended..."):
            b = client.messages.batches.retrieve(st.session_state.batch_id)
            while b.processing_status != "ended":
                time.sleep(3)
                b = client.messages.batches.retrieve(st.session_state.batch_id)
        st.session_state.status = b.processing_status
        st.session_state.status_payload = b.model_dump(mode="json")
        st.rerun()

    if st.session_state.status:
        counts = None
        try:
            b = client.messages.batches.retrieve(st.session_state.batch_id)
            counts = b.request_counts
        except Exception:
            pass
        badge = {"in_progress": "🟡 in progress", "ended": "🟢 ended",
                 "canceling": "🟠 canceling"}.get(st.session_state.status,
                                                  st.session_state.status)
        st.markdown(f"**Status:** {badge}")
        if counts:
            st.caption(f"processing={counts.processing} · succeeded={counts.succeeded} "
                       f"· errored={counts.errored} · expired={counts.expired}")

        # VISUALIZE the raw status response the API returned
        if st.session_state.status_payload:
            with st.expander("🔎 The raw status response (what the poll returns)"):
                st.caption("This is the exact object `batches.retrieve(id)` returns. The "
                           "fields that matter: **processing_status** (in_progress → ended) "
                           "and **request_counts** (how many done / failed / still running).")
                st.json(st.session_state.status_payload)

    # ---- STEP 3: COLLECT ----
    st.markdown("### 3 · Collect the emails")
    st.caption("Gather results, matched back to each prospect by `custom_id`.")
    ready = st.session_state.status == "ended"
    if st.button("📥 Collect results", disabled=not ready):
        rows, total_in, total_out = [], 0, 0
        raw_sample = None
        for result in client.messages.batches.results(st.session_state.batch_id):
            cid = result.custom_id
            name = NAMES.get(cid, cid)
            # capture the FIRST result object raw, for the visualization
            if raw_sample is None:
                raw_sample = result.model_dump(mode="json")
            if result.result.type == "succeeded":
                msg = result.result.message
                total_in += msg.usage.input_tokens
                total_out += msg.usage.output_tokens
                rows.append({"cid": cid, "name": name,
                             "email": pricing.first_text(msg).strip(),
                             "ok": True})
            else:
                rows.append({"cid": cid, "name": name,
                             "email": f"(failed: {result.result.type})", "ok": False})
        st.session_state.results = {"rows": rows, "in": total_in, "out": total_out}
        st.session_state.raw_result_sample = raw_sample
        st.rerun()

    if st.session_state.batch_id and st.button("🔁 Reset (new batch)"):
        st.session_state.batch_id = None
        st.session_state.status = None
        st.session_state.results = None
        st.session_state.sent_requests = None
        st.session_state.status_payload = None
        st.session_state.raw_result_sample = None
        st.rerun()

# ----------------------------------------------------------------------------
# RESULTS + COST BREAKDOWN (full width, below)
# ----------------------------------------------------------------------------
if st.session_state.results:
    R = st.session_state.results
    st.markdown("---")
    st.subheader("✉️ The emails")
    for row in R["rows"]:
        with st.expander(f"{'✅' if row['ok'] else '❌'} {row['name']}  ·  {row['cid']}"):
            st.write(row["email"])

    # VISUALIZE one raw result object — what comes back per request
    if st.session_state.raw_result_sample:
        with st.expander("🔎 One raw result object (the structure that comes back)"):
            st.caption(
                "This is one entry from `batches.results(id)`. Read it top-down: "
                "**custom_id** tells you which prospect it belongs to (results arrive "
                "UNORDERED, so this is how you match); **result.type** is succeeded/errored; "
                "**result.message** is a normal API message, with its own **usage** token counts."
            )
            st.json(st.session_state.raw_result_sample)

    # ---- cost breakdown, same philosophy as the caching app ----
    st.subheader("💰 Where the cost went")
    tin, tout = R["in"], R["out"]
    in_full = pricing.input_cost(MODEL, tin)
    out_full = pricing.output_cost(MODEL, tout)
    normal = in_full + out_full           # one-by-one, full price
    discounted = pricing.batched(normal)  # batch: flat 50% off
    saved = normal - discounted

    st.markdown(
        f"The batch processed **{tin:,} input** + **{tout:,} output** tokens across "
        f"**{len(R['rows'])} emails**. Batch pricing is a flat **50% off** both."
    )

    cost_rows = [
        {"Line": "Input — normal rate", "Cost": pricing.cents(in_full)},
        {"Line": "Output — normal rate", "Cost": pricing.cents(out_full)},
        {"Line": "= One-by-one total (full price)", "Cost": pricing.cents(normal)},
        {"Line": "= As a batch (50% off)", "Cost": pricing.cents(discounted)},
        {"Line": "→ Saved", "Cost": pricing.cents(saved)},
    ]
    st.dataframe(cost_rows, hide_index=True, use_container_width=True)

    a, b, c = st.columns(3)
    a.metric("One-by-one", pricing.cents(normal))
    b.metric("As a batch", pricing.cents(discounted))
    c.metric("Saved (50%)", pricing.cents(saved))

    st.info(f"Five emails is a few tenths of a cent. Scale to **5,000 prospects** "
            f"and the 50% is real money — and your live app's rate limits stayed "
            f"untouched the whole time, because batch has its own separate limits.")
