"""
Check which models are currently available on HuggingFace Inference API.
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('HUGGINGFACE_API_KEY')

# Models to test
test_models = [
    # Current broken ones
    "google/gemma-2-2b-it",
    "meta-llama/Meta-Llama-3-8B-Instruct",
    "mistralai/Mistral-7B-Instruct-v0.3",
    
    # Try some alternatives
    "google/gemma-2-9b-it",
    "microsoft/Phi-3-mini-4k-instruct",
    "meta-llama/Llama-3.2-1B-Instruct",
    "meta-llama/Llama-3.2-3B-Instruct",
    "mistralai/Mistral-7B-Instruct-v0.1",
    "mistralai/Mistral-7B-Instruct-v0.2",
    "Qwen/Qwen2.5-7B-Instruct",
    "HuggingFaceH4/zephyr-7b-beta",
    "tiiuae/falcon-7b-instruct",
]

headers = {"Authorization": f"Bearer {api_key}"}

print("Testing HuggingFace Inference API Model Availability")
print("=" * 80)
print()

available = []
unavailable = []

for model in test_models:
    url = f"https://api-inference.huggingface.co/models/{model}"
    
    try:
        response = requests.post(
            url,
            headers=headers,
            json={"inputs": "Hello"},
            timeout=10
        )
        
        if response.status_code == 200:
            print(f"✓ {model} - AVAILABLE")
            available.append(model)
        elif response.status_code == 410:
            print(f"✗ {model} - DEPRECATED (410 Gone)")
            unavailable.append(model)
        elif response.status_code == 503:
            print(f"⏳ {model} - LOADING (503)")
            available.append(model)  # Model exists, just loading
        else:
            print(f"? {model} - {response.status_code}: {response.text[:100]}")
            
    except Exception as e:
        print(f"✗ {model} - ERROR: {e}")
        unavailable.append(model)

print()
print("=" * 80)
print(f"Available Models: {len(available)}")
for model in available:
    print(f"  ✓ {model}")

print()
print(f"Unavailable Models: {len(unavailable)}")
for model in unavailable:
    print(f"  ✗ {model}")
