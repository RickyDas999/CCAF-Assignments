# -*- coding: utf-8 -*-
"""
01_caching_basics.py  —  prompt caching, the smallest honest example.

WHAT THIS SHOWS
    We send a LONG, stable instruction block (a pretend "company handbook")
    plus a short question. We mark the handbook with cache_control.
        - Call #1  -> Claude has to WRITE the handbook into the cache.
        - Call #2  -> same handbook, new question -> Claude READS it (90% off).
    The `usage` on each response proves which one happened.

    Run it twice within 5 minutes and watch call #2 become a cache READ.

BEFORE YOU RUN
    1) pip install anthropic python-dotenv     (or: uv add anthropic python-dotenv)
    2) put your key in a .env file:  ANTHROPIC_API_KEY=sk-ant-...
"""

import os
from dotenv import load_dotenv
from anthropic import Anthropic

import pricing  # our shared cost math

load_dotenv()
client = Anthropic()  # reads ANTHROPIC_API_KEY from the environment

MODEL = "claude-sonnet-5"

# ----------------------------------------------------------------------------
# The STABLE part. In real life this is a big system prompt, a long document,
# or a pile of tool definitions. It must be long enough to cache
# (roughly 1,024+ tokens) — so we pad it out to make the demo real.
# ----------------------------------------------------------------------------
COMPANY_HANDBOOK = (
    "You are the support assistant for GrowwStacks, an AI automation agency. "
    "Answer strictly using the policies below.\n\n"
    "REFUND POLICY: Clients may request a refund within 14 days of a project "
    "milestone if deliverables do not match the signed scope. Refunds are "
    "processed to the original payment method within 7 business days.\n\n"
    "SUPPORT HOURS: Monday to Saturday, 10:00 to 19:00 IST. Priority clients "
    "receive responses within 2 hours during these windows.\n\n"
    "ESCALATION: Any request mentioning data loss, billing disputes above "
    "USD 500, or legal concerns must be escalated to a human account manager "
    "immediately and never resolved by the assistant alone.\n\n"
    # --- padding so the block comfortably clears the cache minimum ---
    + ("Additional internal guidance for consistency and tone. " * 120)
)


def ask(question: str):
    """Send the cached handbook + a fresh question, and report the receipt."""
    resp = client.messages.create(
        model=MODEL,
        max_tokens=200,
        system=[
            {
                "type": "text",
                "text": COMPANY_HANDBOOK,
                # THIS is the whole trick: cache everything up to this point.
                "cache_control": {"type": "ephemeral"},
            }
        ],
        messages=[{"role": "user", "content": question}],
    )

    u = resp.usage
    # These two fields are your entire source of truth:
    wrote = getattr(u, "cache_creation_input_tokens", 0) or 0
    read = getattr(u, "cache_read_input_tokens", 0) or 0
    fresh_in = u.input_tokens  # the non-cached input (your question)
    out = u.output_tokens

    # Work out what we actually paid vs what it would cost with no cache.
    if read > 0:
        cache_line = pricing.cache_read_cost(MODEL, read)
        tag = "CACHE READ  (90% off)"
    else:
        cache_line = pricing.cache_write_cost(MODEL, wrote, "5m")
        tag = "CACHE WRITE (first time)"

    actual = cache_line + pricing.input_cost(MODEL, fresh_in) + pricing.output_cost(MODEL, out)
    cached_tokens = wrote or read
    uncached = (
        pricing.input_cost(MODEL, cached_tokens + fresh_in)
        + pricing.output_cost(MODEL, out)
    )

    print(f"\nQ: {question}")
    print(f"A: {pricing.first_text(resp).strip()[:200]}")
    print(f"   {tag}")
    print(f"   cached tokens: {cached_tokens:,}   fresh input: {fresh_in}   output: {out}")
    print(f"   you paid:        {pricing.usd(actual)}")
    print(f"   without caching: {pricing.usd(uncached)}")
    print(f"   saved:           {pricing.usd(uncached - actual)}")


if __name__ == "__main__":
    print("=" * 60)
    print("First question  -> expect a CACHE WRITE")
    ask("What are your support hours?")

    print("\n" + "=" * 60)
    print("Second question -> same handbook -> expect a CACHE READ")
    ask("Can I get a refund after 20 days?")
