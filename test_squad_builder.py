"""
Test Squad Builder with all 3 LLM models
Query: Build optimal squad under 100 million for season 2022-23
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from src.llm.generator import FPLAnswerGenerator
import time

def test_squad_builder():
    """Test squad building with all 3 LLM models."""
    
    query = "Build an optimal squad under 100 million for season 2022-23"
    season = "2022-23"
    
    # LLM models to test
    models = [
        "llama-4-maverick",  # Llama 4 Maverick
        "qwen-3-32b",        # Qwen 3 32B
        "gpt-oss-20b"        # GPT OSS 20B
    ]
    
    model_names = {
        "llama-4-maverick": "Llama 4 Maverick",
        "qwen-3-32b": "Qwen 3 32B",
        "gpt-oss-20b": "GPT OSS 20B"
    }
    
    print("=" * 100)
    print("SQUAD BUILDER TEST - ALL 3 LLM MODELS")
    print("=" * 100)
    print(f"\nQuery: {query}")
    print(f"Season: {season}")
    print(f"Budget: 100 million")
    print(f"Formation: 2 GK, 5 DEF, 5 MID, 3 FWD")
    print(f"Optimization: Maximum value ratio (points per million)")
    print()
    
    # Initialize generator
    generator = FPLAnswerGenerator(embedding_model="all-mpnet-base-v2")
    
    for model_id in models:
        model_name = model_names[model_id]
        
        print("=" * 100)
        print(f"MODEL: {model_name} ({model_id})")
        print("=" * 100)
        
        try:
            start_time = time.time()
            
            # Generate answer
            result = generator.answer(
                query=query,
                season=season,
                model=model_id,
                retrieval_mode="baseline"  # Use baseline only for squad building
            )
            
            elapsed = time.time() - start_time
            
            # Display result
            print(f"\n⏱️  Total Time: {elapsed:.2f}s")
            print(f"\n📝 RESPONSE:\n")
            print(result['answer'])
            
            # Display metadata
            if 'metadata' in result:
                meta = result['metadata']
                print(f"\n📊 METADATA:")
                print(f"   Retrieval Time: {meta.get('retrieval_time', 0):.2f}s")
                print(f"   Generation Time: {meta.get('generation_time', 0):.2f}s")
                print(f"   Context Players: {meta.get('context_size', 0)}")
                
                if 'token_usage' in meta:
                    tokens = meta['token_usage']
                    print(f"   Tokens: {tokens.get('total_tokens', 0)} "
                          f"(prompt: {tokens.get('prompt_tokens', 0)}, "
                          f"completion: {tokens.get('completion_tokens', 0)})")
                
                # Show squad summary if available in context
                context = result.get('context', {})
                baseline_results = context.get('baseline_results', {})
                
                if 'squad_builder' in baseline_results:
                    squad_data = baseline_results['squad_builder']
                    print(f"\n   Squad Summary:")
                    print(f"   Total Cost: £{squad_data.get('total_cost', 0):.1f}m")
                    print(f"   Remaining: £{squad_data.get('remaining_budget', 0):.1f}m")
                    print(f"   Total Points: {squad_data.get('total_points', 0)}")
                    print(f"   Squad Size: {squad_data.get('squad_size', 0)}/15")
                    
                    formation = squad_data.get('formation', {})
                    print(f"   Formation: {formation.get('GK', 0)} GK, "
                          f"{formation.get('DEF', 0)} DEF, "
                          f"{formation.get('MID', 0)} MID, "
                          f"{formation.get('FWD', 0)} FWD")
            
            print()
            
        except Exception as e:
            print(f"\n❌ Error with {model_name}: {str(e)}")
            import traceback
            traceback.print_exc()
            print()
    
    # Cleanup
    generator.close()
    
    print("=" * 100)
    print("✅ TEST COMPLETE")
    print("=" * 100)


if __name__ == "__main__":
    test_squad_builder()
