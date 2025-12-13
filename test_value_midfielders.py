"""
Test query: "good midfielders with low budget"
Tests value-for-money queries using price data
"""

from src.retrieval.baseline_retriever import BaselineRetriever
from src.retrieval.embedding_retriever import EmbeddingRetriever
from src.retrieval.hybrid_retriever import HybridRetriever
from src.llm.generator import FPLAnswerGenerator

def main():
    # Initialize retrievers
    baseline = BaselineRetriever()
    embedding = EmbeddingRetriever()
    hybrid = HybridRetriever()
    
    query = "good midfielders with low budget"
    season = "2022-23"
    
    print(f"Query: {query}\n")
    print("=" * 80)
    
    # Test baseline retriever - VALUE QUERY
    print("\n1. BASELINE RETRIEVER (Best Value Midfielders):")
    print("-" * 80)
    baseline_results = baseline.get_best_value_players(
        position="MID", 
        season=season, 
        max_price=8.0,  # Under £8.0m
        min_points=100,
        limit=15
    )
    
    if baseline_results:
        print(f"Retrieved: {len(baseline_results)} midfielders")
        for i, player in enumerate(baseline_results[:10], 1):
            price = player.get('price', 0)
            value_score = player.get('value_score', 0)
            print(f"{i}. {player['player']} - £{price:.1f}m, {player['total_points']} pts, "
                  f"Value: {value_score:.1f} pts/£m")
    else:
        print("No baseline results")
    
    # Test embedding retriever
    print("\n\n2. EMBEDDING RETRIEVER (Semantic Search):")
    print("-" * 80)
    embedding_results = embedding.find_similar_players(query, season=season, top_k=10)
    
    if embedding_results:
        print(f"Retrieved: {len(embedding_results)} players")
        for i, player in enumerate(embedding_results, 1):
            similarity = player.get('similarity', player.get('final_similarity', 0))
            print(f"{i}. {player['player_name']} - Similarity: {similarity:.4f}")
            if 'total_points' in player:
                print(f"   Stats: {player.get('total_points', 0)} pts, "
                      f"{player.get('total_goals', 0)} goals, {player.get('total_assists', 0)} assists")
    else:
        print("No embedding results")
    
    # Test hybrid retriever
    print("\n\n3. HYBRID RETRIEVER:")
    print("-" * 80)
    hybrid_results = hybrid.retrieve(query, season=season)
    
    if hybrid_results and 'unified_results' in hybrid_results:
        unified = hybrid_results['unified_results']
        print(f"\nUnified Results: {len(unified)} players")
        
        # Count sources
        baseline_only = sum(1 for p in unified if p['source'] == 'baseline')
        semantic_only = sum(1 for p in unified if p['source'] == 'semantic')
        hybrid_count = sum(1 for p in unified if p['source'] == 'hybrid')
        
        print(f"From baseline only: {baseline_only}")
        print(f"From semantic only: {semantic_only}")
        print(f"From both (hybrid): {hybrid_count}")
        
        print("\nTop 10 Results:")
        for i, player in enumerate(unified[:10], 1):
            source_icon = "🔷" if player['source'] == 'baseline' else "🟢" if player['source'] == 'semantic' else "🔶"
            print(f"{i}. {source_icon} {player['player_name']} - Source: {player['source']}")
            if 'total_points' in player:
                print(f"   Stats: {player.get('total_points', 0)} pts")
            if 'similarity' in player:
                print(f"   Similarity: {player['similarity']:.4f}")
    else:
        print("No hybrid results")
    
    # Test with LLM generation
    print("\n\n4. LLM GENERATION (3 Models):")
    print("=" * 80)
    
    generator = FPLAnswerGenerator()
    
    # Get context from hybrid retriever
    context = hybrid_results if hybrid_results else {}
    
    # Generate with all 3 models
    models = [
        ("llama-4-maverick", "Llama 4 Maverick"),
        ("qwen-3-32b", "Qwen 3"),
        ("gpt-oss-20b", "GPT OSS")
    ]
    
    for model_id, model_name in models:
        print(f"\n{model_name} Response:")
        print("-" * 80)
        
        try:
            response = generator.answer(
                query=query,
                season=season,
                model=model_id
            )
            print(response)
        except Exception as e:
            print(f"Error: {e}")
    
    baseline.close()
    embedding.close()

if __name__ == "__main__":
    main()
