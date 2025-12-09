"""
Hybrid Embedding Module - Combines numerical features with semantic text embeddings.

This approach addresses the limitation of pure text embeddings by:
1. Creating normalized numerical feature vectors from stats
2. Generating semantic embeddings from enhanced descriptions
3. Combining both for richer similarity matching
"""

import logging
from typing import List, Dict, Any, Tuple
import numpy as np
from sklearn.preprocessing import StandardScaler
from sentence_transformers import SentenceTransformer
from neo4j import GraphDatabase
from config.config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, NEO4J_DATABASE
from tqdm import tqdm

logger = logging.getLogger(__name__)


class HybridEmbedder:
    """
    Creates hybrid embeddings combining numerical features and semantic text.
    """
    
    def __init__(self, model_name: str = "all-mpnet-base-v2"):
        """Initialize hybrid embedder."""
        self.model_name = model_name
        
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.text_dim = self.model.get_sentence_embedding_dimension()
        
        # Numerical feature scaler
        self.scaler = StandardScaler()
        self.numerical_features_fitted = False
        
        # Neo4j connection
        self.driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
        )
        
        logger.info(f"HybridEmbedder initialized. Text dimension: {self.text_dim}")
    
    def close(self):
        """Close Neo4j connection."""
        if self.driver:
            self.driver.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def extract_numerical_features(self, player_data: Dict[str, Any]) -> np.ndarray:
        """
        Extract and normalize key numerical features.
        
        Features selected for their importance in FPL:
        - Goals per 90 minutes
        - Assists per 90 minutes  
        - Points per game
        - ICT index (influence, creativity, threat)
        - Bonus points per game
        - Clean sheets (for defenders/keepers)
        - Minutes played (availability)
        """
        minutes = player_data.get('total_minutes', 0)
        games = player_data.get('games_played', 1)
        games_90 = max(minutes / 90, 0.1)  # Avoid division by zero
        
        # Per-90 stats for fairer comparison
        goals_per_90 = player_data.get('total_goals', 0) / games_90
        assists_per_90 = player_data.get('total_assists', 0) / games_90
        points_per_game = player_data.get('total_points', 0) / games
        
        # Advanced metrics
        ict = player_data.get('avg_ict_index', 0.0)
        influence = player_data.get('avg_influence', 0.0)
        creativity = player_data.get('avg_creativity', 0.0)
        threat = player_data.get('avg_threat', 0.0)
        
        # Other important features
        bonus_per_game = player_data.get('bonus_points', 0) / games
        clean_sheets = player_data.get('clean_sheets', 0)
        
        # Normalized minutes (0-1 scale based on max possible)
        minutes_ratio = min(minutes / 3420, 1.0)  # 3420 = 38 games * 90 mins
        
        features = np.array([
            goals_per_90,
            assists_per_90,
            points_per_game,
            ict,
            influence,
            creativity,
            threat,
            bonus_per_game,
            clean_sheets,
            minutes_ratio
        ])
        
        return features
    
    def create_query_description(self, query: str) -> str:
        """
        Enhance user query with explicit FPL terminology.
        """
        # Add FPL context to query
        enhanced_query = f"Fantasy Premier League player query: {query}"
        
        # Add common related terms
        query_lower = query.lower()
        
        if any(word in query_lower for word in ['striker', 'forward', 'attacker']):
            enhanced_query += " forward striker attacker FWD"
        
        if any(word in query_lower for word in ['midfielder', 'playmaker', 'creative']):
            enhanced_query += " midfielder MID playmaker"
            
        if any(word in query_lower for word in ['defender', 'defence', 'defensive']):
            enhanced_query += " defender DEF fullback wingback"
            
        if any(word in query_lower for word in ['goalkeeper', 'keeper']):
            enhanced_query += " goalkeeper GK keeper"
        
        if any(word in query_lower for word in ['goal', 'score', 'scorer']):
            enhanced_query += " goals scorer finisher"
            
        if any(word in query_lower for word in ['assist', 'creative', 'playmaker']):
            enhanced_query += " assists creative playmaker provider"
            
        if any(word in query_lower for word in ['elite', 'premium', 'top', 'best']):
            enhanced_query += " elite premium world class top tier best"
            
        if any(word in query_lower for word in ['points', 'fpl']):
            enhanced_query += " FPL points returns fantasy premier league"
        
        return enhanced_query
    
    def create_player_description(self, player_data: Dict[str, Any]) -> str:
        """
        Create comprehensive player description with position-specific focus.
        """
        position = player_data.get('position', 'Unknown')
        goals = player_data.get('total_goals', 0)
        assists = player_data.get('total_assists', 0)
        points = player_data.get('total_points', 0)
        ict = player_data.get('avg_ict_index', 0.0)
        minutes = player_data.get('total_minutes', 0)
        games = player_data.get('games_played', 1)
        
        # Calculate per-game stats
        games_90 = max(minutes / 90, 0.1)
        goals_per_90 = goals / games_90
        assists_per_90 = assists / games_90
        points_per_game = points / games
        
        parts = ["Fantasy Premier League"]
        
        # Position-specific description
        if position == 'FWD':
            parts.append("striker forward attacker FWD")
            if goals_per_90 >= 0.6:
                parts.append("elite prolific goal scorer lethal finisher clinical")
            elif goals_per_90 >= 0.4:
                parts.append("consistent goal scorer frequent striker")
            elif goals >= 5:
                parts.append("goal scorer attacking forward")
        
        elif position == 'MID':
            parts.append("midfielder MID playmaker")
            if goals_per_90 >= 0.4:
                parts.append("goal scoring attacking midfielder")
            if assists_per_90 >= 0.3:
                parts.append("creative playmaker assist provider exceptional creativity")
            elif assists >= 5:
                parts.append("playmaker creative assists")
        
        elif position == 'DEF':
            parts.append("defender DEF fullback wingback")
            clean_sheets = player_data.get('clean_sheets', 0)
            if assists >= 5:
                parts.append("attacking defender wingback assists")
            if clean_sheets >= 12:
                parts.append("defensive rock clean sheets excellent defense")
        
        elif position == 'GK':
            parts.append("goalkeeper GK keeper")
            clean_sheets = player_data.get('clean_sheets', 0)
            if clean_sheets >= 15:
                parts.append("elite goalkeeper many clean sheets")
        
        # Performance tier
        if points >= 200:
            parts.append("elite world class premium top tier exceptional FPL asset")
        elif points >= 150:
            parts.append("premium quality excellent top FPL option")
        elif points >= 100:
            parts.append("good quality solid reliable FPL choice")
        
        # ICT and impact
        if ict >= 8:
            parts.append("very high ICT index dominant influential key player")
        elif ict >= 5:
            parts.append("high ICT impact important player")
        
        # Consistency
        bonus = player_data.get('bonus_points', 0)
        if bonus >= 20:
            parts.append("extremely consistent bonus points reliable nailed on")
        elif bonus >= 10:
            parts.append("consistent performer bonus")
        
        # Add actual stats for context
        parts.append(f"{goals} goals {assists} assists {points} points")
        
        return " ".join(parts)
    
    def get_player_features(self, season: str = "2021-22", min_minutes: int = 500) -> List[Dict[str, Any]]:
        """Retrieve player data from Neo4j."""
        query = """
        MATCH (p:Player)-[r:PLAYED_IN]->(f:Fixture)
        WHERE f.season = $season
        WITH p.player_name AS player_name,
             r.position AS position,
             SUM(r.goals_scored) AS total_goals,
             SUM(r.assists) AS total_assists,
             SUM(r.total_points) AS total_points,
             SUM(r.bonus) AS bonus_points,
             SUM(r.clean_sheets) AS clean_sheets,
             COUNT(f) AS games_played,
             SUM(r.minutes) AS total_minutes,
             AVG(r.ict_index) AS avg_ict_index,
             AVG(r.influence) AS avg_influence,
             AVG(r.creativity) AS avg_creativity,
             AVG(r.threat) AS avg_threat
        WHERE total_minutes >= $min_minutes
        RETURN player_name, position, total_goals, total_assists, total_points,
               bonus_points, clean_sheets, games_played, total_minutes,
               avg_ict_index, avg_influence, avg_creativity, avg_threat
        ORDER BY total_points DESC
        """
        
        try:
            with self.driver.session(database=NEO4J_DATABASE) as session:
                result = session.run(query, {"season": season, "min_minutes": min_minutes})
                players = [dict(record) for record in result]
                logger.info(f"Retrieved {len(players)} players with min {min_minutes} minutes")
                return players
        except Exception as e:
            logger.error(f"Failed to retrieve players: {str(e)}")
            return []
    
    def generate_hybrid_embeddings(self, season: str = "2021-22", 
                                   min_minutes: int = 500) -> Tuple[Dict[str, np.ndarray], Dict[str, np.ndarray]]:
        """
        Generate both numerical and text embeddings.
        
        Returns:
            Tuple of (numerical_embeddings_dict, text_embeddings_dict)
        """
        logger.info(f"Generating hybrid embeddings for season {season}")
        
        players = self.get_player_features(season, min_minutes)
        
        if not players:
            return {}, {}
        
        # Extract numerical features
        numerical_features_list = []
        player_names = []
        
        for player in tqdm(players, desc="Extracting numerical features"):
            num_features = self.extract_numerical_features(player)
            numerical_features_list.append(num_features)
            player_names.append(player['player_name'])
        
        # Normalize numerical features
        numerical_array = np.array(numerical_features_list)
        numerical_normalized = self.scaler.fit_transform(numerical_array)
        self.numerical_features_fitted = True
        
        # Generate text embeddings
        descriptions = []
        for player in tqdm(players, desc="Creating descriptions"):
            desc = self.create_player_description(player)
            descriptions.append(desc)
        
        logger.info("Generating text embeddings...")
        text_embeddings = self.model.encode(descriptions, show_progress_bar=True,
                                           convert_to_numpy=True)
        
        # Create dictionaries
        numerical_dict = {name: emb for name, emb in zip(player_names, numerical_normalized)}
        text_dict = {name: emb for name, emb in zip(player_names, text_embeddings)}
        
        logger.info(f"Generated embeddings for {len(player_names)} players")
        return numerical_dict, text_dict
    
    def store_hybrid_embeddings(self, numerical_embeddings: Dict[str, np.ndarray],
                               text_embeddings: Dict[str, np.ndarray],
                               season: str = "2021-22"):
        """Store both embedding types in Neo4j."""
        logger.info(f"Storing {len(numerical_embeddings)} hybrid embeddings")
        
        update_query = """
        MATCH (p:Player {player_name: $player_name})
        SET p.numerical_features = $numerical_emb,
            p.text_embedding = $text_emb
        """
        
        try:
            with self.driver.session(database=NEO4J_DATABASE) as session:
                for player_name in tqdm(numerical_embeddings.keys(), desc="Storing"):
                    session.run(update_query, {
                        "player_name": player_name,
                        "numerical_emb": numerical_embeddings[player_name].tolist(),
                        "text_emb": text_embeddings[player_name].tolist()
                    })
            
            logger.info("Hybrid embeddings stored successfully")
        except Exception as e:
            logger.error(f"Failed to store embeddings: {str(e)}")
