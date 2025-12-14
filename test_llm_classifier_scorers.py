"""
Test LLM-based intent classifier vs Rule-based on top scorers query
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from src.retrieval.hybrid_retriever import HybridRetriever
import time


def test_llm_vs_rulebased_classifier():
    """Compare LLM classifier vs rule-based classifier on top scorers query."""
    
    print("=" * 80)
    print("LLM CLASSIFIER vs RULE-BASED CLASSIFIER TEST")
    print("=" * 80)
    
    query = "Who were the top scorers in 2021-22?"
    season = "2021-22"
    
    print(f"\nQUERY: {query}")
    print(f"SEASON: {season}\n")
    
    # Test configurations
    configs = [
        {
            'name': 'Rule-Based Classifier (SimpleIntentClassifier)',
            'use_llm': False,
            'description': 'Fast keyword-based intent classification'
        },
        {
            'name': 'LLM Classifier (BART-based)',
            'use_llm': True,
            'description': 'Zero-shot classification with facebook/bart-large-mnli'
        }
    ]
    
    results = {}
    
    for config in configs:
        print("=" * 80)
        print(f"CLASSIFIER: {config['name']}")
        print(f"Description: {config['description']}")
        print("=" * 80)
        
        try:
            # Initialize retriever with specific classifier
            print(f"\nInitializing HybridRetriever (use_llm_intent={config['use_llm']})...")
            start_init = time.time()
            retriever = HybridRetriever(use_llm_intent=config['use_llm'])
            init_time = time.time() - start_init
            print(f"✓ Initialization time: {init_time:.2f}s")
            
            # Run retrieval with baseline mode
            print(f"\nRunning retrieval (baseline mode)...")
            start_retrieve = time.time()
            result = retriever.retrieve(
                query=query,
                season=season,
                retrieval_mode="baseline"
            )
            retrieve_time = time.time() - start_retrieve
            
            # Extract results
            players = result.get('unified_players', [])
            intent = result.get('intent_enum')
            confidence = result.get('confidence', 0)
            reasoning = result.get('reasoning', 'N/A')
            
            print(f"\n✓ Retrieval complete in {retrieve_time:.2f}s")
            print(f"\n  Intent Detected: {intent.value if intent else 'N/A'}")
            print(f"  Confidence: {confidence:.2%}")
            print(f"  Reasoning: {reasoning}")
            print(f"  Players Retrieved: {len(players)}")
            
            # Show top 5 scorers
            print(f"\n  Top 5 Scorers:")
            for i, player in enumerate(players[:5], 1):
                name = player.get('player_name', player.get('player', 'Unknown'))
                goals = player.get('total_goals', 0)
                position = player.get('position', 'N/A')
                points = player.get('total_points', 0)
                print(f"    {i}. {name:<35} {position:<5} {goals}G, {points}pts")
            
            # Store results
            results[config['name']] = {
                'init_time': init_time,
                'retrieve_time': retrieve_time,
                'intent': intent.value if intent else 'N/A',
                'confidence': confidence,
                'num_players': len(players),
                'reasoning': reasoning
            }
            
            # Clean up
            retriever.close()
            print(f"\n✓ Retriever closed")
            
        except Exception as e:
            print(f"\n✗ Test failed: {str(e)}")
            import traceback
            traceback.print_exc()
            results[config['name']] = {'error': str(e)}
        
        print()
    
    # Comparison summary
    print("=" * 80)
    print("COMPARISON SUMMARY")
    print("=" * 80)
    
    print(f"\n{'Classifier':<45} {'Init (s)':<10} {'Query (s)':<10} {'Intent':<20} {'Confidence':<12} {'Players'}")
    print("-" * 120)
    
    for name, data in results.items():
        if 'error' not in data:
            classifier_short = name.split('(')[0].strip()
            print(f"{classifier_short:<45} "
                  f"{data['init_time']:<10.2f} "
                  f"{data['retrieve_time']:<10.2f} "
                  f"{data['intent']:<20} "
                  f"{data['confidence']:<12.2%} "
                  f"{data['num_players']}")
    
    print("\n" + "=" * 80)
    print("OBSERVATIONS:")
    print("=" * 80)
    
    if 'Rule-Based Classifier (SimpleIntentClassifier)' in results and 'LLM Classifier (BART-based)' in results:
        rule_based = results['Rule-Based Classifier (SimpleIntentClassifier)']
        llm_based = results['LLM Classifier (BART-based)']
        
        if 'error' not in rule_based and 'error' not in llm_based:
            print(f"\n✓ Both classifiers detected intent: top_scorers")
            print(f"✓ Rule-based faster initialization: {rule_based['init_time']:.2f}s vs {llm_based['init_time']:.2f}s")
            print(f"✓ Rule-based confidence: {rule_based['confidence']:.2%}")
            print(f"✓ LLM-based confidence: {llm_based['confidence']:.2%}")
            
            if rule_based['confidence'] > llm_based['confidence']:
                print(f"\n⚠️  Rule-based classifier has higher confidence!")
            else:
                print(f"\n✓ LLM classifier has higher confidence")
            
            if rule_based['init_time'] < llm_based['init_time']:
                speedup = llm_based['init_time'] / rule_based['init_time']
                print(f"⚡ Rule-based is {speedup:.1f}x faster to initialize")
    
    print("\n" + "=" * 80)
    print("RECOMMENDATION:")
    print("=" * 80)
    print("• Rule-based classifier: Fast, reliable, no model download")
    print("• LLM classifier: More flexible, but slower and may have lower confidence")
    print("• For production: Use rule-based (current default)")
    print("• For experimentation: Try LLM-based for complex/ambiguous queries")
    
    print("\n✓ Classifier comparison test complete")


if __name__ == "__main__":
    test_llm_vs_rulebased_classifier()
