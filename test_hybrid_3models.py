"""
Test Hybrid Setup: 
- Gemma 2 2B → HuggingFace
- Llama 3 8B → HuggingFace  
- Mistral 7B → OpenRouter
"""

import os
from dotenv import load_dotenv
from src.llm.generator import FPLAnswerGenerator

# Load environment variables
load_dotenv()

def test_hybrid_models():
    """Test all 3 models using hybrid backend."""
    
    print("=" * 80)
    print("Testing 3 Models with Hybrid Backend")
    print("=" * 80)
    print("Gemma 2 2B     → HuggingFace API")
    print("Llama 3 8B     → HuggingFace API")
    print("Mistral 7B     → OpenRouter API")
    print("=" * 80)
    print()
    
    # Check API keys
    hf_key = os.getenv('HUGGINGFACE_API_KEY')
    or_key = os.getenv('OPENROUTER_API_KEY')
    
    if not hf_key:
        print("❌ Error: HUGGINGFACE_API_KEY not found in .env file")
        return
    if not or_key:
        print("❌ Error: OPENROUTER_API_KEY not found in .env file")
        return
    
    print(f"✓ HuggingFace API Key: {hf_key[:20]}...")
    print(f"✓ OpenRouter API Key: {or_key[:20]}...")
    print()
    
    # Initialize generator with hybrid backend
    print("Initializing FPL Answer Generator (Hybrid Mode)...")
    generator = FPLAnswerGenerator(llm_backend='hybrid')
    print("✓ Generator initialized")
    print()
    
    # Test query
    test_query = "Who is the top goalscorer in the 2023-24 season?"
    season = "2023-24"
    
    print(f"Test Query: '{test_query}'")
    print(f"Season: {season}")
    print()
    
    # Test each model
    models = [
        ('gemma-2-2b', 'HuggingFace'),
        ('llama-3-8b', 'HuggingFace'),
        ('mistral-7b', 'OpenRouter')
    ]
    
    results = []
    
    for i, (model, backend) in enumerate(models, 1):
        print("=" * 80)
        print(f"Model {i}/3: {model} (via {backend})")
        print("=" * 80)
        
        try:
            result = generator.answer(
                query=test_query,
                season=season,
                model=model,
                task_type='query'
            )
            
            print(f"\n✓ Answer Generated Successfully!")
            print(f"\nAnswer Preview:\n{result['answer'][:300]}...")
            print(f"\nStats:")
            print(f"  - Backend: {backend}")
            print(f"  - Model: {result['model']}")
            print(f"  - Tokens Used: {result['tokens']}")
            print(f"  - Cost: ${result['cost']:.6f}")
            print(f"  - Retrieved Players: {result.get('retrieved_count', 'N/A')}")
            
            results.append({
                'model': model,
                'backend': backend,
                'success': True,
                'tokens': result['tokens'],
                'answer_length': len(result['answer'])
            })
            
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            results.append({
                'model': model,
                'backend': backend,
                'success': False,
                'error': str(e)
            })
        
        print()
    
    # Summary
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    successful = sum(1 for r in results if r['success'])
    print(f"Successful: {successful}/3 models")
    print()
    
    for r in results:
        status = "✓" if r['success'] else "❌"
        print(f"{status} {r['model']:15} ({r['backend']:12}) - ", end="")
        if r['success']:
            print(f"{r['tokens']} tokens, {r['answer_length']} chars")
        else:
            print(f"FAILED - {r.get('error', 'Unknown error')[:50]}")
    
    print("=" * 80)


if __name__ == "__main__":
    test_hybrid_models()
