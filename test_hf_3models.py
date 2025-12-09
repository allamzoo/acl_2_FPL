"""
Test script for 3-model comparison using HuggingFace API.

Models:
1. Gemma 2 2B Instruct (google/gemma-2-2b-it)
2. Llama 3 8B Instruct (meta-llama/Meta-Llama-3-8B-Instruct)
3. Mistral 7B Instruct v0.3 (mistralai/Mistral-7B-Instruct-v0.3)
"""

import os
from dotenv import load_dotenv
from src.llm.generator import FPLAnswerGenerator

# Load environment variables
load_dotenv()

def test_three_models():
    """Test all three HuggingFace models with a simple FPL query."""
    
    print("=" * 80)
    print("Testing 3 HuggingFace Models for FPL Graph-RAG")
    print("=" * 80)
    print()
    
    # Check API key
    api_key = os.getenv('HUGGINGFACE_API_KEY')
    if not api_key:
        print("❌ ERROR: HUGGINGFACE_API_KEY not found in .env file")
        print("Please add your HuggingFace API key to .env:")
        print("HUGGINGFACE_API_KEY=your_key_here")
        return
    
    print(f"✓ HuggingFace API Key: {api_key[:10]}...{api_key[-5:]}")
    print()
    
    # Initialize generator with HuggingFace backend
    print("Initializing FPL Answer Generator with HuggingFace backend...")
    try:
        generator = FPLAnswerGenerator(llm_backend='huggingface')
        print("✓ Generator initialized successfully")
        print()
    except Exception as e:
        print(f"❌ Error initializing generator: {e}")
        return
    
    # Test query
    query = "Who scored the most goals in the 2023/24 season?"
    season = "2023/24"
    
    print(f"Query: '{query}'")
    print(f"Season: {season}")
    print()
    print("=" * 80)
    
    # Test each model
    models = ['gemma-2-2b', 'llama-3-8b', 'mistral-7b']
    
    for i, model in enumerate(models, 1):
        print(f"\n{i}. Testing Model: {model}")
        print("-" * 80)
        
        try:
            result = generator.answer(
                query=query,
                season=season,
                model=model,
                task_type='factual'
            )
            
            print(f"✓ Response generated successfully")
            print(f"\nAnswer:\n{result['answer']}")
            print(f"\nTokens Used: {result['tokens']}")
            print(f"Retrieved Players: {result['retrieved_count']}")
            print(f"Backend: {result.get('backend', 'Unknown')}")
            
        except Exception as e:
            print(f"❌ Error with {model}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("Testing Complete!")
    print("=" * 80)


def test_comparison():
    """Test compare_models() method for side-by-side comparison."""
    
    print("\n" + "=" * 80)
    print("3-Model Comparison Test")
    print("=" * 80)
    print()
    
    # Initialize generator
    generator = FPLAnswerGenerator(llm_backend='huggingface')
    
    # Test query
    query = "Who is the best midfielder for my FPL team under 8 million?"
    season = "2023/24"
    
    print(f"Query: '{query}'")
    print(f"Season: {season}")
    print()
    
    try:
        results = generator.compare_models(
            query=query,
            season=season,
            task_type='recommendation'
        )
        
        print("=" * 80)
        for model, result in results.items():
            print(f"\nModel: {model}")
            print("-" * 80)
            print(f"Answer:\n{result['answer']}")
            print(f"\nTokens: {result['tokens']} | Backend: {result.get('backend', 'Unknown')}")
            print()
        
        print("=" * 80)
        print("Comparison Complete!")
        print("=" * 80)
        
    except Exception as e:
        print(f"❌ Error in comparison: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    # Test individual models
    test_three_models()
    
    # Test comparison
    test_comparison()
