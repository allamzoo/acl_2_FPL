"""Quick test for value query with corrected pricing."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.retrieval.hybrid_retriever import HybridRetriever

retriever = HybridRetriever()

query = "Best value midfielders under 8.0 in 2022-23"

print(f"Query: {query}\n")

results = retriever.retrieve(
    query=query,
    retrieval_mode="baseline",
    season="2022-23"
)

intent = results.get('intent', 'N/A')
if hasattr(intent, 'value'):
    intent_str = intent.value
else:
    intent_str = str(intent)

print(f"Intent: {intent_str}")
print(f"Confidence: {results.get('confidence', 0):.0%}\n")

players = results.get('unified_players', [])
print(f"Found {len(players)} players:\n")

for i, player in enumerate(players[:10], 1):
    name = player.get('player_name', player.get('player', 'Unknown'))
    price = player.get('price', 0)
    points = player.get('total_points', 0)
    value_score = player.get('value_score', 0)
    
    print(f"{i}. {name}")
    print(f"   £{price:.1f}m | {points} pts | Value: {value_score:.1f}")

retriever.close()
