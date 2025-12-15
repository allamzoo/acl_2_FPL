"""Test value-based query retrieval after adding value property to Neo4j."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.retrieval.hybrid_retriever import HybridRetriever
import time

def test_value_query(query, mode, season="2022-23"):
    """Test value-based query."""
    retriever = HybridRetriever()
    
    start = time.time()
    results = retriever.retrieve(
        query=query,
        retrieval_mode=mode,
        season=season
    )
    elapsed = time.time() - start
    
    print(f"\n⏱️  Query Time: {elapsed:.2f}s")
    
    # Get intent info
    intent = results.get('intent', 'N/A')
    if hasattr(intent, 'value'):
        intent_str = intent.value
    else:
        intent_str = str(intent)
    
    print(f"📊 Intent: {intent_str}")
    print(f"🎯 Confidence: {results.get('confidence', results.get('intent_confidence', 0)):.2%}")
    
    # Get players
    players = results.get('unified_players', results.get('players', []))
    print(f"👥 Total Players Retrieved: {len(players)}")
    
    if players:
        print(f"\n📋 BEST VALUE PLAYERS:")
        for i, player in enumerate(players[:10], 1):
            name = player.get('player_name', player.get('player', player.get('name', 'Unknown')))
            position = player.get('position', 'N/A')
            
            print(f"\n  {i}. {name} ({position})")
            
            # Value-specific stats
            price = player.get('price', player.get('value', 0))
            total_points = player.get('total_points', 0)
            value_score = player.get('value_score', player.get('points_per_million', 0))
            
            print(f"     💰 Price: £{price}m")
            print(f"     📊 Total Points: {total_points}")
            print(f"     ⭐ Value Score: {value_score:.1f}")
            
            # Additional stats
            goals = player.get('goals', player.get('total_goals', player.get('goals_scored', 0)))
            assists = player.get('assists', player.get('total_assists', 0))
            minutes = player.get('minutes', player.get('total_minutes', 0))
            
            if goals or assists:
                print(f"     Goals: {goals} | Assists: {assists} | Minutes: {minutes}")
            
            # Show similarity for semantic results
            if 'similarity_score' in player and player['similarity_score'] > 0:
                print(f"     🔍 Similarity: {player['similarity_score']:.3f}")
    else:
        print("⚠️  No players retrieved")
    
    print("-" * 80)
    
    retriever.close()
    return results

def main():
    print("=" * 80)
    print("TESTING: Value-Based Query (After Adding value Property to Neo4j)")
    print("=" * 80)
    
    # Test different value queries
    queries = [
        "Best value midfielders under 8.0",
        "Cheap defenders with good points",
        "Best budget forwards",
        "Players with best points per price ratio",
    ]
    
    modes = [
        ("baseline", "Baseline Only (Cypher)"),
        ("baseline+embedding1", "Baseline + Model 1 (mpnet 768D)"),
    ]
    
    for query in queries:
        print(f"\nQuery: '{query}'")
        print("-" * 80)
        
        for mode, mode_name in modes:
            print(f"\n{'=' * 80}")
            print(f"MODE: {mode_name}")
            print("=" * 80)
            
            results = test_value_query(query, mode)
        
        print("\n" + "=" * 80 + "\n")

if __name__ == "__main__":
    main()
