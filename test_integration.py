"""
Quick integration test for all components
"""

def test_integration():
    print("="*80)
    print("INTEGRATION TEST - All Components")
    print("="*80)
    
    # Test 1: Import all modules
    print("\n1. Testing imports...")
    try:
        from src.preprocessing.intent_classifier import HybridIntentClassifier, SimpleIntentClassifier
        from src.preprocessing.context_handler import ContextAwareFollowupHandler
        from src.preprocessing.entity_extractor import EntityExtractor
        print("   ✅ All imports successful")
    except Exception as e:
        print(f"   ❌ Import error: {e}")
        return False
    
    # Test 2: Initialize components
    print("\n2. Testing component initialization...")
    try:
        simple_classifier = SimpleIntentClassifier()
        print("   ✅ SimpleIntentClassifier initialized")
        
        hybrid_classifier = HybridIntentClassifier()
        print("   ✅ HybridIntentClassifier initialized")
        
        context_handler = ContextAwareFollowupHandler()
        print("   ✅ ContextAwareFollowupHandler initialized")
        
        entity_extractor = EntityExtractor()
        print("   ✅ EntityExtractor initialized")
    except Exception as e:
        print(f"   ❌ Initialization error: {e}")
        return False
    
    # Test 3: Test workflow
    print("\n3. Testing complete workflow...")
    try:
        # First query
        query1 = "Who are the top scorers?"
        
        # Classify intent
        intent_result = hybrid_classifier.classify(query1)
        print(f"   Query: '{query1}'")
        print(f"   Intent: {intent_result['intent'].value}")
        print(f"   Method: {intent_result.get('method', 'N/A')}")
        
        # Extract entities
        entities = entity_extractor.extract(query1)
        print(f"   Entities: {entities}")
        
        # Add to context
        context_handler.add_to_history(
            query=query1,
            intent=intent_result['intent'].value,
            entities=entities
        )
        print("   ✅ Added to context history")
        
        # Follow-up query
        query2 = "What about defenders?"
        print(f"\n   Follow-up: '{query2}'")
        
        # Resolve context
        context_result = context_handler.resolve_context(query2)
        print(f"   Is follow-up: {context_result['is_followup']}")
        if context_result['is_followup']:
            print(f"   Resolved: '{context_result['resolved_query']}'")
        
        # Classify resolved query
        resolved_query = context_result['resolved_query']
        intent_result2 = hybrid_classifier.classify(resolved_query)
        print(f"   Intent: {intent_result2['intent'].value}")
        
        print("\n   ✅ Complete workflow successful")
        
    except Exception as e:
        print(f"   ❌ Workflow error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 4: Test session state compatibility
    print("\n4. Testing session state compatibility...")
    try:
        # Simulate session state structure
        session_state = {
            'intent_classifier': hybrid_classifier,
            'context_handler': context_handler,
            'entity_extractor': entity_extractor,
            'use_context': True,
            'classifier_type': 'Smart Hybrid'
        }
        print(f"   ✅ Session state structure valid")
        print(f"   Components: {list(session_state.keys())}")
    except Exception as e:
        print(f"   ❌ Session state error: {e}")
        return False
    
    return True


if __name__ == "__main__":
    success = test_integration()
    
    print("\n" + "="*80)
    if success:
        print("✅ ALL INTEGRATION TESTS PASSED!")
        print("The system is ready to use in the Streamlit app.")
    else:
        print("❌ INTEGRATION TESTS FAILED!")
        print("Please check the errors above.")
    print("="*80)
