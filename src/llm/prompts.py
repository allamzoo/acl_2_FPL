"""
Prompt Templates Module

Structured prompts with context, persona, and task components.
This structured approach improves answer quality and reduces hallucinations
by explicitly grounding the LLM in the Knowledge Graph data.
"""

from typing import Dict, List, Any


class FPLPromptBuilder:
    """
    Builds structured prompts for FPL Graph-RAG system.
    
    Structure:
    1. PERSONA: Define the assistant's role and expertise
    2. CONTEXT: Retrieved KG information (nodes, relationships, data)
    3. TASK: Clear instructions on what to do with the context
    """
    
    # ==================== PERSONA ====================
    
    FPL_EXPERT_PERSONA = """You are an expert Fantasy Premier League (FPL) analyst with deep knowledge of player statistics, team dynamics, and FPL strategy.

Your expertise includes:
- Player performance analysis (goals, assists, points, form, consistency)
- Statistical insights (xG, xA, ICT index, bonus points, clean sheets)
- Positional analysis (GK, DEF, MID, FWD roles and requirements)
- Value assessment (budget constraints, price vs. performance)
- Team selection strategy (differentials, captains, enablers)
- Fixture analysis and gameweek planning

You provide accurate, data-driven advice based solely on the information provided to you."""
    
    # ==================== TASK TEMPLATES ====================
    
    TASK_ANSWER_QUESTION = """TASK: Answer the user's question using ONLY the information provided in the CONTEXT section above.

Instructions:
1. Base your answer exclusively on the provided player statistics and relationships
2. If the context contains relevant information, provide a detailed, helpful answer
3. Cite specific statistics (goals, assists, points, form) to support your answer
4. If the context does NOT contain enough information to answer the question, say so clearly
5. Do NOT make up information or use knowledge outside the provided context
6. Do NOT hallucinate player names, statistics, or facts not present in the context
7. Be concise but informative - include relevant numbers and comparisons

USER QUESTION: {query}

Your answer:"""

    TASK_RECOMMEND_PLAYERS = """TASK: Recommend players based on the user's criteria using ONLY the information in the CONTEXT section above.

Instructions:
1. Analyze the provided player data against the user's requirements
2. Rank players by relevance to the query (consider stats, position, value)
3. Provide your top 3-5 recommendations with justification
4. Include key statistics for each recommended player
5. Mention any trade-offs or considerations (price, form, fixtures)
6. If no players in the context match the criteria, explain why
7. Do NOT recommend players not present in the context

USER QUERY: {query}

Your recommendations:"""

    TASK_COMPARE_PLAYERS = """TASK: Compare the players mentioned in the user's question using ONLY the information in the CONTEXT section above.

Instructions:
1. Identify the players to compare from the context
2. Present a structured comparison covering relevant statistics
3. Highlight strengths and weaknesses of each player
4. Provide a clear conclusion on which player(s) perform better for specific criteria
5. If any player is missing from the context, state this clearly
6. Use actual numbers from the context to support your comparison
7. Consider multiple dimensions: attacking output, defensive contributions, consistency, value

USER QUERY: {query}

Your comparison:"""

    TASK_EXPLAIN_STATISTICS = """TASK: Explain the player statistics shown in the CONTEXT section above in response to the user's question.

Instructions:
1. Identify relevant statistics from the context
2. Provide clear explanations of what the numbers mean
3. Put statistics in context (e.g., per 90 minutes, season totals, percentiles)
4. Highlight notable patterns or trends in the data
5. Only discuss statistics that are present in the context
6. Help the user understand what the numbers tell us about player performance

USER QUERY: {query}

Your explanation:"""

    # ==================== CONTEXT FORMATTING ====================
    
    @staticmethod
    def format_context(retrieval_context: Dict[str, Any]) -> str:
        """
        Format retrieved KG information into structured context string.
        
        Args:
            retrieval_context: Dictionary containing baseline_results, 
                             semantic_results, and unified_players
                             
        Returns:
            Formatted context string for LLM prompt
        """
        context_parts = []
        
        context_parts.append("=" * 80)
        context_parts.append("CONTEXT: Retrieved Knowledge Graph Information")
        context_parts.append("=" * 80)
        
        # Add unified player results (deduplicated, merged data)
        unified = retrieval_context.get('unified_players', [])
        if unified:
            context_parts.append("\nPLAYER STATISTICS (ranked by relevance):")
            context_parts.append("-" * 80)
            
            for i, player in enumerate(unified[:15], 1):  # Top 15 most relevant
                name = player.get('player_name', 'Unknown')
                pos = player.get('position', 'N/A')
                source = player.get('source', 'unknown')
                sim = player.get('similarity_score', 0)
                
                # Extract statistics (handle different field names)
                goals = player.get('total_goals') or player.get('goals_scored') or player.get('goals', 0)
                assists = player.get('total_assists') or player.get('assists', 0)
                points = player.get('total_points', 0)
                minutes = player.get('minutes', 0)
                
                # Build player info string
                stats = [
                    f"{i}. {name} ({pos})",
                    f"   Goals: {goals}",
                    f"   Assists: {assists}",
                    f"   Total Points: {points}",
                ]
                
                # Add optional stats if available
                if minutes > 0:
                    stats.append(f"   Minutes Played: {minutes}")
                
                if 'goals_per_90' in player:
                    stats.append(f"   Goals per 90: {player['goals_per_90']:.2f}")
                if 'assists_per_90' in player:
                    stats.append(f"   Assists per 90: {player['assists_per_90']:.2f}")
                if 'points_per_game' in player:
                    stats.append(f"   Points per Game: {player['points_per_game']:.2f}")
                    
                if 'ict_index' in player:
                    stats.append(f"   ICT Index: {player['ict_index']:.1f}")
                if 'influence' in player:
                    stats.append(f"   Influence: {player['influence']:.1f}")
                if 'creativity' in player:
                    stats.append(f"   Creativity: {player['creativity']:.1f}")
                if 'threat' in player:
                    stats.append(f"   Threat: {player['threat']:.1f}")
                    
                if 'clean_sheets' in player:
                    stats.append(f"   Clean Sheets: {player['clean_sheets']}")
                if 'bonus' in player:
                    stats.append(f"   Bonus Points: {player['bonus']}")
                
                # Add source/relevance info
                if sim > 0:
                    stats.append(f"   Relevance Score: {sim:.3f} [Source: {source}]")
                else:
                    stats.append(f"   [Source: {source}]")
                    
                context_parts.append("\n".join(stats))
                context_parts.append("")
        
        # Add baseline query results if available
        baseline = retrieval_context.get('baseline_results', {})
        if baseline:
            context_parts.append("\nADDITIONAL STRUCTURED QUERY RESULTS:")
            context_parts.append("-" * 80)
            
            for key, value in baseline.items():
                if value and isinstance(value, list) and len(value) > 0:
                    context_parts.append(f"\n{key}:")
                    for item in value[:10]:  # Limit to top 10
                        context_parts.append(f"  {item}")
        
        context_parts.append("=" * 80)
        
        return "\n".join(context_parts)
    
    # ==================== FULL PROMPT ASSEMBLY ====================
    
    @classmethod
    def build_prompt(
        cls,
        query: str,
        retrieval_context: Dict[str, Any],
        task_type: str = "answer"
    ) -> str:
        """
        Build complete structured prompt with Persona + Context + Task.
        
        Args:
            query: User's question
            retrieval_context: Retrieved KG information from hybrid retriever
            task_type: Type of task - "answer", "recommend", "compare", "explain"
            
        Returns:
            Complete formatted prompt string
        """
        # Select appropriate task template
        task_templates = {
            "answer": cls.TASK_ANSWER_QUESTION,
            "recommend": cls.TASK_RECOMMEND_PLAYERS,
            "compare": cls.TASK_COMPARE_PLAYERS,
            "explain": cls.TASK_EXPLAIN_STATISTICS
        }
        
        task_template = task_templates.get(task_type, cls.TASK_ANSWER_QUESTION)
        
        # Assemble full prompt
        prompt_parts = [
            "=" * 80,
            "PERSONA",
            "=" * 80,
            cls.FPL_EXPERT_PERSONA,
            "",
            cls.format_context(retrieval_context),
            "",
            "=" * 80,
            task_template.format(query=query)
        ]
        
        return "\n".join(prompt_parts)
    
    @classmethod
    def build_simple_prompt(cls, query: str, retrieval_context: Dict[str, Any]) -> str:
        """
        Build simple QA prompt (most common use case).
        
        Args:
            query: User's question
            retrieval_context: Retrieved KG information
            
        Returns:
            Complete prompt for answering questions
        """
        return cls.build_prompt(query, retrieval_context, task_type="answer")


# Convenience function for quick access
def build_fpl_prompt(query: str, context: Dict[str, Any], task: str = "answer") -> str:
    """
    Build structured FPL prompt with persona, context, and task.
    
    Args:
        query: User's question
        context: Retrieved knowledge graph context
        task: Task type - "answer", "recommend", "compare", "explain"
        
    Returns:
        Formatted prompt string ready for LLM
    """
    return FPLPromptBuilder.build_prompt(query, context, task)

