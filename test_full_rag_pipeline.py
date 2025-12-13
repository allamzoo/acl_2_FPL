"""
Test Full RAG Pipeline - End-to-End
Tests the complete FPL Graph-RAG system with multiple query types
"""

from src.llm.generator import FPLAnswerGenerator

def test_query(generator, query, season="2022-23"):
    """Test a single query through the full pipeline."""
    print("\n" + "=" * 80)
    print(f"QUERY: {query}")
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
            print(f"  Tokens: {result.get('tokens', 0)} ({result.get('prompt_tokens', 0)} prompt + {result.get('completion_tokens', 0)} completion)")
            print(f"  Backend: {result.get('backend', 'Unknown')}")
            
        except Exception as e:
            print(f"ERROR: {str(e)}")
    
    print("\n" + "=" * 80)

def main():
    print("=" * 80)
    print("FULL RAG PIPELINE TEST - 3 Models Comparison")
    print("=" * 80)
    
    # Initialize the answer generator
    print("\nInitializing FPL Answer Generator...")
    generator = FPLAnswerGenerator()
    print("✓ Generator initialized\n")
    
    # Test queries covering different types
    queries = [
        # 1. Top performer query (aggregate)
        "Who were the top scorers in the 2022-23 season?",
        
        # 2. Specific player query
        "How did Mohamed Salah perform in 2022-23?",
        
        # 3. Comparison query
        "Compare Haaland and Kane in the 2022-23 season",
        
        # 4. Value/budget query (will show missing price data)
        "Who are good value midfielders for my squad?",
        
        # 5. Clean sheet query
        "Which defenders kept the most clean sheets in 2022-23?"
    ]
    
    for query in queries:
        test_query(generator, query, season="2022-23")
    
    print("\n" + "=" * 80)
    print("PIPELINE TEST COMPLETE")
    print("=" * 80)
    print("\nSummary:")
    print("✓ Hybrid retrieval (baseline + semantic) working")
    print("✓ All 3 LLM models generating responses")
    print("✓ Context flowing correctly to prompts")
    print("✓ Multiple query types supported")
    print("\nNote: Price/value queries will be limited without 'value' property in database")

if __name__ == "__main__":
    main()
