"""
Test retrieval with Gameweek Top Performers query
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from src.retrieval.hybrid_retriever import HybridRetriever


def test_gameweek_query():
    """Test gameweek top performers query with all retrieval modes."""
    
    print("=" * 80)
    print("GAMEWEEK TOP PERFORMERS QUERY TEST")
    print("=" * 80)
    
    # Initialize retriever
    print("\nInitializing HybridRetriever...")
    retriever = HybridRetriever()
    print("✓ Retriever initialized\n")
    
    # Test query
    query = "Who were the top performers in gameweek 1 of 2022-23?"
    season = "2022-23"
    
    print(f"QUERY: {query}")
    print(f"SEASON: {season}\n")
    
    modes = ["baseline", "baseline+embedding1", "baseline+embedding2"]
    
    for mode in modes:
        print("=" * 80)
        print(f"MODE: {mode}")
        print("=" * 80)
        
        try:
            # Retrieve context
            context = retriever.retrieve(query, season, retrieval_mode=mode)
            
            # Extract info
            intent = context.get('intent')
            intent_enum = context.get('intent_enum')
            confidence = context.get('intent_confidence', 0.0)
            
            baseline_results = context.get('baseline_results', {})
            baseline_count = sum(len(v) if isinstance(v, list) else 1 for v in baseline_results.values())
            semantic_count = len(context.get('semantic_results', {}).get('players', []))
            num_players = len(context.get('unified_players', []))
            
            print(f"\n✓ Retrieval successful")
            print(f"  Intent: {intent_enum.value if intent_enum else 'N/A'} → {intent} (confidence: {confidence:.2f})")
            print(f"  Total Players: {num_players}")
            print(f"  Baseline Results: {baseline_count}")
            print(f"  Semantic Players: {semantic_count}")
            
            # Show baseline queries triggered
            if baseline_results:
                print(f"\n  Baseline Queries Triggered:")
                for key in baseline_results.keys():
                    print(f"    • {key}")
            
            # Show players
            print(f"\n  Top 10 Players Retrieved:")
            for i, player in enumerate(context.get('unified_players', [])[:10], 1):
                name = player.get('player_name', player.get('player', 'Unknown'))
                pos = player.get('position', 'N/A')
                goals = player.get('total_goals', player.get('goals', player.get('goals_scored', 0)))
                assists = player.get('total_assists', player.get('assists', 0))
                points = player.get('total_points', player.get('points', 0))
                source = player.get('source', 'unknown')
                similarity = player.get('similarity_score', 0.0)
                
                # Get gameweek-specific info if available
                gw = player.get('gameweek', 'N/A')
                minutes = player.get('minutes', 0)
                
                if source == 'baseline':
                    source_icon = "📊"
                elif source == 'semantic':
                    source_icon = "🔍"
                else:
                    source_icon = "🔀"
                
                print(f"    {i:2d}. {source_icon} {name:30s} ({pos:3s}) - GW{gw} | {points:2d}pts | {goals}G {assists}A | {minutes}min [sim: {similarity:.3f}]")
            
            if num_players > 10:
                print(f"    ... and {num_players - 10} more players")
            
        except Exception as e:
            print(f"\n✗ Retrieval failed: {str(e)}")
            import traceback
            traceback.print_exc()
        
        print()
    
    # Close retriever
    retriever.close()
    print("=" * 80)
    print("✓ Test complete")
    print("=" * 80)


if __name__ == "__main__":
    test_gameweek_query()
