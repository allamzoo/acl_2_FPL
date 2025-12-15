"""Debug version - test gameweek query with detailed output"""
from src.retrieval.hybrid_retriever import HybridRetriever
from src.retrieval.baseline_retriever import BaselineRetriever

print("=" * 80)
print("DEBUG: Testing Gameweek Query")
print("=" * 80)

query = "Who were the best performing midfielders in gameweek 5 season 2021-22?"
season = "2021-22"

print(f"\nQuery: {query}")
print(f"Season: {season}\n")

# Test baseline retriever directly
print("1. Testing BASELINE RETRIEVER DIRECTLY:")
print("-" * 80)
baseline = BaselineRetriever()

# Try the gameweek method directly
print("\nCalling get_gameweek_top_performers(5, '2021-22', position='MID', limit=10)...")
gw_results = baseline.get_gameweek_top_performers(5, season, position='MID', limit=10)
print(f"Results: {len(gw_results)} players")
if gw_results:
    for i, p in enumerate(gw_results[:5], 1):
        print(f"  {i}. {p.get('player', p.get('name'))} ({p.get('position')}) - {p.get('total_points', p.get('points'))} pts")
else:
    print("  No midfielders found")

baseline.close()

# Test hybrid retriever
print("\n\n2. Testing HYBRID RETRIEVER:")
print("-" * 80)
retriever = HybridRetriever()

results = retriever.retrieve(query, season=season, retrieval_mode="baseline")

print(f"\nIntent: {results.get('intent')}")
print(f"Confidence: {results.get('confidence', 0):.2%}")
print(f"Players: {len(results.get('players', []))}")

if results.get('players'):
    print("\nTop 5 players:")
    for i, p in enumerate(results['players'][:5], 1):
        print(f"  {i}. {p.get('player', p.get('name'))} - {p.get('total_points', p.get('points'))} pts")
else:
    print("\n❌ No players returned")
    print("\nContext baseline_results keys:")
    if 'context' in results:
        baseline_results = results['context'].get('baseline_results', {})
        print(f"  Keys: {list(baseline_results.keys())}")
        for key, value in baseline_results.items():
            if isinstance(value, list):
                print(f"  {key}: {len(value)} results")
                if value:
                    print(f"    Sample: {value[0]}")
    
    print("\nUnified players:")
    if 'context' in results:
        unified = results['context'].get('unified_players', [])
        print(f"  Count: {len(unified)}")
        if unified:
            print(f"  Sample: {unified[0]}")

retriever.close()
