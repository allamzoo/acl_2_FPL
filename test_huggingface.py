"""
Test LLM with HuggingFace (Free Tier)
"""

import logging
import time
from src.llm.generator import create_answer_generator

logging.basicConfig(level=logging.INFO, format='%(message)s')


def test_huggingface():
    """Test using HuggingFace free inference API."""
    
    print("=" * 100)
    print(" " * 25 + "HUGGINGFACE LLM TEST (Free Tier)")
    print("=" * 100)
    
    # Use HuggingFace backend
    generator = create_answer_generator(
        llm_backend="huggingface",
        default_llm="mistral-7b"
    )
    
    try:
        query = "Who are the top 5 goalscorers in the Premier League?"
        season = "2022-23"
        
        print(f"\n📋 Query: '{query}'")
        print(f"Season: {season}")
        print(f"Backend: HuggingFace Inference API")
        
        # Test with Mistral 7B first
        print("\n" + "=" * 100)
        print("Testing Mistral 7B Instruct")
        print("=" * 100)
        
        start_time = time.time()
        result = generator.answer(
            query=query,
            season=season,
            model="mistral-7b",
            task_type="answer",
            max_tokens=512,
            temperature=0.3
        )
        elapsed = time.time() - start_time
        
        print(f"\n✓ Answer generated in {elapsed:.2f} seconds")
        
        if result.get('answer') and 'Error' not in result['answer']:
            print(f"\n📝 ANSWER:")
            print("-" * 100)
            print(result['answer'])
            print("-" * 100)
            
            print(f"\n📊 STATISTICS:")
            print(f"  • Model: {result['model']}")
            print(f"  • Backend: {result['backend']}")
            print(f"  • Total Tokens: {result['tokens']}")
            print(f"  • Prompt Tokens: {result['prompt_tokens']}")
            print(f"  • Completion Tokens: {result['completion_tokens']}")
            print(f"  • Time: {elapsed:.2f}s")
            print(f"  • Retrieved Players: {result['context']['num_players']}")
            
            print("\n✅ HuggingFace API is working!")
            
        else:
            print(f"\n⚠️  Error: {result.get('answer', 'Unknown error')}")
            print("\nThis might be due to:")
            print("  • Model loading (HuggingFace models need warm-up)")
            print("  • Rate limiting (free tier has limits)")
            print("  • API key issues")
            
        # Try comparing all three models
        choice = input("\n\nTest all 3 models? (y/n): ").strip().lower()
        
        if choice == 'y':
            print("\n" + "=" * 100)
            print("COMPARING ALL 3 MODELS")
            print("=" * 100)
            print("Note: This may take 2-3 minutes as models need to load...")
            
            comparison = generator.compare_models(
                query=query,
                season=season,
                task_type="answer",
                max_tokens=512,
                temperature=0.3
            )
            
            for model_key in ['mistral-7b', 'llama-3-8b', 'gemma-7b']:
                if model_key in comparison['models']:
                    result = comparison['models'][model_key]
                    
                    print(f"\n{'=' * 100}")
                    print(f"MODEL: {model_key.upper()}")
                    print(f"{'=' * 100}")
                    
                    if not result.get('error'):
                        print(f"\n📝 ANSWER:")
                        print("-" * 100)
                        print(result['answer'][:500])  # First 500 chars
                        if len(result['answer']) > 500:
                            print("... (truncated)")
                        print("-" * 100)
                        
                        print(f"\n📊 Stats: {result['tokens']} tokens")
                    else:
                        print(f"\n⚠️  Error: {result['error']}")
            
            # Show comparison table
            print("\n" + "=" * 100)
            print("COMPARISON TABLE")
            print("=" * 100)
            print(f"\n{'Model':<20} {'Tokens':<12} {'Status'}")
            print("-" * 50)
            
            for model_key in ['mistral-7b', 'llama-3-8b', 'gemma-2b']:
                if model_key in comparison['models']:
                    result = comparison['models'][model_key]
                    status = "✓ Success" if not result.get('error') else "✗ Error"
                    print(f"{model_key:<20} {result['tokens']:<12} {status}")
    
    finally:
        generator.close()
    
    print("\n" + "=" * 100)
    print("✓ TEST COMPLETE")
    print("=" * 100)


if __name__ == "__main__":
    test_huggingface()
