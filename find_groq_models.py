"""Find more working Groq models."""
import requests
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('GROQ_API_KEY')

# Try more models
models = [
    'llama-3.3-70b-versatile',
    'llama-3.1-8b-instant',
    'llama-3.2-1b-preview',
    'llama-3.2-3b-preview',
    'llama-3.2-11b-vision-preview',
    'llama-3.2-90b-vision-preview',
    'gemma-7b-it',
    'gemma2-9b-it',
    'mixtral-8x7b-32768',
    'llama-guard-3-8b',
]

print("Testing Groq models:\n")

working = []
for model in models:
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": model,
            "messages": [{"role": "user", "content": "Hi"}],
            "max_tokens": 5
        }
    )
    
    if response.status_code == 200:
        print(f"✓ {model}")
        working.append(model)
    else:
        print(f"✗ {model}")

print(f"\n\nWorking models ({len(working)}):")
for m in working:
    print(f"  - {m}")
