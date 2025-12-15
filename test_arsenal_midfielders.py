"""Test Arsenal midfielders retrieval."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.retrieval.hybrid_retriever import HybridRetriever
import time

def test_team_position_query(query, mode, season="2021-22"):
    """Test team + position query."""
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
        print(f"\n📋 ARSENAL MIDFIELDERS:")
        for i, player in enumerate(players, 1):
            name = player.get('player_name', player.get('player', player.get('name', 'Unknown')))
            position = player.get('position', 'N/A')
            team = player.get('team_name', player.get('team', 'N/A'))
            
            print(f"\n  {i}. {name} ({position}) - {team}")
            
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
            
            # Value if available
            if 'price' in player or 'value' in player:
                price = player.get('price', player.get('value', 0))
                print(f"     Price: £{price:.1f}m")
                
                # Value ratio
                if price > 0 and total_points > 0:
                    value_ratio = total_points / price
                    print(f"     Value Ratio: {value_ratio:.1f} pts/£m")
            
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
    print("TESTING: Arsenal Midfielders Query")
    print("=" * 80)
    
    # Test query
    query = "best arsenal midfielders"
    
    modes = [
        ("baseline", "Baseline Only (Cypher)"),
        ("baseline+embedding1", "Baseline + Model 1 (mpnet 768D)"),
        ("baseline+embedding2", "Baseline + Model 2 (MiniLM 384D)")
    ]
    
    print(f"\nQuery: '{query}'")
    print("-" * 80)
    
    for mode, mode_name in modes:
        print(f"\n{'=' * 80}")
        print(f"MODE: {mode_name}")
        print("=" * 80)
        
        results = test_team_position_query(query, mode)
        
        # Check entities extracted
        entities = results.get('entities', {})
        teams_extracted = entities.get('teams', [])
        positions_extracted = entities.get('positions', [])
        
        if teams_extracted or positions_extracted:
            print(f"\n🔎 Extracted Entities:")
            if teams_extracted:
                print(f"   Teams: {teams_extracted}")
            if positions_extracted:
                print(f"   Positions: {positions_extracted}")
    
    print("\n" + "=" * 80 + "\n")

if __name__ == "__main__":
    main()
