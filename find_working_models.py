"""
Test which OpenRouter free models are currently available
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('OPENROUTER_API_KEY')

# Free models to test (based on OpenRouter docs)
free_models = [
    'mistralai/mistral-7b-instruct:free',
    'meta-llama/llama-3-8b-instruct:free',  # Try without .1
    'google/gemma-7b-it:free',  # Try 7b instead of 9b
    'nousresearch/hermes-3-llama-3.1-405b:free',
    'qwen/qwen-2-7b-instruct:free',
    'huggingfaceh4/zephyr-7b-beta:free',
    'openchat/openchat-7b:free',
]

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json",
    "HTTP-Referer": "https://github.com/allamzoo/acl_2_FPL",
    "X-Title": "FPL Graph-RAG"
}

working_models = []

for model in free_models:
    print(f"Testing: {model}...", end=" ")
    
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": "Hi"}],
        "max_tokens": 10
    }
    
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=15
        )
        
        if response.status_code == 200:
            print("✓ WORKS!")
            working_models.append(model)
        else:
            print(f"❌ {response.status_code}")
            
    except Exception as e:
        print(f"❌ {str(e)[:50]}")

print(f"\n{'='*80}")
print(f"Working Models ({len(working_models)}):")
print('='*80)
for model in working_models:
    print(f"  ✓ {model}")
