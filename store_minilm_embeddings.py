"""
Generate and store embeddings using all-MiniLM-L6-v2 model.
This creates a separate embedding property for the second model.
"""

import logging
import time
from sentence_transformers import SentenceTransformer
from neo4j import GraphDatabase
from config.config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD
import numpy as np
from sklearn.preprocessing import StandardScaler

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class MiniLMEmbedder:
    """Generate embeddings using all-MiniLM-L6-v2 for model comparison."""
    
    def __init__(self):
        self.driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
        )
        
        # Load MiniLM model (384 dimensions)
        logger.info("Loading all-MiniLM-L6-v2 model...")
        self.text_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.text_dim = 384
        
        self.scaler = StandardScaler()
        logger.info("✓ MiniLM embedder initialized")
    
    def close(self):
        if self.driver:
            self.driver.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def fetch_player_data(self, season: str = "2021-22", min_minutes: int = 500):
        """Fetch player statistics from Neo4j."""
        query = """
        MATCH (p:Player)-[r:PLAYED_IN]->(f:Fixture)<-[:HAS_FIXTURE]-(gw:Gameweek)
        WHERE gw.season = $season
        WITH p.player_name AS player_name,
             p.player_element AS player_id,
             COUNT(DISTINCT f) AS games_played,
             SUM(r.minutes) AS total_minutes,
             SUM(r.total_points) AS total_points,
             SUM(r.goals_scored) AS total_goals,
             SUM(r.assists) AS total_assists,
             SUM(r.clean_sheets) AS clean_sheets,
             SUM(r.goals_conceded) AS goals_conceded,
             SUM(r.saves) AS saves,
             AVG(r.ict_index) AS avg_ict,
             AVG(r.influence) AS avg_influence,
             AVG(r.creativity) AS avg_creativity,
             AVG(r.threat) AS avg_threat,
             r.position AS position
        WHERE total_minutes >= $min_minutes
        RETURN player_name, player_id, position, games_played, total_minutes,
               total_points, total_goals, total_assists, clean_sheets,
               goals_conceded, saves, avg_ict, avg_influence, avg_creativity, avg_threat
        ORDER BY total_points DESC
        """
        
        with self.driver.session() as session:
            result = session.run(query, season=season, min_minutes=min_minutes)
            return [dict(record) for record in result]
    
    def generate_numerical_features(self, players):
        """Generate normalized numerical features."""
        logger.info(f"Generating numerical features for {len(players)} players...")
        
        features = []
        for player in players:
            games = player['games_played']
            minutes = player['total_minutes']
            
            # Per-game and per-90 metrics
            feature_vec = [
                player['total_goals'] / (minutes / 90) if minutes > 0 else 0,  # Goals per 90
                player['total_assists'] / (minutes / 90) if minutes > 0 else 0,  # Assists per 90
                player['total_points'] / games if games > 0 else 0,  # Points per game
                player['clean_sheets'] / games if games > 0 else 0,  # Clean sheets per game
                player['goals_conceded'] / games if games > 0 else 0,  # Goals conceded per game
                player['saves'] / games if games > 0 else 0,  # Saves per game
                player['avg_ict'] or 0,  # ICT index
                player['avg_influence'] or 0,  # Influence
                player['avg_creativity'] or 0,  # Creativity
                player['avg_threat'] or 0  # Threat
            ]
            features.append(feature_vec)
        
        # Normalize
        features_normalized = self.scaler.fit_transform(features)
        
        logger.info(f"✓ Generated {len(features_normalized)} normalized feature vectors")
        return features_normalized
    
    def generate_text_embeddings(self, players):
        """Generate text embeddings using MiniLM."""
        logger.info(f"Generating MiniLM text embeddings for {len(players)} players...")
        
        descriptions = []
        for player in players:
            desc = (
                f"{player['player_name']} is a {player['position']} who played "
                f"{player['games_played']} games with {player['total_goals']} goals, "
                f"{player['total_assists']} assists, and {player['total_points']} total points. "
                f"Clean sheets: {player['clean_sheets']}. "
                f"ICT index: {player['avg_ict']:.1f}."
            )
            descriptions.append(desc)
        
        # Generate embeddings (384 dimensions for MiniLM)
        embeddings = self.text_model.encode(descriptions, show_progress_bar=True)
        
        logger.info(f"✓ Generated {len(embeddings)} text embeddings ({embeddings.shape[1]} dims)")
        return embeddings
    
    def store_embeddings(self, players, numerical_features, text_embeddings):
        """Store embeddings in Neo4j with MiniLM-specific property names."""
        logger.info("Storing MiniLM embeddings in Neo4j...")
        
        query = """
        MATCH (p:Player {player_element: $player_id})
        SET p.numerical_features_minilm = $numerical_features,
            p.text_embedding_minilm = $text_embedding
        RETURN p.player_name AS player
        """
        
        stored = 0
        with self.driver.session() as session:
            for i, player in enumerate(players):
                try:
                    session.run(
                        query,
                        player_id=player['player_id'],
                        numerical_features=numerical_features[i].tolist(),
                        text_embedding=text_embeddings[i].tolist()
                    )
                    stored += 1
                    
                    if (stored % 50) == 0:
                        logger.info(f"  Stored {stored}/{len(players)} embeddings...")
                
                except Exception as e:
                    logger.error(f"Failed to store {player['player_name']}: {e}")
        
        logger.info(f"✓ Stored {stored} MiniLM embeddings")
        return stored


def main():
    print("=" * 100)
    print("GENERATING MINILM EMBEDDINGS (all-MiniLM-L6-v2)")
    print("=" * 100)
    
    start_time = time.time()
    
    with MiniLMEmbedder() as embedder:
        # Fetch player data
        print("\n1. Fetching player data from Neo4j...")
        players = embedder.fetch_player_data(season="2021-22", min_minutes=500)
        
        if not players:
            print("❌ No player data found")
            return
        
        print(f"✓ Fetched {len(players)} players")
        
        # Generate numerical features
        print("\n2. Generating numerical features...")
        numerical_features = embedder.generate_numerical_features(players)
        
        # Generate text embeddings with MiniLM
        print("\n3. Generating MiniLM text embeddings (384 dims)...")
        text_embeddings = embedder.generate_text_embeddings(players)
        
        # Store in Neo4j
        print("\n4. Storing embeddings in Neo4j...")
        stored = embedder.store_embeddings(players, numerical_features, text_embeddings)
        
        total_time = time.time() - start_time
        
        print("\n" + "=" * 100)
        print("SUMMARY")
        print("=" * 100)
        print(f"Players: {stored}")
        print(f"Model: all-MiniLM-L6-v2")
        print(f"Numerical features: 10 dimensions")
        print(f"Text embedding: 384 dimensions")
        print(f"Property names:")
        print(f"  - numerical_features_minilm")
        print(f"  - text_embedding_minilm")
        print(f"Total time: {total_time:.2f}s")
        print("=" * 100)
        print("\n✓ MiniLM embeddings stored!")
        print("\nNow you can use both models:")
        print("  Model 1: all-mpnet-base-v2 (768 dims) - uses 'text_embedding' property")
        print("  Model 2: all-MiniLM-L6-v2 (384 dims) - uses 'text_embedding_minilm' property")


if __name__ == "__main__":
    main()
