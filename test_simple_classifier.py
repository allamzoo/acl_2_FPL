"""
Test retrieval with simple intent classifier (no LLM, no network required)
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from src.retrieval.hybrid_retriever import HybridRetriever


def test_simple_classifier():
    """Test with simple rule-based classifier (no LLM)."""
    
    print("=" * 80)
    print("TESTING SIMPLE INTENT CLASSIFIER + ENTITY EXTRACTOR")
    print("=" * 80)
    
    # Initialize with simple classifier (no LLM)
    print("\nInitializing HybridRetriever with simple classifier...")
    retriever = HybridRetriever(use_llm_intent=False)
    print("✓ Retriever initialized\n")
    
    queries = [
        ("Who were the top scorers in 2022-23?", "2022-23"),
        ("Compare Salah and Haaland in 2022-23", "2022-23"),
        ("Show me Arsenal players from 2022-23", "2022-23"),
    ]
    
    for query, season in queries:
        print("=" * 80)
        print(f"QUERY: {query}")
        print(f"SEASON: {season}")
        print("=" * 80)
        
        try:
            context = retriever.retrieve(query, season, retrieval_mode="baseline")
            
            intent = context.get('intent', 'unknown')
            players = context.get('unified_players', [])
            baseline_results = context.get('baseline_results', {})
            
            print(f"\n✓ Intent: {intent}")
            print(f"✓ Baseline queries: {list(baseline_results.keys())}")
            print(f"✓ Total players: {len(players)}")
            
            if players:
                print(f"\nTop 5 players:")
                for i, player in enumerate(players[:5], 1):
                    name = player.get('player_name', player.get('player', 'Unknown'))
                    pos = player.get('position', 'N/A')
                    goals = player.get('total_goals', player.get('goals', 0))
                    print(f"  {i}. {name} ({pos}) - {goals} goals")
            else:
                print("\n⚠️  No players retrieved")
                print(f"   Baseline results: {baseline_results}")
            
        except Exception as e:
            print(f"\n✗ Error: {str(e)}")
            import traceback
            traceback.print_exc()
        
        print()
    
    retriever.close()
    print("\n✓ Test complete")


if __name__ == "__main__":
    test_simple_classifier()
