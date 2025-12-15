"""
Entity Extraction Module

Extracts FPL-specific entities from user input:
- Player names
- Team names
- Positions (FWD, MID, DEF, GK)
- Seasons
- Gameweeks
- Statistics (points, goals, assists, etc.)
- Numerical thresholds
"""

import re
from typing import Dict, List, Any, Optional
import logging
from neo4j import GraphDatabase
from config.config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, NEO4J_DATABASE

logger = logging.getLogger(__name__)


class EntityExtractor:
    """
    Extract FPL-specific entities from natural language queries.
    Uses pattern matching and database lookup for accurate entity recognition.
    """
    
    def __init__(self):
        """Initialize entity extractor with Neo4j connection for entity validation."""
        self.driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
        )
        
        # Cache of known entities from database
        self._player_cache = None
        self._team_cache = None
        
        # Predefined patterns
        self.positions = ["FWD", "MID", "DEF", "GK", "FORWARD", "MIDFIELDER", "DEFENDER", "GOALKEEPER"]
        self.position_map = {
            # General positions
            "forward": "FWD", "forwards": "FWD", "striker": "FWD", "strikers": "FWD",
            "midfielder": "MID", "midfielders": "MID", "mid": "MID",
            "defender": "DEF", "defenders": "DEF", "def": "DEF", "defence": "DEF", "defense": "DEF",
            "goalkeeper": "GK", "goalkeepers": "GK", "keeper": "GK", "keepers": "GK",
            "fwd": "FWD", "gk": "GK",
            # Specific defender positions (all map to DEF since DB doesn't differentiate)
            "lb": "DEF", "left back": "DEF", "left-back": "DEF", "leftback": "DEF",
            "rb": "DEF", "right back": "DEF", "right-back": "DEF", "rightback": "DEF",
            "cb": "DEF", "centre back": "DEF", "center back": "DEF", "centre-back": "DEF", "center-back": "DEF",
            "fullback": "DEF", "full back": "DEF", "full-back": "DEF", "fb": "DEF",
            "wingback": "DEF", "wing back": "DEF", "wing-back": "DEF", "wb": "DEF",
            # Specific midfielder positions
            "cm": "MID", "central midfielder": "MID", "central-midfielder": "MID",
            "cdm": "MID", "defensive midfielder": "MID", "dm": "MID",
            "cam": "MID", "attacking midfielder": "MID", "am": "MID",
            "lm": "MID", "left midfielder": "MID", "left-midfielder": "MID",
            "rm": "MID", "right midfielder": "MID", "right-midfielder": "MID",
            "winger": "MID", "wingers": "MID", "lw": "MID", "rw": "MID",
            # Specific forward positions
            "st": "FWD", "cf": "FWD", "centre forward": "FWD", "center forward": "FWD"
        }
        
        logger.info("Entity extractor initialized")
    
    def close(self):
        """Close Neo4j driver connection."""
        if self.driver:
            self.driver.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    # =========================================================================
    # Main Extraction Method
    # =========================================================================
    
    def extract(self, query: str) -> Dict[str, Any]:
        """
        Extract all entities from a user query.
        
        Args:
            query: User's natural language query
            
        Returns:
            Dictionary containing extracted entities
        """
        entities = {
            "player_names": self.extract_player_names(query),
            "team_names": self.extract_team_names(query),
            "positions": self.extract_positions(query),
            "seasons": self.extract_seasons(query),
            "gameweeks": self.extract_gameweeks(query),
            "thresholds": self.extract_thresholds(query),
            "stats_mentioned": self.extract_stats(query),
            "limit": self.extract_limit(query),
            "raw_query": query
        }
        
        logger.info(f"Extracted entities: {entities}")
        return entities
    
    # =========================================================================
    # Player Name Extraction
    # =========================================================================
    
    def extract_player_names(self, query: str) -> List[str]:
        """
        Extract player names from query.
        Uses database lookup for validation.
        
        Args:
            query: User query
            
        Returns:
            List of player names found
        """
        # Load player cache if not loaded
        if self._player_cache is None:
            self._load_player_cache()
        
        found_players = []
        
        # Search for known players in query
        for player_name in self._player_cache:
            # Check for full name or last name
            name_lower = player_name.lower()
            query_lower = query.lower()
            
            # Check full name match
            if name_lower in query_lower:
                found_players.append(player_name)
                continue
            
            # Check last name match (for common names like "Salah", "Kane")
            parts = player_name.split()
            if len(parts) > 1:
                last_name = parts[-1].lower()
                # Use word boundary to avoid partial matches
                if re.search(rf'\b{re.escape(last_name)}\b', query_lower):
                    if player_name not in found_players:  # Avoid duplicates
                        found_players.append(player_name)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_players = []
        for player in found_players:
            if player not in seen:
                seen.add(player)
                unique_players.append(player)
        
        return unique_players[:5]  # Limit to top 5 matches
    
    def _load_player_cache(self):
        """Load all player names from database into cache."""
        try:
            with self.driver.session(database=NEO4J_DATABASE) as session:
                result = session.run("MATCH (p:Player) RETURN DISTINCT p.player_name as name")
                self._player_cache = [record["name"] for record in result if record["name"]]
                logger.info(f"Loaded {len(self._player_cache)} players into cache")
        except Exception as e:
            logger.error(f"Failed to load player cache: {str(e)}")
            self._player_cache = []
    
    # =========================================================================
    # Team Name Extraction
    # =========================================================================
    
    def extract_team_names(self, query: str) -> List[str]:
        """
        Extract team names from query.
        
        Args:
            query: User query
            
        Returns:
            List of team names found
        """
        # Load team cache if not loaded
        if self._team_cache is None:
            self._load_team_cache()
        
        found_teams = []
        query_lower = query.lower()
        
        for team_name in self._team_cache:
            if team_name.lower() in query_lower:
                found_teams.append(team_name)
        
        return found_teams
    
    def _load_team_cache(self):
        """Load all team names from database into cache."""
        try:
            with self.driver.session(database=NEO4J_DATABASE) as session:
                result = session.run("MATCH (t:Team) RETURN t.name as name")
                self._team_cache = [record["name"] for record in result]
                logger.info(f"Loaded {len(self._team_cache)} teams into cache")
        except Exception as e:
            logger.error(f"Failed to load team cache: {str(e)}")
            self._team_cache = []
    
    # =========================================================================
    # Position Extraction
    # =========================================================================
    
    def extract_positions(self, query: str) -> List[str]:
        """
        Extract player positions from query.
        
        Args:
            query: User query
            
        Returns:
            List of positions (FWD, MID, DEF, GK)
        """
        positions_found = []
        query_lower = query.lower()
        
        # Check for position keywords
        for keyword, position in self.position_map.items():
            if re.search(rf'\b{keyword}s?\b', query_lower):
                if position not in positions_found:
                    positions_found.append(position)
        
        return positions_found
    
    # =========================================================================
    # Season Extraction
    # =========================================================================
    
    def extract_seasons(self, query: str) -> List[str]:
        """
        Extract seasons from query (e.g., "2021-22", "2022-23", "2022/2023").
        
        Args:
            query: User query
            
        Returns:
            List of seasons found
        """
        seasons = []
        
        # Pattern 1: 2022/2023 (full year format) - convert to short format
        pattern_full = r'\b(20\d{2})[/-](20\d{2})\b'
        for match in re.finditer(pattern_full, query):
            year1 = match.group(1)
            year2 = match.group(2)
            # Convert to short format: 2022/2023 -> 2022-23
            season = f"{year1}-{year2[-2:]}"
            if season not in seasons:
                seasons.append(season)
        
        # Pattern 2: 2021-22, 2022-23, etc. (short format)
        pattern_short = r'\b(20\d{2})[-/](\d{2})\b'
        for match in re.finditer(pattern_short, query):
            # Skip if already matched by full pattern
            if not re.match(r'20\d{2}', match.group(2)):
                season = f"{match.group(1)}-{match.group(2)}"
                if season not in seasons:
                    seasons.append(season)
        
        # If no season found, return most recent season as default
        if not seasons:
            # Could be made configurable
            seasons = ["2022-23"]  # Default season (updated to latest available)
        
        return seasons
    
    # =========================================================================
    # Gameweek Extraction
    # =========================================================================
    
    def extract_gameweeks(self, query: str) -> List[int]:
        """
        Extract gameweek numbers from query.
        
        Args:
            query: User query
            
        Returns:
            List of gameweek numbers
        """
        gameweeks = []
        
        # Pattern: "gameweek 5", "GW 10", "week 3"
        patterns = [
            r'\bgameweek\s+(\d+)\b',
            r'\bgw\s*(\d+)\b',
            r'\bweek\s+(\d+)\b',
        ]
        
        query_lower = query.lower()
        
        for pattern in patterns:
            matches = re.finditer(pattern, query_lower)
            for match in matches:
                gw = int(match.group(1))
                if 1 <= gw <= 38 and gw not in gameweeks:  # Valid gameweek range
                    gameweeks.append(gw)
        
        return gameweeks
    
    # =========================================================================
    # Threshold Extraction
    # =========================================================================
    
    def extract_thresholds(self, query: str) -> Dict[str, Any]:
        """
        Extract numerical thresholds from query.
        Examples: "more than 15 goals", "at least 200 points", ">= 10 assists"
        
        Args:
            query: User query
            
        Returns:
            Dictionary with threshold information
        """
        thresholds = {}
        
        # Patterns for threshold extraction
        patterns = [
            # "more than X", "over X", "above X"
            (r'(?:more than|over|above)\s+(\d+)\s+(\w+)', 'gt'),
            # "at least X", "minimum X", ">= X"
            (r'(?:at least|minimum|>=)\s+(\d+)\s+(\w+)', 'gte'),
            # "less than X", "under X", "below X"
            (r'(?:less than|under|below)\s+(\d+)\s+(\w+)', 'lt'),
            # "exactly X", "= X"
            (r'(?:exactly|=)\s+(\d+)\s+(\w+)', 'eq'),
            # "> X", "< X" operators
            (r'>\s*(\d+)\s+(\w+)', 'gt'),
            (r'<\s*(\d+)\s+(\w+)', 'lt'),
        ]
        
        query_lower = query.lower()
        
        for pattern, operator in patterns:
            matches = re.finditer(pattern, query_lower)
            for match in matches:
                value = int(match.group(1))
                stat_type = match.group(2)
                
                # Map common stat mentions
                stat_mapping = {
                    'goals': 'goals_scored',
                    'goal': 'goals_scored',
                    'assists': 'assists',
                    'assist': 'assists',
                    'points': 'total_points',
                    'point': 'total_points',
                }
                
                stat = stat_mapping.get(stat_type, stat_type)
                thresholds[stat] = {'value': value, 'operator': operator}
        
        return thresholds
    
    # =========================================================================
    # Stats Extraction
    # =========================================================================
    
    def extract_stats(self, query: str) -> List[str]:
        """
        Extract mentioned statistics from query.
        
        Args:
            query: User query
            
        Returns:
            List of stat types mentioned
        """
        stats = []
        query_lower = query.lower()
        
        stat_keywords = {
            'goals': ['goals', 'goal', 'scored', 'scoring'],
            'assists': ['assists', 'assist', 'playmaker'],
            'points': ['points', 'point', 'total points'],
            'clean_sheets': ['clean sheet', 'clean sheets'],
            'ict': ['ict', 'influence', 'creativity', 'threat'],
            'bonus': ['bonus', 'bps'],
            'minutes': ['minutes', 'played'],
            'form': ['form'],
        }
        
        for stat, keywords in stat_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                if stat not in stats:
                    stats.append(stat)
        
        return stats
    
    # =========================================================================
    # Limit Extraction
    # =========================================================================
    
    def extract_limit(self, query: str) -> int:
        """
        Extract result limit from query (e.g., "top 10", "best 5").
        
        Args:
            query: User query
            
        Returns:
            Limit number (default 10)
        """
        # Pattern: "top 5", "best 10", "first 3"
        patterns = [
            r'\btop\s+(\d+)\b',
            r'\bbest\s+(\d+)\b',
            r'\bfirst\s+(\d+)\b',
        ]
        
        query_lower = query.lower()
        
        for pattern in patterns:
            match = re.search(pattern, query_lower)
            if match:
                limit = int(match.group(1))
                return min(limit, 50)  # Cap at 50
        
        return 10  # Default limit
    
    # =========================================================================
    # Helper: Get Default Season
    # =========================================================================
    
    def get_default_season(self) -> str:
        """
        Get the default season from database or use fallback.
        
        Returns:
            Default season string
        """
        try:
            with self.driver.session(database=NEO4J_DATABASE) as session:
                result = session.run("MATCH (s:Season) RETURN s.season_name as name ORDER BY name DESC LIMIT 1")
                record = result.single()
                if record:
                    return record["name"]
        except Exception as e:
            logger.error(f"Failed to get default season: {str(e)}")
        
        return "2021-22"  # Fallback
