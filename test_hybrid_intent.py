"""
Test Smart Hybrid Intent Classifier

Tests the smart agent that uses rules first, then LLM intelligence for hard cases.
"""

from src.preprocessing.intent_classifier import HybridIntentClassifier, SimpleIntentClassifier, Intent


def test_hybrid_classifier():
    """Test smart hybrid classifier with various queries."""
    
    print("=" * 80)
    print("SMART HYBRID INTENT CLASSIFIER TEST")
    print("Rules first (fast), LLM for uncertain cases (smart)")
    print("=" * 80)
    
    # Initialize classifiers
    hybrid = HybridIntentClassifier()
    simple = SimpleIntentClassifier()
    
    # Test queries - mix of clear and ambiguous
    test_queries = [
        # Clear queries - rules should be confident, LLM should agree
        "Who are the top scorers in the Premier League?",
        "Show me top 10 defenders by goals in 2023-24",
        "Compare Haaland and Kane",
        
        # Ambiguous queries - rules uncertain, LLM adds intelligence
        "Best players this season",  # Ambiguous - best at what?
        "Show me the stars",  # Very vague
        "Who's on fire?",  # Could be form or top performers
        "Arsenal's squad",  # Team analysis
        
        # Tricky queries - rules might misclassify
        "Players with more than 10 goals",  # High performers, not top scorers
        "How is Salah doing lately?",  # Form, not stats
        "Top players in gameweek 15",  # Gameweek, not season
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'=' * 80}")
        print(f"Query {i}: '{query}'")
        print("=" * 80)
        
        # Get rule-based result
        rule_result = simple.classify(query)
        print(f"\n📋 RULE-BASED SUGGESTION:")
        print(f"   Intent: {rule_result['intent'].value}")
        print(f"   Confidence: {rule_result['confidence']:.2f}")
        print(f"   Reasoning: {rule_result['reasoning']}")
        
        # Get hybrid result (LLM decision)
        hybrid_result = hybrid.classify(query)
        
        print(f"\n🤖 LLM DECISION:")
        print(f"   Intent: {hybrid_result['intent'].value}")
        print(f"   Confidence: {hybrid_result['confidence']:.2f}")
        print(f"   Method: {hybrid_result.get('method', 'N/A')}")
        
        if 'agrees_with_rules' in hybrid_result:
            if hybrid_result['agrees_with_rules']:
                print(f"   ✅ LLM AGREES with rule-based suggestion")
            else:
                print(f"   🔄 LLM OVERRIDES rule-based suggestion")
                print(f"      Rule suggested: {hybrid_result['rule_based_suggestion']['intent']}")
        
        if 'all_scores' in hybrid_result:
            print(f"\n   Top 3 LLM predictions:")
            for label, score in list(hybrid_result['all_scores'].items())[:3]:
                print(f"      {score:.2f} - {label}")


def test_rule_failures():
    """Test cases where rules fail and LLM should help."""
    
    print("\n\n" + "=" * 80)
    print("TESTING RULE-BASED FAILURES")
    print("Cases where rules are uncertain or wrong")
    print("=" * 80)
    
    hybrid = HybridIntentClassifier()
    
    # Queries where rules struggle
    tricky_queries = [
        ("Best midfielders", "Ambiguous - could be top scorers, assisters, or form"),
        ("Show me legends", "Vague - what makes a legend?"),
        ("Who should I pick?", "Complex FPL advice question"),
        ("Performance comparison between teams", "Team analysis vs comparison"),
        ("Recent hot players", "Form or gameweek performers?"),
    ]
    
    for query, description in tricky_queries:
        print(f"\n{'=' * 80}")
        print(f"Query: '{query}'")
        print(f"Challenge: {description}")
        print("=" * 80)
        
        result = hybrid.classify(query)
        
        print(f"\n🤖 LLM Classification:")
        print(f"   Intent: {result['intent'].value}")
        print(f"   Confidence: {result['confidence']:.2f}")
        
        if 'rule_based_suggestion' in result:
            rule_intent = result['rule_based_suggestion']['intent']
            rule_conf = result['rule_based_suggestion']['confidence']
            print(f"\n📋 Rule-based suggested: {rule_intent} (confidence: {rule_conf:.2f})")
            
            if result.get('agrees_with_rules'):
                print(f"   ✅ LLM agrees with rules")
            else:
                print(f"   🔄 LLM used deeper understanding to override")


if __name__ == "__main__":
    test_hybrid_classifier()
    test_rule_failures()
    
    print("\n\n" + "=" * 80)
    print("✅ Hybrid Intent Classifier Test Complete!")
    print("=" * 80)
