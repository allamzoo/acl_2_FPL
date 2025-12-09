"""
Store feature embeddings in Neo4j for semantic similarity search.
"""

import logging
import time
from src.embeddings.feature_embeddings import FeatureEmbedder

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    # Model selection - using all-mpnet-base-v2 for better quality
    MODEL_NAME = "all-mpnet-base-v2"
    SEASON = "2021-22"
    PROPERTY_NAME = "feature_embedding_mpnet"
    
    print("=" * 100)
    print(f"STORING FEATURE EMBEDDINGS IN NEO4J")
    print("=" * 100)
    print(f"\nModel: {MODEL_NAME}")
    print(f"Season: {SEASON}")
    print(f"Property: {PROPERTY_NAME}")
    print()
    
    # Initialize embedder
    logger.info("Initializing embedder...")
    start_time = time.time()
    
    with FeatureEmbedder(model_name=MODEL_NAME) as embedder:
        init_time = time.time() - start_time
        logger.info(f"Model loaded in {init_time:.2f}s")
        logger.info(f"Embedding dimension: {embedder.embedding_dim}")
        
        # Generate embeddings
        logger.info("\nGenerating embeddings...")
        gen_start = time.time()
        embeddings = embedder.generate_embeddings(season=SEASON, description_type="detailed")
        gen_time = time.time() - gen_start
        
        logger.info(f"Generated {len(embeddings)} embeddings in {gen_time:.2f}s")
        
        if not embeddings:
            logger.error("No embeddings generated. Exiting.")
            return
        
        # Store in Neo4j
        logger.info("\nStoring embeddings in Neo4j...")
        store_start = time.time()
        embedder.store_embeddings_in_neo4j(
            embeddings=embeddings,
            season=SEASON,
            property_name=PROPERTY_NAME
        )
        store_time = time.time() - store_start
        
        logger.info(f"Stored embeddings in {store_time:.2f}s")
        
        # Try to create vector index (may require Neo4j 5.11+)
        logger.info("\nAttempting to create vector index...")
        try:
            embedder.create_vector_index(
                index_name="player_feature_mpnet_index",
                property_name=PROPERTY_NAME
            )
        except Exception as e:
            logger.warning(f"Could not create vector index: {str(e)}")
            logger.info("Vector index creation skipped (may require Neo4j 5.11+)")
        
        # Summary
        total_time = time.time() - start_time
        print("\n" + "=" * 100)
        print("SUMMARY")
        print("=" * 100)
        print(f"Model: {MODEL_NAME}")
        print(f"Embeddings: {len(embeddings)}")
        print(f"Dimension: {embedder.embedding_dim}")
        print(f"Property: {PROPERTY_NAME}")
        print(f"Total time: {total_time:.2f}s")
        print("=" * 100)
        print("\n✓ Embeddings stored successfully in Neo4j!")
        print(f"  Players now have '{PROPERTY_NAME}' property with {embedder.embedding_dim}-dimensional vectors")
        print()


if __name__ == "__main__":
    main()
