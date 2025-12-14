"""
Context-Aware Follow-up Handler

Maintains conversation context and resolves follow-up queries intelligently.
Uses LLM to understand references and context from previous queries.
"""

from typing import Dict, Any, List, Optional
import logging
from dataclasses import dataclass, asdict
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class QueryContext:
    """Store context from a query."""
    query: str
    intent: str
    entities: Dict[str, Any]
    timestamp: datetime
    response_summary: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return data


class ContextAwareFollowupHandler:
    """
    Smart follow-up handler that maintains conversation context.
    
    Features:
    - Remembers last N queries and their context
    - Detects follow-up queries (pronouns, references, etc.)
    - Uses LLM to resolve ambiguous references
    - Enriches current query with previous context
    """
    
    def __init__(
        self,
        max_history: int = 5,
        use_llm: bool = True,
        model_name: str = "llama-4-maverick"
    ):
        """
        Initialize context handler.
        
        Args:
            max_history: Maximum number of queries to remember
            use_llm: Use LLM for smart context resolution
            model_name: LLM model for context resolution
        """
        self.max_history = max_history
        self.history: List[QueryContext] = []
        self.use_llm = use_llm
        self.model_name = model_name
        
        # Initialize LLM if enabled
        self.llm_manager = None
        if use_llm:
            try:
                from src.llm.models import create_llm_manager
                self.llm_manager = create_llm_manager(backend='groq')
                logger.info("Context handler initialized with LLM support")
            except Exception as e:
                logger.warning(f"LLM not available for context: {e}")
                self.use_llm = False
    
    def is_followup_query(self, query: str) -> bool:
        """
        Detect if query is a follow-up (contains references/pronouns).
        
        Args:
            query: User query
            
        Returns:
            True if likely a follow-up query
        """
        query_lower = query.lower().strip()
        
        # Quick check: if it starts with common question words, likely not a follow-up
        if query_lower.startswith(('who are', 'who is', 'what are', 'what is', 
                                    'show me', 'get me', 'find', 'list', 'display')):
            return False
        
        # But "who's better/faster/more" etc are follow-ups (comparisons without subjects)
        if query_lower.startswith('who') and any(word in query_lower for word in 
                                                   ['better', 'worse', 'faster', 'slower', 'more', 'less']):
            return True
        
        # Follow-up indicators
        followup_patterns = [
            # Direct references
            'what about', 'how about', 'and the', 'and their',
            'what if', 'also show', 'also get',
            # Anaphoric references
            'them', 'those', 'these', 'that', 'this',
            'his', 'her', 'their', 'theirs',
            # Conjunctions at start
            query_lower.startswith(('and ', 'but ', 'or ', 'also ')),
        ]
        
        # Check patterns
        for pattern in followup_patterns:
            if isinstance(pattern, str) and pattern in query_lower:
                return True
            elif isinstance(pattern, bool) and pattern:
                return True
        
        # Very short queries without question words are likely follow-ups
        if len(query_lower.split()) <= 2 and not query_lower.startswith(('who', 'what', 'where', 'when', 'why', 'how', 'show', 'get')):
            return True
        
        return False
    
    def resolve_context(self, query: str) -> Dict[str, Any]:
        """
        Resolve query context by enriching with previous conversation.
        
        Args:
            query: Current user query
            
        Returns:
            Dictionary with resolved query and context info
        """
        # If no history, return as-is
        if not self.history:
            return {
                "resolved_query": query,
                "is_followup": False,
                "original_query": query,
                "context_used": None
            }
        
        # Check if it's a follow-up
        is_followup = self.is_followup_query(query)
        
        if not is_followup:
            return {
                "resolved_query": query,
                "is_followup": False,
                "original_query": query,
                "context_used": None
            }
        
        # It's a follow-up - resolve with LLM
        if self.use_llm and self.llm_manager:
            resolved = self._llm_resolve_context(query)
            return {
                "resolved_query": resolved,
                "is_followup": True,
                "original_query": query,
                "context_used": self._get_recent_context_summary(),
                "method": "llm"
            }
        else:
            # Fallback: simple context concatenation
            resolved = self._simple_resolve_context(query)
            return {
                "resolved_query": resolved,
                "is_followup": True,
                "original_query": query,
                "context_used": self._get_recent_context_summary(),
                "method": "simple"
            }
    
    def _llm_resolve_context(self, query: str) -> str:
        """
        Use LLM to intelligently resolve query with context.
        
        Args:
            query: Current query with potential references
            
        Returns:
            Resolved standalone query
        """
        # Get recent conversation context
        context_summary = self._get_recent_context_summary()
        
        # Build prompt
        prompt = f"""You are helping resolve follow-up queries in a conversation about FPL (Fantasy Premier League).

Previous conversation:
{context_summary}

Current query: "{query}"

This query appears to be a follow-up that references the previous conversation. Rewrite it as a complete, standalone query that includes the necessary context from the conversation history.

Rules:
- Make the query self-contained (no pronouns or references)
- Keep the same intent and meaning
- Be concise but complete
- Use specific names, teams, positions mentioned in history

Respond with ONLY the rewritten query, nothing else."""

        try:
            result = self.llm_manager.generate(
                prompt=prompt,
                model=self.model_name,
                temperature=0.2,
                max_tokens=100
            )
            
            resolved_query = result.get('response', '').strip()
            
            # Validation: make sure it's not empty and different from original
            if resolved_query and resolved_query != query:
                logger.info(f"LLM resolved: '{query}' → '{resolved_query}'")
                return resolved_query
            else:
                logger.warning("LLM resolution failed, using fallback")
                return self._simple_resolve_context(query)
                
        except Exception as e:
            logger.error(f"LLM context resolution failed: {e}")
            return self._simple_resolve_context(query)
    
    def _simple_resolve_context(self, query: str) -> str:
        """
        Simple rule-based context resolution (fallback).
        
        Args:
            query: Current query
            
        Returns:
            Query with context prepended
        """
        if not self.history:
            return query
        
        # Get last query context
        last_context = self.history[-1]
        
        # Extract key entities from last query
        entities_str = ""
        if last_context.entities:
            players = last_context.entities.get('players', [])
            teams = last_context.entities.get('teams', [])
            positions = last_context.entities.get('positions', [])
            
            if players:
                entities_str += f" players: {', '.join(players)}"
            if teams:
                entities_str += f" team: {', '.join(teams)}"
            if positions:
                entities_str += f" position: {', '.join(positions)}"
        
        # Prepend context to query
        if entities_str:
            resolved = f"{query} (context:{entities_str})"
        else:
            resolved = f"{query} (related to: {last_context.query})"
        
        logger.info(f"Simple resolved: '{query}' → '{resolved}'")
        return resolved
    
    def _get_recent_context_summary(self) -> str:
        """Get summary of recent conversation context."""
        if not self.history:
            return "No previous conversation"
        
        # Get last 3 queries
        recent = self.history[-3:]
        
        summary_lines = []
        for i, ctx in enumerate(recent, 1):
            line = f"{i}. Query: \"{ctx.query}\"\n   Intent: {ctx.intent}"
            if ctx.entities:
                entities_parts = []
                if ctx.entities.get('players'):
                    entities_parts.append(f"Players: {', '.join(ctx.entities['players'])}")
                if ctx.entities.get('teams'):
                    entities_parts.append(f"Teams: {', '.join(ctx.entities['teams'])}")
                if ctx.entities.get('positions'):
                    entities_parts.append(f"Positions: {', '.join(ctx.entities['positions'])}")
                if entities_parts:
                    line += f"\n   Entities: {'; '.join(entities_parts)}"
            summary_lines.append(line)
        
        return "\n".join(summary_lines)
    
    def add_to_history(
        self,
        query: str,
        intent: str,
        entities: Dict[str, Any],
        response_summary: Optional[str] = None
    ):
        """
        Add query to conversation history.
        
        Args:
            query: User query
            intent: Classified intent
            entities: Extracted entities
            response_summary: Optional summary of response
        """
        context = QueryContext(
            query=query,
            intent=intent,
            entities=entities,
            timestamp=datetime.now(),
            response_summary=response_summary
        )
        
        self.history.append(context)
        
        # Maintain max history size
        if len(self.history) > self.max_history:
            self.history.pop(0)
        
        logger.info(f"Added to history: {query} (history size: {len(self.history)})")
    
    def clear_history(self):
        """Clear conversation history."""
        self.history.clear()
        logger.info("Conversation history cleared")
    
    def get_history(self) -> List[Dict[str, Any]]:
        """Get conversation history as list of dicts."""
        return [ctx.to_dict() for ctx in self.history]
    
    def get_last_context(self) -> Optional[QueryContext]:
        """Get the last query context."""
        return self.history[-1] if self.history else None
