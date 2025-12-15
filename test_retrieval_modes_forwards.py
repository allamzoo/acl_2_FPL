"""
Test retrieval of forwards above £7m using all three retrieval modes:
1. Baseline only
2. Baseline + Embedding Model 1 (all-mpnet-base-v2)
3. Baseline + Embedding Model 2 (all-MiniLM-L6-v2)
"""

from src.retrieval.hybrid_retriever import HybridRetriever
import time

def test_retrieval_modes():
    query = "Best forwards above 7 million in 2022-23"
    season = "2022-23"
    
    print("="*80)
    print(f"Query: {query}")
    print("="*80)
    print()
    
    # Mode 1: Baseline Only
    print("🔵 MODE 1: BASELINE ONLY")
    print("-" * 80)
    retriever_baseline = HybridRetriever(
        embedding_model="all-mpnet-base-v2",
        use_hybrid_embeddings=True
    )
    
    start = time.time()
    results_baseline = retriever_baseline.retrieve(
        query=query,
        season=season,
        retrieval_mode="baseline"
    )
    time_baseline = time.time() - start
    
    print(f"⏱️  Retrieval Time: {time_baseline:.3f}s")
    print(f"📊 Players Retrieved: {len(results_baseline['unified_players'])}")
    print(f"🎯 Intent: {results_baseline.get('intent', 'unknown')}")
    print(f"📈 Confidence: {results_baseline.get('intent_confidence', 0):.0%}")
    
    print("\nTop 5 Players:")
    for i, player in enumerate(results_baseline['unified_players'][:5], 1):
        name = player.get('player_name') or player.get('player') or player.get('name', 'Unknown')
        price = player.get('price', 0)
        points = player.get('total_points', 0)
        value = player.get('value_score', 0)
        print(f"  {i}. {name} - £{price:.1f}m, {points} pts, Value: {value:.1f}")
    
    print("\n")
    
    # Mode 2: Baseline + Model 1 (all-mpnet-base-v2)
    print("🟢 MODE 2: BASELINE + MODEL 1 (all-mpnet-base-v2, 768D)")
    print("-" * 80)
    
    start = time.time()
    results_model1 = retriever_baseline.retrieve(
        query=query,
        season=season,
        retrieval_mode="baseline+embedding1"
    )
    time_model1 = time.time() - start
    
    print(f"⏱️  Retrieval Time: {time_model1:.3f}s")
    print(f"📊 Players Retrieved: {len(results_model1['unified_players'])}")
    print(f"🎯 Intent: {results_model1.get('intent', 'unknown')}")
    print(f"📈 Confidence: {results_model1.get('intent_confidence', 0):.0%}")
    
    # Show breakdown if available
    if 'baseline_results' in results_model1:
        print(f"   └─ Baseline: {len(results_model1['baseline_results'])} players")
    if 'semantic_results' in results_model1:
        print(f"   └─ Semantic (Model 1): {len(results_model1['semantic_results'])} players")
    
    print("\nTop 5 Players:")
    for i, player in enumerate(results_model1['unified_players'][:5], 1):
        name = player.get('player_name') or player.get('player') or player.get('name', 'Unknown')
        price = player.get('price', 0)
        points = player.get('total_points', 0)
        value = player.get('value_score', 0)
        print(f"  {i}. {name} - £{price:.1f}m, {points} pts, Value: {value:.1f}")
    
    print("\n")
    
    # Mode 3: Baseline + Model 2 (all-MiniLM-L6-v2)
    print("🟡 MODE 3: BASELINE + MODEL 2 (all-MiniLM-L6-v2, 384D)")
    print("-" * 80)
    
    start = time.time()
    results_model2 = retriever_baseline.retrieve(
        query=query,
        season=season,
        retrieval_mode="baseline+embedding2"
    )
    time_model2 = time.time() - start
    
    print(f"⏱️  Retrieval Time: {time_model2:.3f}s")
    print(f"📊 Players Retrieved: {len(results_model2['unified_players'])}")
    print(f"🎯 Intent: {results_model2.get('intent', 'unknown')}")
    print(f"📈 Confidence: {results_model2.get('intent_confidence', 0):.0%}")
    
    # Show breakdown if available
    if 'baseline_results' in results_model2:
        print(f"   └─ Baseline: {len(results_model2['baseline_results'])} players")
    if 'semantic_results' in results_model2:
        print(f"   └─ Semantic (Model 2): {len(results_model2['semantic_results'])} players")
    
    print("\nTop 5 Players:")
    for i, player in enumerate(results_model2['unified_players'][:5], 1):
        name = player.get('player_name') or player.get('player') or player.get('name', 'Unknown')
        price = player.get('price', 0)
        points = player.get('total_points', 0)
        value = player.get('value_score', 0)
        print(f"  {i}. {name} - £{price:.1f}m, {points} pts, Value: {value:.1f}")
    
    print("\n")
    
    # Summary Comparison
    print("="*80)
    print("📊 SUMMARY COMPARISON")
    print("="*80)
    print(f"{'Mode':<30} {'Time':<12} {'Players':<10} {'Intent':<15}")
    print("-" * 80)
    print(f"{'Baseline Only':<30} {f'{time_baseline:.3f}s':<12} {len(results_baseline['unified_players']):<10} {results_baseline.get('intent', 'unknown'):<15}")
    print(f"{'Baseline + Model 1 (mpnet)':<30} {f'{time_model1:.3f}s':<12} {len(results_model1['unified_players']):<10} {results_model1.get('intent', 'unknown'):<15}")
    print(f"{'Baseline + Model 2 (MiniLM)':<30} {f'{time_model2:.3f}s':<12} {len(results_model2['unified_players']):<10} {results_model2.get('intent', 'unknown'):<15}")
    
    # Check for differences in top players
    print("\n🔍 Top Player Comparison:")
    baseline_top = results_baseline['unified_players'][0].get('player_name') or results_baseline['unified_players'][0].get('player', 'Unknown')
    model1_top = results_model1['unified_players'][0].get('player_name') or results_model1['unified_players'][0].get('player', 'Unknown')
    model2_top = results_model2['unified_players'][0].get('player_name') or results_model2['unified_players'][0].get('player', 'Unknown')
    
    print(f"  Baseline: {baseline_top}")
    print(f"  + Model 1: {model1_top}")
    print(f"  + Model 2: {model2_top}")
    
    if baseline_top == model1_top == model2_top:
        print("  ✅ All modes agree on top player")
    else:
        print("  ⚠️  Different top players retrieved")

if __name__ == "__main__":
    test_retrieval_modes()
