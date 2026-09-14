# -*- coding: utf-8 -*-
"""
03_batch_check.py  —  check a batch's status, and collect it when ready.

THE POINT OF A SEPARATE FILE
    Batch work is asynchronous. You submit (02_batch_emails.py), then walk
    away. Later — minutes or hours — you come back and check. This file is
    that "come back later" step. Run it as many times as you like:
      - if the batch is still running, it tells you and exits.
      - once it's ended, it collects the emails and shows the 50% saving.

    This mirrors real production: a submit job and a separate collect job,
    not one process blocking for 24 hours.

BEFORE YOU RUN
    Run 02_batch_emails.py first — it writes batch_state.json with the id.
    Then run this:  python 03_batch_check.py
"""

import json
import os

from dotenv import load_dotenv
from anthropic import Anthropic

import pricing

load_dotenv()
client = Anthropic()

BATCH_STATE_FILE = "batch_state.json"


def load_state():
    """Read the batch id + prospect map that the submit script saved."""
    if not os.path.exists(BATCH_STATE_FILE):
        print(f"No {BATCH_STATE_FILE} found. Run 02_batch_emails.py first to "
              "submit a batch.")
        raise SystemExit(1)
    with open(BATCH_STATE_FILE) as f:
        return json.load(f)


def collect(batch_id: str, model: str, prospects: dict):
    """Stream the finished results, match by custom_id, show the savings."""
    print("\nResults are in. Matching each email back by custom_id:\n")

    total_in = total_out = 0
    n_ok = n_fail = 0
    for result in client.messages.batches.results(batch_id):
        cid = result.custom_id
        name = prospects.get(cid, cid)

        if result.result.type == "succeeded":
            msg = result.result.message
            total_in += msg.usage.input_tokens
            total_out += msg.usage.output_tokens
            email = pricing.first_text(msg).strip()
            print(f"--- Email for {name} ({cid}) ---")
            print(email)
            print()
            n_ok += 1
        else:
            # partial failures arrive HERE in the results, not as an exception
            print(f"--- {name} ({cid}) FAILED: {result.result.type} ---\n")
            n_fail += 1

    # cost comparison: one-by-one vs batched (50% off)
    normal = pricing.input_cost(model, total_in) + pricing.output_cost(model, total_out)
    discounted = pricing.batched(normal)
    print("=" * 60)
    print(f"COLLECTED: {n_ok} succeeded, {n_fail} failed")
    print("COST COMPARISON")
    print(f"  total input tokens:   {total_in:,}")
    print(f"  total output tokens:  {total_out:,}")
    print(f"  one-by-one (normal):  {pricing.usd(normal)}")
    print(f"  as a batch (50% off): {pricing.usd(discounted)}")
    print(f"  saved:                {pricing.usd(normal - discounted)}")
    print("\nScale this to 5,000 prospects and the 50% is real money —")
    print("and your live app's rate limits stay untouched the whole time.")


def main():
    state = load_state()
    batch_id = state["batch_id"]
    model = state.get("model", "claude-haiku-4-5-20251001")
    prospects = state.get("prospects", {})

    # 1) CHECK status ------------------------------------------------------
    batch = client.messages.batches.retrieve(batch_id)
    status = batch.processing_status
    counts = batch.request_counts  # how many succeeded / errored / still processing

    print(f"Batch:  {batch_id}")
    print(f"Status: {status}")
    print(f"Counts: processing={counts.processing}  succeeded={counts.succeeded}  "
          f"errored={counts.errored}  canceled={counts.canceled}  expired={counts.expired}")

    # 2) COLLECT if ready, otherwise tell the user to check back -----------
    if status == "ended":
        collect(batch_id, model, prospects)
    else:
        print("\nNot ready yet. This is the async part — the batch is still "
              "processing.\nRun this script again in a bit:  python 03_batch_check.py")


if __name__ == "__main__":
    main()
