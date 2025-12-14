"""
Test retrieval for "best lb" (left back) query in 2021-22 season
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from src.retrieval.hybrid_retriever import HybridRetriever


def test_best_lb_query():
    """Test best left back query for 2021-22 season across all 3 retrieval modes."""
    
    print("=" * 80)
    print("BEST LEFT BACK (LB) QUERY - RETRIEVAL TEST")
    print("=" * 80)
    
    # Initialize retriever
    print("\nInitializing Hybrid Retriever...")
    retriever = HybridRetriever(use_llm_intent=False)
    print("✓ Retriever initialized (using rule-based intent classifier)\n")
    
    # Test query
    query = "Who was the best lb in season 2021-22?"
    season = "2021-22"
    
    print(f"QUERY: {query}")
    print(f"SEASON: {season}")
    print(f"NOTE: LB = Left Back (defender position)\n")
    
    # Test all 3 modes
    modes = [
        ("baseline", "Baseline Only (Cypher)"),
        ("baseline+embedding1", "Baseline + Model 1 (all-mpnet-base-v2)"),
        ("baseline+embedding2", "Baseline + Model 2 (all-MiniLM-L6-v2)")
    ]
    
    for mode_key, mode_desc in modes:
        print("=" * 80)
        print(f"MODE: {mode_desc}")
        print("=" * 80)
        
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
            entities = result.get('entities', {})
            
            print(f"\n✓ Retrieval complete")
            print(f"  Intent: {intent.value if intent else 'N/A'} (confidence: {confidence:.2%})")
            print(f"  Total players: {len(players)}")
            
            # Show extracted entities
            print(f"\n  Extracted Entities:")
            print(f"    Positions: {entities.get('positions', [])}")
            print(f"    Player names: {entities.get('player_names', [])}")
            print(f"    Teams: {entities.get('team_names', [])}")
            print(f"    Season: {entities.get('seasons', [])}")
            
            # Count by source
            baseline_players = [p for p in players if p.get('source') == 'baseline']
            semantic_players = [p for p in players if p.get('source') == 'semantic']
            overlap_players = [p for p in players if p.get('source') == 'overlap']
            
            print(f"\n  Breakdown: {len(baseline_players)} baseline, {len(semantic_players)} semantic, {len(overlap_players)} overlap")
            
            # Show top 10 defenders
            print(f"\n  Top 10 Players:")
            for i, player in enumerate(players[:10], 1):
                name = player.get('player_name', player.get('player', 'Unknown'))
                position = player.get('position', 'N/A')
                points = player.get('total_points', 0)
                clean_sheets = player.get('total_clean_sheets', player.get('clean_sheets', 0))
                source = player.get('source', 'unknown')
                similarity = player.get('similarity_score', 0)
                
                # Source icon
                if source == 'baseline':
                    icon = "📊"
                    extra = f"{position:<5} {points}pts, {clean_sheets}CS"
                elif source == 'semantic':
                    icon = "🔍"
                    extra = f"{position:<5} {points}pts, {clean_sheets}CS (sim: {similarity:.3f})"
                else:  # overlap
                    icon = "🔀"
                    extra = f"{position:<5} {points}pts, {clean_sheets}CS (sim: {similarity:.3f})"
                
                print(f"    {i:2d}. {icon} {name:<35} {extra}")
            
            # Show unique semantic players
            if semantic_players:
                print(f"\n  Unique Semantic Players (top 5):")
                for i, player in enumerate(semantic_players[:5], 1):
                    name = player.get('player_name', player.get('player', 'Unknown'))
                    position = player.get('position', 'N/A')
                    points = player.get('total_points', 0)
                    similarity = player.get('similarity_score', 0)
                    print(f"    {i}. {name:<35} {position:<5} {points}pts (sim: {similarity:.3f})")
            
        except Exception as e:
            print(f"\n✗ Retrieval failed: {str(e)}")
            import traceback
            traceback.print_exc()
        
        print()
    
    print("=" * 80)
    print("OBSERVATIONS:")
    print("=" * 80)
    print("• LB = Left Back (specific defender position)")
    print("• Query tests entity extraction (position detection)")
    print("• Baseline may return all defenders or high-performing defenders")
    print("• Semantic models may find positionally similar players")
    print("• Common top LBs in 2021-22: Robertson, Cancelo, Chilwell, etc.")
    print("• Rule-based classifier should identify this as player search or position query")
    
    print("\n✓ Left back query test complete")


if __name__ == "__main__":
    test_best_lb_query()
