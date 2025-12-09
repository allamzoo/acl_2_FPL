"""
Test OpenRouter with 3 models: Gemma 2, Llama 3, Mistral 7B
"""

import os
from dotenv import load_dotenv
from src.llm.generator import FPLAnswerGenerator

# Load environment variables
load_dotenv()

def test_openrouter_models():
    """Test all 3 models on OpenRouter."""
    
    print("=" * 80)
    print("Testing 3 Models on OpenRouter (FREE)")
    print("=" * 80)
    print()
    
    # Check API key
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print("❌ Error: OPENROUTER_API_KEY not found in .env file")
        return
    
    print(f"✓ API Key found: {api_key[:20]}...")
    print()
    
    # Initialize generator with OpenRouter backend
    print("Initializing FPL Answer Generator with OpenRouter...")
    generator = FPLAnswerGenerator(llm_backend='openrouter')
    print("✓ Generator initialized")
    print()
    
    # Test query
    test_query = "Who is the top goalscorer in the 2023-24 season?"
    season = "2023-24"
    
    print(f"Test Query: '{test_query}'")
    print(f"Season: {season}")
    print()
    
    # Test each model
    models = ['gemma-2-2b', 'llama-3-8b', 'mistral-7b']
    
    for i, model in enumerate(models, 1):
        print("=" * 80)
        print(f"Model {i}/3: {model}")
        print("=" * 80)
        
        try:
            result = generator.answer(
                query=test_query,
                season=season,
                model=model,
                task_type='query'
            )
            
            print(f"\n✓ Answer:\n{result['answer'][:500]}...")
            print(f"\nStats:")
            print(f"  - Model: {result['model']}")
            print(f"  - Tokens: {result['tokens']}")
            print(f"  - Cost: ${result['cost']:.6f}")
            print(f"  - Retrieved Players: {result['retrieved_count']}")
            
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
        
        print()
    
    print("=" * 80)
    print("Test Complete!")
    print("=" * 80)


if __name__ == "__main__":
    test_openrouter_models()
