"""
Test script for Intent Classifier
Tests LLM-based intent classification with various FPL queries.
"""

from src.preprocessing.intent_classifier import LLMIntentClassifier, SimpleIntentClassifier
import json


def test_intent_classifier():
    """Test intent classification with sample queries."""
    
    # Test queries covering all intents
    test_queries = [
        # PLAYER_SEARCH
        "Who is Mohamed Salah?",
        "Find player named Kane",
        
        # PLAYER_STATS
        "What are Salah's stats for 2021-22 season?",
        "Show me Kevin De Bruyne's performance in 2021-22",
        
        # TOP_SCORERS
        "Who scored the most goals among forwards in 2021-22?",
        "Top 10 goal scorers for midfielders",
        
        # TOP_ASSISTERS
        "Who had the most assists in 2021-22?",
        "Best playmakers among midfielders",
        
        # TEAM_ANALYSIS
        "Show me Liverpool's squad for 2021-22",
        "Which players played for Arsenal?",
        
        # GAMEWEEK_PERFORMERS
        "Who were the best players in gameweek 1?",
        "Top performers in GW 10 of 2021-22",
        
        # PLAYER_COMPARISON
        "Compare Salah and Kane in 2021-22",
        "How does Son compare to Mane?",
        
        # HIGH_PERFORMERS
        "Which players scored more than 15 goals?",
        "Find players with at least 20 goals in 2021-22",
        
        # PLAYER_FORM
        "How has Salah performed in recent gameweeks?",
        "Show me Kane's form over the last 5 games",
        
        # ICT_ANALYSIS
        "Who has the best ICT index among midfielders?",
        "Top players by influence, creativity and threat",
    ]
    
    print("=" * 80)
    print("INTENT CLASSIFIER TEST")
    print("=" * 80)
    
    # First, test with SimpleIntentClassifier (keyword-based fallback)
    print("\n" + "=" * 80)
    print("SIMPLE KEYWORD-BASED CLASSIFIER")
    print("=" * 80)
    
    simple_classifier = SimpleIntentClassifier()
    
    for query in test_queries[:5]:  # Test first 5 with simple classifier
        result = simple_classifier.classify(query)
        print(f"\nQuery: {query}")
        print(f"Intent: {result['intent'].value}")
        print(f"Confidence: {result['confidence']}")
        print(f"Reasoning: {result['reasoning']}")
        print(f"Retriever method: {simple_classifier.get_query_mapping(result['intent'])}")
    
    # Now test with LLM-based classifier
    print("\n\n" + "=" * 80)
    print("LLM-BASED CLASSIFIER")
    print("=" * 80)
    print("\nInitializing LLM classifier...")
    
    try:
        # Try with smaller, faster model first
        classifier = LLMIntentClassifier(model_name="facebook/bart-large-mnli")
        
        print("Testing with sample queries...\n")
        
        for i, query in enumerate(test_queries[:8], 1):  # Test 8 queries with LLM
            print(f"\n{'-' * 80}")
            print(f"Test {i}: {query}")
            print('-' * 80)
            
            result = classifier.classify(query)
            
            print(f"Intent: {result['intent'].value}")
            print(f"Confidence: {result['confidence']:.2f}")
            print(f"Reasoning: {result['reasoning']}")
            print(f"Retriever method: {classifier.get_query_mapping(result['intent'])}")
        
        print("\n" + "=" * 80)
        print("✓ LLM CLASSIFIER TEST COMPLETED")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n✗ LLM classifier failed: {str(e)}")
        print("\nThis is likely due to:")
        print("1. Missing HUGGINGFACE_API_KEY in .env file")
        print("2. Rate limiting on free tier")
        print("3. Model not available")
        print("\nFalling back to Simple Classifier for remaining tests...")
        
        # Fallback to simple classifier
        simple_classifier = SimpleIntentClassifier()
        for query in test_queries:
            result = simple_classifier.classify(query)
            print(f"\nQuery: {query}")
            print(f"  → {result['intent'].value} (confidence: {result['confidence']:.2f})")


if __name__ == "__main__":
    test_intent_classifier()
