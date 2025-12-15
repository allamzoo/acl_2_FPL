"""Test player comparison retrieval."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.retrieval.hybrid_retriever import HybridRetriever
import time

def test_comparison(query, mode, season="2021-22"):
    """Test player comparison query."""
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
    
    # Get players from unified_players
    players = results.get('unified_players', results.get('players', []))
    print(f"👥 Total Players Retrieved: {len(players)}")
    
    if players:
        print(f"\n📋 PLAYER COMPARISON:")
        for i, player in enumerate(players, 1):
            name = player.get('player_name', player.get('player', player.get('name', 'Unknown')))
            position = player.get('position', 'N/A')
            
            print(f"\n  {i}. {name} ({position})")
            
            # Season stats
            total_points = player.get('total_points', 0)
            goals = player.get('goals', player.get('total_goals', player.get('goals_scored', 0)))
            assists = player.get('assists', player.get('total_assists', 0))
            games = player.get('games_played', 0)
            minutes = player.get('minutes', player.get('total_minutes', 0))
            
            print(f"     Total Points: {total_points}")
            print(f"     Goals: {goals} | Assists: {assists}")
            print(f"     Games: {games} | Minutes: {minutes}")
            
            # Additional stats if available
            if 'avg_ict' in player or 'avg_ict_index' in player:
                ict = player.get('avg_ict', player.get('avg_ict_index', 0))
                print(f"     Avg ICT Index: {ict:.1f}")
            
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
    print("TESTING: Player Comparison Query")
    print("=" * 80)
    
    # Test different comparison queries
    queries = [
        "Compare Mohamed Salah and Harry Kane in 2021-22",
        "Salah vs Kane 2021-22",
        "Compare Haaland and Kane performance",
    ]
    
    modes = [
        ("baseline", "Baseline Only (Cypher)"),
        ("baseline+embedding1", "Baseline + Model 1 (mpnet 768D)"),
        ("baseline+embedding2", "Baseline + Model 2 (MiniLM 384D)")
    ]
    
    for query in queries:
        print(f"\nQuery: '{query}'")
        print("-" * 80)
        
        for mode, mode_name in modes:
            print(f"\n{'=' * 80}")
            print(f"MODE: {mode_name}")
            print("=" * 80)
            
            results = test_comparison(query, mode)
            
            # Check entities extracted
            entities = results.get('entities', {})
            players_extracted = entities.get('players', [])
            if players_extracted:
                print(f"\n🔎 Extracted Players: {players_extracted}")
        
        print("\n" + "=" * 80 + "\n")

if __name__ == "__main__":
    main()
