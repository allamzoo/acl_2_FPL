"""
Test semantic search with queries that should return top FPL performers.
"""

import logging
from src.retrieval.embedding_retriever import EmbeddingRetriever

logging.basicConfig(level=logging.INFO, format='%(message)s')

print("=" * 100)
print("SEMANTIC SEARCH - TOP PERFORMERS TEST")
print("=" * 100)

# Queries designed to find elite players
test_queries = [
    "Elite premium midfielder who scores many goals and assists, top FPL points",
    "World class striker prolific goal scorer high points",
    "Best defensive midfielder playmaker creative assists",
    "Top attacking full back defender with assists and bonus",
    "Premium forward consistent scorer high ICT elite performer"
]

with EmbeddingRetriever() as retriever:
    for query in test_queries:
        print(f"\n{'=' * 100}")
        print(f"Query: {query}")
        print('=' * 100)
        
        results = retriever.semantic_search(query, top_k=10, season="2021-22")
        
        if results['players']:
            for i, player in enumerate(results['players'], 1):
                print(f"{i:2d}. {player['player_name']:<30} ({player['position']}) "
                      f"Sim: {player['similarity_score']:.3f} | "
                      f"G:{player['total_goals']:2d} A:{player['total_assists']:2d} "
                      f"Pts:{player['total_points']:3d} ICT:{player['avg_ict_index']:.1f}")

print("\n" + "=" * 100)
print("✓ Test completed!")
print("=" * 100)
