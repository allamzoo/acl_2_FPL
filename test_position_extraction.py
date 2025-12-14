"""
Quick test of entity extraction for position detection
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

from src.preprocessing.entity_extractor import EntityExtractor


def test_position_extraction():
    """Test if position abbreviations are extracted correctly."""
    
    print("=" * 80)
    print("POSITION EXTRACTION TEST")
    print("=" * 80)
    
    extractor = EntityExtractor()
    
    test_queries = [
        "Who was the best lb in season 2021-22?",
        "Best left back in 2021/22",
        "Top rb this season",
        "Who are the best centre backs?",
        "Best CB in the league",
        "Top strikers and forwards",
        "Best CDM midfielder",
        "Who is the best winger?",
        "Top LW and RW players"
    ]
    
    for query in test_queries:
        entities = extractor.extract(query)
        positions = entities.get('positions', [])
        
        print(f"\nQuery: {query}")
        print(f"Positions extracted: {positions}")
    
    print("\n" + "=" * 80)
    print("✓ Position extraction test complete")
    
    extractor.close()


if __name__ == "__main__":
    test_position_extraction()
