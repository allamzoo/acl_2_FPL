"""
Test retrieval for top scorer queries in different seasons
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from src.retrieval.hybrid_retriever import HybridRetriever
import json


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80)


def print_retrieval_results(query: str, season: str, retriever: HybridRetriever):
    """Test retrieval for a specific query and season."""
    print_section(f"Query: {query}")
    print(f"Season: {season}")
    
    # Test all three retrieval modes
    modes = ["baseline", "baseline+embedding1", "baseline+embedding2"]
    
    for mode in modes:
        print(f"\n{'─' * 80}")
        print(f"🔍 RETRIEVAL MODE: {mode}")
        print(f"{'─' * 80}")
        
        try:
            # Retrieve context
            context = retriever.retrieve(query, season, retrieval_mode=mode)
            
            # Display intent classification
            print(f"\n📊 Intent Classification:")
            print(f"   Intent: {context['intent']} ({context.get('intent_enum', 'N/A')})")
            print(f"   Confidence: {context.get('intent_confidence', 0):.2f}")
            
            # Display baseline results
            print(f"\n📋 Baseline Results:")
            baseline_results = context.get('baseline_results', {})
            if baseline_results:
                for key, value in baseline_results.items():
                    print(f"   {key}:")
                    if isinstance(value, list):
                        print(f"      Count: {len(value)}")
                        for i, item in enumerate(value[:5], 1):  # Show top 5
                            player_name = item.get('player') or item.get('player_name', 'Unknown')
                            goals = item.get('total_goals') or item.get('goals', 0)
                            assists = item.get('total_assists') or item.get('assists', 0)
                            points = item.get('total_points') or item.get('points', 0)
                            print(f"      {i}. {player_name}: {goals}G, {assists}A, {points} pts")
                    else:
                        print(f"      {value}")
            else:
                print("   ❌ No baseline results")
            
            # Display semantic results
            print(f"\n🔎 Semantic Search Results:")
            semantic_results = context.get('semantic_results', {})
            if semantic_results and semantic_results.get('players'):
                players = semantic_results['players']
                print(f"   Count: {len(players)}")
                for i, player in enumerate(players[:5], 1):  # Show top 5
                    sim_score = player.get('similarity_score', 0)
                    player_name = player.get('player_name', 'Unknown')
                    goals = player.get('total_goals', 0)
                    assists = player.get('total_assists', 0)
                    points = player.get('total_points', 0)
                    print(f"   {i}. {player_name} (sim: {sim_score:.3f}): {goals}G, {assists}A, {points} pts")
            else:
                print("   ❌ No semantic results")
            
            # Display unified results
            print(f"\n🎯 Unified Results (Merged):")
            unified = context.get('unified_players', [])
            if unified:
                print(f"   Total players: {len(unified)}")
                for i, player in enumerate(unified[:10], 1):  # Show top 10
                    player_name = player.get('player_name', 'Unknown')
                    source = player.get('source', 'unknown')
                    sim_score = player.get('similarity_score', 0)
                    goals = player.get('total_goals') or player.get('goals', 0)
                    assists = player.get('total_assists') or player.get('assists', 0)
                    points = player.get('total_points') or player.get('points', 0)
                    
                    sim_str = f", sim: {sim_score:.3f}" if sim_score > 0 else ""
                    print(f"   {i}. {player_name} [{source}]{sim_str}: {goals}G, {assists}A, {points} pts")
            else:
                print("   ❌ No unified results")
            
        except Exception as e:
            print(f"❌ Error during retrieval: {e}")
            import traceback
            traceback.print_exc()


def main():
    print_section("TOP SCORER RETRIEVAL TEST")
    print("Testing retrieval for top scorer queries across different seasons")
    
    # Initialize retriever
    print("\n🔧 Initializing HybridRetriever...")
    retriever = HybridRetriever()
    print("✓ Retriever initialized")
    
    # Test queries
    test_cases = [
        ("top scorer in season 2022/2023", "2022-23"),
        ("top scorers 2021/2022", "2021-22"),
    ]
    
    for query, season in test_cases:
        print_retrieval_results(query, season, retriever)
    
    # Close retriever
    retriever.close()
    print_section("TEST COMPLETE")


if __name__ == "__main__":
    main()
