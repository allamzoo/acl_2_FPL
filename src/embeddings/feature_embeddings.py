"""
Feature Vector Embeddings Module

Creates vector representations for feature combinations.
For FPL: Constructs text from numerical properties and embeds them.
"""

from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict, Any
from src.utils.neo4j_utils import Neo4jConnection
from config.config import EmbeddingConfig
import logging

logger = logging.getLogger(__name__)


class FeatureEmbedder:
    """
    Create and manage feature embeddings for FPL players.
    Constructs text descriptions from numerical properties and embeds them.
    """
    
    def __init__(self, model_name: str = None, neo4j_connection: Neo4jConnection = None):
        """
        Initialize feature embedder.
        
        Args:
            model_name: Name of embedding model to use
            neo4j_connection: Neo4j connection instance
        """
        self.model_name = model_name or EmbeddingConfig.DEFAULT_MODEL
        logger.info(f"Loading feature embedding model: {self.model_name}")
        self.model = SentenceTransformer(self.model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
        self.neo4j = neo4j_connection
    
    def create_player_description(self, player_data: Dict[str, Any]) -> str:
        """
        Create a text description from player properties.
        
        Args:
            player_data: Dictionary with player properties
            
        Returns:
            Text description of player
        """
        # Extract key features
        name = player_data.get("name", "Unknown")
        team = player_data.get("team", "Unknown")
        position = player_data.get("position", "Unknown")
        points = player_data.get("total_points", 0)
        goals = player_data.get("goals", 0)
        assists = player_data.get("assists", 0)
        price = player_data.get("price", 0)
        form = player_data.get("form", 0)
        clean_sheets = player_data.get("clean_sheets", 0)
        
        # Construct description
        description = (
            f"Player: {name}, Team: {team}, Position: {position}, "
            f"Total Points: {points}, Goals: {goals}, Assists: {assists}, "
            f"Clean Sheets: {clean_sheets}, Price: £{price}m, Form: {form}"
        )
        
        return description
    
    def embed_player_features(self, player_data: Dict[str, Any]) -> np.ndarray:
        """
        Create embedding for a player's features.
        
        Args:
            player_data: Dictionary with player properties
            
        Returns:
            Embedding vector as numpy array
        """
        description = self.create_player_description(player_data)
        embedding = self.model.encode([description])[0]
        return embedding
    
    def embed_all_players(self) -> List[Dict[str, Any]]:
        """
        Create embeddings for all players in the database.
        
        Returns:
            List of dictionaries with player ID, name, and embedding
        """
        if not self.neo4j:
            raise ValueError("Neo4j connection required for this operation")
        
        logger.info("Fetching all players from database...")
        query = """
            MATCH (p:Player)
            RETURN id(p) AS player_id, p.name AS name, p
            LIMIT 1000
        """
        
        players = self.neo4j.execute_query(query)
        logger.info(f"Creating embeddings for {len(players)} players...")
        
        player_embeddings = []
        for player in players:
            player_data = dict(player["p"])
            embedding = self.embed_player_features(player_data)
            
            player_embeddings.append({
                "player_id": player["player_id"],
                "name": player["name"],
                "embedding": embedding.tolist(),
                "description": self.create_player_description(player_data)
            })
        
        logger.info(f"Created {len(player_embeddings)} embeddings")
        return player_embeddings
    
    def store_embeddings_in_neo4j(self, player_embeddings: List[Dict[str, Any]]):
        """
        Store embeddings as properties in Neo4j nodes.
        
        Args:
            player_embeddings: List of player embeddings from embed_all_players()
        """
        if not self.neo4j:
            raise ValueError("Neo4j connection required for this operation")
        
        logger.info("Storing embeddings in Neo4j...")
        
        for player_emb in player_embeddings:
            query = """
                MATCH (p:Player)
                WHERE id(p) = $player_id
                SET p.embedding = $embedding,
                    p.feature_description = $description
            """
            params = {
                "player_id": player_emb["player_id"],
                "embedding": player_emb["embedding"],
                "description": player_emb["description"]
            }
            self.neo4j.execute_write_query(query, params)
        
        logger.info(f"Stored {len(player_embeddings)} embeddings in Neo4j")
    
    def create_vector_index(self, index_name: str = "player_embeddings"):
        """
        Create a vector similarity index in Neo4j for fast retrieval.
        
        Args:
            index_name: Name for the vector index
        """
        if not self.neo4j:
            raise ValueError("Neo4j connection required for this operation")
        
        logger.info(f"Creating vector index: {index_name}")
        
        # Create vector index
        query = f"""
            CREATE VECTOR INDEX {index_name} IF NOT EXISTS
            FOR (p:Player)
            ON p.embedding
            OPTIONS {{
                indexConfig: {{
                    `vector.dimensions`: {self.embedding_dim},
                    `vector.similarity_function`: 'cosine'
                }}
            }}
        """
        
        try:
            self.neo4j.execute_write_query(query)
            logger.info(f"Vector index {index_name} created successfully")
        except Exception as e:
            logger.error(f"Failed to create vector index: {e}")
            logger.info("Note: Vector indexes require Neo4j 5.11+ with Vector Search support")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the embedding model."""
        return {
            "model_name": self.model_name,
            "embedding_dimension": self.embedding_dim,
            "max_sequence_length": self.model.max_seq_length
        }


class EmbeddingComparator:
    """
    Compare different embedding models for FPL feature embeddings.
    """
    
    def __init__(self, neo4j_connection: Neo4jConnection = None):
        """
        Initialize comparator with multiple embedding models.
        
        Args:
            neo4j_connection: Neo4j connection instance
        """
        self.models = {
            "model_1": FeatureEmbedder(EmbeddingConfig.MODEL_1, neo4j_connection),
            "model_2": FeatureEmbedder(EmbeddingConfig.MODEL_2, neo4j_connection)
        }
        logger.info(f"Initialized comparator with {len(self.models)} models")
    
    def compare_embeddings(self, player_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate embeddings using both models and compare them.
        
        Args:
            player_data: Player properties dictionary
            
        Returns:
            Dictionary with embeddings and model info from both models
        """
        comparison = {}
        
        for model_name, embedder in self.models.items():
            embedding = embedder.embed_player_features(player_data)
            comparison[model_name] = {
                "embedding": embedding,
                "model_info": embedder.get_model_info()
            }
        
        return comparison
    
    def get_model_names(self) -> List[str]:
        """Get names of all models being compared."""
        return list(self.models.keys())
