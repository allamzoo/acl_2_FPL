"""
Test full RAG pipeline with Qwen model for top scorers 2021-22 query
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from src.llm.generator import FPLAnswerGenerator


def test_qwen_model():
    """Test top scorers 2021-22 query with Qwen 3 32B model across all 3 retrieval modes."""
    
    print("=" * 80)
    print("QWEN 3 32B MODEL TEST - TOP SCORERS 2021-22")
    print("=" * 80)
    
    # Initialize generator
    print("\nInitializing FPL Answer Generator...")
    generator = FPLAnswerGenerator(default_llm="qwen-3-32b")
    print("✓ Generator initialized with Qwen 3 32B\n")
    
    # Test query
    query = "Who were the top scorers in 2021-22?"
    season = "2021-22"
    
    print(f"QUERY: {query}")
    print(f"SEASON: {season}\n")
    
    # Test all 3 modes
    modes = [
        ("baseline", "Baseline Only (Cypher)"),
        ("baseline+embedding1", "Baseline + Model 1 (all-mpnet-base-v2)"),
        ("baseline+embedding2", "Baseline + Model 2 (all-MiniLM-L6-v2)")
    ]
    
    results = {}
    
    for mode_key, mode_desc in modes:
        print("=" * 80)
        print(f"MODE: {mode_desc}")
        print("=" * 80)
        
        try:
            # Generate answer with Qwen model
            result = generator.answer(
                query=query,
                season=season,
                model="qwen-3-32b",
                retrieval_mode=mode_key,
                temperature=0.3,
                max_tokens=1024  # Increased for Qwen (needs space for thinking + answer)
            )
            
            # Extract info
            answer = result.get('answer', 'No answer generated')
            context_info = result.get('context', {})
            num_players = len(context_info.get('unified_players', []))
            intent = context_info.get('intent_enum')
            tokens = result.get('tokens_used', 0)
            model_used = result.get('model', 'unknown')
            
            print(f"\n✓ Answer generated")
            print(f"  Model: {model_used}")
            print(f"  Intent: {intent.value if intent else 'N/A'}")
            print(f"  Players in context: {num_players}")
            print(f"  Tokens used: {tokens}")
            
            # Show top 5 players in context
            print(f"\n  Top 5 Players in Context:")
            for i, player in enumerate(context_info.get('unified_players', [])[:5], 1):
                name = player.get('player_name', player.get('player', 'Unknown'))
                goals = player.get('total_goals', player.get('goals', 0))
                position = player.get('position', 'N/A')
                source = player.get('source', 'unknown')
                source_icon = "📊" if source == 'baseline' else "🔍" if source == 'semantic' else "🔀"
                print(f"    {i}. {source_icon} {name:<35} {position:<5} {goals}G")
            
            print(f"\n🤖 Qwen 3 32B Answer:")
            print("-" * 80)
            print(answer)
            print("-" * 80)
            
            results[mode_key] = {
                'answer': answer,
                'num_players': num_players,
                'tokens': tokens,
                'model': model_used
            }
            
        except Exception as e:
            print(f"\n✗ Generation failed: {str(e)}")
            import traceback
            traceback.print_exc()
        
        print()
    
    # Summary comparison
    print("=" * 80)
    print("COMPARISON SUMMARY - QWEN 3 32B")
    print("=" * 80)
    
    print(f"\n{'Mode':<30} {'Players':<10} {'Tokens':<10} {'Model'}")
    print("-" * 80)
    for mode_key, mode_desc in modes:
        if mode_key in results:
            r = results[mode_key]
            print(f"{mode_key:<30} {r['num_players']:<10} {r['tokens']:<10} {r['model']}")
    
    print("\n" + "=" * 80)
    print("OBSERVATIONS:")
    print("=" * 80)
    print("• Qwen 3 32B: Large multilingual model with strong reasoning capabilities")
    print("• Expected top scorers: Son & Salah (23G each), Ronaldo (18G), Kane (17G)")
    print("• Compare answer quality with Llama 4 Maverick")
    print("• Baseline mode should provide most focused factual answers")
    print("• Embedding modes add semantic context for richer responses")
    
    print("\n✓ Qwen 3 32B test complete")


if __name__ == "__main__":
    test_qwen_model()
