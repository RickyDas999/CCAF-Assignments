from anthropic import Anthropic
from dotenv import load_dotenv

def main() -> None:

    load_dotenv()
    client = Anthropic()
    messages = []

    # Turn 1
    messages.append({'role': 'user', 'content': 'What is the capital of France?'})
    r1 = client.messages.create(model='claude-sonnet-5', max_tokens=100, messages=messages)

    r1_text = next(b.text for b in r1.content if b.type == 'text')
    print('Turn 1:', r1_text)

    # Put Claude reply back into its history
    messages.append({'role': 'assistant', 'content': r1_text})

    # Turn 2 works because Turn 1 still in messages
    messages.append({'role': 'user', 'content': 'What is its population?'})
    r2 = client.messages.create(model='claude-sonnet-5', max_tokens=100, messages=messages)

    r2_text = next(b.text for b in r2.content if b.type == 'text')
    print('Turn 2:', r2_text)

    # Send Turn 2 to history
    messages.append({'role': 'assistant', 'content': r2_text})

    # Ask Turn 3 with contect
    messages.append({'role': 'user', 'content': 'What is the most popular thing to do there?'})
    r3 = client.messages.create(model='claude-sonnet-5', max_tokens=100, messages=messages)
    r3_text = next(b.text for b in r3.content if b.type == 'text')
    print('Turn 3:', r3_text)


if __name__ == '__main__':
    main()
