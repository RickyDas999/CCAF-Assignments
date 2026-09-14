# -*- coding: utf-8 -*-
"""
02_batch_emails.py  —  the Batch API, a real GrowwStacks use case.

THE STORY
    We want to sell GrowwStacks services to 5 different prospects. Each one
    gets a PERSONALIZED outreach email, written for their role and pain point.
    Nobody is waiting on the line — we're fine getting these back later.

    So instead of 5 live API calls at full price, we bundle all 5 into ONE
    batch. Anthropic processes them asynchronously (within 24 hours, usually
    minutes) at a flat 50% discount. We poll until it's done, then collect.

    This is the OPPOSITE of the caching demo: caching was for a live chat;
    batching is for bulk work where latency doesn't matter.

    TWO-FILE FLOW (the real pattern):
      02_batch_emails.py  → submits the batch, saves the id, exits.
      03_batch_check.py   → run later; checks status, collects when ready.

BEFORE YOU RUN
    pip install anthropic python-dotenv   (or: uv add anthropic python-dotenv)
    .env with:  ANTHROPIC_API_KEY=sk-ant-...
"""

import json
from dotenv import load_dotenv
from anthropic import Anthropic

import pricing

load_dotenv()
client = Anthropic()

MODEL = "claude-haiku-4-5-20251001"  # cheap + fast: perfect for bulk generation
BATCH_STATE_FILE = "batch_state.json"  # where we save the id to collect later

# ----------------------------------------------------------------------------
# Our 5 prospects. In real life this comes from a CRM / spreadsheet.
# Each has a custom_id — that's how we match the result back to the person,
# because batch results come back UNORDERED.
# ----------------------------------------------------------------------------
PROSPECTS = [
    {
        "custom_id": "prospect-ravi-ecom",
        "name": "Ravi",
        "role": "Founder of a mid-size e-commerce brand",
        "pain": "drowning in manual customer-support tickets",
    },
    {
        "custom_id": "prospect-meera-clinic",
        "name": "Dr. Meera",
        "role": "Owner of a chain of dental clinics",
        "pain": "no-shows and manual appointment reminders eating staff time",
    },
    {
        "custom_id": "prospect-sanjay-logistics",
        "name": "Sanjay",
        "role": "Ops head at a logistics company",
        "pain": "invoice data entry from hundreds of PDFs every week",
    },
    {
        "custom_id": "prospect-anita-saas",
        "name": "Anita",
        "role": "Head of Marketing at a B2B SaaS startup",
        "pain": "can't personalize outreach at scale",
    },
    {
        "custom_id": "prospect-farhan-realty",
        "name": "Farhan",
        "role": "Real-estate broker running a small team",
        "pain": "leads going cold because follow-ups are slow and manual",
    },
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
    """Turn each prospect into one batch request."""
    requests = []
    for p in PROSPECTS:
        user_msg = (
            f"Prospect name: {p['name']}\n"
            f"Role: {p['role']}\n"
            f"Pain point: {p['pain']}\n\n"
            "Write their personalized GrowwStacks outreach email."
        )
        requests.append(
            {
                "custom_id": p["custom_id"],
                "params": {
                    "model": MODEL,
                    "max_tokens": 400,
                    "system": SYSTEM_BRIEF,
                    "messages": [{"role": "user", "content": user_msg}],
                },
            }
        )
    return requests


def main():
    requests = build_requests()

    # 1) SUBMIT the batch --------------------------------------------------
    print(f"Submitting {len(requests)} personalized emails as ONE batch...")
    batch = client.messages.batches.create(requests=requests)
    print(f"  batch id: {batch.id}")
    print(f"  status:   {batch.processing_status}")

    # 2) SAVE the id + prospect map so we can collect later ----------------
    # THIS is the real batch pattern: you DON'T sit and wait. You submit,
    # save the id, walk away, and check back in a separate run. That's what
    # 03_batch_check.py does — it reads this file and collects when ready.
    state = {
        "batch_id": batch.id,
        "model": MODEL,
        "prospects": {p["custom_id"]: p["name"] for p in PROSPECTS},
    }
    with open(BATCH_STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)

    print(f"\nSaved batch id to {BATCH_STATE_FILE}.")
    print("Batches finish within 24 hours (usually minutes). To collect results, run:")
    print("    python 03_batch_check.py")


if __name__ == "__main__":
    main()
