"""Test query for best forwards above £7 million."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.retrieval.hybrid_retriever import HybridRetriever

retriever = HybridRetriever()

query = "Best forwards above 7 million in 2022-23"

print("="*80)
print(f"Query: {query}")
print("="*80)

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

print(f"\nIntent: {intent_str}")
print(f"Confidence: {results.get('confidence', 0):.0%}\n")

players = results.get('unified_players', [])
print(f"Found {len(players)} forwards:\n")

if players:
    for i, player in enumerate(players, 1):
        name = player.get('player_name', player.get('player', 'Unknown'))
        price = player.get('price', 0)
        points = player.get('total_points', 0)
        goals = player.get('total_goals', player.get('goals', 0))
        assists = player.get('total_assists', player.get('assists', 0))
        value_score = player.get('value_score', 0)
        
        print(f"{i}. {name}")
        print(f"   💰 Price: £{price:.1f}m")
        print(f"   📊 Points: {points}")
        print(f"   ⚽ Goals: {goals} | 🎯 Assists: {assists}")
        print(f"   ⭐ Value Score: {value_score:.1f}")
        print()
else:
    print("⚠️  No players found!")

retriever.close()
