"""
Test retrieval for best right back (rb) query in season 2021-22
Tests entity extraction and all 3 retrieval modes
"""

import sys
import time
from src.retrieval.hybrid_retriever import HybridRetriever
from src.preprocessing.entity_extractor import EntityExtractor
from src.utils.neo4j_utils import Neo4jConnection

def main():
    # Initialize
    print("=" * 80)
    print("TESTING BEST RB QUERY - Season 2021-22")
    print("=" * 80)
    
    neo4j_conn = Neo4jConnection()
    entity_extractor = EntityExtractor(neo4j_conn)
    
    query = "Who was the best rb in season 2021-22?"
    print(f"\nQuery: '{query}'")
    print("-" * 80)
    
    # Test entity extraction first
    print("\n🔍 ENTITY EXTRACTION TEST:")
    entities = entity_extractor.extract_entities(query)
    print(f"Extracted Entities:")
    print(f"  - Players: {entities.get('players', [])}")
    print(f"  - Teams: {entities.get('teams', [])}")
    print(f"  - Positions: {entities.get('positions', [])}")
    print(f"  - Seasons: {entities.get('seasons', [])}")
    print(f"  - Gameweeks: {entities.get('gameweeks', [])}")
    
    # Test all 3 retrieval modes
    modes = [
        ("baseline", "Baseline Only (Cypher)"),
        ("baseline+embedding1", "Baseline + Model 1 (mpnet 768D)"),
        ("baseline+embedding2", "Baseline + Model 2 (MiniLM 384D)")
    ]
    
    for mode, mode_desc in modes:
        print(f"\n{'=' * 80}")
        print(f"MODE: {mode_desc}")
        print("=" * 80)
        
        retriever = HybridRetriever(
            neo4j_conn=neo4j_conn,
            entity_extractor=entity_extractor,
            retrieval_mode=mode,
            use_llm_intent=False  # Use rule-based classifier
        )
        
        start_time = time.time()
        results = retriever.retrieve(query)
        elapsed = time.time() - start_time
        
        print(f"\n⏱️  Query Time: {elapsed:.2f}s")
        print(f"📊 Intent: {results['intent']} (confidence: {results['confidence']:.2%})")
        print(f"🎯 Total Players Retrieved: {len(results['players'])}")
        
        if results['players']:
            print(f"\n📋 TOP PLAYERS (showing top 10):")
            for i, player in enumerate(results['players'][:10], 1):
                name = player.get('name', 'Unknown')
                position = player.get('position', 'N/A')
                total_points = player.get('total_points', 0)
                
                # Additional stats
                goals = player.get('total_goals', player.get('goals_scored', 0))
                assists = player.get('total_assists', player.get('assists', 0))
                clean_sheets = player.get('clean_sheets', 0)
                minutes = player.get('minutes', 0)
                
                print(f"  {i}. {name} ({position})")
                print(f"     Total Points: {total_points}")
                print(f"     Goals: {goals} | Assists: {assists} | Clean Sheets: {clean_sheets}")
                print(f"     Minutes: {minutes}")
                
                # Show similarity score if available (semantic results)
                if 'similarity' in player:
                    print(f"     Similarity: {player['similarity']:.3f}")
                print()
        else:
            print("\n⚠️  No players retrieved")
        
        print("-" * 80)
    
    neo4j_conn.close()
    print("\n✅ Test completed!")

if __name__ == "__main__":
    main()
