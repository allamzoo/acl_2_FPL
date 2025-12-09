"""Quick test to see Groq error details."""
import requests
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('GROQ_API_KEY')

# Test models
models = [
    'llama-3.1-8b-instant',
    'llama-3.1-70b-versatile', 
    'gemma2-9b-it',
    'llama3-8b-8192',
    'gemma-7b-it'
]

for model in models:
    print(f"\nTesting: {model}")
    
    response = requests.post(
        "https://api.groq.com/openai/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        },
        json={
            "model": model,
            "messages": [{"role": "user", "content": "Hi"}],
            "max_tokens": 10
        }
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code != 200:
        print(f"Error: {response.text}")
    else:
        print("✓ Success")
