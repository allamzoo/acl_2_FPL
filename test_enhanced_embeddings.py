"""
Test enhanced embeddings with better semantic matching.
"""

import logging
from src.retrieval.embedding_retriever import EmbeddingRetriever

logging.basicConfig(level=logging.INFO, format='%(message)s')

print("=" * 100)
print("ENHANCED EMBEDDINGS - SIMILARITY TEST")
print("=" * 100)

# Use the enhanced property
retriever = EmbeddingRetriever(
    model_name="all-mpnet-base-v2",
    embedding_property="feature_embedding_enhanced"
)

test_queries = [
    "Elite world class striker prolific goal scorer",
    "Premium midfielder creative playmaker lots of assists", 
    "Top FPL points scorer highest returns",
    "Attacking fullback defender with assists",
    "Consistent performer bonus points nailed on"
]

try:
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
finally:
    retriever.close()

print("\n" + "=" * 100)
print("✓ Test completed!")
print("=" * 100)
