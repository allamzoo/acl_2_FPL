"""
Generate and store enhanced embeddings with better semantic descriptions.
"""

import logging
import time
from src.embeddings.numerical_embeddings import NumericalFeatureEmbedder

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    MODEL_NAME = "all-mpnet-base-v2"
    SEASON = "2021-22"
    PROPERTY_NAME = "feature_embedding_enhanced"
    
    print("=" * 100)
    print(f"STORING ENHANCED EMBEDDINGS")
    print("=" * 100)
    print(f"Model: {MODEL_NAME}")
    print(f"Property: {PROPERTY_NAME}")
    print()
    
    start_time = time.time()
    
    with NumericalFeatureEmbedder(model_name=MODEL_NAME) as embedder:
        # Generate embeddings
        embeddings = embedder.generate_embeddings(season=SEASON)
        
        if not embeddings:
            logger.error("No embeddings generated")
            return
        
        # Store in Neo4j
        embedder.store_embeddings_in_neo4j(
            embeddings=embeddings,
            season=SEASON,
            property_name=PROPERTY_NAME
        )
        
        # Summary
        total_time = time.time() - start_time
        print("\n" + "=" * 100)
        print("SUMMARY")
        print("=" * 100)
        print(f"Embeddings: {len(embeddings)}")
        print(f"Dimension: {embedder.embedding_dim}")
        print(f"Property: {PROPERTY_NAME}")
        print(f"Total time: {total_time:.2f}s")
        print("=" * 100)
        print(f"\n✓ Enhanced embeddings stored!")


if __name__ == "__main__":
    main()
