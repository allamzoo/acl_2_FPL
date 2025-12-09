"""
Visual Demonstration: Structured Prompt Components
Shows how PERSONA + CONTEXT + TASK work together
"""

from src.retrieval.hybrid_retriever import HybridRetriever
from src.llm.prompts import FPLPromptBuilder


def demonstrate_prompt_components():
    """
    Visual demonstration of the three-component structure:
    1. PERSONA - Defines the assistant's role
    2. CONTEXT - Retrieved Knowledge Graph information
    3. TASK - Clear instructions on what to do
    """
    
    print("=" * 100)
    print("STRUCTURED PROMPT DEMONSTRATION")
    print("Three-Component Architecture: PERSONA → CONTEXT → TASK")
    print("=" * 100)
    
    # Initialize retriever
    retriever = HybridRetriever(embedding_model="all-mpnet-base-v2", use_hybrid_embeddings=True)
    
    # Example query
    query = "Who are the top goalscorers?"
    season = "2022-23"
    
    print(f"\nUser Query: '{query}'")
    print(f"Season: {season}\n")
    
    # Retrieve context
    print("Step 1: Retrieving Knowledge Graph data...")
    context = retriever.retrieve(query, season)
    print(f"✓ Retrieved {len(context.get('unified_players', []))} relevant players\n")
    
    # =====================================================================
    # COMPONENT 1: PERSONA
    # =====================================================================
    print("\n" + "🎭 " + "=" * 95)
    print("COMPONENT 1: PERSONA (Defines the assistant's role)")
    print("=" * 100)
    print("\nPurpose: Establishes who the AI is and what expertise it has")
    print("Effect: Sets expectations for expert-level, domain-specific advice\n")
    print("-" * 100)
    print(FPLPromptBuilder.FPL_EXPERT_PERSONA)
    print("-" * 100)
    print("\n✅ Why this matters:")
    print("   • Defines the AI as an 'FPL expert' (not generic chatbot)")
    print("   • Lists specific expertise areas (player analysis, statistics, strategy)")
    print("   • Sets tone: 'accurate, data-driven advice'")
    print("   • Explicitly states: 'based solely on information provided'")
    
    input("\nPress Enter to see COMPONENT 2: CONTEXT...")
    
    # =====================================================================
    # COMPONENT 2: CONTEXT
    # =====================================================================
    print("\n" + "📊 " + "=" * 95)
    print("COMPONENT 2: CONTEXT (Retrieved Knowledge Graph Information)")
    print("=" * 100)
    print("\nPurpose: Provides factual, structured data from Neo4j database")
    print("Effect: Grounds the LLM in actual data, prevents hallucinations\n")
    print("-" * 100)
    
    formatted_context = FPLPromptBuilder.format_context(context)
    print(formatted_context)
    
    print("\n✅ Why this matters:")
    print("   • All data comes from Neo4j Knowledge Graph (not LLM's training data)")
    print("   • Shows player nodes with relationships (played_in season, statistics)")
    print("   • Includes relevance scores from hybrid retrieval (Cypher + embeddings)")
    print("   • Source tags show data origin: [baseline], [semantic], or [hybrid]")
    print("   • Structured format makes it easy for LLM to parse and use")
    
    print("\n📈 Context Data Breakdown:")
    unified = context.get('unified_players', [])
    baseline = context.get('baseline_results', {})
    semantic = context.get('semantic_results', {})
    
    print(f"   • Unified Players: {len(unified)} (deduplicated from both methods)")
    print(f"   • Baseline Results: {len([k for k,v in baseline.items() if v])} query types")
    print(f"   • Semantic Results: {len(semantic.get('players', []))} similar players")
    print(f"   • Data includes: goals, assists, points, ICT, clean sheets, etc.")
    
    input("\nPress Enter to see COMPONENT 3: TASK...")
    
    # =====================================================================
    # COMPONENT 3: TASK
    # =====================================================================
    print("\n" + "📝 " + "=" * 95)
    print("COMPONENT 3: TASK (Clear instructions on what to do)")
    print("=" * 100)
    print("\nPurpose: Explicitly tells the LLM how to use the context")
    print("Effect: Reduces hallucinations by setting strict boundaries\n")
    print("-" * 100)
    
    # Show the answer task (most common)
    task_instruction = FPLPromptBuilder.TASK_ANSWER_QUESTION.format(query=query)
    print(task_instruction)
    print("-" * 100)
    
    print("\n✅ Why this matters:")
    print("   • Explicit constraint: 'using ONLY the information provided'")
    print("   • Clear fallback: 'If context does NOT contain info, say so clearly'")
    print("   • Multiple safeguards: 'Do NOT make up information', 'Do NOT hallucinate'")
    print("   • Requires citations: 'Cite specific statistics to support your answer'")
    print("   • Defines output style: 'Be concise but informative'")
    
    print("\n📋 Available Task Types:")
    print("   1. 'answer'    - General question answering (default)")
    print("   2. 'recommend' - Player recommendations with justification")
    print("   3. 'compare'   - Structured player comparisons")
    print("   4. 'explain'   - Statistical explanations")
    
    input("\nPress Enter to see FULL ASSEMBLED PROMPT...")
    
    # =====================================================================
    # FULL PROMPT ASSEMBLY
    # =====================================================================
    print("\n" + "🔗 " + "=" * 95)
    print("FULL ASSEMBLED PROMPT (All 3 Components Together)")
    print("=" * 100)
    print("\nThis is what actually gets sent to the LLM:\n")
    print("=" * 100)
    
    full_prompt = FPLPromptBuilder.build_prompt(query, context, task_type="answer")
    print(full_prompt)
    
    print("\n" + "=" * 100)
    print("PROMPT STATISTICS")
    print("=" * 100)
    print(f"Total Length: {len(full_prompt)} characters")
    print(f"Approx Tokens: ~{len(full_prompt) // 4} tokens (rough estimate)")
    
    # Count sections
    persona_length = len(FPLPromptBuilder.FPL_EXPERT_PERSONA)
    context_length = len(formatted_context)
    task_length = len(task_instruction)
    
    print(f"\nComponent Breakdown:")
    print(f"  • PERSONA:  {persona_length:5d} chars ({persona_length/len(full_prompt)*100:5.1f}%)")
    print(f"  • CONTEXT:  {context_length:5d} chars ({context_length/len(full_prompt)*100:5.1f}%)")
    print(f"  • TASK:     {task_length:5d} chars ({task_length/len(full_prompt)*100:5.1f}%)")
    
    retriever.close()
    
    # =====================================================================
    # EXPLANATION SUMMARY
    # =====================================================================
    print("\n" + "=" * 100)
    print("WHY THIS STRUCTURE WORKS")
    print("=" * 100)
    
    print("""
┌─────────────────────────────────────────────────────────────────────────────┐
│ PROBLEM: LLMs can hallucinate (make up facts, invent statistics)           │
│ SOLUTION: Structured prompting with explicit grounding                      │
└─────────────────────────────────────────────────────────────────────────────┘

🎭 PERSONA Component:
   ✓ Establishes expert role ("FPL analyst")
   ✓ Lists specific knowledge areas
   ✓ Sets expectation: "based solely on information provided"
   
   WHY: Primes the LLM to think like a domain expert who relies on data

📊 CONTEXT Component:
   ✓ Provides factual KG data (nodes: players, relationships: played_in)
   ✓ Retrieved via hybrid method (Cypher queries + semantic embeddings)
   ✓ Structured format with clear labels
   
   WHY: Gives LLM actual facts to work with instead of relying on training data

📝 TASK Component:
   ✓ Explicit instructions: "ONLY use provided information"
   ✓ Multiple anti-hallucination safeguards
   ✓ Clear fallback if info missing
   ✓ Requires citations and evidence
   
   WHY: Creates strict boundaries on what LLM can/cannot say

┌─────────────────────────────────────────────────────────────────────────────┐
│ RESULT: LLM answers are grounded in Knowledge Graph data                   │
│         Hallucinations reduced by explicit constraints                      │
│         Answer quality improved by expert persona and clear instructions    │
└─────────────────────────────────────────────────────────────────────────────┘

📚 Research Backing:
   • Chain-of-Thought prompting improves reasoning
   • Role-based prompting (persona) improves domain responses
   • Retrieval-Augmented Generation (RAG) reduces hallucinations
   • Explicit constraints in instructions improve compliance
   
🎯 Our Implementation:
   ✅ PERSONA: FPL expert role (domain-specific)
   ✅ CONTEXT: KG-retrieved facts (RAG approach)
   ✅ TASK: Clear constraints ("ONLY use provided info")
   
   = High-quality, factual, non-hallucinated FPL advice!
""")
    
    print("=" * 100)
    print("✓ DEMONSTRATION COMPLETE")
    print("=" * 100)
    print("\nThe structured prompt system is ready for LLM integration!")
    print("Next step: Send these prompts to LLMs (GPT-4, Claude, Gemini, etc.)")


if __name__ == "__main__":
    demonstrate_prompt_components()
