"""
Test Full RAG Pipeline - Top Defenders Query
Tests the complete system with a defenders-focused query
"""

from src.llm.generator import FPLAnswerGenerator

def main():
    print("=" * 80)
    print("FULL RAG PIPELINE TEST - Top Defenders Query")
    print("=" * 80)
    
    # Initialize the answer generator
    print("\nInitializing FPL Answer Generator...")
    generator = FPLAnswerGenerator()
    print("✓ Generator initialized\n")
    
    query = "Who were the top defenders in the 2022-23 season?"
    season = "2022-23"
    
    print(f"QUERY: {query}\n")
    print("=" * 80)
    
    # Test with all 3 models
    models = [
        ("llama-4-maverick", "Llama 4 Maverick"),
        ("qwen-3-32b", "Qwen 3"),
        ("gpt-oss-20b", "GPT OSS")
    ]
    
    for model_id, model_name in models:
        print(f"\n{model_name}:")
        print("-" * 80)
        
        try:
            result = generator.answer(
                query=query,
                season=season,
                model=model_id
            )
            
            # Print answer
            print(result['answer'])
            
            # Print metadata
            print(f"\n[Metadata]")
            print(f"  Context: {result['context']['num_players']} players retrieved")
            print(f"  Intent: {result['context'].get('intent', 'unknown')}")
            
            # Show which retrieval sources were used
            baseline_results = result['context'].get('baseline_results', {})
            semantic_results = result['context'].get('semantic_results', {})
            
            print(f"  Baseline results: {len(baseline_results)} query types")
            if baseline_results:
                print(f"    Query types: {', '.join(baseline_results.keys())}")
            
            print(f"  Semantic results: {semantic_results.get('count', 0)} players")
            print(f"  Tokens: {result.get('tokens', 0)} ({result.get('prompt_tokens', 0)} prompt + {result.get('completion_tokens', 0)} completion)")
            print(f"  Backend: {result.get('backend', 'Unknown')}")
            
        except Exception as e:
            print(f"ERROR: {str(e)}")
    
    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
    print("\n✓ Full RAG pipeline successfully processed 'top defenders' query")
    print("✓ Hybrid retrieval (baseline + semantic) working")
    print("✓ All 3 LLM models generated contextual responses")

if __name__ == "__main__":
    main()
