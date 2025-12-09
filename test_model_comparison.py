"""
Compare the two embedding models: all-mpnet-base-v2 vs all-MiniLM-L6-v2
"""

import logging
import time
import numpy as np
from sentence_transformers import SentenceTransformer
from neo4j import GraphDatabase
from config.config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, NEO4J_DATABASE

logging.basicConfig(level=logging.INFO, format='%(message)s')

def extract_query_numerical_features(query: str) -> np.ndarray:
    """Extract numerical preferences from query."""
    query_lower = query.lower()
    preferences = np.zeros(10)
    
    if any(word in query_lower for word in ['goal', 'score', 'scorer', 'striker', 'prolific']):
        preferences[0] = 1.0
    if any(word in query_lower for word in ['assist', 'creative', 'playmaker', 'provider']):
        preferences[1] = 1.0
    if any(word in query_lower for word in ['points', 'fpl', 'top', 'best', 'premium', 'elite']):
        preferences[2] = 1.0
        preferences[3] = 0.8
    if any(word in query_lower for word in ['ict', 'impact', 'influential', 'dominant']):
        preferences[3] = 1.0
        preferences[4] = 0.8
    if any(word in query_lower for word in ['creative', 'creativity']):
        preferences[5] = 1.0
    if any(word in query_lower for word in ['threat', 'attacking', 'attack']):
        preferences[6] = 1.0
    if any(word in query_lower for word in ['consistent', 'bonus', 'reliable']):
        preferences[7] = 1.0
    if any(word in query_lower for word in ['clean sheet', 'defensive', 'defense']):
        preferences[8] = 1.0
    if any(word in query_lower for word in ['nailed', 'regular', 'starter']):
        preferences[9] = 1.0
    
    if np.sum(preferences) == 0:
        preferences[2] = 1.0
        preferences[3] = 0.5
    
    return preferences


def search_with_model(model_name: str, num_prop: str, text_prop: str, query: str, top_k: int = 5):
    """Search using specified model embeddings."""
    model = SentenceTransformer(model_name)
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    
    # Generate query embedding
    start_time = time.time()
    query_text_emb = model.encode(query, convert_to_numpy=True)
    query_num_pref = extract_query_numerical_features(query)
    encode_time = time.time() - start_time
    
    # Retrieve players
    cypher_query = f"""
    MATCH (p:Player)-[r:PLAYED_IN]->(f:Fixture)
    WHERE p.{num_prop} IS NOT NULL AND p.{text_prop} IS NOT NULL
    WITH p, SUM(r.minutes) as total_minutes
    WHERE total_minutes >= 500
    RETURN DISTINCT p.player_name AS name,
           p.{num_prop} AS num_features,
           p.{text_prop} AS text_emb
    """
    
    search_start = time.time()
    with driver.session(database=NEO4J_DATABASE) as session:
        result = session.run(cypher_query)
        players = [dict(record) for record in result]
    
    # Calculate similarities
    similarities = []
    for player in players:
        text_emb = np.array(player['text_emb'])
        text_sim = np.dot(query_text_emb, text_emb) / (
            np.linalg.norm(query_text_emb) * np.linalg.norm(text_emb)
        )
        
        num_features = np.array(player['num_features'])
        num_sim = np.dot(query_num_pref, num_features) / (
            np.linalg.norm(query_num_pref) + 1e-6
        )
        num_sim = (num_sim + 3) / 6
        num_sim = max(0, min(1, num_sim))
        
        combined_sim = 0.7 * num_sim + 0.3 * text_sim
        
        similarities.append({
            'player_name': player['name'],
            'similarity_score': float(combined_sim)
        })
    
    similarities.sort(key=lambda x: x['similarity_score'], reverse=True)
    search_time = time.time() - search_start
    
    driver.close()
    
    return similarities[:top_k], encode_time, search_time


def main():
    print("=" * 100)
    print("EMBEDDING MODEL COMPARISON: all-mpnet-base-v2 vs all-MiniLM-L6-v2")
    print("=" * 100)
    
    test_queries = [
        "Elite premium midfielder with goals and assists",
        "Prolific striker goal scorer",
        "Creative playmaker with assists",
        "Defender with clean sheets",
        "High ICT index player"
    ]
    
    for query in test_queries:
        print(f"\n{'=' * 100}")
        print(f"Query: '{query}'")
        print('=' * 100)
        
        # Test MPNet (768 dims)
        mpnet_results, mpnet_encode, mpnet_search = search_with_model(
            "all-mpnet-base-v2",
            "numerical_features",
            "text_embedding",
            query
        )
        
        # Test MiniLM (384 dims)
        minilm_results, minilm_encode, minilm_search = search_with_model(
            "all-MiniLM-L6-v2",
            "numerical_features_minilm",
            "text_embedding_minilm",
            query
        )
        
        print(f"\n{'MPNet (768 dims)':<40} | {'MiniLM (384 dims)':<40}")
        print("-" * 100)
        
        for i in range(5):
            mpnet_player = mpnet_results[i]['player_name'][:35]
            mpnet_sim = mpnet_results[i]['similarity_score']
            
            minilm_player = minilm_results[i]['player_name'][:35]
            minilm_sim = minilm_results[i]['similarity_score']
            
            print(f"{i+1}. {mpnet_player:<35} {mpnet_sim:.3f} | {minilm_player:<35} {minilm_sim:.3f}")
        
        print(f"\nPerformance:")
        print(f"  Encode time:  MPNet: {mpnet_encode:.3f}s | MiniLM: {minilm_encode:.3f}s (faster: {mpnet_encode/minilm_encode:.2f}x)")
        print(f"  Search time:  MPNet: {mpnet_search:.3f}s | MiniLM: {minilm_search:.3f}s")
    
    print("\n" + "=" * 100)
    print("SUMMARY")
    print("=" * 100)
    print("\nall-mpnet-base-v2:")
    print("  ✓ 768 dimensions - richer semantic representation")
    print("  ✓ Better quality embeddings")
    print("  ✗ Slower encoding (2-3x)")
    print("  ✗ Larger model size")
    
    print("\nall-MiniLM-L6-v2:")
    print("  ✓ 384 dimensions - compact representation")
    print("  ✓ Faster encoding (2-3x)")
    print("  ✓ Smaller model size")
    print("  ✗ Potentially lower quality")
    
    print("\n" + "=" * 100)


if __name__ == "__main__":
    main()
