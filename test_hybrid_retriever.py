"""
Test Hybrid Retriever - Combines Cypher baseline + embedding semantic search
"""

import logging
from src.retrieval.hybrid_retriever import HybridRetriever

logging.basicConfig(level=logging.INFO, format='%(message)s')

def main():
    print("=" * 100)
    print("HYBRID RETRIEVER TEST")
    print("Combining Baseline Cypher Queries + Semantic Embeddings")
    print("=" * 100)
    
    retriever = HybridRetriever(
        embedding_model="all-mpnet-base-v2",
        use_hybrid_embeddings=True,
        top_k_semantic=5
    )
    
    test_queries = [
        # Diverse FPL manager queries
        "Cheap defenders under 5 million with good clean sheet record",
        "High scoring strikers with at least 15 goals",
        "Creative midfielders with most assists",
        "Consistent players with good form last 5 games",
        "Differential captain options with high ceiling",
        "Budget enablers under 4.5 million",
        "Premium forwards worth the money",
        "Set piece specialists for corners and free kicks"
    ]
    
    try:
        for query in test_queries:
            print(f"\n{'=' * 100}")
            print(f"QUERY: '{query}'")
            print('=' * 100)
            
            # Retrieve unified context
            context = retriever.retrieve(query, season="2022-23")
            
            # Print BASELINE results
            print("\n" + "=" * 100)
            print("BASELINE RESULTS")
            print("=" * 100)
            if context['baseline_results']:
                for key, value in context['baseline_results'].items():
                    print(f"\n{key.upper()}:")
                    if isinstance(value, list):
                        for i, item in enumerate(value[:10], 1):
                            name = item.get('player') or item.get('player_name') or item.get('name', 'Unknown')
                            goals = item.get('total_goals') or item.get('goals', 0)
                            assists = item.get('total_assists') or item.get('assists', 0)
                            points = item.get('total_points', 0)
                            print(f"  {i}. {name:<35} {goals}G, {assists}A, {points} pts")
            else:
                print("No baseline results")
            
            # Print SEMANTIC results
            print("\n" + "=" * 100)
            print("SEMANTIC EMBEDDING RESULTS")
            print("=" * 100)
            if context['semantic_results'].get('players'):
                for i, player in enumerate(context['semantic_results']['players'][:10], 1):
                    print(f"{i}. {player['player_name']:<35} ({player.get('position', 'N/A')}) "
                          f"Sim: {player.get('similarity_score', 0):.3f} | "
                          f"{player.get('total_goals', 0)}G, {player.get('total_assists', 0)}A, "
                          f"{player.get('total_points', 0)} pts")
            else:
                print("No semantic results")
            
            # Print MERGED results
            print("\n" + "=" * 100)
            print("MERGED UNIFIED RESULTS")
            print("=" * 100)
            if context['unified_players']:
                for i, player in enumerate(context['unified_players'][:15], 1):
                    source = player.get('source', 'unknown')
                    sim = player.get('similarity_score', 0)
                    goals = player.get('total_goals') or player.get('goals', 0)
                    assists = player.get('total_assists') or player.get('assists', 0)
                    points = player.get('total_points', 0)
                    
                    if sim > 0:
                        print(f"{i:2d}. {player['player_name']:<35} [{source:8s}] "
                              f"Sim: {sim:.3f} | {goals}G, {assists}A, {points} pts")
                    else:
                        print(f"{i:2d}. {player['player_name']:<35} [{source:8s}] "
                              f"           | {goals}G, {assists}A, {points} pts")
            else:
                print("No unified results")
            
            print()
            
    finally:
        retriever.close()
    
    print("=" * 100)
    print("✓ HYBRID RETRIEVAL TESTS COMPLETED")
    print("=" * 100)


if __name__ == "__main__":
    main()
