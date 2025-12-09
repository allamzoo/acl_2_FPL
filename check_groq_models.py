"""
Check available Groq models
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('GROQ_API_KEY')

if not api_key:
    print("❌ GROQ_API_KEY not found in .env")
    print("\nAdd to .env:")
    print("GROQ_API_KEY=your_groq_key_here")
    exit(1)

print(f"✓ API Key found: {api_key[:20]}...")
print("\nFetching available models from Groq...\n")

# Get models list
headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

try:
    response = requests.get(
        "https://api.groq.com/openai/v1/models",
        headers=headers,
        timeout=10
    )
    
    if response.status_code == 200:
        models = response.json()
        print("=" * 80)
        print("AVAILABLE GROQ MODELS:")
        print("=" * 80)
        
        # Look for the models you mentioned
        target_keywords = ['llama-4', 'maverick', 'qwen', 'gpt', 'oss']
        
        for model in models.get('data', []):
            model_id = model.get('id', '')
            
            # Highlight models matching your keywords
            is_target = any(keyword in model_id.lower() for keyword in target_keywords)
            
            if is_target:
                print(f"✓ {model_id}")
            else:
                print(f"  {model_id}")
        
        print("=" * 80)
        
    else:
        print(f"❌ Error {response.status_code}: {response.text}")
        
except Exception as e:
    print(f"❌ Error: {e}")
