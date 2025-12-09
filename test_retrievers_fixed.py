"""Test the fixed retrievers with correct schema"""
import sys
sys.path.append('C:\\Users\\Marwan Allam\\fpl-graph-rag')

from src.retrieval.baseline_retriever import BaselineRetriever
from src.retrieval.hybrid_retriever import HybridRetriever

print("=" * 60)
print("TESTING FIXED RETRIEVERS")
print("=" * 60)

# Test baseline retriever
baseline = BaselineRetriever()
print("\n1. Testing get_top_scorers (FWD, 2022-23)...")
scorers = baseline.get_top_scorers(position="FWD", season="2022-23", limit=5)
print(f"   Retrieved {len(scorers)} scorers")
if scorers:
    for i, player in enumerate(scorers[:3], 1):
        print(f"   {i}. {player.get('player', 'Unknown')} - {player.get('total_goals', 0)} goals, {player.get('total_points', 0)} pts")

print("\n2. Testing get_player_season_stats (Haaland, 2022-23)...")
haaland = baseline.get_player_season_stats(player_name="Haaland", season="2022-23")
print(f"   Retrieved {len(haaland)} results")
if haaland:
    h = haaland[0]
    print(f"   {h.get('player', 'Unknown')}: {h.get('goals', 0)} goals, {h.get('assists', 0)} assists, {h.get('total_points', 0)} points")

print("\n3. Testing get_gameweek_top_performers (GW 1, 2022-23)...")
gw_top = baseline.get_gameweek_top_performers(gameweek=1, season="2022-23", limit=5)
print(f"   Retrieved {len(gw_top)} players")
if gw_top:
    for i, player in enumerate(gw_top[:3], 1):
        print(f"   {i}. {player.get('player', 'Unknown')} - {player.get('points', 0)} pts")

print("\n4. Testing hybrid retriever...")
hybrid = HybridRetriever()
results = hybrid.retrieve(query="Who were the top scorers in 2022-23?")
print(f"   Unified players: {len(results['unified_players'])}")
print(f"   Baseline count: {len(results.get('baseline', {}))}")
print(f"   Semantic count: {results.get('semantic_count', 0)}")
if results['unified_players']:
    for i, player in enumerate(results['unified_players'][:3], 1):
        name = player.get('name', player.get('player_name', 'Unknown'))
        print(f"   {i}. {name} from {player.get('source', 'unknown')}")

baseline.close()
hybrid.close()

print("\n" + "=" * 60)
print("✅ RETRIEVAL TEST COMPLETE!")
print("=" * 60)
