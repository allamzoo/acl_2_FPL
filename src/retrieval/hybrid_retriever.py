"""
Hybrid Retrieval Module

Combines baseline Cypher queries with embedding-based semantic search
to provide comprehensive context for LLM generation.
"""

import logging
from typing import List, Dict, Any, Optional
from .baseline_retriever import BaselineRetriever
from .embedding_retriever import EmbeddingRetriever

logger = logging.getLogger(__name__)


class HybridRetriever:
    """
    Hybrid retriever that combines:
    1. Baseline Cypher queries (deterministic, structured)
    2. Embedding-based semantic search (flexible, similarity-based)
    """
    
    def __init__(self, 
                 embedding_model: str = "all-mpnet-base-v2",
                 use_hybrid_embeddings: bool = True,
                 top_k_semantic: int = 5):
        """
        Initialize hybrid retriever.
        
        Args:
            embedding_model: Model for semantic search
            use_hybrid_embeddings: Use numerical+text hybrid embeddings
            top_k_semantic: Number of semantic results to retrieve
        """
        self.baseline = BaselineRetriever()
        self.embedding = EmbeddingRetriever(
            model_name=embedding_model,
            use_hybrid=use_hybrid_embeddings
        )
        self.top_k = top_k_semantic
        
        logger.info(f"HybridRetriever initialized (model: {embedding_model}, "
                   f"hybrid_embeddings: {use_hybrid_embeddings})")
    
    def close(self):
        """Close all connections."""
        self.baseline.close()
        self.embedding.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    # =========================================================================
    # Intent-based Retrieval Routing
    # =========================================================================
    
    def _classify_query_intent(self, query: str) -> str:
        """
        Classify the query intent to determine retrieval strategy.
        
        Returns:
            'specific' - Looking for specific player/team/stat
            'semantic' - Similarity-based search
            'comparative' - Comparing players
            'aggregate' - Top scorers, rankings, etc.
        """
        query_lower = query.lower()
        
        # Specific entity lookups
        if any(word in query_lower for word in ['who is', 'show me', 'find', 'get stats']):
            return 'specific'
        
        # Comparative queries
        if any(word in query_lower for word in ['compare', 'vs', 'versus', 'better', 'difference']):
            return 'comparative'
        
        # Aggregate/ranking queries
        if any(word in query_lower for word in ['top', 'best', 'most', 'highest', 'leaders']):
            return 'aggregate'
        
        # Default to semantic for descriptive queries
        return 'semantic'
    
    def _extract_player_names(self, query: str) -> List[str]:
        """Extract potential player names from query."""
        # Simple heuristic: capitalized words that might be names
        words = query.split()
        potential_names = []
        
        for i, word in enumerate(words):
            if word and word[0].isupper() and word.lower() not in ['i', 'who', 'show', 'find', 'the']:
                # Check for multi-word names
                name_parts = [word]
                for j in range(i+1, min(i+3, len(words))):
                    if words[j] and words[j][0].isupper():
                        name_parts.append(words[j])
                    else:
                        break
                potential_names.append(' '.join(name_parts))
        
        return potential_names
    
    def _extract_position(self, query: str) -> Optional[str]:
        """Extract position filter from query."""
        query_lower = query.lower()
        
        position_map = {
            'goalkeeper': 'GK',
            'keeper': 'GK',
            'gk': 'GK',
            'defender': 'DEF',
            'defence': 'DEF',
            'def': 'DEF',
            'fullback': 'DEF',
            'midfielder': 'MID',
            'midfield': 'MID',
            'mid': 'MID',
            'forward': 'FWD',
            'striker': 'FWD',
            'fwd': 'FWD',
            'attacker': 'FWD'
        }
        
        for keyword, position in position_map.items():
            if keyword in query_lower:
                return position
        
        return None
    
    def _extract_team(self, query: str) -> Optional[str]:
        """Extract team name from query."""
        # Common FPL teams
        teams = [
            'Arsenal', 'Aston Villa', 'Brentford', 'Brighton', 'Burnley',
            'Chelsea', 'Crystal Palace', 'Everton', 'Leeds', 'Leicester',
            'Liverpool', 'Man City', 'Man Utd', 'Newcastle', 'Norwich',
            'Southampton', 'Spurs', 'Tottenham', 'Watford', 'West Ham', 'Wolves'
        ]
        
        query_lower = query.lower()
        for team in teams:
            if team.lower() in query_lower:
                return team
        
        return None
    
    # =========================================================================
    # Unified Retrieval Methods
    # =========================================================================
    
    def retrieve(self, query: str, season: str = "2021-22") -> Dict[str, Any]:
        """
        Main retrieval method that combines baseline and semantic approaches.
        Always runs BOTH methods then merges results.
        
        Args:
            query: Natural language query
            season: FPL season
            
        Returns:
            Unified context with results from both retrievers
        """
        intent = self._classify_query_intent(query)
        logger.info(f"Query intent: {intent} | Query: '{query}'")
        
        context = {
            'query': query,
            'season': season,
            'intent': intent,
            'baseline_results': {},
            'semantic_results': {},
            'unified_players': []
        }
        
        # ALWAYS run semantic search first
        logger.info("Running semantic embedding search...")
        semantic_results = self.embedding.semantic_search(query, top_k=10, season=season)
        context['semantic_results'] = semantic_results
        
        # ALWAYS run baseline query based on intent
        logger.info("Running baseline Cypher query...")
        if intent == 'specific':
            context = self._retrieve_baseline_specific(query, season, context)
        elif intent == 'comparative':
            context = self._retrieve_baseline_comparative(query, season, context)
        elif intent == 'aggregate':
            context = self._retrieve_baseline_aggregate(query, season, context)
        else:  # semantic - still get some baseline data
            context = self._retrieve_baseline_for_semantic(query, season, context)
        
        # Merge and deduplicate results
        logger.info("Merging and deduplicating results...")
        context['unified_players'] = self._merge_results(context)
        
        return context
    
    def _retrieve_baseline_specific(self, query: str, season: str, context: Dict) -> Dict:
        """Get baseline data for specific player/team lookups."""
        player_names = self._extract_player_names(query)
        
        if player_names:
            for name in player_names[:2]:
                player_stats = self.baseline.get_player_season_stats(name, season)
                if player_stats:
                    context['baseline_results'][f'player_{name}'] = player_stats
        
        team = self._extract_team(query)
        if team:
            team_players = self.baseline.get_team_players(team, season, top_n=10)
            context['baseline_results']['team_players'] = team_players
        
        return context
    
    def _retrieve_baseline_comparative(self, query: str, season: str, context: Dict) -> Dict:
        """Get baseline data for player comparison queries."""
        player_names = self._extract_player_names(query)
        
        if len(player_names) >= 2:
            comparison = self.baseline.compare_players(player_names[0], player_names[1], season)
            context['baseline_results']['comparison'] = comparison
        
        return context
    
    def _retrieve_baseline_aggregate(self, query: str, season: str, context: Dict) -> Dict:
        """Get baseline data for top/best/ranking queries."""
        query_lower = query.lower()
        position = self._extract_position(query)
        
        if 'goal' in query_lower or 'scorer' in query_lower:
            if position:
                results = self.baseline.get_top_scorers(position, season, limit=10)
            else:
                results = []
                for pos in ['FWD', 'MID']:
                    results.extend(self.baseline.get_top_scorers(pos, season, limit=5))
            context['baseline_results']['top_scorers'] = results
            
        elif 'assist' in query_lower:
            if position:
                results = self.baseline.get_top_assisters(position, season, limit=10)
            else:
                results = []
                for pos in ['MID', 'FWD']:
                    results.extend(self.baseline.get_top_assisters(pos, season, limit=5))
            context['baseline_results']['top_assisters'] = results
            
        elif 'ict' in query_lower or 'index' in query_lower:
            if position:
                results = self.baseline.get_best_ict_performers(position, season, limit=10)
            else:
                results = self.baseline.get_best_ict_performers('MID', season, limit=10)
            context['baseline_results']['best_ict'] = results
            
        elif 'point' in query_lower or 'performer' in query_lower:
            results = self.baseline.get_high_performers(season, min_goals=10)
            context['baseline_results']['high_performers'] = results
        
        return context
    
    def _retrieve_baseline_for_semantic(self, query: str, season: str, context: Dict) -> Dict:
        """Get baseline stats for top semantic matches."""
        # Get detailed stats for top 3 semantic matches
        if context['semantic_results'].get('players'):
            top_player_names = [p['player_name'] for p in context['semantic_results']['players'][:3]]
            for name in top_player_names:
                stats = self.baseline.get_player_season_stats(name, season)
                if stats:
                    context['baseline_results'][f'player_{name}'] = stats
        
        return context
    
    def _merge_results(self, context: Dict) -> List[Dict[str, Any]]:
        """
        Merge baseline and semantic results into unified player list.
        Deduplicates and combines information.
        """
        player_map = {}  # player_name -> merged data
        
        # Add semantic results first (they have similarity scores)
        if context['semantic_results'].get('players'):
            for player in context['semantic_results']['players']:
                name = player['player_name']
                player_map[name] = {
                    'player_name': name,
                    'source': 'semantic',
                    'similarity_score': player.get('similarity_score', 0.0),
                    **player
                }
        
        # Merge in baseline results
        for key, value in context['baseline_results'].items():
            if isinstance(value, list):
                for item in value:
                    name = item.get('player') or item.get('player_name') or item.get('name')
                    if name:
                        if name in player_map:
                            # Merge data
                            player_map[name].update(item)
                            player_map[name]['source'] = 'hybrid'
                        else:
                            # Add new player from baseline
                            player_map[name] = {
                                'player_name': name,
                                'source': 'baseline',
                                'similarity_score': 0.0,
                                **item
                            }
        
        # Convert to sorted list (by similarity score)
        unified = list(player_map.values())
        unified.sort(key=lambda x: x.get('similarity_score', 0), reverse=True)
        
        return unified
    
    # =========================================================================
    # Formatted Context for LLM
    # =========================================================================
    
    def format_context_for_llm(self, context: Dict) -> str:
        """
        Format the unified context into a clean string for LLM consumption.
        
        Args:
            context: Retrieved context dictionary
            
        Returns:
            Formatted string ready for LLM prompt
        """
        lines = []
        lines.append(f"Query: {context['query']}")
        lines.append(f"Season: {context['season']}")
        lines.append(f"Intent: {context['intent']}")
        lines.append("")
        
        # Add baseline results summary
        if context['baseline_results']:
            lines.append("=== BASELINE QUERY RESULTS ===")
            for key, value in context['baseline_results'].items():
                lines.append(f"\n{key.upper()}:")
                if isinstance(value, list):
                    for i, item in enumerate(value[:5], 1):  # Top 5
                        lines.append(f"  {i}. {self._format_item(item)}")
                else:
                    lines.append(f"  {value}")
            lines.append("")
        
        # Add semantic results
        if context['semantic_results'].get('players'):
            lines.append("=== SEMANTIC SEARCH RESULTS ===")
            for i, player in enumerate(context['semantic_results']['players'][:5], 1):
                lines.append(f"{i}. {player['player_name']} ({player.get('position', 'N/A')})")
                lines.append(f"   Similarity: {player.get('similarity_score', 0):.3f}")
                lines.append(f"   Stats: {player.get('total_goals', 0)}G, "
                           f"{player.get('total_assists', 0)}A, "
                           f"{player.get('total_points', 0)} pts")
            lines.append("")
        
        # Add unified top players
        if context['unified_players']:
            lines.append("=== TOP UNIFIED RESULTS ===")
            for i, player in enumerate(context['unified_players'][:10], 1):
                lines.append(f"{i}. {player['player_name']} (Source: {player.get('source', 'unknown')})")
                if player.get('similarity_score', 0) > 0:
                    lines.append(f"   Similarity: {player['similarity_score']:.3f}")
                stats_parts = []
                if 'total_goals' in player or 'goals' in player:
                    goals = player.get('total_goals') or player.get('goals', 0)
                    stats_parts.append(f"{goals}G")
                if 'total_assists' in player or 'assists' in player:
                    assists = player.get('total_assists') or player.get('assists', 0)
                    stats_parts.append(f"{assists}A")
                if 'total_points' in player:
                    stats_parts.append(f"{player['total_points']} pts")
                if stats_parts:
                    lines.append(f"   Stats: {', '.join(stats_parts)}")
        
        return '\n'.join(lines)
    
    def _format_item(self, item: Dict) -> str:
        """Format a single item for display."""
        if 'player' in item and 'total_goals' in item:
            return f"{item['player']} - {item['total_goals']}G, {item.get('total_assists', 0)}A, {item.get('total_points', 0)} pts"
        elif 'player_name' in item:
            return f"{item['player_name']} - {item}"
        else:
            return str(item)
