"""
Test 3-Model LLM Comparison for FPL Graph-RAG

Compares performance of:
1. Llama 3.1 8B Instant (Meta)
2. Llama 3.1 70B Versatile (Meta)
3. Gemma 2 9B Instruct (Google)

All models run on Groq API (fast & free).
"""

import os
from dotenv import load_dotenv
from src.llm.generator import FPLAnswerGenerator

# Load environment variables
load_dotenv()


def print_separator(title="", width=100):
    """Print formatted separator."""
    if title:
        padding = (width - len(title) - 2) // 2
        print(f"\n{'='*padding} {title} {'='*padding}")
    else:
        print("="*width)


def print_result(result: dict, query: str):
    """Print formatted result."""
    print(f"\nQuery: '{query}'")
    print(f"Model: {result.get('model_info', {}).get('description', result.get('model'))}")
    print(f"Backend: {result.get('backend', 'Unknown')}")
    print(f"\nAnswer:\n{result.get('response', 'No response')}")
    print(f"\nStats:")
    print(f"  - Tokens: {result.get('tokens', 0)} (Prompt: {result.get('prompt_tokens', 0)}, Completion: {result.get('completion_tokens', 0)})")
    print(f"  - Cost: ${result.get('cost', 0):.4f}")
    print(f"  - Retrieved players: {result.get('retrieved_count', 0)}")
    
    if 'error' in result:
        print(f"\n⚠️  Error: {result['error']}")


def test_single_model():
    """Test single model answer generation."""
    print_separator("Test 1: Single Model (Llama 3.1 8B)")
    
    generator = FPLAnswerGenerator(llm_backend='groq')
    
    query = "Who is the top goalscorer in the 2022-23 season?"
    
    print(f"\nGenerating answer with Llama 3.1 8B...")
    result = generator.answer(
        query=query,
        season="2022-23",
        model="llama-3.1-8b",
        task_type="answer"
    )
    
    print_separator()
    print_result(result, query)
    print_separator()


def test_three_model_comparison():
    """Test all 3 models on same question."""
    print_separator("Test 2: Three-Model Comparison")
    
    generator = FPLAnswerGenerator(llm_backend='groq')
    
    query = "Who are the best midfielders under £8m in 2022-23?"
    
    print(f"\nQuery: '{query}'")
    print(f"Season: 2022-23")
    print("\nGenerating answers from all 3 models...\n")
    
    # Compare all models
    results = generator.compare_models(
        query=query,
        season="2022-23",
        task_type="recommend"
    )
    
    print_separator()
    
    # Print each model's response
    for model_key, result in results.items():
        print_separator(f"Model: {model_key.upper()}")
        print_result(result, query)
    
    print_separator()
    
    # Summary comparison
    print_separator("COMPARISON SUMMARY")
    print(f"\n{'Model':<20} {'Tokens':<10} {'Cost':<10} {'Players':<10}")
    print("-" * 50)
    
    for model_key, result in results.items():
        model_name = model_key
        tokens = result.get('tokens', 0)
        cost = result.get('cost', 0)
        players = result.get('retrieved_count', 0)
        print(f"{model_name:<20} {tokens:<10} ${cost:<9.4f} {players:<10}")
    
    print_separator()


def test_task_types():
    """Test different task types with Llama 3.1 70B."""
    print_separator("Test 3: Task Type Comparison (Llama 3.1 70B)")
    
    generator = FPLAnswerGenerator(llm_backend='groq')
    
    tasks = [
        ("Who scored the most goals?", "answer"),
        ("Which defenders should I pick?", "recommend"),
        ("Compare Haaland and Kane", "compare"),
        ("Why is Salah expensive?", "explain")
    ]
    
    for query, task_type in tasks:
        print(f"\n{'-'*80}")
        print(f"Task Type: {task_type.upper()}")
        print(f"Query: '{query}'")
        print(f"{'-'*80}")
        
        result = generator.answer(
            query=query,
            season="2022-23",
            model="llama-3.1-70b",
            task_type=task_type
        )
        
        print(f"\nAnswer:\n{result.get('response', 'No response')}")
        print(f"Tokens: {result.get('tokens', 0)}")
    
    print_separator()


def main():
    """Run all tests."""
    print_separator("FPL Graph-RAG: 3-Model LLM Comparison Test", 100)
    print("\nModels being tested:")
    print("  1. Llama 3.1 8B Instant - Fast, versatile, excellent instruction following")
    print("  2. Llama 3.1 70B Versatile - Powerful, excellent reasoning")
    print("  3. Gemma 2 9B Instruct - Efficient, good for structured outputs")
    print("\nBackend: Groq (fast & free)")
    
    # Check API key
    if not os.getenv('GROQ_API_KEY'):
        print("\n❌ ERROR: GROQ_API_KEY not found in .env file")
        print("Please add your Groq API key to .env:")
        print("GROQ_API_KEY=your_key_here")
        return
    
    print("\n✓ Groq API key found")
    
    # Run tests
    try:
        # Test 1: Single model
        test_single_model()
        
        input("\nPress Enter to continue to Test 2 (Three-Model Comparison)...")
        
        # Test 2: Three-model comparison
        test_three_model_comparison()
        
        input("\nPress Enter to continue to Test 3 (Task Types)...")
        
        # Test 3: Task types
        test_task_types()
        
        print_separator("ALL TESTS COMPLETE", 100)
        print("\n✓ Successfully tested all 3 models")
        print("\nNext steps:")
        print("  1. Review answer quality and accuracy")
        print("  2. Check for hallucinations (incorrect stats)")
        print("  3. Compare reasoning quality across models")
        print("  4. Document which model performs best for FPL queries")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
