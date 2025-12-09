"""
Generate and store hybrid embeddings (numerical + semantic).
"""

import logging
import time
from src.embeddings.hybrid_embeddings import HybridEmbedder

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def main():
    print("=" * 100)
    print("GENERATING HYBRID EMBEDDINGS (Numerical + Semantic)")
    print("=" * 100)
    
    start_time = time.time()
    
    with HybridEmbedder() as embedder:
        # Generate both types of embeddings
        numerical_emb, text_emb = embedder.generate_hybrid_embeddings(
            season="2021-22",
            min_minutes=500
        )
        
        if not numerical_emb or not text_emb:
            print("❌ Failed to generate embeddings")
            return
        
        # Store in Neo4j
        embedder.store_hybrid_embeddings(numerical_emb, text_emb)
        
        total_time = time.time() - start_time
        
        print("\n" + "=" * 100)
        print("SUMMARY")
        print("=" * 100)
        print(f"Players: {len(numerical_emb)}")
        print(f"Numerical features: 10 dimensions (goals/90, assists/90, pts/game, ICT, etc.)")
        print(f"Text embedding: {embedder.text_dim} dimensions")
        print(f"Total time: {total_time:.2f}s")
        print("=" * 100)
        print("\n✓ Hybrid embeddings stored!")
        print("  Each player now has:")
        print("    - numerical_features: Normalized stats vector")
        print("    - text_embedding: Semantic description embedding")

if __name__ == "__main__":
    main()
