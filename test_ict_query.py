"""
Test retrieval for ICT Index query across all 3 modes
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from src.retrieval.hybrid_retriever import HybridRetriever


def test_ict_index_query():
    """Test ICT Index query across 3 retrieval modes."""
    
    print("=" * 80)
    print("ICT INDEX QUERY - RETRIEVAL TEST")
    print("=" * 80)
    
    # Initialize retriever
    print("\nInitializing Hybrid Retriever...")
    retriever = HybridRetriever(use_llm_intent=False)
    print("✓ Retriever initialized (using rule-based intent classifier)\n")
    
    # Test query
    query = "Who are the best players by ICT index in 2022-23?"
    season = "2022-23"
    
    print(f"QUERY: {query}")
    print(f"SEASON: {season}\n")
    
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
            
            print(f"\n✓ Retrieval complete")
            print(f"  Intent: {intent.value if intent else 'N/A'} (confidence: {confidence:.2f})")
            print(f"  Total players: {len(players)}")
            
            # Count by source
            baseline_players = [p for p in players if p.get('source') == 'baseline']
            semantic_players = [p for p in players if p.get('source') == 'semantic']
            overlap_players = [p for p in players if p.get('source') == 'overlap']
            
            print(f"  Breakdown: {len(baseline_players)} baseline, {len(semantic_players)} semantic, {len(overlap_players)} overlap")
            
            # Debug: check available fields in first player
            if players:
                print(f"\n  [DEBUG] Available fields: {list(players[0].keys())[:15]}")
            
            # Show top 10 players by ICT index
            print(f"\n  Top 10 Players by ICT Index:")
            for i, player in enumerate(players[:10], 1):
                name = player.get('player_name', player.get('player', 'Unknown'))
                
                # Try multiple field names for ICT metrics
                avg_ict = player.get('avg_ict_index', player.get('avg_ict', 0))
                influence = player.get('avg_influence', 0)
                creativity = player.get('avg_creativity', 0)
                threat = player.get('avg_threat', 0)
                total_points = player.get('total_points', 0)
                
                source = player.get('source', 'unknown')
                similarity = player.get('similarity_score', 0)
                
                # Source icon
                if source == 'baseline':
                    icon = "📊"
                    extra = f"ICT:{avg_ict:.1f}"
                elif source == 'semantic':
                    icon = "🔍"
                    extra = f"ICT:{avg_ict:.1f} (sim:{similarity:.3f})"
                else:  # overlap
                    icon = "🔀"
                    extra = f"ICT:{avg_ict:.1f} (sim:{similarity:.3f})"
                
                print(f"    {i:2d}. {icon} {name:<30} {extra}")
                
                # Show detailed breakdown for top 3
                if i <= 3 and avg_ict > 0:
                    print(f"        └─ Influence:{influence:.1f}, Creativity:{creativity:.1f}, Threat:{threat:.1f}, Points:{total_points}")
            
            # Show unique semantic players
            if semantic_players:
                print(f"\n  Unique Semantic Players (top 5):")
                for i, player in enumerate(semantic_players[:5], 1):
                    name = player.get('player_name', player.get('player', 'Unknown'))
                    avg_ict = player.get('avg_ict_index', player.get('avg_ict', 0))
                    similarity = player.get('similarity_score', 0)
                    total_points = player.get('total_points', 0)
                    print(f"    {i}. {name:<30} ICT:{avg_ict:.1f}, Pts:{total_points} (sim:{similarity:.3f})")
            
        except Exception as e:
            print(f"\n✗ Retrieval failed: {str(e)}")
            import traceback
            traceback.print_exc()
        
        print()
    
    print("=" * 80)
    print("OBSERVATIONS:")
    print("=" * 80)
    print("• ICT Index = Influence + Creativity + Threat (FPL's advanced metric)")
    print("• High ICT players have strong overall impact on games")
    print("• Baseline returns top ICT performers from Cypher query")
    print("• Semantic models may add stylistically similar players")
    print("• Model 1 (mpnet): Stat-focused, may find similar high-impact players")
    print("• Model 2 (MiniLM): Balanced, may discover different player types")
    
    print("\n✓ ICT Index retrieval test complete")


if __name__ == "__main__":
    test_ict_index_query()
