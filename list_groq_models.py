"""Get list of available models from Groq API."""
import requests
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv('GROQ_API_KEY')

# Get models list
response = requests.get(
    "https://api.groq.com/openai/v1/models",
    headers={"Authorization": f"Bearer {api_key}"}
)

if response.status_code == 200:
    models = response.json()
    print(f"Available models on Groq:\n")
    for model in models.get('data', []):
        print(f"  - {model['id']}")
        if 'owned_by' in model:
            print(f"    Owner: {model['owned_by']}")
else:
    print(f"Error: {response.status_code}")
    print(response.text)
