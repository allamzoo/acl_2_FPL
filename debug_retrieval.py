"""
Debug retrieval system - check if Neo4j has data and retrieval works
"""

import os
from dotenv import load_dotenv
from src.retrieval.hybrid_retriever import HybridRetriever

load_dotenv()

def debug_retrieval():
    """Debug the retrieval system."""
    
    print("=" * 80)
    print("DEBUGGING RETRIEVAL SYSTEM")
    print("=" * 80)
    print()
    
    # Check Neo4j connection
    neo4j_uri = os.getenv('NEO4J_URI')
    neo4j_user = os.getenv('NEO4J_USERNAME')
    neo4j_db = os.getenv('NEO4J_DATABASE')
    
    print(f"Neo4j URI: {neo4j_uri}")
    print(f"Neo4j User: {neo4j_user}")
    print(f"Neo4j Database: {neo4j_db}")
    print()
    
    # Initialize retriever
    print("Initializing retriever...")
    try:
        retriever = HybridRetriever(use_hybrid_embeddings=True)
        print("✓ Retriever initialized")
    except Exception as e:
        print(f"❌ Failed to initialize retriever: {e}")
        return
    
    print()
    
    # Test 1: Check if database has data using baseline retriever
    print("=" * 80)
    print("TEST 1: Database Data Check")
    print("=" * 80)
    
    try:
        # Use baseline retriever to check data
        test_result = retriever.baseline.driver.session().run(
            "MATCH (p:Player) RETURN count(p) as count"
        )
        player_count = test_result.single()['count']
        print(f"Total Players in DB: {player_count}")
        
        # Get sample players
        test_result = retriever.baseline.driver.session().run("""
            MATCH (p:Player)
            RETURN p.name as name, p.position as position, p.total_points as points
            ORDER BY p.total_points DESC
            LIMIT 5
        """)
        
        print("\nTop 5 Players by Points:")
        for i, record in enumerate(test_result, 1):
            print(f"  {i}. {record['name']} ({record['position']}) - {record['points']} pts")
        
    except Exception as e:
        print(f"❌ Database query failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print()
    
    # Test 2: Test retrieval for Haaland
    print("=" * 80)
    print("TEST 2: Retrieve Haaland Data")
    print("=" * 80)
    
    try:
        context = retriever.retrieve(
            query="Haaland",
            season="2023-24"
        )
        
        print(f"Intent: {context.get('intent', 'N/A')}")
        print(f"Retrieved {len(context.get('unified_players', []))} players")
        print()
        
        if context.get('unified_players'):
            print("Retrieved Players:")
            for i, player in enumerate(context['unified_players'][:3], 1):
                print(f"\n{i}. {player.get('name', 'Unknown')}")
                print(f"   Position: {player.get('position', 'N/A')}")
                print(f"   Team: {player.get('team', 'N/A')}")
                print(f"   Goals: {player.get('goals_scored', player.get('goals', 0))}")
                print(f"   Points: {player.get('total_points', 0)}")
        else:
            print("❌ No players retrieved!")
            print("\nBaseline results:", context.get('baseline_results', {}))
            print("Semantic results:", len(context.get('semantic_results', {}).get('players', [])))
            
    except Exception as e:
        print(f"❌ Retrieval failed: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    
    # Test 3: Test retrieval for top scorers
    print("=" * 80)
    print("TEST 3: Retrieve Top Goalscorers")
    print("=" * 80)
    
    try:
        context = retriever.retrieve(
            query="Who is the top goalscorer?",
            season="2023-24"
        )
        
        print(f"Intent: {context.get('intent', 'N/A')}")
        print(f"Retrieved {len(context.get('unified_players', []))} players")
        print()
        
        if context.get('unified_players'):
            print("Top Retrieved Players:")
            for i, player in enumerate(context['unified_players'][:5], 1):
                goals = player.get('goals_scored', player.get('goals', 0))
                points = player.get('total_points', 0)
                print(f"{i}. {player.get('name', 'Unknown'):20} - {goals:2} goals, {points:3} pts")
        else:
            print("❌ No players retrieved!")
            print("\nBaseline results:", context.get('baseline_results', {}))
            print("Semantic results:", len(context.get('semantic_results', {}).get('players', [])))
            
    except Exception as e:
        print(f"❌ Retrieval failed: {e}")
        import traceback
        traceback.print_exc()
    
    print()
    print("=" * 80)
    print("Debug Complete")
    print("=" * 80)
    
    retriever.close()


if __name__ == "__main__":
    debug_retrieval()
