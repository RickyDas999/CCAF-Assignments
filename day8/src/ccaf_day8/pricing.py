# -*- coding: utf-8 -*-
"""
pricing.py  —  the ONE place all cost math lives.

Every other file (the caching chat, the batching script) imports its numbers
from here, so the dollars you see are always consistent and always real.

Prices are per MILLION tokens (MTok), in US dollars, verified 2026.
If Anthropic changes a rate, you edit it ONCE, here.
"""

# ----------------------------------------------------------------------------
# MODEL RATES  (USD per 1,000,000 tokens)
# ----------------------------------------------------------------------------
# Two models the learner can pick between:
#   - Sonnet 5   : the balanced default
#   - Haiku 4.5  : the cheap/fast one (great for bulk classification)
MODELS = {
    "claude-sonnet-5": {
        "label": "Claude Sonnet 5",
        "input_per_mtok": 2.00,    # $ per 1M input tokens
        "output_per_mtok": 10.00,  # $ per 1M output tokens
        "cache_min_tokens": 1024,  # min prefix length before caching engages
    },
    "claude-haiku-4-5-20251001": {
        "label": "Claude Haiku 4.5",
        "input_per_mtok": 1.00,
        "output_per_mtok": 5.00,
        "cache_min_tokens": 4096,  # Haiku 4.5 needs a LARGER prefix than Sonnet
    },
}

# ----------------------------------------------------------------------------
# PROMPT CACHING MULTIPLIERS  (multipliers ON TOP OF the base input price)
# ----------------------------------------------------------------------------
# These are the same across models — they scale each model's input price.
#   - Writing to the cache costs a little MORE than normal input (you're storing it)
#   - Reading from the cache costs 90% LESS (this is the whole point)
CACHE_MULTIPLIERS = {
    "write_5m": 1.25,   # 5-minute cache write  = 1.25x base input
    "write_1h": 2.00,   # 1-hour  cache write   = 2.00x base input
    "read":     0.10,   # cache hit (any TTL)   = 0.10x base input  (90% off)
}

# ----------------------------------------------------------------------------
# BATCH DISCOUNT
# ----------------------------------------------------------------------------
# The Batch API is a flat 50% off BOTH input and output, every model.
BATCH_DISCOUNT = 0.50   # multiply normal cost by this


# ----------------------------------------------------------------------------
# COST HELPERS  —  small, obvious functions. No magic.
# ----------------------------------------------------------------------------
def _mtok(tokens: int) -> float:
    """Convert a raw token count into 'millions of tokens'."""
    return tokens / 1_000_000


def input_cost(model: str, tokens: int) -> float:
    """Plain input cost at the normal (uncached) rate."""
    return _mtok(tokens) * MODELS[model]["input_per_mtok"]


def output_cost(model: str, tokens: int) -> float:
    """Plain output cost."""
    return _mtok(tokens) * MODELS[model]["output_per_mtok"]


def cache_write_cost(model: str, tokens: int, ttl: str = "5m") -> float:
    """
    Cost to WRITE `tokens` into the cache.
    ttl = '5m' (default) or '1h'.
    """
    base = MODELS[model]["input_per_mtok"]
    mult = CACHE_MULTIPLIERS["write_1h"] if ttl == "1h" else CACHE_MULTIPLIERS["write_5m"]
    return _mtok(tokens) * base * mult


def cache_read_cost(model: str, tokens: int) -> float:
    """Cost to READ `tokens` from the cache — the 90%-off price."""
    base = MODELS[model]["input_per_mtok"]
    return _mtok(tokens) * base * CACHE_MULTIPLIERS["read"]


def batched(cost: float) -> float:
    """Apply the flat 50% Batch API discount to any cost."""
    return cost * BATCH_DISCOUNT


def usd(amount: float) -> str:
    """
    Format a dollar amount for display.
    These numbers are tiny, so we show enough decimal places to see them.
    """
    if amount == 0:
        return "$0.00"
    if amount < 0.01:
        return f"${amount:.6f}"      # e.g. $0.000123
    return f"${amount:,.4f}"          # e.g. $0.0123


def cents(amount: float) -> str:
    """
    Format a dollar amount as CENTS — far more readable for tiny per-call costs.
    $0.000123  ->  '0.0123¢'      (a hundredth of a cent, but legible)
    $0.0200    ->  '2.00¢'
    Keeps everything on one short, comparable scale so it fits in a panel.
    """
    c = amount * 100.0
    if c == 0:
        return "0¢"
    if c < 1:
        return f"{c:.4f}¢"          # sub-cent: show 4 decimals
    if c < 100:
        return f"{c:.2f}¢"          # normal cents
    return f"${amount:,.2f}"        # a dollar or more: switch to $


# ----------------------------------------------------------------------------
# quick self-test so you can eyeball the math: `python pricing.py`
# ----------------------------------------------------------------------------
if __name__ == "__main__":
    m = "claude-sonnet-5"
    toks = 10_000
    print(f"Model: {MODELS[m]['label']}   |   {toks:,} tokens\n")
    print(f"  Normal input .......... {usd(input_cost(m, toks))}")
    print(f"  5m cache WRITE (1.25x) . {usd(cache_write_cost(m, toks, '5m'))}")
    print(f"  1h cache WRITE (2.00x) . {usd(cache_write_cost(m, toks, '1h'))}")
    print(f"  Cache READ (0.10x) ..... {usd(cache_read_cost(m, toks))}")
    print(f"  Same, batched (50% off)  {usd(batched(input_cost(m, toks)))}")


# ----------------------------------------------------------------------------
# SAFE TEXT EXTRACTION
# ----------------------------------------------------------------------------
def first_text(response) -> str:
    """
    Pull the assistant's text out of a response SAFELY.

    Why this exists: some models (e.g. Sonnet 5) can return a ThinkingBlock as
    the FIRST item in response.content. Doing response.content[0].text then
    crashes with 'ThinkingBlock has no attribute text'. This walks the blocks
    and returns the first real text block instead.
    """
    for block in response.content:
        # a text block has a .text attribute; thinking/tool blocks do not
        if getattr(block, "type", None) == "text" and hasattr(block, "text"):
            return block.text
    # fallback: join any text-bearing blocks, or return empty string
    parts = [b.text for b in response.content if hasattr(b, "text")]
    return "\n".join(parts) if parts else ""
