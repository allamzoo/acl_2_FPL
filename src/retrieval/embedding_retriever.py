"""
Embedding-based Retrieval Module

Uses vector embeddings for semantic similarity search in the knowledge graph.
"""

import logging
from typing import List, Dict, Any
import numpy as np
from sentence_transformers import SentenceTransformer
from neo4j import GraphDatabase
from config.config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, NEO4J_DATABASE

logger = logging.getLogger(__name__)


class EmbeddingRetriever:
    """
    Semantic retrieval using vector embeddings.
    Finds players based on similarity to natural language queries.
    """
    
    def __init__(self, model_name: str = "all-mpnet-base-v2",
                 embedding_property: str = "feature_embedding_enhanced",
                 use_hybrid: bool = True,
                 numerical_weight: float = 0.7,
                 text_weight: float = 0.3):
        """
        Initialize the embedding retriever.
        
        Args:
            model_name: Sentence transformer model name
            embedding_property: Neo4j property containing embeddings (legacy)
            use_hybrid: Whether to use hybrid numerical+text embeddings
            numerical_weight: Weight for numerical similarity (0-1)
            text_weight: Weight for text similarity (0-1)
        """
        self.model_name = model_name
        self.embedding_property = embedding_property
        self.use_hybrid = use_hybrid
        self.numerical_weight = numerical_weight
        self.text_weight = text_weight
        
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        
        # For numerical feature normalization
        from sklearn.preprocessing import StandardScaler
        self.scaler = StandardScaler()
        
        # Neo4j connection
        self.driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
        )
        
        if use_hybrid:
            logger.info(f"EmbeddingRetriever initialized (HYBRID mode: {numerical_weight:.1f} numerical + {text_weight:.1f} text)")
        else:
            logger.info("EmbeddingRetriever initialized (text-only mode)")
    
    def close(self):
        """Close Neo4j connection."""
        if self.driver:
            self.driver.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def find_similar_players(self, query: str, top_k: int = 10,
                           season: str = None, min_minutes: int = 500,
                           position_filter: str = None) -> List[Dict[str, Any]]:
        """
        Find players similar to a natural language query.
        
        Args:
            query: Natural language query
            top_k: Number of results to return
            season: Optional season filter
            min_minutes: Minimum minutes played to filter out bench players
            position_filter: Optional position filter (GK, DEF, MID, FWD)
            
        Returns:
            List of player dictionaries with similarity scores
        """
        # Auto-detect position from query if not explicitly provided
        if not position_filter:
            position_filter = self._extract_position_from_query(query)
        
        if position_filter:
            logger.info(f"Searching for: '{query}' [Position: {position_filter}]")
        else:
            logger.info(f"Searching for: '{query}'")
        
        if self.use_hybrid:
            return self._hybrid_search(query, top_k, min_minutes, position_filter)
        else:
            return self._text_only_search(query, top_k, min_minutes, position_filter)
    
    def _extract_position_from_query(self, query: str) -> str:
        """Extract position from query text."""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['goalkeeper', 'keeper', 'gk']):
            return 'GK'
        elif any(word in query_lower for word in ['defender', 'defence', 'def', 'fullback', 'wing back', 'wingback', 'centre back', 'center back']):
            return 'DEF'
        elif any(word in query_lower for word in ['midfielder', 'midfield', 'mid']):
            return 'MID'
        elif any(word in query_lower for word in ['forward', 'striker', 'fwd', 'attacker']):
            return 'FWD'
        
        return None
    
    def _text_only_search(self, query: str, top_k: int, min_minutes: int, position_filter: str = None) -> List[Dict[str, Any]]:
        """Legacy text-only search."""
        query_embedding = self.model.encode(query, convert_to_numpy=True)
        
        cypher_query = f"""
        MATCH (p:Player)-[r:PLAYED_IN]->(f:Fixture)
        WHERE p.{self.embedding_property} IS NOT NULL
        WITH p, SUM(r.minutes) as total_minutes
        WHERE total_minutes >= $min_minutes
        RETURN DISTINCT p.player_name AS name, 
               p.{self.embedding_property} AS embedding
        """
        
        try:
            with self.driver.session(database=NEO4J_DATABASE) as session:
                result = session.run(cypher_query, {"min_minutes": min_minutes})
                players = [dict(record) for record in result]
            
            if not players:
                logger.warning("No players with embeddings found")
                return []
            
            seen = set()
            unique_players = []
            for player in players:
                if player['name'] not in seen:
                    seen.add(player['name'])
                    unique_players.append(player)
            
            similarities = []
            for player in unique_players:
                player_emb = np.array(player['embedding'])
                similarity = np.dot(query_embedding, player_emb) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(player_emb)
                )
                similarities.append({
                    'player_name': player['name'],
                    'similarity_score': float(similarity)
                })
            
            similarities.sort(key=lambda x: x['similarity_score'], reverse=True)
            top_results = similarities[:top_k]
            
            logger.info(f"Found {len(top_results)} similar players (from {len(unique_players)} eligible)")
            return top_results
            
        except Exception as e:
            logger.error(f"Similarity search failed: {str(e)}")
            return []
    
    def _extract_query_numerical_features(self, query: str) -> np.ndarray:
        """
        Extract implied numerical features from query text.
        Returns a weighted preference vector.
        """
        query_lower = query.lower()
        
        # Initialize neutral preferences
        preferences = np.zeros(10)
        
        # Goals importance
        if any(word in query_lower for word in ['goal', 'score', 'scorer', 'striker', 'prolific']):
            preferences[0] = 1.0  # goals_per_90
        
        # Assists importance  
        if any(word in query_lower for word in ['assist', 'creative', 'playmaker', 'provider']):
            preferences[1] = 1.0  # assists_per_90
        
        # Points importance
        if any(word in query_lower for word in ['points', 'fpl', 'top', 'best', 'premium', 'elite']):
            preferences[2] = 1.0  # points_per_game
            preferences[3] = 0.8  # ict
        
        # ICT/Impact importance
        if any(word in query_lower for word in ['ict', 'impact', 'influential', 'dominant']):
            preferences[3] = 1.0  # ict
            preferences[4] = 0.8  # influence
        
        # Creativity
        if any(word in query_lower for word in ['creative', 'creativity']):
            preferences[5] = 1.0  # creativity
        
        # Threat
        if any(word in query_lower for word in ['threat', 'attacking', 'attack']):
            preferences[6] = 1.0  # threat
        
        # Consistency/Bonus
        if any(word in query_lower for word in ['consistent', 'bonus', 'reliable']):
            preferences[7] = 1.0  # bonus_per_game
        
        # Clean sheets
        if any(word in query_lower for word in ['clean sheet', 'defensive', 'defense']):
            preferences[8] = 1.0  # clean_sheets
        
        # Availability
        if any(word in query_lower for word in ['nailed', 'regular', 'starter']):
            preferences[9] = 1.0  # minutes_ratio
        
        # If nothing specific mentioned, prefer overall quality
        if np.sum(preferences) == 0:
            preferences[2] = 1.0  # points_per_game
            preferences[3] = 0.5  # ict
        
        return preferences
    
    def _hybrid_search(self, query: str, top_k: int, min_minutes: int, position_filter: str = None) -> List[Dict[str, Any]]:
        """
        Hybrid search combining numerical features and semantic text.
        
        Args:
            query: Search query
            top_k: Number of results
            min_minutes: Minimum minutes filter
            position_filter: Optional position filter (GK, DEF, MID, FWD)
        """
        # Generate text embedding for query
        query_text_emb = self.model.encode(query, convert_to_numpy=True)
        
        # Extract numerical preferences from query
        query_num_preferences = self._extract_query_numerical_features(query)
        
        # Retrieve players with hybrid embeddings
        cypher_query = """
        MATCH (p:Player)-[r:PLAYED_IN]->(f:Fixture)
        WHERE p.numerical_features IS NOT NULL AND p.text_embedding IS NOT NULL
        """
        
        # Add position filter if provided
        if position_filter:
            cypher_query += " AND r.position = $position"
        
        cypher_query += """
        WITH p, SUM(r.minutes) as total_minutes
        WHERE total_minutes >= $min_minutes
        RETURN DISTINCT p.player_name AS name,
               p.numerical_features AS num_features,
               p.text_embedding AS text_emb
        """
        
        try:
            params = {"min_minutes": min_minutes}
            if position_filter:
                params["position"] = position_filter
            
            with self.driver.session(database=NEO4J_DATABASE) as session:
                result = session.run(cypher_query, params)
                players = [dict(record) for record in result]
            
            if not players:
                logger.warning("No players with hybrid embeddings found")
                return []
            
            similarities = []
            for player in players:
                # Text similarity (semantic)
                text_emb = np.array(player['text_emb'])
                text_sim = np.dot(query_text_emb, text_emb) / (
                    np.linalg.norm(query_text_emb) * np.linalg.norm(text_emb)
                )
                
                # Numerical similarity (feature matching)
                num_features = np.array(player['num_features'])
                # Weighted dot product based on query preferences
                num_sim = np.dot(query_num_preferences, num_features) / (
                    np.linalg.norm(query_num_preferences) + 1e-6
                )
                # Normalize to 0-1 range
                num_sim = (num_sim + 3) / 6  # Assuming normalized features are roughly -3 to +3
                num_sim = max(0, min(1, num_sim))
                
                # Combined similarity
                combined_sim = (self.numerical_weight * num_sim + 
                               self.text_weight * text_sim)
                
                similarities.append({
                    'player_name': player['name'],
                    'similarity_score': float(combined_sim),
                    'numerical_score': float(num_sim),
                    'text_score': float(text_sim)
                })
            
            # Sort by combined similarity
            similarities.sort(key=lambda x: x['similarity_score'], reverse=True)
            top_results = similarities[:top_k]
            
            logger.info(f"Found {len(top_results)} similar players (hybrid: {len(players)} total)")
            return top_results
            
        except Exception as e:
            logger.error(f"Hybrid search failed: {str(e)}")
            return []
    
    def get_player_details(self, player_names: List[str], 
                          season: str = "2021-22") -> List[Dict[str, Any]]:
        """
        Get detailed statistics for a list of players.
        
        Args:
            player_names: List of player names
            season: Season to get stats for
            
        Returns:
            List of player detail dictionaries
        """
        query = """
        MATCH (p:Player)-[r:PLAYED_IN]->(f:Fixture)
        WHERE p.player_name IN $player_names AND f.season = $season
        WITH p.player_name AS player_name,
             r.position AS position,
             SUM(r.goals_scored) AS total_goals,
             SUM(r.assists) AS total_assists,
             SUM(r.total_points) AS total_points,
             SUM(r.bonus) AS bonus_points,
             SUM(r.clean_sheets) AS clean_sheets,
             COUNT(f) AS games_played,
             SUM(r.minutes) AS total_minutes,
             AVG(r.ict_index) AS avg_ict_index
        RETURN player_name, position, total_goals, total_assists, 
               total_points, bonus_points, clean_sheets, games_played,
               total_minutes, avg_ict_index
        ORDER BY total_points DESC
        """
        
        try:
            with self.driver.session(database=NEO4J_DATABASE) as session:
                result = session.run(query, {
                    "player_names": player_names,
                    "season": season
                })
                return [dict(record) for record in result]
        except Exception as e:
            logger.error(f"Failed to get player details: {str(e)}")
            return []
    
    def semantic_search(self, query: str, top_k: int = 5, 
                       season: str = "2021-22", position_filter: str = None) -> Dict[str, Any]:
        """
        Perform semantic search and return detailed results.
        
        Args:
            query: Natural language query
            top_k: Number of results
            season: Season to search
            position_filter: Optional position filter (GK, DEF, MID, FWD)
            
        Returns:
            Dictionary with similar players and their details
        """
        # Find similar players
        similar_players = self.find_similar_players(query, top_k=top_k, position_filter=position_filter)
        
        if not similar_players:
            return {
                'query': query,
                'players': [],
                'count': 0
            }
        
        # Get player names
        player_names = [p['player_name'] for p in similar_players]
        
        # Get detailed stats
        player_details = self.get_player_details(player_names, season=season)
        
        # Merge similarity scores with details
        results = []
        for similar in similar_players:
            # Find matching detail
            detail = next(
                (d for d in player_details if d['player_name'] == similar['player_name']),
                None
            )
            
            if detail:
                detail['similarity_score'] = similar['similarity_score']
                results.append(detail)
        
        return {
            'query': query,
            'players': results,
            'count': len(results)
        }
    
    def format_results_for_llm(self, results: Dict[str, Any]) -> str:
        """
        Format semantic search results for LLM context.
        
        Args:
            results: Results from semantic_search()
            
        Returns:
            Formatted text for LLM
        """
        if not results['players']:
            return f"No players found matching: {results['query']}"
        
        output = [f"Query: {results['query']}"]
        output.append(f"Found {results['count']} similar players:\n")
        
        for i, player in enumerate(results['players'], 1):
            output.append(f"{i}. {player['player_name']} ({player['position']})")
            output.append(f"   Similarity: {player['similarity_score']:.3f}")
            output.append(f"   Goals: {player.get('total_goals', 0)}, "
                        f"Assists: {player.get('total_assists', 0)}, "
                        f"Points: {player.get('total_points', 0)}")
            output.append(f"   Games: {player.get('games_played', 0)}, "
                        f"Minutes: {player.get('total_minutes', 0)}")
            output.append(f"   ICT Index: {player.get('avg_ict_index', 0):.1f}\n")
        
        return "\n".join(output)
