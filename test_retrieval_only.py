"""
Test retrieval modes WITHOUT LLM generation
Compare context retrieved by each mode
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from src.retrieval.hybrid_retriever import HybridRetriever
import json


def test_retrieval_modes():
    """Test all 3 retrieval modes and compare results."""
    
    print("=" * 80)
    print("RETRIEVAL MODE COMPARISON (No LLM)")
    print("=" * 80)
    
    # Initialize retriever
    print("\nInitializing HybridRetriever...")
    retriever = HybridRetriever()
    print("✓ Retriever initialized\n")
    
    # Test query
    query = "Who were the top scorers in 2022-23?"
    season = "2022-23"
    
    print(f"QUERY: {query}")
    print(f"SEASON: {season}\n")
    
    modes = ["baseline", "baseline+embedding1", "baseline+embedding2"]
    
    results = {}
    
    for mode in modes:
        print("=" * 80)
        print(f"MODE: {mode}")
        print("=" * 80)
        
        try:
            # Retrieve context
            context = retriever.retrieve(query, season, retrieval_mode=mode)
            
            # Count players from unified_players
            num_players = len(context.get('unified_players', []))
            
            # Count baseline and semantic
            baseline_results = context.get('baseline_results', {})
            baseline_count = sum(len(v) if isinstance(v, list) else 1 for v in baseline_results.values())
            semantic_count = len(context.get('semantic_results', {}).get('players', []))
            
            print(f"\n✓ Retrieval successful")
            print(f"  Total Players: {num_players}")
            print(f"  Baseline Results: {baseline_count}")
            print(f"  Semantic Players: {semantic_count}")
            
            # Show player names
            print(f"\n  Players Retrieved:")
            for i, player in enumerate(context.get('unified_players', [])[:15], 1):
                name = player.get('player_name', player.get('player', 'Unknown'))
                pos = player.get('position', 'N/A')
                goals = player.get('total_goals', player.get('goals', 0))
                assists = player.get('total_assists', player.get('assists', 0))
                points = player.get('total_points', player.get('points', 0))
                source = player.get('source', 'unknown')
                similarity = player.get('similarity_score', 0.0)
                
                if source == 'baseline':
                    source_icon = "📊"
                elif source == 'semantic':
                    source_icon = "🔍"
                else:
                    source_icon = "🔀"
                
                print(f"    {i:2d}. {source_icon} {name:30s} ({pos:3s}) - {goals:2d}G, {assists:2d}A, {points:3d}pts [sim: {similarity:.3f}]")
            
            if num_players > 15:
                print(f"    ... and {num_players - 15} more players")
            
            # Show baseline query details
            if baseline_results:
                print(f"\n  Baseline Queries Used:")
                for key in baseline_results.keys():
                    print(f"    • {key}")
            
            # Save results
            results[mode] = {
                'num_players': num_players,
                'baseline_count': baseline_count,
                'semantic_count': semantic_count,
                'players': context.get('unified_players', [])[:10]  # Save top 10
            }
            
        except Exception as e:
            print(f"\n✗ Retrieval failed: {str(e)}")
            import traceback
            traceback.print_exc()
        
        print()
    
    # Comparison summary
    print("=" * 80)
    print("COMPARISON SUMMARY")
    print("=" * 80)
    
    print(f"\n{'Mode':<25} {'Total Players':<15} {'Baseline':<12} {'Semantic':<10}")
    print("-" * 80)
    for mode in modes:
        if mode in results:
            r = results[mode]
            print(f"{mode:<25} {r['num_players']:<15} {r['baseline_count']:<12} {r['semantic_count']:<10}")
    
    print("\nKey Observations:")
    print("  • baseline: Pure Cypher queries, no semantic search")
    print("  • baseline+embedding1: Adds semantic with 70% stat / 30% text weighting")
    print("  • baseline+embedding2: Adds semantic with 50% stat / 50% text weighting")
    
    # Close retriever
    retriever.close()
    print("\n✓ Test complete")


if __name__ == "__main__":
    test_retrieval_modes()
