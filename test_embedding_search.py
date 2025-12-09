"""
Test semantic similarity search with stored embeddings.
"""

import logging
from src.embeddings.feature_embeddings import FeatureEmbedder

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def test_similarity_search():
    """Test finding similar players using embeddings."""
    
    MODEL_NAME = "all-mpnet-base-v2"
    
    print("=" * 100)
    print("SEMANTIC SIMILARITY SEARCH TEST")
    print("=" * 100)
    
    with FeatureEmbedder(model_name=MODEL_NAME) as embedder:
        # Override property name to match what we stored
        test_queries = [
            "High scoring forward with lots of goals",
            "Midfielder with great assists and creativity",
            "Defender with clean sheets and bonus points",
            "Player with high ICT index and influence",
            "Top FPL points scorer"
        ]
        
        for query in test_queries:
            print(f"\n{'=' * 100}")
            print(f"Query: '{query}'")
            print('=' * 100)
            
            # We need to modify the find_similar_players to use correct property
            # For now, let's manually query
            query_embedding = embedder.model.encode(query, convert_to_numpy=True)
            
            cypher_query = """
            MATCH (p:Player)
            WHERE p.feature_embedding_mpnet IS NOT NULL
            RETURN p.player_name AS name, 
                   p.feature_embedding_mpnet AS embedding
            LIMIT 100
            """
            
            try:
                with embedder.driver.session(database="neo4j") as session:
                    result = session.run(cypher_query)
                    players = [dict(record) for record in result]
                
                if not players:
                    print("No players with embeddings found")
                    continue
                
                # Calculate similarities
                import numpy as np
                similarities = []
                for player in players:
                    player_emb = np.array(player['embedding'])
                    # Cosine similarity
                    similarity = np.dot(query_embedding, player_emb) / (
                        np.linalg.norm(query_embedding) * np.linalg.norm(player_emb)
                    )
                    similarities.append({
                        'player_name': player['name'],
                        'similarity': float(similarity)
                    })
                
                # Sort and get top 5
                similarities.sort(key=lambda x: x['similarity'], reverse=True)
                top_5 = similarities[:5]
                
                print(f"\nTop 5 similar players:")
                for i, result in enumerate(top_5, 1):
                    print(f"  {i}. {result['player_name']:<30} (similarity: {result['similarity']:.4f})")
                    
            except Exception as e:
                print(f"Error: {str(e)}")
    
    print("\n" + "=" * 100)
    print("✓ Similarity search test completed!")
    print("=" * 100)


if __name__ == "__main__":
    test_similarity_search()
