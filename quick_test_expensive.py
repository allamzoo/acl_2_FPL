"""Quick test to check if expensive players query works"""

from src.retrieval.baseline_retriever import BaselineRetriever
from src.retrieval.hybrid_retriever import HybridRetriever

# Test baseline retriever directly
print("=" * 80)
print("TEST 1: Direct Baseline Query")
print("=" * 80)
baseline = BaselineRetriever()
results = baseline.get_most_expensive_players(season="2021-22", limit=10, min_points=50)
print(f"\nFound {len(results)} players\n")

for i, player in enumerate(results[:10], 1):
    name = player.get('player_name', 'Unknown')
    price = player.get('price', 0)
    points = player.get('total_points', 0)
    pos = player.get('position', 'N/A')
    print(f"{i:2d}. {name:30s} - £{price:5.1f}m, {points:3d}pts ({pos})")

baseline.close()

# Test via hybrid retriever
print("\n" + "=" * 80)
print("TEST 2: Via Hybrid Retriever")
print("=" * 80)

retriever = HybridRetriever()
query = "Most expensive players in season 2022"
season = "2021-22"

print(f"\nQuery: {query}")
print(f"Season: {season}\n")

context = retriever.retrieve(query, season, retrieval_mode="baseline")

print(f"Intent: {context.get('intent', 'unknown')}")
print(f"Confidence: {context.get('intent_confidence', 0):.0%}")
print(f"Baseline results keys: {list(context.get('baseline_results', {}).keys())}")
print(f"Total players: {len(context.get('unified_players', []))}\n")

for i, player in enumerate(context.get('unified_players', [])[:10], 1):
    name = player.get('player_name', player.get('player', 'Unknown'))
    price = player.get('price', 0)
    points = player.get('total_points', 0)
    pos = player.get('position', 'N/A')
    print(f"{i:2d}. {name:30s} - £{price:5.1f}m, {points:3d}pts ({pos})")

retriever.close()
