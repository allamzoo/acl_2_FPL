"""
Test Structured Prompt Builder - Persona + Context + Task
"""

from src.retrieval.hybrid_retriever import HybridRetriever
from src.llm.prompts import FPLPromptBuilder, build_fpl_prompt


def test_prompt_structure():
    """Test the structured prompt builder with real KG context."""
    
    print("=" * 100)
    print("TESTING STRUCTURED PROMPT BUILDER")
    print("Structure: PERSONA + CONTEXT + TASK")
    print("=" * 100)
    
    # Initialize retriever
    retriever = HybridRetriever(
        embedding_model="all-mpnet-base-v2",
        use_hybrid_embeddings=True
    )
    
    # Test queries with different task types
    test_cases = [
        {
            "query": "Who are the best attacking midfielders with high creativity?",
            "task": "answer",
            "season": "2022-23"
        },
        {
            "query": "Recommend cheap defenders under 5 million for my FPL team",
            "task": "recommend",
            "season": "2022-23"
        },
        {
            "query": "Compare Mohamed Salah and Kevin De Bruyne",
            "task": "compare",
            "season": "2022-23"
        }
    ]
    
    try:
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{'#' * 100}")
            print(f"TEST CASE {i}: {test_case['task'].upper()} TASK")
            print(f"Query: {test_case['query']}")
            print(f"{'#' * 100}\n")
            
            # Retrieve context from Knowledge Graph
            print("Step 1: Retrieving context from Knowledge Graph...")
            context = retriever.retrieve(test_case['query'], test_case['season'])
            print(f"✓ Retrieved {len(context.get('unified_players', []))} relevant players\n")
            
            # Build structured prompt
            print("Step 2: Building structured prompt...\n")
            prompt = build_fpl_prompt(
                query=test_case['query'],
                context=context,
                task=test_case['task']
            )
            
            # Display the prompt
            print("=" * 100)
            print("GENERATED PROMPT (Ready for LLM)")
            print("=" * 100)
            print(prompt)
            print("\n" + "=" * 100)
            print(f"Prompt Length: {len(prompt)} characters")
            print("=" * 100)
            
            # Show structure breakdown
            print("\n📋 PROMPT STRUCTURE BREAKDOWN:")
            print(f"   ✓ PERSONA: FPL Expert role defined")
            print(f"   ✓ CONTEXT: {len(context.get('unified_players', []))} players with stats")
            print(f"   ✓ TASK: {test_case['task'].capitalize()} instructions included")
            print(f"   ✓ USER QUERY: '{test_case['query']}'")
            
            if i < len(test_cases):
                input("\nPress Enter to see next test case...")
    
    finally:
        retriever.close()
    
    print("\n" + "=" * 100)
    print("✓ PROMPT STRUCTURE TESTS COMPLETED")
    print("=" * 100)
    print("\nKey Features:")
    print("  • PERSONA: Defines FPL expert role and expertise")
    print("  • CONTEXT: Retrieved KG data (nodes, relationships, statistics)")
    print("  • TASK: Clear instructions to prevent hallucinations")
    print("\nThis structured approach grounds the LLM in actual data and reduces hallucinations!")


def test_prompt_components():
    """Test individual prompt components."""
    
    print("\n" + "=" * 100)
    print("TESTING INDIVIDUAL PROMPT COMPONENTS")
    print("=" * 100)
    
    # Show persona
    print("\n" + "=" * 80)
    print("1. PERSONA COMPONENT")
    print("=" * 80)
    print(FPLPromptBuilder.FPL_EXPERT_PERSONA)
    
    # Show task templates
    print("\n" + "=" * 80)
    print("2. TASK TEMPLATES")
    print("=" * 80)
    print("\nAvailable task types:")
    print("  • answer: General question answering")
    print("  • recommend: Player recommendations")
    print("  • compare: Player comparisons")
    print("  • explain: Statistical explanations")
    
    print("\n" + "=" * 80)
    print("Sample ANSWER task template:")
    print("=" * 80)
    print(FPLPromptBuilder.TASK_ANSWER_QUESTION.format(query="[User's question here]"))
    
    print("\n" + "=" * 80)
    print("✓ Component tests completed")
    print("=" * 80)


if __name__ == "__main__":
    # Test individual components first
    test_prompt_components()
    
    input("\nPress Enter to test full prompt generation with real KG data...")
    
    # Test full prompt generation
    test_prompt_structure()
