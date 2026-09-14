import requests, os
from dotenv import load_dotenv

load_dotenv()

response = requests.post(
    'https://api.anthropic.com/v1/messages',
    headers={
        'anthropic-version': '2023-06-01',
        'content-type': 'application/json',
        'x-api-key': os.environ['ANTHROPIC_API_KEY'],
    },
    json={
        'model': 'claude-sonnet-5',
        'max_tokens': 200,
        'messages': [{'role':'user','content':'What is the easiest way to stay lean.'}]
    }
)

print(response.json()['content'][0]['text'])