"""
Compare the two embedding models: all-mpnet-base-v2 vs all-MiniLM-L6-v2
"""

import logging
from src.retrieval.embedding_retriever import EmbeddingRetriever

logging.basicConfig(level=logging.INFO, format='%(message)s')

def test_model(model_name, property_suffix, queries):
    """Test a specific model."""
    print(f"\n{'=' * 100}")
    print(f"MODEL: {model_name}")
    print('=' * 100)
    
    # Create retriever with model-specific properties
    retriever = EmbeddingRetriever(
        model_name=model_name,
        use_hybrid=True,
        numerical_weight=0.7,
        text_weight=0.3
    )
    
    # Override the hybrid search to use model-specific properties
    original_hybrid = retriever._hybrid_search
    
    def custom_hybrid_search(query, top_k, min_minutes):
        query_text_emb = retriever.model.encode(query, convert_to_numpy=True)
        query_num_preferences = retriever._extract_query_numerical_features(query)
        
        cypher_query = f"""
        MATCH (p:Player)-[r:PLAYED_IN]->(f:Fixture)
        WHERE p.numerical_features{property_suffix} IS NOT NULL 
          AND p.text_embedding{property_suffix} IS NOT NULL
        WITH p, SUM(r.minutes) as total_minutes
        WHERE total_minutes >= $min_minutes
        RETURN DISTINCT p.player_name AS name,
               p.numerical_features{property_suffix} AS num_features,
               p.text_embedding{property_suffix} AS text_emb
        """
        
        import numpy as np
        try:
            with retriever.driver.session(database="neo4j") as session:
                result = session.run(cypher_query, {"min_minutes": min_minutes})
                players = [dict(record) for record in result]
            
            if not players:
                return []
            
            similarities = []
            for player in players:
                text_emb = np.array(player['text_emb'])
                text_sim = np.dot(query_text_emb, text_emb) / (
                    np.linalg.norm(query_text_emb) * np.linalg.norm(text_emb)
                )
                
                num_features = np.array(player['num_features'])
                num_sim = np.dot(query_num_preferences, num_features) / (
                    np.linalg.norm(query_num_preferences) + 1e-6
                )
                num_sim = (num_sim + 3) / 6
                num_sim = max(0, min(1, num_sim))
                
                combined_sim = (retriever.numerical_weight * num_sim + 
                               retriever.text_weight * text_sim)
                
                similarities.append({
                    'player_name': player['name'],
                    'similarity_score': float(combined_sim)
                })
            
            similarities.sort(key=lambda x: x['similarity_score'], reverse=True)
            return similarities[:top_k]
            
        except Exception as e:
            print(f"Error: {e}")
            return []
    
    retriever._hybrid_search = custom_hybrid_search
    
    try:
        for query in queries:
            print(f"\nQuery: '{query}'")
            print('-' * 100)
            
            results = retriever.semantic_search(query, top_k=5, season="2021-22")
            
            if results['players']:
                for i, player in enumerate(results['players'], 1):
                    print(f"{i}. {player['player_name']:<30} ({player['position']}) "
                          f"Sim: {player['similarity_score']:.3f} | "
                          f"G:{player['total_goals']:2d} A:{player['total_assists']:2d} Pts:{player['total_points']:3d}")
            else:
                print("No results found")
    finally:
        retriever.close()


def main():
    print("=" * 100)
    print("EMBEDDING MODEL COMPARISON")
    print("=" * 100)
    print("\nComparing two models on the same queries:")
    print("  1. all-mpnet-base-v2 (768 dimensions) - Higher quality")
    print("  2. all-MiniLM-L6-v2 (384 dimensions) - Faster, smaller")
    
    test_queries = [
        "High scoring forward with lots of goals",
        "Creative midfielder with assists",
        "Defender with clean sheets"
    ]
    
    # Test MPNet model
    test_model(
        model_name="all-mpnet-base-v2",
        property_suffix="",  # Uses numerical_features and text_embedding
        queries=test_queries
    )
    
    # Test MiniLM model
    test_model(
        model_name="all-MiniLM-L6-v2", 
        property_suffix="_minilm",  # Uses numerical_features_minilm and text_embedding_minilm
        queries=test_queries
    )
    
    print("\n" + "=" * 100)
    print("COMPARISON COMPLETE")
    print("=" * 100)
    print("\nKey Differences:")
    print("  • MPNet (768-dim): Better semantic understanding, higher quality matches")
    print("  • MiniLM (384-dim): 2x faster, half the size, still good quality")
    print("\nBoth use same numerical features (70% weight) + text embeddings (30% weight)")
    print("=" * 100)


if __name__ == "__main__":
    main()
