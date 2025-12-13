"""
Test to show baseline, embeddings, and merged results separately
"""
import sys
sys.path.append('C:\\Users\\Marwan Allam\\fpl-graph-rag')

from src.retrieval.baseline_retriever import BaselineRetriever
from src.retrieval.embedding_retriever import EmbeddingRetriever
from src.retrieval.hybrid_retriever import HybridRetriever
import json

print("=" * 80)
print("RETRIEVAL BREAKDOWN TEST")
print("=" * 80)

query = "Who were the top scorers in the 2022-23 season?"
print(f"\nQuery: {query}")
print("=" * 80)

# Test 1: Baseline Retriever Alone
print("\n1️⃣  BASELINE RETRIEVER (Factual Cypher Queries)")
print("-" * 80)

baseline = BaselineRetriever()
baseline_results = baseline.get_top_scorers(position="FWD", season="2022-23", limit=10)

print(f"Retrieved: {len(baseline_results)} players\n")
for i, player in enumerate(baseline_results[:5], 1):
    print(f"{i}. {player.get('player', 'Unknown'):25s} - "
          f"{player.get('total_goals', 0):2d} goals, "
          f"{player.get('total_assists', 0):2d} assists, "
          f"{player.get('total_points', 0):3d} pts")

print(f"\nBaseline Source: Deterministic Cypher query on graph structure")
baseline.close()

# Test 2: Embedding Retriever Alone
print("\n" + "=" * 80)
print("2️⃣  EMBEDDING RETRIEVER (Semantic Similarity Search)")
print("-" * 80)

embedding = EmbeddingRetriever()
semantic_results = embedding.find_similar_players(
    query=query, 
    top_k=10,
    season="2022-23",
    min_minutes=500
)

print(f"Retrieved: {len(semantic_results)} players\n")
for i, player in enumerate(semantic_results[:5], 1):
    print(f"{i}. {player.get('player_name', 'Unknown'):25s} - "
          f"Similarity: {player.get('similarity_score', 0):.4f}")

# Get details for semantic results
if semantic_results:
    player_names = [p['player_name'] for p in semantic_results[:5]]
    semantic_details = embedding.get_player_details(player_names, season="2022-23")
    
    print(f"\nWith Stats:")
    for player in semantic_details[:5]:
        print(f"  {player.get('player_name', 'Unknown'):25s} - "
              f"{player.get('total_goals', 0):2d} goals, "
              f"{player.get('total_assists', 0):2d} assists, "
              f"{player.get('total_points', 0):3d} pts")

print(f"\nEmbedding Source: Vector similarity to query embeddings")
embedding.close()

# Test 3: Hybrid Retriever (Merged Results)
print("\n" + "=" * 80)
print("3️⃣  HYBRID RETRIEVER (Baseline + Embeddings MERGED)")
print("-" * 80)

hybrid = HybridRetriever()
merged_results = hybrid.retrieve(query=query)

print(f"\nMerged Results Summary:")
print(f"  Total unified players: {len(merged_results['unified_players'])}")
print(f"  From baseline only: {sum(1 for p in merged_results['unified_players'] if p.get('source') == 'baseline')}")
print(f"  From semantic only: {sum(1 for p in merged_results['unified_players'] if p.get('source') == 'semantic')}")
print(f"  From both (hybrid): {sum(1 for p in merged_results['unified_players'] if p.get('source') == 'hybrid')}")

print(f"\nTop 10 Unified Players:")
for i, player in enumerate(merged_results['unified_players'][:10], 1):
    name = player.get('player_name', player.get('player', 'Unknown'))
    source = player.get('source', 'unknown')
    sim_score = player.get('similarity_score', 0)
    goals = player.get('total_goals', 0)
    points = player.get('total_points', 0)
    
    # Format source with emoji
    source_icon = {
        'baseline': '📊',
        'semantic': '🔍', 
        'hybrid': '⚡'
    }.get(source, '❓')
    
    print(f"{i:2d}. {source_icon} [{source:8s}] {name:25s} - "
          f"{goals:2d} goals, {points:3d} pts" + 
          (f", sim: {sim_score:.4f}" if sim_score > 0 else ""))

print("\n" + "-" * 80)
print("Merging Strategy:")
print("  • Baseline results added first (deterministic facts)")
print("  • Semantic results added with similarity scores")
print("  • Duplicates unified with combined metadata")
print("  • Hybrid source = player appears in both retrievers")

hybrid.close()

# Show what gets sent to LLMs
print("\n" + "=" * 80)
print("4️⃣  CONTEXT SENT TO LLMs")
print("-" * 80)

# Format the context like it would be sent to LLMs
context_preview = merged_results['unified_players'][:5]
print(f"\nSample of context (first 5 players):")
print(json.dumps(context_preview, indent=2))

print("\n" + "=" * 80)
print("✅ RETRIEVAL BREAKDOWN COMPLETE")
print("=" * 80)
