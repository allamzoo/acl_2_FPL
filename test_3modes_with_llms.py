"""
Test all 3 retrieval modes with LLM generation
Shows how baseline-only, baseline+model1, and baseline+model2 affect LLM answers
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from src.llm.generator import FPLAnswerGenerator


def test_3_modes_with_llms():
    """Test all 3 retrieval modes and send results to LLMs."""
    
    print("=" * 80)
    print("3 RETRIEVAL MODES → LLM GENERATION TEST")
    print("=" * 80)
    
    # Initialize generator
    print("\nInitializing FPL Answer Generator...")
    generator = FPLAnswerGenerator(default_llm="llama-4-maverick")
    print("✓ Generator initialized\n")
    
    # Test query
    query = "Who were the top scorers in 2022-23?"
    season = "2022-23"
    
    print(f"QUERY: {query}")
    print(f"SEASON: {season}\n")
    
    # Test all 3 modes
    modes = [
        ("baseline", "Baseline Only (Cypher)"),
        ("baseline+embedding1", "Baseline + Model 1 (all-mpnet-base-v2, 768 dims)"),
        ("baseline+embedding2", "Baseline + Model 2 (all-MiniLM-L6-v2, 384 dims)")
    ]
    
    results = {}
    
    for mode_key, mode_desc in modes:
        print("=" * 80)
        print(f"MODE: {mode_desc}")
        print("=" * 80)
        
        try:
            # Generate answer with this mode
            result = generator.answer(
                query=query,
                season=season,
                model="llama-4-maverick",
                retrieval_mode=mode_key,
                temperature=0.3
            )
            
            # Extract info
            answer = result.get('answer', 'No answer generated')
            context_info = result.get('context', {})
            num_players = len(context_info.get('unified_players', []))
            tokens = result.get('tokens_used', 0)
            
            print(f"\n✓ Answer generated")
            print(f"  Players in context: {num_players}")
            print(f"  Tokens used: {tokens}")
            print(f"\n🦙 Llama 4 Answer:")
            print("-" * 80)
            print(answer)
            print("-" * 80)
            
            results[mode_key] = {
                'answer': answer,
                'num_players': num_players,
                'tokens': tokens
            }
            
        except Exception as e:
            print(f"\n✗ Generation failed: {str(e)}")
            import traceback
            traceback.print_exc()
        
        print()
    
    # Summary comparison
    print("=" * 80)
    print("COMPARISON SUMMARY")
    print("=" * 80)
    
    print(f"\n{'Mode':<30} {'Players':<10} {'Tokens':<10}")
    print("-" * 80)
    for mode_key, mode_desc in modes:
        if mode_key in results:
            r = results[mode_key]
            print(f"{mode_key:<30} {r['num_players']:<10} {r['tokens']:<10}")
    
    print("\n" + "=" * 80)
    print("KEY TAKEAWAYS:")
    print("=" * 80)
    print("1. Baseline mode: Fast, deterministic, only Cypher results")
    print("2. Embedding1 mode: Adds mpnet semantic search (768 dims, stat-focused)")
    print("3. Embedding2 mode: Adds MiniLM semantic search (384 dims, balanced)")
    print("\nMore context generally leads to:")
    print("  ✓ More comprehensive answers")
    print("  ✓ Higher token usage")
    print("  ✓ Better coverage of edge cases")
    
    print("\n✓ Test complete")


if __name__ == "__main__":
    test_3_modes_with_llms()
