"""
Test 3 Retrieval Modes with 3 LLMs
Compares: baseline-only, baseline+embedding1, baseline+embedding2
"""

from src.llm.generator import FPLAnswerGenerator

def main():
    print("=" * 80)
    print("RETRIEVAL MODE COMPARISON TEST")
    print("=" * 80)
    
    # Initialize generator
    print("\nInitializing FPL Answer Generator...")
    generator = FPLAnswerGenerator()
    print("✓ Generator initialized\n")
    
    query = "Who were the top scorers in 2022-23?"
    season = "2022-23"
    
    print(f"QUERY: {query}\n")
    
    # Test 3 retrieval modes
    modes = [
        ("baseline", "Baseline Only (No Embeddings)"),
        ("baseline+embedding1", "Baseline + Embedding Model 1"),
        ("baseline+embedding2", "Baseline + Embedding Model 2")
    ]
    
    # Test 3 LLMs
    llms = [
        ("llama-4-maverick", "🦙 Llama 4"),
        ("qwen-3-32b", "🤖 Qwen 3"),
        ("gpt-oss-20b", "🔷 GPT OSS")
    ]
    
    for mode_id, mode_name in modes:
        print("\n" + "=" * 80)
        print(f"MODE: {mode_name}")
        print("=" * 80)
        
        for llm_id, llm_name in llms:
            print(f"\n{llm_name}:")
            print("-" * 80)
            
            try:
                result = generator.answer(
                    query=query,
                    season=season,
                    model=llm_id,
                    retrieval_mode=mode_id
                )
                
                # Print answer
                print(result['answer'][:500] + "..." if len(result['answer']) > 500 else result['answer'])
                
                # Print metadata
                print(f"\n[Metadata]")
                print(f"  Retrieval Mode: {result['context'].get('retrieval_mode', 'unknown')}")
                print(f"  Players Retrieved: {result['context']['num_players']}")
                
                baseline_results = result['context'].get('baseline_results', {})
                semantic_results = result['context'].get('semantic_results', {})
                
                print(f"  Baseline Queries: {len(baseline_results)}")
                print(f"  Semantic Players: {semantic_results.get('count', 0)}")
                print(f"  Tokens: {result.get('tokens', 0)}")
                
            except Exception as e:
                print(f"ERROR: {str(e)}")
    
    print("\n" + "=" * 80)
    print("✓ COMPARISON TEST COMPLETE")
    print("=" * 80)
    print("Summary:")
    print("  Mode 1 (baseline): Uses only Cypher queries")
    print("  Mode 2 (baseline+embedding1): Merges baseline with embedding (70% stats, 30% text)")
    print("  Mode 3 (baseline+embedding2): Merges baseline with embedding (50% stats, 50% text)")
    print("  Both embedding modes use all-mpnet-base-v2 with different weighting strategies")

if __name__ == "__main__":
    main()
