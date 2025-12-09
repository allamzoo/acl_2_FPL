"""
Test script for Baseline Retriever
Tests all 10 Cypher queries to ensure they work correctly.
"""

from src.retrieval.baseline_retriever import BaselineRetriever
import json


def test_baseline_retriever():
    """Test all baseline retrieval methods."""
    
    print("=" * 80)
    print("BASELINE RETRIEVER TEST")
    print("=" * 80)
    
    with BaselineRetriever() as retriever:
        
        # Test 1: Find Player by Name
        print("\n1. FIND PLAYER BY NAME (Salah)")
        print("-" * 80)
        results = retriever.find_player_by_name("Salah")
        print(json.dumps(results, indent=2))
        
        # Test 2: Top Scorers by Position
        print("\n2. TOP SCORERS - FORWARDS (2021-22)")
        print("-" * 80)
        results = retriever.get_top_scorers("FWD", "2021-22", limit=5)
        print(json.dumps(results, indent=2))
        
        # Test 3: Player Season Statistics
        print("\n3. PLAYER SEASON STATS (Salah, 2021-22)")
        print("-" * 80)
        results = retriever.get_player_season_stats("Salah", "2021-22")
        print(json.dumps(results, indent=2, default=str))
        
        # Test 4: Players by Team
        print("\n4. TEAM PLAYERS (Liverpool, 2021-22)")
        print("-" * 80)
        results = retriever.get_team_players("Liverpool", "2021-22")
        print(json.dumps(results[:5], indent=2))  # Show top 5
        print(f"Total players: {len(results)}")
        
        # Test 5: Gameweek Top Performers
        print("\n5. GAMEWEEK TOP PERFORMERS (GW 1, 2021-22)")
        print("-" * 80)
        results = retriever.get_gameweek_top_performers(1, "2021-22", limit=5)
        print(json.dumps(results, indent=2))
        
        # Test 6: Compare Players
        print("\n6. COMPARE PLAYERS (Salah vs Kane, 2021-22)")
        print("-" * 80)
        results = retriever.compare_players("Salah", "Kane", "2021-22")
        print(json.dumps(results, indent=2, default=str))
        
        # Test 7: High Performers by Threshold
        print("\n7. HIGH PERFORMERS (>= 15 goals, 2021-22)")
        print("-" * 80)
        results = retriever.get_high_performers(15, "2021-22")
        print(json.dumps(results, indent=2))
        
        # Test 8: Top Assisters
        print("\n8. TOP ASSISTERS - MIDFIELDERS (2021-22)")
        print("-" * 80)
        results = retriever.get_top_assisters("MID", "2021-22", limit=5)
        print(json.dumps(results, indent=2))
        
        # Test 9: Player Form
        print("\n9. PLAYER FORM (Salah, last 5 GW, 2021-22)")
        print("-" * 80)
        results = retriever.get_player_form("Salah", "2021-22", last_n_gw=5)
        print(json.dumps(results, indent=2))
        
        # Test 10: Best ICT Players
        print("\n10. BEST ICT INDEX - MIDFIELDERS (2021-22)")
        print("-" * 80)
        results = retriever.get_top_ict_players("MID", "2021-22", limit=5)
        print(json.dumps(results, indent=2))
        
        # Test formatting for LLM
        print("\n" + "=" * 80)
        print("FORMATTED FOR LLM CONTEXT")
        print("=" * 80)
        results = retriever.get_top_scorers("FWD", "2021-22", limit=3)
        formatted = retriever.format_results_for_llm(results, "Top Scorers")
        print(formatted)
    
    print("\n" + "=" * 80)
    print("✓ ALL TESTS COMPLETED")
    print("=" * 80)


if __name__ == "__main__":
    test_baseline_retriever()
