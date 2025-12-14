"""
Test retrieval for top scorers query across two different seasons
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from src.retrieval.hybrid_retriever import HybridRetriever


def test_scorers_multiple_seasons():
    """Test top scorers query for 2022-23 and 2021-22 seasons."""
    
    print("=" * 80)
    print("TOP SCORERS QUERY - TWO SEASONS COMPARISON")
    print("=" * 80)
    
    # Initialize retriever
    print("\nInitializing Hybrid Retriever...")
    retriever = HybridRetriever(use_llm_intent=False)
    print("✓ Retriever initialized (using rule-based intent classifier)\n")
    
    # Test queries for both seasons
    test_cases = [
        {
            'query': 'Who were the top scorers in 2022-23?',
            'season': '2022-23'
        },
        {
            'query': 'Who were the top scorers in 2021-22?',
            'season': '2021-22'
        }
    ]
    
    # Test all 3 modes for each season
    modes = [
        ("baseline", "Baseline Only (Cypher)"),
        ("baseline+embedding1", "Baseline + Model 1 (all-mpnet-base-v2)"),
        ("baseline+embedding2", "Baseline + Model 2 (all-MiniLM-L6-v2)")
    ]
    
    for test_case in test_cases:
        query = test_case['query']
        season = test_case['season']
        
        print("=" * 80)
        print(f"SEASON: {season}")
        print(f"QUERY: {query}")
        print("=" * 80)
        
        for mode_key, mode_desc in modes:
            print(f"\n{'─' * 80}")
            print(f"MODE: {mode_desc}")
            print(f"{'─' * 80}")
            
            try:
                # Retrieve context
                result = retriever.retrieve(
                    query=query,
                    season=season,
                    retrieval_mode=mode_key
                )
                
                # Extract info
                players = result.get('unified_players', [])
                intent = result.get('intent_enum')
                confidence = result.get('confidence', 0)
                
                print(f"\n✓ Retrieval complete")
                print(f"  Intent: {intent.value if intent else 'N/A'} (confidence: {confidence:.2f})")
                print(f"  Total players: {len(players)}")
                
                # Count by source
                baseline_players = [p for p in players if p.get('source') == 'baseline']
                semantic_players = [p for p in players if p.get('source') == 'semantic']
                overlap_players = [p for p in players if p.get('source') == 'overlap']
                
                print(f"  Breakdown: {len(baseline_players)} baseline, {len(semantic_players)} semantic, {len(overlap_players)} overlap")
                
                # Show top 10 scorers
                print(f"\n  Top 10 Scorers:")
                for i, player in enumerate(players[:10], 1):
                    name = player.get('player_name', player.get('player', 'Unknown'))
                    # Try multiple possible field names for goals
                    goals = player.get('total_goals', player.get('goals_scored', player.get('goals', 0)))
                    source = player.get('source', 'unknown')
                    similarity = player.get('similarity_score', 0)
                    
                    # Debug: print first player's keys to see available fields
                    if i == 1:
                        print(f"  [DEBUG] Available fields: {list(player.keys())[:10]}")
                    
                    # Source icon
                    if source == 'baseline':
                        icon = "📊"
                        extra = f"{goals}G"
                    elif source == 'semantic':
                        icon = "🔍"
                        extra = f"{goals}G (sim: {similarity:.3f})"
                    else:  # overlap
                        icon = "🔀"
                        extra = f"{goals}G (sim: {similarity:.3f})"
                    
                    print(f"    {i:2d}. {icon} {name:<30} {extra}")
                
                # Show unique semantic players (not in baseline)
                if semantic_players:
                    print(f"\n  Unique Semantic Players (top 5):")
                    for i, player in enumerate(semantic_players[:5], 1):
                        name = player.get('player_name', player.get('player', 'Unknown'))
                        goals = player.get('total_goals', player.get('goals_scored', player.get('goals', 0)))
                        similarity = player.get('similarity_score', 0)
                        print(f"    {i}. {name:<30} {goals}G (similarity: {similarity:.3f})")
                
            except Exception as e:
                print(f"\n✗ Retrieval failed: {str(e)}")
                import traceback
                traceback.print_exc()
        
        print("\n")
    
    print("=" * 80)
    print("OBSERVATIONS:")
    print("=" * 80)
    print("• Baseline mode returns deterministic top scorers from Cypher queries")
    print("• Embedding Model 1 (mpnet): 768D, stat-focused (70/30 weighting)")
    print("• Embedding Model 2 (MiniLM): 384D, balanced (50/50 weighting)")
    print("• Different seasons should return different top scorers")
    print("• Semantic models may find additional relevant players based on query context")
    
    print("\n✓ Two-season retrieval test complete")


if __name__ == "__main__":
    test_scorers_multiple_seasons()
