"""
Debug intent classification
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from src.preprocessing.intent_classifier import LLMIntentClassifier, SimpleIntentClassifier


def test_intent_classification():
    """Test intent classifiers with top scorers query."""
    
    print("=" * 80)
    print("INTENT CLASSIFICATION DEBUG")
    print("=" * 80)
    
    query = "Who were the top scorers in 2022-23?"
    
    # Test SimpleIntentClassifier
    print("\n1. SimpleIntentClassifier (Rule-based)")
    print("-" * 80)
    simple = SimpleIntentClassifier()
    result = simple.classify(query)
    print(f"Query: {query}")
    print(f"Intent: {result['intent']}")
    print(f"Confidence: {result['confidence']}")
    print(f"Reasoning: {result.get('reasoning', 'N/A')}")
    
    # Test LLMIntentClassifier
    print("\n2. LLMIntentClassifier (BART-based)")
    print("-" * 80)
    llm = LLMIntentClassifier()
    
    if llm.available:
        result = llm.classify(query)
        print(f"Query: {query}")
        print(f"Intent: {result['intent']}")
        print(f"Confidence: {result['confidence']:.4f}")
        print(f"Reasoning: {result.get('reasoning', 'N/A')}")
        print(f"\nAll scores:")
        for label, score in result.get('all_scores', {}).items():
            print(f"  {label}: {score:.4f}")
    else:
        print("LLM classifier not available")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    test_intent_classification()
