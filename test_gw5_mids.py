"""
Test retrieval for best performing midfielders in gameweek 5 season 2021-22
Tests gameweek-specific queries across all 3 retrieval modes
"""

import sys
import time
from src.retrieval.hybrid_retriever import HybridRetriever

def main():
    print("=" * 80)
    print("TESTING: Best Performing Midfielders in Gameweek 5 (2021-22)")
    print("=" * 80)
    
    # Initialize retriever
    print("\n🔧 Initializing HybridRetriever...")
    retriever = HybridRetriever()
    
    query = "Who were the best performing midfielders in gameweek 5 season 2021-22?"
    print(f"\nQuery: '{query}'")
    print("-" * 80)
    
    # Test all 3 retrieval modes
    modes = [
        ("baseline", "Baseline Only (Cypher)"),
        ("baseline+embedding1", "Baseline + Model 1 (mpnet 768D)"),
        ("baseline+embedding2", "Baseline + Model 2 (MiniLM 384D)")
    ]
    
    for mode, mode_desc in modes:
        print(f"\n{'=' * 80}")
        print(f"MODE: {mode_desc}")
        print("=" * 80)
        
        start_time = time.time()
        results = retriever.retrieve(query, season="2021-22", retrieval_mode=mode)
        elapsed = time.time() - start_time
        
        print(f"\n⏱️  Query Time: {elapsed:.2f}s")
        
        # Get intent info
        intent = results.get('intent', 'N/A')
        if hasattr(intent, 'value'):
            intent_str = intent.value
        else:
            intent_str = str(intent)
        
        print(f"📊 Intent: {intent_str}")
        print(f"🎯 Confidence: {results.get('confidence', results.get('intent_confidence', 0)):.2%}")
        
        # Get players from unified_players in context
        players = results.get('unified_players', results.get('players', []))
        print(f"👥 Total Players Retrieved: {len(players)}")
        
        if players:
            print(f"\n📋 TOP 10 MIDFIELDERS (Gameweek 5):")
            for i, player in enumerate(players[:10], 1):
                name = player.get('player_name', player.get('player', player.get('name', 'Unknown')))
                position = player.get('position', 'N/A')
                
                # Gameweek-specific points (not season total)
                gw_points = player.get('total_points', player.get('points', 0))
                
                print(f"\n  {i}. {name} ({position})")
                print(f"     GW5 Points: {gw_points}")
                
                # Show gameweek stats if available
                if 'goals_scored' in player or 'goals' in player:
                    goals = player.get('goals_scored', player.get('goals', 0))
                    assists = player.get('assists', 0)
                    minutes = player.get('minutes', 0)
                    print(f"     Goals: {goals} | Assists: {assists} | Minutes: {minutes}")
                
                # Show bonus and ICT if available
                if 'bonus' in player:
                    bonus = player.get('bonus', 0)
                    bps = player.get('bps', 0)
                    print(f"     Bonus: {bonus} | BPS: {bps}")
                
                # Show similarity for semantic results
                if 'similarity' in player:
                    print(f"     Similarity: {player['similarity']:.3f}")
        else:
            print("\n⚠️  No players retrieved")
        
        print("-" * 80)
    
    retriever.close()
    
    print("\n" + "=" * 80)
    print("✅ TEST COMPLETE")
    print("=" * 80)
    print("\nExpected behavior:")
    print("  • Intent should be: gameweek_performers")
    print("  • Should return GW5 performance (not season totals)")
    print("  • Players filtered by position: MID")
    print("  • Ranked by gameweek points")
    print("\nNote: This tests if gameweek-specific queries work correctly")
    print("      vs season-aggregated queries")

if __name__ == "__main__":
    main()
