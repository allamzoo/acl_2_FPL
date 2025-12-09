"""
Test Groq API integration with 3 models.
Quick test to verify API key and model availability.
"""

import os
from dotenv import load_dotenv
from src.llm.models import GroqLLM

# Load environment variables
load_dotenv()

def test_groq_models():
    """Test all 3 Groq models."""
    
    models = {
        'llama-3.1-8b': 'llama-3.1-8b-instant',
        'llama-3.1-70b': 'llama-3.1-70b-versatile',
        'gemma-2-9b': 'gemma2-9b-it'
    }
    
    test_prompt = "What is 2+2? Answer in one sentence."
    
    print("="*80)
    print("Testing Groq API with 3 Free Models")
    print("="*80)
    
    # Check API key
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        print("\n❌ ERROR: GROQ_API_KEY not found in .env file")
        print("Add your Groq API key to .env:")
        print("GROQ_API_KEY=your_key_here")
        return
    
    print(f"\n✓ Groq API Key found: {api_key[:20]}...")
    print("\nTesting models...\n")
    
    for model_key, model_name in models.items():
        print(f"\n{'='*80}")
        print(f"Model: {model_key} ({model_name})")
        print("="*80)
        
        llm = GroqLLM(model_name)
        result = llm.generate(test_prompt, max_tokens=50, temperature=0.3)
        
        if 'error' in result:
            print(f"❌ Error: {result['error']}")
        else:
            print(f"✓ Response: {result['response']}")
            print(f"Tokens: {result['tokens']} (Prompt: {result['prompt_tokens']}, Completion: {result['completion_tokens']})")
            print(f"Backend: {result['backend']}")
            print(f"Cost: ${result['cost']:.4f}")


if __name__ == "__main__":
    test_groq_models()
