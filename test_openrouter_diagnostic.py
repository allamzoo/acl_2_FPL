"""
Diagnostic script to check OpenRouter API response details
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('OPENROUTER_API_KEY')

# Test models
models_to_test = [
    'google/gemma-2-9b-it:free',
    'meta-llama/llama-3.1-8b-instruct:free',
    'mistralai/mistral-7b-instruct:free',
]

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://github.com/allamzoo/acl_2_FPL",
    "X-Title": "FPL Graph-RAG"
}

for model in models_to_test:
    print(f"\n{'='*80}")
    print(f"Testing: {model}")
    print('='*80)
    
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "Say hello"}],
        "max_tokens": 50
    }
    
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:500]}")
        
        if response.status_code == 200:
            print("✓ SUCCESS!")
        else:
            print("❌ FAILED")
            
    except Exception as e:
        print(f"Error: {e}")
