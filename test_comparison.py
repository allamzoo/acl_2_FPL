"""
Comprehensive 3-Model Comparison Test
Tests all 3 Groq models side-by-side with the same query
"""

import os
from dotenv import load_dotenv
from src.llm.generator import FPLAnswerGenerator

load_dotenv()

def compare_models():
    """Compare all 3 models side-by-side."""
    
    print("=" * 80)
    print("3-MODEL COMPARISON TEST")
    print("=" * 80)
    print()
    
    # Initialize generator
    generator = FPLAnswerGenerator(llm_backend='hybrid')
    
    # Test queries
    queries = [
        ("Who is the top goalscorer in the 2023-24 season?", "2023-24", "query"),
        ("Which midfielder has the best points per game?", "2023-24", "analysis"),
        ("Should I transfer in Haaland?", "2023-24", "advice"),
    ]
    
    for i, (query, season, task_type) in enumerate(queries, 1):
        print("=" * 80)
        print(f"TEST {i}/3: {query}")
        print("=" * 80)
        print(f"Task Type: {task_type}")
        print()
        
        try:
            # Use compare_models method for side-by-side comparison
            comparison = generator.compare_models(
                query=query,
                season=season,
                task_type=task_type
            )
            
            # Display results
            results = comparison.get('models', {})
            for model_key, result in results.items():
                model_name = {
                    'llama-4-maverick': 'Llama 4 Maverick',
                    'qwen-3-32b': 'Qwen 3 32B',
                    'gpt-oss-20b': 'GPT OSS 20B'
                }.get(model_key, model_key)
                
                print(f"\n{'='*80}")
                print(f"{model_name}")
                print('='*80)
                
                # Show answer
                answer = result.get('answer', 'N/A')
                print(f"{answer[:300]}...")
                
                # Show stats
                print(f"\nStats: {result.get('tokens', 0)} tokens, "
                      f"{len(answer)} chars, "
                      f"${result.get('cost', 0):.6f}")
            
            print("\n")
            
        except Exception as e:
            print(f"❌ Error: {e}\n")
    
    print("=" * 80)
    print("Comparison test complete!")
    print("=" * 80)


if __name__ == "__main__":
    compare_models()
