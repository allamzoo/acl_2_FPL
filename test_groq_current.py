"""Test current Groq models from their docs."""
import requests
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('GROQ_API_KEY')

# Current models from Groq docs (Dec 2025)
models = [
    'llama-3.3-70b-versatile',  # Llama 3.3
    'llama-3.1-8b-instant',      # Llama 3.1 8B (works)
    'mixtral-8x7b-32768',        # Mixtral
    'gemma2-9b-it',              # Gemma 2
]

print("Testing Groq models (December 2025):\n")

for model in models:
    print(f"Testing: {model}...")
    
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": model,
            "messages": [{"role": "user", "content": "Say hi"}],
            "max_tokens": 10
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        content = result['choices'][0]['message']['content']
        print(f"  ✓ {model} - Working! Response: {content}\n")
    else:
        error = response.json().get('error', {}).get('message', response.text)
        print(f"  ✗ {model} - Error: {error[:100]}\n")
