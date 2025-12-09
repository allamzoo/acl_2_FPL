"""
Test position filtering in embedding search
"""

import logging
from src.retrieval.embedding_retriever import EmbeddingRetriever

logging.basicConfig(level=logging.INFO, format='%(message)s')

retriever = EmbeddingRetriever(
    model_name="all-mpnet-base-v2",
    use_hybrid=True
)

print("=" * 100)
print("TEST: Position Filtering")
print("=" * 100)

# Test WITHOUT position filter
print("\n1. WITHOUT Position Filter:")
print("-" * 100)
results = retriever.semantic_search("Bargain defender from top 4 team", top_k=5, season="2021-22")
if results.get('players'):
    for i, player in enumerate(results['players'], 1):
        print(f"{i}. {player['player_name']:<35} ({player.get('position', 'N/A')}) Sim: {player.get('similarity_score', 0):.3f}")

# Test WITH position filter (auto-detected)
print("\n\n2. WITH Auto-Detected Position Filter:")
print("-" * 100)
results = retriever.semantic_search("Bargain defender from top 4 team", top_k=5, season="2021-22")
if results.get('players'):
    for i, player in enumerate(results['players'], 1):
        print(f"{i}. {player['player_name']:<35} ({player.get('position', 'N/A')}) Sim: {player.get('similarity_score', 0):.3f}")

# Test explicit filter
print("\n\n3. WITH Explicit DEF Filter:")
print("-" * 100)
results = retriever.semantic_search("Bargain top 4 team player", top_k=5, season="2021-22", position_filter="DEF")
if results.get('players'):
    for i, player in enumerate(results['players'], 1):
        print(f"{i}. {player['player_name']:<35} ({player.get('position', 'N/A')}) Sim: {player.get('similarity_score', 0):.3f}")

retriever.close()
print("\n" + "=" * 100)
