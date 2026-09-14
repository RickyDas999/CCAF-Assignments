# Task 3 · Three failure modes of the tool_use round trip

Each break was applied to `d12_practice.py`, run, observed, then reverted with
`git checkout -- d12_practice.py` before moving to the next one. The working
file at HEAD never carries any of these breaks.

## 1. Broken `tool_use_id`

**Change:** set `tool_use_id` in the `tool_result` block to a made-up string
instead of the real `block.id` from the `tool_use` block.

**Result:** `anthropic.BadRequestError: Error code: 400`
```
messages.2.content.0: unexpected `tool_use_id` found in `tool_result` blocks:
toolu_totally_made_up_id. Each `tool_result` block must have a corresponding
`tool_use` block in the previous message.
```

**Why:** the API cross-checks every `tool_result.tool_use_id` against the
`tool_use` block(s) in the immediately preceding assistant message. IDs are
opaque and must be threaded through exactly as issued — you can't invent one.

## 2. Skipped assistant turn

**Change:** commented out `messages.append({"role": "assistant", "content":
response.content})`, so the `tool_result` user message was appended directly
after the first user message.

**Result:** `anthropic.BadRequestError: Error code: 400`
```
messages.0.content.1: unexpected `tool_use_id` found in `tool_result` blocks:
toolu_...  Each `tool_result` block must have a corresponding `tool_use`
block in the previous message.
```

**Why:** same underlying rule as #1, reached a different way — without the
assistant's `tool_use` turn in the list, there is no "previous message"
containing that `tool_use_id` for the `tool_result` to match against, even
though the id itself is valid. Confirmed by `print_messages_state`: the list
only grew 1 → 2 instead of 1 → 2 → 3, i.e. by one message instead of two.

## 3. No `stop_reason` gate ("guess from text")

**Change:** asked "hi" instead of the order question, with no check on
`response.stop_reason` before assuming a `tool_use` block would be present.

**Result:** local Python crash, not an API error:
```
UnboundLocalError: cannot access local variable 'block_id' where it is not
associated with a value
```

**Why:** Claude answered "hi" with plain text and `stop_reason == "end_turn"`
— no `tool_use` block at all. The loop over `response.content` never took the
`tool_use` branch, so `block_id` and `res` were never assigned, and the
unconditional `messages.append(...tool_use_id: block_id...)` after the loop
blew up. The fix is to branch on `response.stop_reason == "tool_use"` before
doing any of the tool-result bookkeeping, rather than assuming a tool call
happened.

## Confirmed fixed

After reverting all three breaks, `d12_practice.py` runs end-to-end again:
`stop_reason` → `tool_use` → tool executed → `tool_result` appended → final
call → `stop_reason` → `end_turn` with a plain-English answer.
