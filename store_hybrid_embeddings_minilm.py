"""
Generate hybrid embeddings with all-MiniLM-L6-v2 model for comparison.
"""

import logging
import time
from src.embeddings.hybrid_embeddings import HybridEmbedder

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    MODEL_NAME = "all-MiniLM-L6-v2"
    
    print("=" * 100)
    print(f"GENERATING HYBRID EMBEDDINGS WITH {MODEL_NAME}")
    print("=" * 100)
    
    start_time = time.time()
    
    with HybridEmbedder(model_name=MODEL_NAME) as embedder:
        # Generate both types of embeddings
        numerical_emb, text_emb = embedder.generate_hybrid_embeddings(
            season="2021-22",
            min_minutes=500
        )
        
        if not numerical_emb or not text_emb:
            print("❌ Failed to generate embeddings")
            return
        
        # Store with different property names for comparison
        print("\nStoring embeddings with MiniLM-specific properties...")
        update_query = """
        MATCH (p:Player {player_name: $player_name})
        SET p.numerical_features_minilm = $numerical_emb,
            p.text_embedding_minilm = $text_emb
        """
        
        from tqdm import tqdm
        with embedder.driver.session(database="neo4j") as session:
            for player_name in tqdm(numerical_emb.keys(), desc="Storing"):
                session.run(update_query, {
                    "player_name": player_name,
                    "numerical_emb": numerical_emb[player_name].tolist(),
                    "text_emb": text_emb[player_name].tolist()
                })
        
        total_time = time.time() - start_time
        
        print("\n" + "=" * 100)
        print("SUMMARY")
        print("=" * 100)
        print(f"Model: {MODEL_NAME}")
        print(f"Players: {len(numerical_emb)}")
        print(f"Numerical features: 10 dimensions (same as MPNet)")
        print(f"Text embedding: {embedder.text_dim} dimensions")
        print(f"Total time: {total_time:.2f}s")
        print("=" * 100)
        print("\n✓ MiniLM hybrid embeddings stored!")
        print("  Properties created:")
        print("    - numerical_features_minilm: Normalized stats vector")
        print("    - text_embedding_minilm: Semantic description embedding")
        print("\n  Now you have 2 models to compare:")
        print("    1. all-mpnet-base-v2 (768 dims) - Better quality")
        print("    2. all-MiniLM-L6-v2 (384 dims) - Faster, smaller")

if __name__ == "__main__":
    main()
