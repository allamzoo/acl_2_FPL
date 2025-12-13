"""
Baseline Retrieval Module

Implements deterministic Cypher-based retrieval from Neo4j.
Uses predefined Cypher queries to retrieve structured information from the KG.
"""

from neo4j import GraphDatabase
from typing import List, Dict, Any, Optional
from config.config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, NEO4J_DATABASE
import logging

logger = logging.getLogger(__name__)


class BaselineRetriever:
    """
    Baseline retriever using Cypher queries for deterministic KG retrieval.
    """
    
    def __init__(self):
        """Initialize Neo4j connection."""
        self.driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
        )
        logger.info("Baseline retriever initialized")
    
    def close(self):
        """Close Neo4j driver connection."""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j connection closed")
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    # =========================================================================
    # Query 1: Find Player by Name
    # =========================================================================
    
    def find_player_by_name(self, player_name: str) -> List[Dict[str, Any]]:
        """
        Search for players by name.
        
        Args:
            player_name: Player name or partial name to search
            
        Returns:
            List of player records with name and ID
        """
        query = """
        MATCH (p:Player)
        WHERE p.player_name CONTAINS $player_name
        RETURN p.player_name AS name, 
               p.player_element AS id
        LIMIT 10
        """
        
        return self._execute_query(query, {"player_name": player_name})
    
    # =========================================================================
    # Query 2: Top Scorers by Position
    # =========================================================================
    
    def get_top_scorers(self, position: str, season: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get top goal scorers for a specific position in a season.
        
        Args:
            position: Player position (FWD, MID, DEF, GK)
            season: Season (e.g., "2021-22", "2022-23")
            limit: Maximum number of results
            
        Returns:
            List of top scorers with stats
        """
        query = """
        MATCH (p:Player)-[played:PLAYED_IN]->(f:Fixture)<-[:HAS_FIXTURE]-(gw:Gameweek)
        WHERE played.position = $position 
          AND gw.season = $season
        WITH p.player_name AS player, 
             played.position AS position,
             SUM(played.goals_scored) AS total_goals,
             SUM(played.assists) AS total_assists,
             SUM(played.total_points) AS total_points
        ORDER BY total_goals DESC
        LIMIT $limit
        RETURN player, position, total_goals, total_assists, total_points
        """
        
        return self._execute_query(query, {
            "position": position,
            "season": season,
            "limit": limit
        })
    
    # =========================================================================
    # Query 3: Player Season Statistics
    # =========================================================================
    
    def get_player_season_stats(self, player_name: str, season: str) -> List[Dict[str, Any]]:
        """
        Get comprehensive statistics for a player in a specific season.
        
        Args:
            player_name: Player name or partial name
            season: Season (e.g., "2021-22", "2022-23")
            
        Returns:
            Player's complete season statistics
        """
        query = """
        MATCH (p:Player)-[played:PLAYED_IN]->(f:Fixture)<-[:HAS_FIXTURE]-(gw:Gameweek)
        WHERE p.player_name CONTAINS $player_name 
          AND gw.season = $season
        RETURN p.player_name AS player,
               gw.season AS season,
               COUNT(f) AS games_played,
               SUM(played.minutes) AS total_minutes,
               SUM(played.goals_scored) AS goals,
               SUM(played.assists) AS assists,
               SUM(played.total_points) AS total_points,
               SUM(played.bonus) AS bonus_points,
               SUM(played.clean_sheets) AS clean_sheets,
               SUM(played.yellow_cards) AS yellow_cards,
               SUM(played.red_cards) AS red_cards,
               AVG(played.ict_index) AS avg_ict_index
        """
        
        return self._execute_query(query, {
            "player_name": player_name,
            "season": season
        })
    
    # =========================================================================
    # Query 4: Players by Team
    # =========================================================================
    
    def get_team_players(self, team_name: str, season: str) -> List[Dict[str, Any]]:
        """
        Get all players who played for a specific team.
        
        Args:
            team_name: Team name
            season: Season (e.g., "2021-22", "2022-23")
            
        Returns:
            List of players with their stats
        """
        query = """
        MATCH (p:Player)-[:PLAYS_FOR]->(t:Team)
        MATCH (p)-[played:PLAYED_IN]->(f:Fixture)<-[:HAS_FIXTURE]-(gw:Gameweek)
        WHERE t.name = $team_name 
          AND gw.season = $season
        WITH p.player_name AS player, 
             played.position AS position,
             SUM(played.total_points) AS total_points
        RETURN player, position, total_points
        ORDER BY total_points DESC
        """
        
        return self._execute_query(query, {
            "team_name": team_name,
            "season": season
        })
    
    # =========================================================================
    # Query 5: Gameweek Top Performers
    # =========================================================================
    
    def get_gameweek_top_performers(self, gameweek: int, season: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Find top performers in a specific gameweek.
        
        Args:
            gameweek: Gameweek number
            season: Season (e.g., "2021-22", "2022-23")
            limit: Maximum number of results
            
        Returns:
            List of top performers in the gameweek
        """
        query = """
        MATCH (p:Player)-[played:PLAYED_IN]->(f:Fixture)<-[:HAS_FIXTURE]-(gw:Gameweek)
        WHERE gw.GW_number = $gameweek 
          AND gw.season = $season
        RETURN p.player_name AS player,
               played.position AS position,
               played.total_points AS points,
               played.goals_scored AS goals,
               played.assists AS assists,
               played.bonus AS bonus,
               played.minutes AS minutes
        ORDER BY played.total_points DESC
        LIMIT $limit
        """
        
        return self._execute_query(query, {
            "gameweek": gameweek,
            "season": season,
            "limit": limit
        })
    
    # =========================================================================
    # Query 6: Compare Two Players
    # =========================================================================
    
    def compare_players(self, player1: str, player2: str, season: str) -> List[Dict[str, Any]]:
        """
        Compare statistics between two players in a season.
        
        Args:
            player1: First player name
            player2: Second player name
            season: Season (e.g., "2021-22", "2022-23")
            
        Returns:
            Comparison statistics for both players
        """
        query = """
        MATCH (p:Player)-[played:PLAYED_IN]->(f:Fixture)<-[:HAS_FIXTURE]-(gw:Gameweek)
        WHERE (p.player_name CONTAINS $player1 OR p.player_name CONTAINS $player2)
          AND gw.season = $season
        WITH p.player_name AS player,
             SUM(played.goals_scored) AS goals,
             SUM(played.assists) AS assists,
             SUM(played.total_points) AS total_points,
             SUM(played.minutes) AS minutes,
             AVG(played.ict_index) AS avg_ict,
             COUNT(gw) AS games_played
        RETURN player, goals, assists, total_points, minutes, avg_ict, games_played
        ORDER BY total_points DESC
        """
        
        return self._execute_query(query, {
            "player1": player1,
            "player2": player2,
            "season": season
        })
    
    # =========================================================================
    # Query 7: High Performers by Threshold
    # =========================================================================
    
    def get_high_performers(self, min_goals: int, season: str) -> List[Dict[str, Any]]:
        """
        Find players exceeding specific performance thresholds.
        
        Args:
            min_goals: Minimum number of goals
            season: Season (e.g., "2021-22", "2022-23")
            
        Returns:
            List of high-performing players
        """
        query = """
        MATCH (p:Player)-[played:PLAYED_IN]->(f:Fixture)<-[:HAS_FIXTURE]-(gw:Gameweek)
        WHERE gw.season = $season
        WITH p.player_name AS player,
             played.position AS position,
             SUM(played.goals_scored) AS total_goals,
             SUM(played.assists) AS total_assists,
             SUM(played.total_points) AS total_points
        WHERE total_goals >= $min_goals
        RETURN player, position, total_goals, total_assists, total_points
        ORDER BY total_goals DESC
        """
        
        return self._execute_query(query, {
            "min_goals": min_goals,
            "season": season
        })
    
    # =========================================================================
    # Query 8: Best Assisters by Position
    # =========================================================================
    
    def get_top_assisters(self, position: str, season: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get top assist providers for a specific position.
        
        Args:
            position: Player position (FWD, MID, DEF, GK)
            season: Season (e.g., "2021-22", "2022-23")
            limit: Maximum number of results
            
        Returns:
            List of top assisters
        """
        query = """
        MATCH (p:Player)-[played:PLAYED_IN]->(f:Fixture)<-[:HAS_FIXTURE]-(gw:Gameweek)
        WHERE played.position = $position 
          AND gw.season = $season
        WITH p.player_name AS player,
             played.position AS position,
             SUM(played.assists) AS total_assists,
             SUM(played.goals_scored) AS total_goals,
             SUM(played.total_points) AS total_points
        ORDER BY total_assists DESC
        LIMIT $limit
        RETURN player, position, total_assists, total_goals, total_points
        """
        
        return self._execute_query(query, {
            "position": position,
            "season": season,
            "limit": limit
        })
    
    # =========================================================================
    # Query 9: Player Form (Recent Gameweeks)
    # =========================================================================
    
    def get_player_form(self, player_name: str, season: str, last_n_gw: int = 5) -> List[Dict[str, Any]]:
        """
        Analyze player performance over recent gameweeks.
        
        Args:
            player_name: Player name or partial name
            season: Season (e.g., "2021-22", "2022-23")
            last_n_gw: Number of recent gameweeks to analyze
            
        Returns:
            Player's recent form statistics
        """
        query = """
        MATCH (p:Player)-[played:PLAYED_IN]->(f:Fixture)<-[:HAS_FIXTURE]-(gw:Gameweek)
        WHERE p.player_name CONTAINS $player_name 
          AND gw.season = $season
        WITH p.player_name AS player,
             gw.GW_number AS gameweek,
             played.total_points AS points,
             played.goals_scored AS goals,
             played.assists AS assists,
             played.minutes AS minutes
        ORDER BY gameweek DESC
        LIMIT $last_n_gw
        RETURN player, gameweek, points, goals, assists, minutes
        ORDER BY gameweek ASC
        """
        
        return self._execute_query(query, {
            "player_name": player_name,
            "season": season,
            "last_n_gw": last_n_gw
        })
    
    # =========================================================================
    # Query 10: Best Players by ICT Index
    # =========================================================================
    
    def get_top_ict_players(self, position: str, season: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Find players with highest ICT (Influence, Creativity, Threat) index.
        
        Args:
            position: Player position (FWD, MID, DEF, GK)
            season: Season (e.g., "2021-22", "2022-23")
            limit: Maximum number of results
            
        Returns:
            List of top ICT performers
        """
        query = """
        MATCH (p:Player)-[played:PLAYED_IN]->(f:Fixture)<-[:HAS_FIXTURE]-(gw:Gameweek)
        WHERE played.position = $position 
          AND gw.season = $season
          AND played.minutes > 0
        WITH p.player_name AS player,
             played.position AS position,
             AVG(played.ict_index) AS avg_ict_index,
             AVG(played.influence) AS avg_influence,
             AVG(played.creativity) AS avg_creativity,
             AVG(played.threat) AS avg_threat,
             SUM(played.total_points) AS total_points
        ORDER BY avg_ict_index DESC
        LIMIT $limit
        RETURN player, position, 
               ROUND(avg_ict_index * 10) / 10 AS avg_ict,
               ROUND(avg_influence * 10) / 10 AS avg_influence,
               ROUND(avg_creativity * 10) / 10 AS avg_creativity,
               ROUND(avg_threat * 10) / 10 AS avg_threat,
               total_points
        """
        
        return self._execute_query(query, {
            "position": position,
            "season": season,
            "limit": limit
        })
    
    # =========================================================================
    # Query 11: Top Clean Sheet Defenders/Goalkeepers
    # =========================================================================
    
    def get_top_clean_sheet_keepers(self, position: str, season: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Find players with most clean sheets (typically defenders and goalkeepers).
        
        Args:
            position: Player position (DEF or GK typically)
            season: Season (e.g., "2021-22", "2022-23")
            limit: Maximum number of results
            
        Returns:
            List of top clean sheet players
        """
        query = """
        MATCH (p:Player)-[played:PLAYED_IN]->(f:Fixture)<-[:HAS_FIXTURE]-(gw:Gameweek)
        WHERE played.position = $position 
          AND gw.season = $season
          AND played.minutes > 0
        WITH p.player_name AS player,
             played.position AS position,
             SUM(played.clean_sheets) AS total_clean_sheets,
             SUM(played.goals_scored) AS total_goals,
             SUM(played.assists) AS total_assists,
             SUM(played.total_points) AS total_points,
             COUNT(f) AS games_played
        ORDER BY total_clean_sheets DESC
        LIMIT $limit
        RETURN player, position, total_clean_sheets, total_goals, 
               total_assists, total_points, games_played
        """
        
        return self._execute_query(query, {
            "position": position,
            "season": season,
            "limit": limit
        })
    
    # =========================================================================
    # Helper Methods
    # =========================================================================
    
    def _execute_query(self, query: str, parameters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Execute a Cypher query and return results.
        
        Args:
            query: Cypher query string
            parameters: Query parameters
            
        Returns:
            List of result records as dictionaries
        """
        try:
            with self.driver.session(database=NEO4J_DATABASE) as session:
                result = session.run(query, parameters)
                records = [dict(record) for record in result]
                logger.info(f"Query executed successfully. Retrieved {len(records)} records.")
                return records
        except Exception as e:
            logger.error(f"Query execution failed: {str(e)}")
            logger.error(f"Query: {query}")
            logger.error(f"Parameters: {parameters}")
            return []
    
    def format_results_for_llm(self, results: List[Dict[str, Any]], query_type: str) -> str:
        """
        Format query results into a readable string for LLM context.
        
        Args:
            results: Query results
            query_type: Type of query executed
            
        Returns:
            Formatted string representation of results
        """
        if not results:
            return f"No results found for {query_type} query."
        
        formatted = f"=== {query_type.upper()} RESULTS ===\n\n"
        
        for i, record in enumerate(results, 1):
            formatted += f"{i}. "
            for key, value in record.items():
                if isinstance(value, float):
                    formatted += f"{key}: {value:.2f}, "
                else:
                    formatted += f"{key}: {value}, "
            formatted = formatted.rstrip(", ") + "\n"
        
        return formatted
    
    # =========================================================================
    # Query 12: Best Value Players (Points per Price)
    # =========================================================================
    
    def get_best_value_players(self, position: str, season: str, 
                               max_price: float = None, min_points: int = 100,
                               limit: int = 10) -> List[Dict[str, Any]]:
        """
        Find best value-for-money players (high points per price ratio).
        
        Args:
            position: Player position (FWD, MID, DEF, GK)
            season: Season (e.g., "2021-22", "2022-23")
            max_price: Maximum price threshold (e.g., 7.0 for £7.0m)
            min_points: Minimum total points threshold
            limit: Maximum number of results
            
        Returns:
            List of players with best value (points per million)
        """
        query = """
        MATCH (p:Player)-[played:PLAYED_IN]->(f:Fixture)<-[:HAS_FIXTURE]-(gw:Gameweek)
        WHERE played.position = $position 
          AND gw.season = $season
          AND played.minutes > 0
          AND p.value IS NOT NULL
        WITH p.player_name AS player,
             p.value AS price,
             played.position AS position,
             SUM(played.total_points) AS total_points,
             SUM(played.goals_scored) AS total_goals,
             SUM(played.assists) AS total_assists,
             SUM(played.minutes) AS total_minutes
        WHERE total_points >= $min_points
        """
        
        # Add price filter if specified
        if max_price is not None:
            query += " AND price <= $max_price\n"
        
        query += """
        WITH player, price, position, total_points, total_goals, total_assists, total_minutes,
             (total_points * 10.0 / price) AS points_per_million
        ORDER BY points_per_million DESC
        LIMIT $limit
        RETURN player, price, position, total_points, total_goals, total_assists, 
               total_minutes, ROUND(points_per_million * 10) / 10 AS value_score
        """
        
        params = {
            "position": position,
            "season": season,
            "min_points": min_points,
            "limit": limit
        }
        
        if max_price is not None:
            params["max_price"] = max_price
        
        return self._execute_query(query, params)
