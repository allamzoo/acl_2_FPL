"""
Test Context-Aware Follow-up Handler

Demonstrates conversation context and smart follow-up resolution.
"""

from src.preprocessing.context_handler import ContextAwareFollowupHandler


def test_followup_detection():
    """Test follow-up query detection."""
    
    print("\n" + "="*80)
    print("FOLLOW-UP DETECTION TEST")
    print("="*80)
    
    handler = ContextAwareFollowupHandler(use_llm=False)
    
    test_queries = [
        ("Who are the top scorers?", False),
        ("What about defenders?", True),
        ("Show me Arsenal players", False),
        ("And Liverpool?", True),
        ("Compare Haaland and Kane", False),
        ("Who's better?", True),
        ("them", True),
        ("more", True),
        ("best", True),
    ]
    
    for query, expected in test_queries:
        is_followup = handler.is_followup_query(query)
        status = "✅" if is_followup == expected else "❌"
        print(f"{status} '{query}' → Follow-up: {is_followup} (expected: {expected})")


def test_context_resolution():
    """Test context-aware query resolution."""
    
    print("\n" + "="*80)
    print("CONTEXT RESOLUTION TEST")
    print("="*80)
    
    handler = ContextAwareFollowupHandler()
    
    # Conversation 1: Position-based follow-up
    print("\n📖 Conversation 1: Position Follow-up")
    print("-" * 80)
    
    query1 = "Who are the top scorers?"
    handler.add_to_history(
        query=query1,
        intent="top_scorers",
        entities={"positions": ["FWD"]},
        response_summary="Haaland leads with 36 goals..."
    )
    print(f"User: {query1}")
    print(f"[Added to context: intent=top_scorers, positions=FWD]")
    
    query2 = "What about defenders?"
    result = handler.resolve_context(query2)
    print(f"\nUser: {query2}")
    print(f"✨ Resolved: {result['resolved_query']}")
    print(f"   Is follow-up: {result['is_followup']}")
    print(f"   Method: {result.get('method', 'N/A')}")
    
    # Conversation 2: Team-based follow-up
    print("\n\n📖 Conversation 2: Team Follow-up")
    print("-" * 80)
    
    handler.clear_history()
    
    query1 = "Show me Arsenal players"
    handler.add_to_history(
        query=query1,
        intent="team_analysis",
        entities={"teams": ["Arsenal"]},
        response_summary="Arsenal has 25 players..."
    )
    print(f"User: {query1}")
    print(f"[Added to context: intent=team_analysis, teams=Arsenal]")
    
    query2 = "And Liverpool?"
    result = handler.resolve_context(query2)
    print(f"\nUser: {query2}")
    print(f"✨ Resolved: {result['resolved_query']}")
    print(f"   Is follow-up: {result['is_followup']}")
    print(f"   Method: {result.get('method', 'N/A')}")
    
    # Conversation 3: Comparison follow-up
    print("\n\n📖 Conversation 3: Comparison Follow-up")
    print("-" * 80)
    
    handler.clear_history()
    
    query1 = "Compare Haaland and Kane"
    handler.add_to_history(
        query=query1,
        intent="player_comparison",
        entities={"players": ["Haaland", "Kane"]},
        response_summary="Both are excellent strikers..."
    )
    print(f"User: {query1}")
    print(f"[Added to context: intent=player_comparison, players=Haaland, Kane]")
    
    query2 = "Who scored more?"
    result = handler.resolve_context(query2)
    print(f"\nUser: {query2}")
    print(f"✨ Resolved: {result['resolved_query']}")
    print(f"   Is follow-up: {result['is_followup']}")
    print(f"   Method: {result.get('method', 'N/A')}")
    
    # Conversation 4: Multiple follow-ups
    print("\n\n📖 Conversation 4: Multiple Follow-ups")
    print("-" * 80)
    
    handler.clear_history()
    
    conversations = [
        ("Who are the top scorers?", "top_scorers", {"positions": ["FWD"]}),
        ("What about midfielders?", "top_scorers", {"positions": ["MID"]}),
        ("And their assists?", "top_assisters", {"positions": ["MID"]}),
    ]
    
    for i, (query, intent, entities) in enumerate(conversations, 1):
        print(f"\n{i}. User: {query}")
        
        if i > 1:
            result = handler.resolve_context(query)
            if result['is_followup']:
                print(f"   💬 Resolved: {result['resolved_query']}")
        
        handler.add_to_history(
            query=query,
            intent=intent,
            entities=entities
        )


def test_conversation_history():
    """Test conversation history management."""
    
    print("\n\n" + "="*80)
    print("CONVERSATION HISTORY TEST")
    print("="*80)
    
    handler = ContextAwareFollowupHandler(max_history=3)
    
    # Add multiple queries
    queries = [
        ("Who are the top scorers?", "top_scorers"),
        ("Show me Arsenal players", "team_analysis"),
        ("Compare Haaland and Kane", "player_comparison"),
        ("What about defenders?", "top_scorers"),
        ("And Liverpool?", "team_analysis"),
    ]
    
    print(f"\nMax history size: {handler.max_history}")
    print("-" * 80)
    
    for i, (query, intent) in enumerate(queries, 1):
        handler.add_to_history(
            query=query,
            intent=intent,
            entities={}
        )
        
        print(f"\n{i}. Added: '{query}'")
        print(f"   History size: {len(handler.history)}")
        print(f"   Queries in history:")
        for j, ctx in enumerate(handler.history, 1):
            print(f"      {j}. {ctx.query}")


def test_smart_llm_resolution():
    """Test LLM-based context resolution."""
    
    print("\n\n" + "="*80)
    print("SMART LLM RESOLUTION TEST")
    print("="*80)
    
    handler = ContextAwareFollowupHandler(use_llm=True)
    
    if not handler.use_llm:
        print("⚠️ LLM not available, skipping smart resolution test")
        return
    
    # Test complex follow-ups that need LLM
    print("\n📖 Complex Follow-up Scenarios")
    print("-" * 80)
    
    # Scenario 1: Vague reference
    handler.clear_history()
    handler.add_to_history(
        query="Who are the top goal scorers in the Premier League?",
        intent="top_scorers",
        entities={"positions": ["FWD"], "stats": ["goals"]},
    )
    
    query = "What about the playmakers?"
    print(f"\nUser: {query}")
    result = handler.resolve_context(query)
    print(f"✨ Resolved: {result['resolved_query']}")
    print(f"   Method: {result.get('method', 'N/A')}")
    
    # Scenario 2: Pronoun reference
    handler.clear_history()
    handler.add_to_history(
        query="Compare Salah and Haaland in 2023-24",
        intent="player_comparison",
        entities={"players": ["Salah", "Haaland"], "seasons": ["2023-24"]},
    )
    
    query = "Who is faster?"
    print(f"\nUser: {query}")
    result = handler.resolve_context(query)
    print(f"✨ Resolved: {result['resolved_query']}")
    print(f"   Method: {result.get('method', 'N/A')}")


if __name__ == "__main__":
    test_followup_detection()
    test_context_resolution()
    test_conversation_history()
    test_smart_llm_resolution()
    
    print("\n\n" + "="*80)
    print("✅ All Context Handler Tests Complete!")
    print("="*80)
