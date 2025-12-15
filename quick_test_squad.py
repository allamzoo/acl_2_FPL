"""Quick test to check squad builder retrieval"""

from src.retrieval.baseline_retriever import BaselineRetriever
from src.retrieval.hybrid_retriever import HybridRetriever

print("=" * 80)
print("TEST 1: Direct Baseline Squad Builder")
print("=" * 80)

baseline = BaselineRetriever()
squad_data = baseline.build_squad_under_budget(season="2022-23", budget=100.0, min_points=30, min_games=10)

print(f"\nSquad Size: {squad_data['squad_size']}/15")
print(f"Total Cost: £{squad_data['total_cost']:.1f}m")
print(f"Remaining Budget: £{squad_data['remaining_budget']:.1f}m")
print(f"Total Points: {squad_data['total_points']}")
print(f"\nFormation: {squad_data['formation']}")

print("\nSquad Players:")
for i, player in enumerate(squad_data['squad'], 1):
    print(f"{i:2d}. {player['player_name']:30s} ({player['position']}) - "
          f"£{player['price']:.1f}m, {player['total_points']}pts, "
          f"Value: {player['value_ratio']:.1f}")

baseline.close()

print("\n" + "=" * 80)
print("TEST 2: Via Hybrid Retriever")
print("=" * 80)

retriever = HybridRetriever()
query = "Build an optimal squad under 100 million for season 2022-23"
season = "2022-23"

print(f"\nQuery: {query}")
print(f"Season: {season}\n")

context = retriever.retrieve(query, season, retrieval_mode="baseline")

print(f"Intent: {context.get('intent', 'unknown')}")
print(f"Confidence: {context.get('intent_confidence', 0):.0%}")
print(f"Baseline results keys: {list(context.get('baseline_results', {}).keys())}")

if 'squad_builder' in context.get('baseline_results', {}):
    squad_data = context['baseline_results']['squad_builder']
    print(f"\n✅ Squad builder data found!")
    print(f"Squad Size: {squad_data['squad_size']}/15")
    print(f"Total Cost: £{squad_data['total_cost']:.1f}m")
    print(f"Formation: {squad_data['formation']}")
else:
    print("\n❌ Squad builder data NOT found in context")

retriever.close()
