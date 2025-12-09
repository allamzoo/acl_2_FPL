"""
Test 3 Groq Models:
1. Llama 4 Maverick 17B
2. Qwen 3 32B
3. GPT OSS 20B
"""

import os
from dotenv import load_dotenv
from src.llm.generator import FPLAnswerGenerator

# Load environment variables
load_dotenv()

def test_groq_models():
    """Test all 3 Groq models."""
    
    print("=" * 80)
    print("Testing 3 Groq Models (FREE)")
    print("=" * 80)
    print("1. Llama 4 Maverick 17B - Latest Meta model with 128K context")
    print("2. Qwen 3 32B           - Powerful reasoning and analysis")
    print("3. GPT OSS 20B          - OpenAI open source model")
    print("=" * 80)
    print()
    
    # Check API key
    api_key = os.getenv('GROQ_API_KEY')
    if not api_key:
        print("❌ Error: GROQ_API_KEY not found in .env file")
        return
    
    print(f"✓ Groq API Key: {api_key[:20]}...")
    print()
    
    # Initialize generator with hybrid backend (will use Groq for all 3)
    print("Initializing FPL Answer Generator (Groq Backend)...")
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
        ('llama-4-maverick', 'Llama 4 Maverick 17B'),
        ('qwen-3-32b', 'Qwen 3 32B'),
        ('gpt-oss-20b', 'GPT OSS 20B')
    ]
    
    results = []
    
    for i, (model_key, model_name) in enumerate(models, 1):
        print("=" * 80)
        print(f"Model {i}/3: {model_name}")
        print("=" * 80)
        
        try:
            result = generator.answer(
                query=test_query,
                season=season,
                model=model_key,
                task_type='query'
            )
            
            print(f"\n✓ Success!")
            print(f"\nAnswer Preview:")
            print("-" * 80)
            answer_preview = result['answer'][:400]
            print(answer_preview)
            if len(result['answer']) > 400:
                print("...")
            print("-" * 80)
            
            print(f"\nStats:")
            print(f"  - Model: {model_name}")
            print(f"  - Tokens Used: {result['tokens']}")
            print(f"  - Cost: ${result['cost']:.6f}")
            print(f"  - Answer Length: {len(result['answer'])} chars")
            
            results.append({
                'model': model_name,
                'success': True,
                'tokens': result['tokens'],
                'answer_length': len(result['answer'])
            })
            
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")
            results.append({
                'model': model_name,
                'success': False,
                'error': str(e)
            })
        
        print()
    
    # Summary
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    successful = sum(1 for r in results if r['success'])
    print(f"Results: {successful}/3 models successful")
    print()
    
    for r in results:
        status = "✓" if r['success'] else "❌"
        print(f"{status} {r['model']:25} - ", end="")
        if r['success']:
            print(f"{r['tokens']:4} tokens, {r['answer_length']:4} chars")
        else:
            print(f"FAILED")
    
    print("=" * 80)
    
    if successful == 3:
        print("\n🎉 All 3 models working! Ready for comparison testing.")
    elif successful > 0:
        print(f"\n⚠️  {successful} model(s) working. Check errors above.")
    else:
        print("\n❌ All models failed. Check API key and network connection.")


if __name__ == "__main__":
    test_groq_models()
