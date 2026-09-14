from anthropic import Anthropic
from dotenv import load_dotenv


load_dotenv()
client = Anthropic()
messages = []
messages.append({'role': 'user', "content": 'What is the easiest way to stay lean?'})
r1 = client.messages.create(model='claude-sonnet-5', max_tokens=100, messages=messages)
print("r1: ", r1.content[0].text)