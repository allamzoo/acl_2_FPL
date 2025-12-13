"""
Test Full RAG Pipeline - Single Custom Query
Interactive test for any query
"""

from src.llm.generator import FPLAnswerGenerator

def main():
    print("=" * 80)
    print("FULL RAG PIPELINE - SINGLE QUERY TEST")
    print("=" * 80)
    
    # Initialize the answer generator
    print("\nInitializing FPL Answer Generator...")
    generator = FPLAnswerGenerator()
    print("✓ Generator initialized\n")
    
    # Test query
    query = "Which midfielder had the best assists in 2022-23?"
    season = "2022-23"
    
    print(f"QUERY: {query}")
    print(f"SEASON: {season}\n")
    print("=" * 80)
    
    # Test with all 3 models
    models = [
        ("llama-4-maverick", "🦙 Llama 4 Maverick"),
        ("qwen-3-32b", "🤖 Qwen 3"),
        ("gpt-oss-20b", "🔷 GPT OSS")
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
            print(f"  Players Retrieved: {result['context']['num_players']}")
            print(f"  Intent: {result['context'].get('intent', 'unknown')}")
            
            # Show retrieval breakdown
            baseline_results = result['context'].get('baseline_results', {})
            semantic_results = result['context'].get('semantic_results', {})
            
            if baseline_results:
                print(f"  Baseline Queries: {', '.join(baseline_results.keys())}")
            
            if semantic_results:
                print(f"  Semantic Matches: {semantic_results.get('count', 0)} players")
            
            print(f"  Tokens: {result.get('tokens', 0)} (prompt: {result.get('prompt_tokens', 0)}, completion: {result.get('completion_tokens', 0)})")
            print(f"  Backend: {result.get('backend', 'Unknown')}")
            
        except Exception as e:
            print(f"ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("✓ PIPELINE TEST COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()
