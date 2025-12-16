#!/usr/bin/env python3
"""Test squad builder with updated logic."""

from src.retrieval.baseline_retriever import BaselineRetriever

def test_squad_builder():
    """Test the build_squad_under_budget function."""
    retriever = BaselineRetriever()
    
    try:
        # Build squad
        result = retriever.build_squad_under_budget(
            season="2022-23",
            budget=100.0,
            min_points=30,
            min_games=10
        )
        
        print(f"\n{'='*60}")
        print(f"SQUAD BUILDER TEST - 15 Players Under £100m")
        print(f"{'='*60}\n")
        
        print(f"Squad Size: {result['squad_size']}/15")
        print(f"Total Cost: £{result['total_cost']}m")
        print(f"Remaining Budget: £{result['remaining_budget']}m")
        print(f"Total Points: {result['total_points']}")
        print(f"\nFormation: {result['formation']}")
        
        print(f"\n{'='*60}")
        print("SQUAD LIST:")
        print(f"{'='*60}\n")
        
        # Group by position
        for pos in ['GK', 'DEF', 'MID', 'FWD']:
            players = [p for p in result['squad'] if p['position'] == pos]
            print(f"\n{pos} ({len(players)} players):")
            print("-" * 60)
            for i, player in enumerate(players, 1):
                print(f"{i}. {player['player_name']:30s} ({player['team']:15s}) - "
                      f"£{player['price']}m, {player['total_points']} pts")
        
        print(f"\n{'='*60}\n")
        
        # Check if exactly 15 players
        if result['squad_size'] == 15:
            print("✅ SUCCESS: Squad contains exactly 15 players!")
        else:
            print(f"❌ WARNING: Squad contains {result['squad_size']} players instead of 15")
        
        # Check if under budget
        if result['total_cost'] <= 100.0:
            print(f"✅ SUCCESS: Total cost £{result['total_cost']}m is under £100m budget!")
        else:
            print(f"❌ ERROR: Total cost £{result['total_cost']}m exceeds £100m budget!")
            
    finally:
        retriever.close()

if __name__ == "__main__":
    test_squad_builder()
