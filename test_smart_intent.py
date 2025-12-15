"""
Quick test for Smart Hybrid Intent Classifier
"""

from src.preprocessing.intent_classifier import HybridIntentClassifier, SimpleIntentClassifier


def main():
    print("\n" + "="*80)
    print("SMART HYBRID INTENT CLASSIFIER - QUICK TEST")
    print("="*80)
    
    # Initialize classifiers
    print("\n⏳ Initializing classifiers...")
    simple = SimpleIntentClassifier()
    hybrid = HybridIntentClassifier(confidence_threshold=0.85)
    
    # Test queries
    queries = [
        # Clear queries - rules should handle these
        ("Who are the top scorers?", "CLEAR - Rules confident"),
        ("Compare Haaland and Kane", "CLEAR - Rules confident"),
        
        # Ambiguous queries - LLM should help
        ("Best players this season", "AMBIGUOUS - Best at what?"),
        ("Show me the stars", "VAGUE - Needs context understanding"),
        ("Who's performing well?", "UNCLEAR - Form or top performers?"),
    ]
    
    for query, description in queries:
        print(f"\n{'='*80}")
        print(f"Query: '{query}'")
        print(f"Type: {description}")
        print("="*80)
        
        # Rule-based result
        rule_result = simple.classify(query)
        print(f"\n📋 RULE-BASED:")
        print(f"   Intent: {rule_result['intent'].value}")
        print(f"   Confidence: {rule_result['confidence']:.2f}")
        
        # Hybrid result
        print("\n🤖 SMART HYBRID:")
        hybrid_result = hybrid.classify(query)
        print(f"   Intent: {hybrid_result['intent'].value}")
        print(f"   Confidence: {hybrid_result['confidence']:.2f}")
        print(f"   Method: {hybrid_result.get('method', 'N/A')}")
        print(f"   LLM Used: {hybrid_result.get('llm_used', False)}")
        
        if hybrid_result.get('llm_used'):
            print(f"   💡 LLM was smart - handled uncertain case!")
            if 'rule_based_suggestion' in hybrid_result:
                print(f"      Rule suggested: {hybrid_result['rule_based_suggestion']['intent']}")
        else:
            print(f"   ⚡ Rules were confident - no LLM needed (fast!)")
    
    print("\n" + "="*80)
    print("✅ Test Complete!")
    print("="*80)


if __name__ == "__main__":
    main()
