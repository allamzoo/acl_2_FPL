"""
Test LLM Model Comparison - Mistral 7B vs Llama 3 8B vs Gemma 7B

Compares three free models on:
1. Answer quality
2. Response accuracy
3. Token usage
4. Speed
5. Following instructions
"""

import logging
import time
from src.llm.generator import create_answer_generator

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)

logger = logging.getLogger(__name__)


def print_separator(title="", char="=", width=100):
    """Print formatted separator."""
    if title:
        padding = (width - len(title) - 2) // 2
        print(f"\n{char * padding} {title} {char * padding}")
    else:
        print(f"\n{char * width}")


def print_model_response(model_key: str, result: dict):
    """Print formatted model response."""
    print(f"\n{'='*100}")
    print(f"MODEL: {model_key.upper()}")
    print(f"Full Name: {result['model_info']['description']}")
    print(f"Strengths: {', '.join(result['model_info']['strengths'])}")
    print(f"{'='*100}")
    
    print(f"\n📝 ANSWER:")
    print(f"{'-'*100}")
    print(result['answer'])
    print(f"{'-'*100}")
    
    print(f"\n📊 STATISTICS:")
    print(f"  • Total Tokens: {result['tokens']}")
    print(f"  • Prompt Tokens: {result['prompt_tokens']}")
    print(f"  • Completion Tokens: {result['completion_tokens']}")
    print(f"  • Cost: ${result['cost']:.6f}")
    print(f"  • Backend: {result['backend']}")
    
    if result.get('error'):
        print(f"\n⚠️  ERROR: {result['error']}")


def test_single_model():
    """Test a single model with one query."""
    print_separator("SINGLE MODEL TEST", "=")
    print("Testing one model with FPL question")
    
    # Initialize generator (uses OpenRouter by default)
    generator = create_answer_generator(
        llm_backend="openrouter",
        default_llm="mistral-7b"
    )
    
    try:
        # Test query
        query = "Who are the top goalscorers in the Premier League?"
        season = "2022-23"
        
        print(f"\n📋 Query: '{query}'")
        print(f"Season: {season}")
        
        # Generate answer
        print("\nProcessing...")
        start_time = time.time()
        
        result = generator.answer(
            query=query,
            season=season,
            model="mistral-7b",
            task_type="answer",
            max_tokens=512,
            temperature=0.3
        )
        
        elapsed_time = time.time() - start_time
        
        # Display result
        print_separator("RESULT")
        print(f"\n✓ Answer generated in {elapsed_time:.2f} seconds")
        
        print(f"\n📝 ANSWER:")
        print(f"{'-'*100}")
        print(result['answer'])
        print(f"{'-'*100}")
        
        print(f"\n📊 CONTEXT SUMMARY:")
        print(f"  • Retrieved Players: {result['context']['num_players']}")
        print(f"  • Prompt Length: {result['prompt_length']} characters")
        
        print(f"\n📊 MODEL STATISTICS:")
        print(f"  • Model: {result['model']}")
        print(f"  • Total Tokens: {result['tokens']}")
        print(f"  • Prompt Tokens: {result['prompt_tokens']}")
        print(f"  • Completion Tokens: {result['completion_tokens']}")
        print(f"  • Cost: ${result['cost']:.6f}")
        print(f"  • Time: {elapsed_time:.2f}s")
        
    finally:
        generator.close()
    
    print_separator("✓ SINGLE MODEL TEST COMPLETE")


def test_model_comparison():
    """Compare all three models on same query."""
    print_separator("THREE-MODEL COMPARISON TEST", "=")
    print("Comparing Mistral 7B vs Llama 3 8B vs Gemma 7B")
    
    # Initialize generator
    generator = create_answer_generator(llm_backend="openrouter")
    
    try:
        # List available models
        print("\n📋 Available Models:")
        for model in generator.list_available_models():
            print(f"\n  • {model['key']}:")
            print(f"    Name: {model['name']}")
            print(f"    Description: {model['description']}")
            print(f"    Strengths: {', '.join(model['strengths'])}")
        
        # Test queries
        test_queries = [
            {
                'query': "Who are the best midfielders with high creativity and assists?",
                'season': "2022-23",
                'task': "answer"
            },
            {
                'query': "Recommend cheap defenders under 5 million for my FPL team",
                'season': "2022-23",
                'task': "recommend"
            }
        ]
        
        for i, test_case in enumerate(test_queries, 1):
            print_separator(f"TEST QUERY {i}", "=")
            print(f"Query: '{test_case['query']}'")
            print(f"Season: {test_case['season']}")
            print(f"Task Type: {test_case['task']}")
            
            # Compare all models
            print("\n⏳ Generating answers from all 3 models...")
            start_time = time.time()
            
            comparison = generator.compare_models(
                query=test_case['query'],
                season=test_case['season'],
                task_type=test_case['task'],
                max_tokens=512,
                temperature=0.3
            )
            
            elapsed_time = time.time() - start_time
            
            # Display results
            print(f"\n✓ All answers generated in {elapsed_time:.2f} seconds")
            
            print(f"\n📊 CONTEXT INFO:")
            print(f"  • Retrieved Players: {comparison['context']['num_players']}")
            print(f"  • Prompt Length: {comparison['prompt_length']} characters")
            
            # Show each model's response
            for model_key in ['qwen-2.5', 'phi-3-mini', 'gemma-2b']:
                if model_key in comparison['models']:
                    print_model_response(model_key, comparison['models'][model_key])
            
            # Comparison table
            print_separator("COMPARISON TABLE")
            print(f"\n{'Model':<20} {'Tokens':<12} {'Completion':<12} {'Cost':<12} {'Status'}")
            print(f"{'-'*70}")
            
            for model_key in ['qwen-2.5', 'phi-3-mini', 'gemma-2b']:
                if model_key in comparison['models']:
                    result = comparison['models'][model_key]
                    status = "✓ Success" if not result.get('error') else "✗ Error"
                    print(f"{model_key:<20} {result['tokens']:<12} {result['completion_tokens']:<12} "
                          f"${result['cost']:<11.6f} {status}")
            
            if i < len(test_queries):
                input("\n\nPress Enter to continue to next test query...")
        
        # Final statistics
        print_separator("CUMULATIVE STATISTICS")
        stats = generator.get_model_stats()
        
        print(f"\n{'Model':<20} {'Total Tokens':<15} {'Total Cost'}")
        print(f"{'-'*50}")
        for model_key, model_stats in stats.items():
            print(f"{model_key:<20} {model_stats['total_tokens']:<15} ${model_stats['total_cost']:.6f}")
        
    finally:
        generator.close()
    
    print_separator("✓ THREE-MODEL COMPARISON COMPLETE", "=")


def test_different_tasks():
    """Test models with different task types."""
    print_separator("TASK TYPE COMPARISON", "=")
    print("Testing different task types: answer, recommend, compare")
    
    generator = create_answer_generator(llm_backend="openrouter", default_llm="mistral-7b")
    
    try:
        tasks = [
            {
                'query': "Who are the top goalscorers?",
                'task': "answer",
                'description': "General question answering"
            },
            {
                'query': "Recommend premium forwards worth the money",
                'task': "recommend",
                'description': "Player recommendations"
            },
            {
                'query': "Compare Mohamed Salah and Kevin De Bruyne",
                'task': "compare",
                'description': "Player comparison"
            }
        ]
        
        for i, task_case in enumerate(tasks, 1):
            print_separator(f"TASK {i}: {task_case['task'].upper()}")
            print(f"Description: {task_case['description']}")
            print(f"Query: '{task_case['query']}'")
            
            result = generator.answer(
                query=task_case['query'],
                season="2022-23",
                model="mistral-7b",
                task_type=task_case['task'],
                max_tokens=512
            )
            
            print(f"\n📝 ANSWER:")
            print(f"{'-'*100}")
            print(result['answer'])
            print(f"{'-'*100}")
            
            print(f"\n📊 Stats: {result['tokens']} tokens")
            
            if i < len(tasks):
                input("\n\nPress Enter for next task type...")
    
    finally:
        generator.close()
    
    print_separator("✓ TASK TYPE COMPARISON COMPLETE")


def main():
    """Run all tests."""
    print("="*100)
    print(" "*35 + "LLM MODEL COMPARISON TESTS")
    print(" "*20 + "Mistral 7B vs Llama 3 8B vs Gemma 7B")
    print("="*100)
    
    print("\n🔑 SETUP:")
    print("  Make sure you have set up your API keys:")
    print("  1. Copy .env.example to .env")
    print("  2. Add your OPENROUTER_API_KEY or HUGGINGFACE_API_KEY")
    print("  3. Get keys from:")
    print("     - OpenRouter: https://openrouter.ai/keys")
    print("     - HuggingFace: https://huggingface.co/settings/tokens")
    
    print("\n📋 TESTS:")
    print("  1. Single model test (quick validation)")
    print("  2. Three-model comparison (main comparison)")
    print("  3. Task type comparison (answer/recommend/compare)")
    
    choice = input("\n\nSelect test (1/2/3) or 'all' for all tests: ").strip().lower()
    
    try:
        if choice == '1':
            test_single_model()
        elif choice == '2':
            test_model_comparison()
        elif choice == '3':
            test_different_tasks()
        elif choice == 'all':
            test_single_model()
            input("\n\nPress Enter to continue to model comparison...")
            test_model_comparison()
            input("\n\nPress Enter to continue to task type tests...")
            test_different_tasks()
        else:
            print("Invalid choice. Running model comparison...")
            test_model_comparison()
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*100)
    print(" "*35 + "✓ ALL TESTS COMPLETE")
    print("="*100)


if __name__ == "__main__":
    main()
