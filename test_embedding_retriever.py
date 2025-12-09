"""
Test the Embedding Retriever with real queries.
"""

import logging
from src.retrieval.embedding_retriever import EmbeddingRetriever

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    print("=" * 100)
    print("EMBEDDING RETRIEVER TEST")
    print("=" * 100)
    
    # Test queries representing different search types
    test_queries = [
        "Cheap budget striker under 7 million",
        "Differential pick with low ownership",
        "Set piece specialist who takes free kicks",
        "Box-to-box midfielder with high work rate",
        "Wing back who gets forward often",
        "Captain option for big hauls",
        "Explosive player with high ceiling",
        "Consistent points every week",
        "Player in form with momentum",
        "Bargain defender from top 4 team"
    ]
    
    with EmbeddingRetriever() as retriever:
        for query in test_queries:
            print(f"\n{'=' * 100}")
            print(f"QUERY: '{query}'")
            print('=' * 100)
            
            # Perform semantic search
            results = retriever.semantic_search(query, top_k=5, season="2021-22")
            
            # Format for LLM
            formatted = retriever.format_results_for_llm(results)
            print(formatted)
    
    print("\n" + "=" * 100)
    print("✓ All tests completed!")
    print("=" * 100)


if __name__ == "__main__":
    main()
