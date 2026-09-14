import os
import json

from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()

def preview_content(content, width=40):
    text = content if isinstance(content, str) else str(content)
    text = text.replace("\n", " ")
    return text[:width] + ("..." if len(text) > width else "")

def print_messages_state(label, messages):
    print(f"\n=== {label} | len(messages)={len(messages)} ===")
    for i, msg in enumerate(messages):
        print(f"  [{i}] role={msg['role']:<9} preview={preview_content(msg['content'])!r}")

def main():

    api_key = os.getenv("ANTHROPIC_API_KEY")

    if not api_key:
        print("ANTHROPIC_API_KEY missing. Copy .env.example to .env and fill it in.")
        return

    client = Anthropic(api_key=api_key)
    order = {"A-1043": "Shipped, arriving Friday"}
    tools = [{
        "name": "get_order_status",
        "description": "Gets the order for a specified order number",
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string"
                }
            },
            "required": ["order_id"]
        },
    }]

    def run_order_lookup(order_id):
        if order.get(order_id, 0) == 0:
            return f"Order ID: {order_id}, cannot be found"
        return order[order_id]

    messages = [{"role": "user", "content": "Where is order A-1043"}]
    print_messages_state("Initial user message", messages)

    while True:
        response = client.messages.create(
            model='claude-sonnet-5',
            max_tokens=240,
            tools=tools,
            messages=messages
        )
        print(f"stop_reason: {response.stop_reason}")

        if response.stop_reason == "tool_use":
            tool_use_block = None
            for block in response.content:
                if block.type == "text" and block.text.strip():
                    print(f'Claude also said: "{block.text.strip()}"')
                elif block.type == "tool_use":
                    tool_use_block = block
                    print(json.dumps({"type": block.type, "id": block.id,
                                        "name": block.name, "input": block.input}, indent=2))

            messages.append({"role": "assistant", "content": response.content})
            print_messages_state("Appended assistant tool_use turn", messages)

            order_id = tool_use_block.input['order_id']
            result = run_order_lookup(order_id)
            print(f"Tool result: {result}")

            messages.append({"role": "user", "content": [
                {"type": "tool_result", "tool_use_id": tool_use_block.id, "content": result}
            ]})
            print_messages_state("Appended user tool_result turn", messages)
            continue

        elif response.stop_reason == "end_turn":
            for block in response.content:
                if block.type == "text":
                    print(block.text.strip())
            break

        elif response.stop_reason == "max_tokens":
            print("WARNING: response was cut off at max_tokens before finishing. "
                  "A real system should retry with a higher max_tokens or treat "
                  "the output as incomplete rather than trusting it as-is.")
            break

        elif response.stop_reason == "stop_sequence":
            print(f"Hit stop_sequence: {response.stop_sequence!r}. A real system "
                  "would treat this as an intentional cutoff point (e.g. end of "
                  "a structured section) and decide whether to resume generation "
                  "or use the output as final.")
            break

        elif response.stop_reason == "pause_turn":
            print("pause_turn: a long-running server-side tool call (e.g. web "
                  "search) was paused mid-turn. A real system should send the "
                  "messages list back unchanged in another create() call to let "
                  "Claude continue where it left off.")
            break

        elif response.stop_reason == "refusal":
            print("refusal: Claude declined to continue generating for safety "
                  "reasons. A real system should stop, surface this to the user "
                  "or logs, and not retry the same request unmodified.")
            break

        else:
            print(f"Unhandled stop_reason: {response.stop_reason}")
            break


if __name__ == "__main__":
    main()
