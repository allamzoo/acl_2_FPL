"""
Hybrid Retrieval Module

Combines baseline Cypher queries with embedding-based semantic search
to provide comprehensive context for LLM generation.
"""

import logging
from typing import List, Dict, Any, Optional
from .baseline_retriever import BaselineRetriever
from .embedding_retriever import EmbeddingRetriever
from src.preprocessing.intent_classifier import LLMIntentClassifier, SimpleIntentClassifier, Intent
from src.preprocessing.entity_extractor import EntityExtractor

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
                 top_k_semantic: int = 5,
                 use_llm_intent: bool = False):  # Default to False (rule-based is more reliable)
        """
        Initialize hybrid retriever with two embedding configurations.
        
        Args:
            embedding_model: Model for both semantic search configurations
            use_hybrid_embeddings: Use numerical+text hybrid embeddings
            top_k_semantic: Number of semantic results to retrieve
            use_llm_intent: Use LLM-based intent classifier (vs simple rule-based)
        """
        self.baseline = BaselineRetriever()
        
        # Initialize intent classifier (LLM or simple fallback)
        self.use_llm_intent = use_llm_intent
        if use_llm_intent:
            try:
                self.intent_classifier = LLMIntentClassifier()
                logger.info("✓ LLM Intent Classifier initialized")
            except Exception as e:
                logger.warning(f"LLM classifier failed, using simple fallback: {e}")
                self.intent_classifier = SimpleIntentClassifier()
        else:
            self.intent_classifier = SimpleIntentClassifier()
            logger.info("✓ Simple Intent Classifier initialized")
        
        # Initialize entity extractor
        self.entity_extractor = EntityExtractor()
        logger.info("✓ Entity Extractor initialized")
        
        # Initialize both embedding retrievers using the same model
        # but with different weighting strategies for diversification
        # Model 1: Balanced (70% stats, 30% text) - favors statistical similarity
        # Model 2: Equal (50% stats, 50% text) - balanced stat and semantic similarity
        self.embedding_model_1 = EmbeddingRetriever(
            model_name=embedding_model,  # all-mpnet-base-v2 with balanced weighting
            use_hybrid=use_hybrid_embeddings
        )
        self.embedding_model_2 = EmbeddingRetriever(
            model_name=embedding_model,  # Same model, equal weighting strategy
            use_hybrid=use_hybrid_embeddings,
            numerical_weight=0.5,  # Equal weighting: 50% stats, 50% text
            text_weight=0.5
        )
        
        # Keep reference for backward compatibility
        self.embedding = self.embedding_model_1
        
        self.top_k = top_k_semantic
        
        logger.info(f"HybridRetriever initialized with:")
        logger.info(f"  Embedding Model: {embedding_model}")
        logger.info(f"  Model 1 weighting: 70% numerical, 30% text (stat-focused)")
        logger.info(f"  Model 2 weighting: 50% numerical, 50% text (balanced)")
        logger.info(f"  Hybrid embeddings: {use_hybrid_embeddings}")
        logger.info(f"  Intent Classifier: {'LLM-based' if use_llm_intent else 'Rule-based'}")
    
    def close(self):
        """Close all connections."""
        self.baseline.close()
        self.embedding_model_1.close()
        self.embedding_model_2.close()
        self.entity_extractor.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    # =========================================================================
    # Intent-based Retrieval Routing (Using LLM Intent Classifier)
    # =========================================================================
    
    def _classify_query_intent(self, query: str) -> Dict[str, Any]:
        """
        Classify the query intent using LLM-based or rule-based classifier.
        
        Returns:
            Dictionary with intent classification and strategy
        """
        result = self.intent_classifier.classify(query)
        intent_enum = result.get('intent', Intent.UNKNOWN)
        confidence = result.get('confidence', 0.0)
        
        logger.info(f"Intent: {intent_enum.value} (confidence: {confidence:.2f})")
        
        # Map Intent enum to retrieval strategy
        if intent_enum in [Intent.PLAYER_SEARCH, Intent.PLAYER_STATS]:
            strategy = 'specific'
        elif intent_enum == Intent.PLAYER_COMPARISON:
            strategy = 'comparative'
        elif intent_enum in [Intent.TOP_SCORERS, Intent.TOP_ASSISTERS, Intent.TEAM_ANALYSIS, 
                             Intent.HIGH_PERFORMERS, Intent.ICT_ANALYSIS,
                             Intent.GAMEWEEK_PERFORMERS, Intent.PLAYER_FORM]:
            strategy = 'aggregate'
        else:
            strategy = 'semantic'
        
        return {
            'strategy': strategy,
            'intent': intent_enum,
            'confidence': confidence,
            'reasoning': result.get('reasoning', 'Unknown')
        }
    
    def _extract_player_names(self, query: str) -> List[str]:
        """Extract player names using entity extractor."""
        entities = self.entity_extractor.extract(query)
        return entities.get('player_names', [])
    
    def _extract_entities(self, query: str) -> Dict[str, Any]:
        """Extract all entities using entity extractor."""
        return self.entity_extractor.extract(query)
    
    def _extract_position(self, query: str) -> Optional[str]:
        """Extract position filter using entity extractor."""
        entities = self.entity_extractor.extract(query)
        positions = entities.get('positions', [])
        return positions[0] if positions else None
    
    def _extract_team(self, query: str) -> Optional[str]:
        """Extract team name using entity extractor."""
        entities = self.entity_extractor.extract(query)
        teams = entities.get('team_names', [])
        return teams[0] if teams else None
    
    def _extract_price_threshold(self, query: str) -> Optional[float]:
        """Extract price threshold using entity extractor."""
        entities = self.entity_extractor.extract(query)
        thresholds = entities.get('thresholds', {})
        return thresholds.get('price') if thresholds else None
    
    # =========================================================================
    # Unified Retrieval Methods
    # =========================================================================
    
    def retrieve(self, query: str, season: str = "2021-22", 
                 retrieval_mode: str = "baseline+embedding1") -> Dict[str, Any]:
        """
        Main retrieval method with configurable retrieval strategy.
        
        Args:
            query: Natural language query
            season: FPL season
            retrieval_mode: Strategy to use:
                - 'baseline' - Baseline only (no embeddings, no merge)
                - 'baseline+embedding1' - Baseline + Embedding Model 1 (merged)
                - 'baseline+embedding2' - Baseline + Embedding Model 2 (merged)
            
        Returns:
            Unified context with results based on selected mode
        """
        intent_result = self._classify_query_intent(query)
        intent = intent_result['strategy']
        intent_enum = intent_result['intent']
        logger.info(f"Query intent: {intent} ({intent_enum.value}) | Confidence: {intent_result['confidence']:.2f} | Mode: {retrieval_mode}")
        
        context = {
            'query': query,
            'season': season,
            'intent': intent,
            'intent_enum': intent_enum,
            'intent_confidence': intent_result['confidence'],
            'retrieval_mode': retrieval_mode,
            'baseline_results': {},
            'semantic_results': {},
            'unified_players': []
        }
        
        # Run baseline query based on intent (ALWAYS)
        logger.info("Running baseline Cypher query...")
        if intent == 'specific':
            context = self._retrieve_baseline_specific(query, season, context)
        elif intent == 'comparative':
            context = self._retrieve_baseline_comparative(query, season, context)
        elif intent == 'aggregate':
            context = self._retrieve_baseline_aggregate(query, season, context)
        else:  # semantic - still get some baseline data
            context = self._retrieve_baseline_for_semantic(query, season, context)
        
        # Conditionally run semantic search based on retrieval_mode
        if retrieval_mode == "baseline":
            # Baseline only - no semantic search, no merge
            logger.info("Mode: baseline-only (skipping semantic search)")
            context['semantic_results'] = {'players': [], 'count': 0}
            # Use baseline results directly as unified
            baseline_players = []
            for key, results in context['baseline_results'].items():
                if isinstance(results, list):
                    for item in results:
                        player_dict = {'player_name': item.get('player', item.get('player_name', 'Unknown')),
                                     'source': 'baseline',
                                     'similarity_score': 0.0}
                        player_dict.update(item)
                        baseline_players.append(player_dict)
            context['unified_players'] = baseline_players
            
        elif retrieval_mode == "baseline+embedding1":
            # Baseline + Embedding Model 1
            logger.info("Mode: baseline + embedding model 1 (merging results)")
            semantic_results = self.embedding_model_1.semantic_search(query, top_k=10, season=season)
            context['semantic_results'] = semantic_results
            context['unified_players'] = self._merge_results(context)
            
        elif retrieval_mode == "baseline+embedding2":
            # Baseline + Embedding Model 2
            logger.info("Mode: baseline + embedding model 2 (merging results)")
            semantic_results = self.embedding_model_2.semantic_search(query, top_k=10, season=season)
            context['semantic_results'] = semantic_results
            context['unified_players'] = self._merge_results(context)
            
        else:
            raise ValueError(f"Invalid retrieval_mode: {retrieval_mode}. "
                           f"Must be 'baseline', 'baseline+embedding1', or 'baseline+embedding2'")
        
        return context
    
    def _retrieve_baseline_specific(self, query: str, season: str, context: Dict) -> Dict:
        """Get baseline data for specific player/team lookups."""
        entities = self._extract_entities(query)
        
        player_names = entities.get('player_names', [])
        if player_names:
            for name in player_names[:2]:
                player_stats = self.baseline.get_player_season_stats(name, season)
                if player_stats:
                    context['baseline_results'][f'player_{name}'] = player_stats
        
        team_names = entities.get('team_names', [])
        if team_names:
            team = team_names[0]
            team_players = self.baseline.get_team_players(team, season, top_n=10)
            context['baseline_results']['team_players'] = team_players
        
        return context
    
    def _retrieve_baseline_comparative(self, query: str, season: str, context: Dict) -> Dict:
        """Get baseline data for player comparison queries."""
        entities = self._extract_entities(query)
        player_names = entities.get('player_names', [])
        
        if len(player_names) >= 2:
            comparison = self.baseline.compare_players(player_names[0], player_names[1], season)
            context['baseline_results']['comparison'] = comparison
        
        return context
    
    def _retrieve_baseline_aggregate(self, query: str, season: str, context: Dict) -> Dict:
        """Get baseline data for top/best/ranking queries."""
        query_lower = query.lower()
        entities = self._extract_entities(query)
        
        # Extract position from entities
        positions = entities.get('positions', [])
        position = positions[0] if positions else None
        
        # Budget/Value queries - check for price-related keywords
        if any(keyword in query_lower for keyword in ['budget', 'cheap', 'value', 'low price', 'affordable']):
            # Extract price threshold if mentioned (e.g., "under 7.0", "below 6.5")
            max_price = self._extract_price_threshold(query)
            
            if position:
                results = self.baseline.get_best_value_players(
                    position, season, max_price=max_price, min_points=100, limit=10
                )
            else:
                # Default to midfielders for value queries
                results = self.baseline.get_best_value_players(
                    'MID', season, max_price=max_price, min_points=100, limit=10
                )
            context['baseline_results']['best_value'] = results
            
        elif 'clean sheet' in query_lower or 'cleansheet' in query_lower:
            # Clean sheet queries - typically for defenders or goalkeepers
            if position:
                results = self.baseline.get_top_clean_sheet_keepers(position, season, limit=10)
            else:
                # Default to defenders for clean sheet queries
                results = self.baseline.get_top_clean_sheet_keepers('DEF', season, limit=10)
            context['baseline_results']['top_clean_sheets'] = results
            
        elif 'goal' in query_lower or 'scorer' in query_lower:
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
                results = self.baseline.get_top_ict_players(position, season, limit=10)
            else:
                results = self.baseline.get_top_ict_players('MID', season, limit=10)
            context['baseline_results']['best_ict'] = results
            
        elif 'point' in query_lower or 'performer' in query_lower:
            results = self.baseline.get_high_performers(min_goals=10, season=season)
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
        
        Implementation:
        1. Combines nodes/data from both retrieval methods
        2. Removes duplicates by player_name (uses dictionary)
        3. Ranks by similarity score (semantic relevance)
        4. Tags source: 'baseline', 'semantic', or 'hybrid'
        
        Returns:
            Sorted, deduplicated list of players with merged data
        """
        # Step 1: COMBINE - Use dictionary to track all players
        player_map = {}  # player_name -> merged data
        
        # Add semantic results first (they have similarity scores and detailed stats)
        if context['semantic_results'].get('players'):
            for player in context['semantic_results']['players']:
                name = player['player_name']
                player_map[name] = {
                    'player_name': name,
                    'source': 'semantic',
                    'similarity_score': player.get('similarity_score', 0.0),
                    **player  # Include all stats: goals, assists, points, position, etc.
                }
        
        # Step 2: MERGE - Add baseline results and combine with semantic
        for key, value in context['baseline_results'].items():
            if isinstance(value, list):
                for item in value:
                    name = item.get('player') or item.get('player_name') or item.get('name')
                    if name:
                        if name in player_map:
                            # DUPLICATE FOUND - Merge data and mark as hybrid
                            player_map[name].update(item)
                            player_map[name]['source'] = 'hybrid'
                        else:
                            # New player from baseline only
                            player_map[name] = {
                                'player_name': name,
                                'source': 'baseline',
                                'similarity_score': 0.0,  # No semantic match
                                **item
                            }
        
        # Step 3: RANK/PRIORITIZE - Sort by similarity score (highest first)
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
