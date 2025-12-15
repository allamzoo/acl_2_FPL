"""Debug script to test price threshold extraction."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.retrieval.hybrid_retriever import HybridRetriever

retriever = HybridRetriever()

queries = [
    "Best forwards above 7 million in 2022-23",
    "Best forwards under 7 million in 2022-23",
    "Best midfielders over 8.0",
    "Cheap defenders below 5.0"
]

for query in queries:
    print(f"\nQuery: {query}")
    print("="*60)
    
    query_lower = query.lower()
    entities = retriever.entity_extractor.extract(query)
    
    print(f"Extracted entities: {entities}")
    
    # Check price threshold
    threshold = retriever._extract_price_threshold(query)
    print(f"Price threshold: {threshold}")
    
    # Check keywords
    has_under = any(word in query_lower for word in ['under', 'below', 'cheaper than', 'less than'])
    has_above = any(word in query_lower for word in ['above', 'over', 'more than', 'at least'])
    
    print(f"Has 'under' keywords: {has_under}")
    print(f"Has 'above' keywords: {has_above}")
    
    if has_under:
        print(f"→ Would set max_price = {threshold}")
    elif has_above:
        print(f"→ Would set min_price = {threshold}")

retriever.close()
