# hello_pip.py
import requests
res = requests.get("https://example.com")
print("Status:", res.status_code)
print(res.text[:200])
