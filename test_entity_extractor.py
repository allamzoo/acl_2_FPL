"""
Entity Extractor Test Script
Tests extraction of FPL entities from natural language queries.
"""

from src.preprocessing.entity_extractor import EntityExtractor
from colorama import init, Fore, Style
import json

init(autoreset=True)


def test_entity_extractor():
    """Test entity extraction with various queries."""
    
    print("=" * 100)
    print(f"{Fore.CYAN}{Style.BRIGHT}ENTITY EXTRACTOR TEST")
    print("=" * 100)
    
    test_queries = [
        # Player names
        "Who is Mohamed Salah?",
        "Show me stats for Harry Kane and Son",
        "Compare Salah vs De Bruyne",
        
        # Team names
        "Liverpool players in 2021-22",
        "Show me Arsenal's squad",
        "Manchester City team performance",
        
        # Positions
        "Top forwards in the league",
        "Best midfielders and defenders",
        "Who are the top goalkeepers?",
        
        # Seasons
        "Player stats for 2021-22 season",
        "Performance in 2022-23",
        "Compare 2021/22 and 2022/23",
        
        # Gameweeks
        "Best players in gameweek 1",
        "GW 10 top performers",
        "Week 5 statistics",
        
        # Thresholds
        "Players with more than 15 goals",
        "Who scored at least 20 goals?",
        "Forwards with over 200 points",
        "Players with >= 10 assists",
        
        # Limits
        "Top 5 scorers",
        "Best 10 midfielders",
        "First 3 players",
        
        # Complex queries
        "Top 10 forwards with more than 15 goals in 2021-22",
        "Compare Salah and Kane's performance in gameweek 5",
        "Liverpool midfielders with at least 100 points in 2021-22",
        "Show me Arsenal's top 5 scorers for the season",
    ]
    
    with EntityExtractor() as extractor:
        for i, query in enumerate(test_queries, 1):
            print(f"\n{Fore.YELLOW}{'─' * 100}")
            print(f"{Fore.YELLOW}{Style.BRIGHT}Test {i}: {Fore.WHITE}{query}")
            print(f"{Fore.YELLOW}{'─' * 100}")
            
            entities = extractor.extract(query)
            
            # Display extracted entities
            print(f"{Fore.CYAN}Players: {Fore.WHITE}{entities['player_names'] or 'None'}")
            print(f"{Fore.CYAN}Teams: {Fore.WHITE}{entities['team_names'] or 'None'}")
            print(f"{Fore.CYAN}Positions: {Fore.WHITE}{entities['positions'] or 'None'}")
            print(f"{Fore.CYAN}Seasons: {Fore.WHITE}{entities['seasons'] or 'None'}")
            print(f"{Fore.CYAN}Gameweeks: {Fore.WHITE}{entities['gameweeks'] or 'None'}")
            print(f"{Fore.CYAN}Thresholds: {Fore.WHITE}{entities['thresholds'] or 'None'}")
            print(f"{Fore.CYAN}Stats Mentioned: {Fore.WHITE}{entities['stats_mentioned'] or 'None'}")
            print(f"{Fore.CYAN}Limit: {Fore.WHITE}{entities['limit']}")
    
    print(f"\n{Fore.GREEN}{'=' * 100}")
    print(f"{Fore.GREEN}{Style.BRIGHT}✓ ALL TESTS COMPLETED")
    print(f"{Fore.GREEN}{'=' * 100}")


def test_specific_extractions():
    """Test specific extraction methods individually."""
    
    print(f"\n\n{Fore.MAGENTA}{Style.BRIGHT}DETAILED EXTRACTION TESTS")
    print("=" * 100)
    
    with EntityExtractor() as extractor:
        
        # Test player name extraction
        print(f"\n{Fore.CYAN}{'─' * 100}")
        print(f"{Fore.CYAN}{Style.BRIGHT}Player Name Extraction")
        print(f"{Fore.CYAN}{'─' * 100}")
        
        test_cases = [
            "Salah scored 3 goals",
            "Kane and Son performance",
            "Mohamed Salah vs Harry Kane",
            "De Bruyne assist",
        ]
        
        for query in test_cases:
            players = extractor.extract_player_names(query)
            print(f"{Fore.WHITE}'{query}' → {Fore.GREEN}{players}")
        
        # Test position extraction
        print(f"\n{Fore.CYAN}{'─' * 100}")
        print(f"{Fore.CYAN}{Style.BRIGHT}Position Extraction")
        print(f"{Fore.CYAN}{'─' * 100}")
        
        test_cases = [
            "Top forwards and midfielders",
            "Best goalkeeper performance",
            "Defender stats",
            "FWD and MID comparison",
        ]
        
        for query in test_cases:
            positions = extractor.extract_positions(query)
            print(f"{Fore.WHITE}'{query}' → {Fore.GREEN}{positions}")
        
        # Test threshold extraction
        print(f"\n{Fore.CYAN}{'─' * 100}")
        print(f"{Fore.CYAN}{Style.BRIGHT}Threshold Extraction")
        print(f"{Fore.CYAN}{'─' * 100}")
        
        test_cases = [
            "more than 15 goals",
            "at least 200 points",
            ">= 10 assists",
            "over 100 points and more than 5 goals",
        ]
        
        for query in test_cases:
            thresholds = extractor.extract_thresholds(query)
            print(f"{Fore.WHITE}'{query}' → {Fore.GREEN}{thresholds}")
        
        # Test gameweek extraction
        print(f"\n{Fore.CYAN}{'─' * 100}")
        print(f"{Fore.CYAN}{Style.BRIGHT}Gameweek Extraction")
        print(f"{Fore.CYAN}{'─' * 100}")
        
        test_cases = [
            "gameweek 1 performance",
            "GW 10 stats",
            "week 5 top scorers",
            "GW1, GW5 and gameweek 10",
        ]
        
        for query in test_cases:
            gameweeks = extractor.extract_gameweeks(query)
            print(f"{Fore.WHITE}'{query}' → {Fore.GREEN}{gameweeks}")
    
    print(f"\n{Fore.MAGENTA}{'=' * 100}")


if __name__ == "__main__":
    test_entity_extractor()
    test_specific_extractions()
