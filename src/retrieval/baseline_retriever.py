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
    
    def get_top_scorers(self, position: Optional[str] = None, season: str = "2022-23", limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get top goal scorers for a specific position in a season.
        
        Args:
            position: Player position (FWD, MID, DEF, GK) or None for all positions
            season: Season (e.g., "2021-22", "2022-23")
            limit: Maximum number of results
            
        Returns:
            List of top scorers with stats
        """
        # Build query conditionally based on whether position is specified
        if position:
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
            params = {"position": position, "season": season, "limit": limit}
        else:
            query = """
            MATCH (p:Player)-[played:PLAYED_IN]->(f:Fixture)<-[:HAS_FIXTURE]-(gw:Gameweek)
            WHERE gw.season = $season
            WITH p.player_name AS player, 
                 played.position AS position,
                 SUM(played.goals_scored) AS total_goals,
                 SUM(played.assists) AS total_assists,
                 SUM(played.total_points) AS total_points
            ORDER BY total_goals DESC
            LIMIT $limit
            RETURN player, position, total_goals, total_assists, total_points
            """
            params = {"season": season, "limit": limit}
        
        return self._execute_query(query, params)
    
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
    
    def get_gameweek_top_performers(self, gameweek: int, season: str, 
                                   position: str = None, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Find top performers in a specific gameweek.
        
        Args:
            gameweek: Gameweek number
            season: Season (e.g., "2021-22", "2022-23")
            position: Optional position filter (FWD, MID, DEF, GK)
            limit: Maximum number of results
            
        Returns:
            List of top performers in the gameweek
        """
        query = """
        MATCH (p:Player)-[played:PLAYED_IN]->(f:Fixture)<-[:HAS_FIXTURE]-(gw:Gameweek)
        WHERE gw.GW_number = $gameweek 
          AND gw.season = $season
        """
        
        # Add position filter if specified
        if position:
            query += " AND played.position = $position\n"
        
        query += """
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
        
        params = {
            "gameweek": gameweek,
            "season": season,
            "limit": limit
        }
        
        if position:
            params["position"] = position
        
        return self._execute_query(query, params)
    
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
    
    def get_top_assisters(self, position: Optional[str] = None, season: str = "2022-23", limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get top assist providers for a specific position.
        
        Args:
            position: Player position (FWD, MID, DEF, GK) or None for all positions
            season: Season (e.g., "2021-22", "2022-23")
            limit: Maximum number of results
            
        Returns:
            List of top assisters
        """
        # Build query conditionally based on whether position is specified
        if position:
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
            params = {"position": position, "season": season, "limit": limit}
        else:
            query = """
            MATCH (p:Player)-[played:PLAYED_IN]->(f:Fixture)<-[:HAS_FIXTURE]-(gw:Gameweek)
            WHERE gw.season = $season
            WITH p.player_name AS player,
                 played.position AS position,
                 SUM(played.assists) AS total_assists,
                 SUM(played.goals_scored) AS total_goals,
                 SUM(played.total_points) AS total_points
            ORDER BY total_assists DESC
            LIMIT $limit
            RETURN player, position, total_assists, total_goals, total_points
            """
            params = {"season": season, "limit": limit}
        
        return self._execute_query(query, params)
    
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
                               max_price: float = None, min_price: float = None,
                               min_points: int = 100, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Find best value-for-money players (high points per price ratio).
        
        Args:
            position: Player position (FWD, MID, DEF, GK)
            season: Season (e.g., "2021-22", "2022-23")
            max_price: Maximum price threshold (e.g., 7.0 for £7.0m)
            min_price: Minimum price threshold (e.g., 7.0 for £7.0m)
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
          AND played.value IS NOT NULL
        WITH p.player_name AS player,
             AVG(played.value) / 10.0 AS price,
             played.position AS position,
             SUM(played.total_points) AS total_points,
             SUM(played.goals_scored) AS total_goals,
             SUM(played.assists) AS total_assists,
             SUM(played.minutes) AS total_minutes
        WHERE total_points >= $min_points
        """
        
        # Add price filters if specified
        if max_price is not None:
            query += " AND price <= $max_price\n"
        if min_price is not None:
            query += " AND price >= $min_price\n"
        
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
        if min_price is not None:
            params["min_price"] = min_price
        
        return self._execute_query(query, params)
    
    def get_most_expensive_players(self, season: str = "2021-22", position: str = None, 
                                    limit: int = 10, min_points: int = 0) -> List[Dict]:
        """
        Get the most expensive players in a season.
        
        Args:
            season: Season string (e.g., "2021-22")
            position: Filter by position (optional)
            limit: Number of players to return
            min_points: Minimum total points threshold
            
        Returns:
            List of players with price and stats
        """
        query = """
        MATCH (p:Player)-[played:PLAYED_IN]->(f:Fixture)<-[:HAS_FIXTURE]-(gw:Gameweek)
        WHERE gw.season = $season
          AND played.minutes > 0
          AND played.value IS NOT NULL
        """
        
        if position:
            query += " AND played.position = $position\n"
        
        query += """
        WITH p.player_name AS player,
             AVG(played.value) / 10.0 AS price,
             played.position AS position,
             SUM(played.total_points) AS total_points,
             SUM(played.goals_scored) AS total_goals,
             SUM(played.assists) AS total_assists,
             SUM(played.minutes) AS total_minutes,
             SUM(played.clean_sheets) AS clean_sheets
        WHERE total_points >= $min_points
        WITH player, price, position, total_points, total_goals, total_assists, 
             total_minutes, clean_sheets
        ORDER BY price DESC
        LIMIT $limit
        RETURN player AS player_name,
               price,
               position,
               total_points,
               total_goals,
               total_assists,
               total_minutes,
               clean_sheets
        """
        
        params = {
            "season": season,
            "limit": limit,
            "min_points": min_points
        }
        
        if position:
            params["position"] = position
        
        return self._execute_query(query, params)
    
    def build_squad_under_budget(self, season: str = "2021-22", budget: float = 100.0,
                                  min_points: int = 30, min_games: int = 10) -> Dict[str, Any]:
        """
        Build an optimal 15-player FPL squad under budget constraint.
        Squad composition: 2 GK, 5 DEF, 5 MID, 3 FWD
        Optimization: Maximize value ratio (points per million)
        
        Args:
            season: Season string (e.g., "2021-22")
            budget: Total budget in millions (default 100.0)
            min_points: Minimum points threshold (default 30)
            min_games: Minimum games played (default 10)
            
        Returns:
            Dictionary with squad players and summary stats
        """
        # Query to get top value players by position
        query = """
        MATCH (p:Player)-[r:PLAYED_IN]->(f:Fixture)<-[:HAS_FIXTURE]-(gw:Gameweek)
        WHERE r.total_points IS NOT NULL
          AND r.value IS NOT NULL
          AND gw.season = $season
          AND r.minutes > 0
        WITH p.player_name AS player_name,
             r.position AS position,
             SUM(r.total_points) AS total_points,
             SUM(r.goals_scored) AS goals,
             SUM(r.assists) AS assists,
             AVG(r.value) / 10.0 AS price,
             COUNT(DISTINCT f) AS games_played
        WHERE total_points >= $min_points
          AND games_played >= $min_games
          AND price IS NOT NULL
        WITH position, player_name, total_points, goals, assists, price,
             toFloat(total_points) / (price * 10.0) AS value_ratio
        ORDER BY position, value_ratio DESC
        
        WITH position, COLLECT({
            player: player_name,
            total_points: total_points,
            goals: goals,
            assists: assists,
            price: price,
            value_ratio: value_ratio
        }) AS players_by_position
        
        RETURN position, players_by_position
        """
        
        params = {
            "season": season,
            "min_points": min_points,
            "min_games": min_games
        }
        
        results = self._execute_query(query, params)
        
        # Organize players by position
        players_by_pos = {}
        for record in results:
            pos = record['position']
            players = record['players_by_position']
            players_by_pos[pos] = players
        
        # FPL formation requirements
        formation = {
            'GK': 2,
            'DEF': 5,
            'MID': 5,
            'FWD': 3
        }
        
        # Greedy selection - pick best value ratio players per position
        selected_squad = []
        total_cost = 0.0
        total_points = 0
        
        for pos, count in formation.items():
            if pos not in players_by_pos:
                continue
                
            available = players_by_pos[pos]
            selected = 0
            
            for player_data in available:
                if selected >= count:
                    break
                    
                player_price = player_data['price']
                
                # Check if adding this player keeps us under budget
                if total_cost + player_price <= budget:
                    selected_squad.append({
                        'player_name': player_data['player'],
                        'position': pos,
                        'price': player_price,
                        'total_points': player_data['total_points'],
                        'goals': player_data['goals'],
                        'assists': player_data['assists'],
                        'value_ratio': player_data['value_ratio']
                    })
                    total_cost += player_price
                    total_points += player_data['total_points']
                    selected += 1
        
        return {
            'squad': selected_squad,
            'total_cost': round(total_cost, 1),
            'remaining_budget': round(budget - total_cost, 1),
            'total_points': total_points,
            'squad_size': len(selected_squad),
            'season': season,
            'formation': {pos: len([p for p in selected_squad if p['position'] == pos]) 
                         for pos in formation.keys()}
        }
