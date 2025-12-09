"""
Neo4j Schema Exploration Script
Explores the structure and properties of the FPL Knowledge Graph.
"""

from neo4j import GraphDatabase
from config.config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, NEO4J_DATABASE


def explore_schema():
    """Explore and display the schema of the Neo4j database."""
    
    driver = GraphDatabase.driver(
        NEO4J_URI,
        auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
    )
    
    try:
        with driver.session(database=NEO4J_DATABASE) as session:
            print("=" * 80)
            print("FPL KNOWLEDGE GRAPH SCHEMA EXPLORATION")
            print("=" * 80)
            
            # Explore each node type
            labels = ["Player", "Team", "Position", "Fixture", "Gameweek", "Season"]
            
            for label in labels:
                print(f"\n{'=' * 80}")
                print(f"NODE: {label}")
                print("=" * 80)
                
                # Get sample node with all properties
                query = f"""
                MATCH (n:{label})
                RETURN n
                LIMIT 1
                """
                result = session.run(query)
                record = result.single()
                
                if record:
                    node = record["n"]
                    print(f"\nProperties:")
                    for key, value in dict(node).items():
                        print(f"  - {key}: {value} ({type(value).__name__})")
                
                # Count nodes
                count_query = f"MATCH (n:{label}) RETURN count(n) as count"
                count = session.run(count_query).single()["count"]
                print(f"\nTotal {label} nodes: {count:,}")
                
                # Show a few examples
                if label == "Player":
                    examples_query = """
                    MATCH (p:Player)
                    RETURN p.name, p.team, p.position
                    LIMIT 5
                    """
                    print("\nSample Players:")
                    for rec in session.run(examples_query):
                        print(f"  - {rec['p.name']} ({rec['p.position']}) - {rec['p.team']}")
                
                elif label == "Team":
                    examples_query = "MATCH (t:Team) RETURN t.name LIMIT 10"
                    print("\nTeams:")
                    teams = [rec['t.name'] for rec in session.run(examples_query)]
                    print(f"  {', '.join(teams)}")
                
                elif label == "Season":
                    examples_query = "MATCH (s:Season) RETURN s.name ORDER BY s.name"
                    print("\nSeasons:")
                    seasons = [rec['s.name'] for rec in session.run(examples_query)]
                    print(f"  {', '.join(map(str, seasons))}")
            
            # Explore relationships
            print(f"\n{'=' * 80}")
            print("RELATIONSHIPS")
            print("=" * 80)
            
            rel_types = ["PLAYED_IN", "PLAYS_AS", "HAS_FIXTURE", "HAS_HOME_TEAM", 
                        "HAS_AWAY_TEAM", "HAS_GW"]
            
            for rel_type in rel_types:
                query = f"""
                MATCH (a)-[r:{rel_type}]->(b)
                RETURN labels(a)[0] as from_label, 
                       labels(b)[0] as to_label,
                       keys(r) as properties,
                       r
                LIMIT 1
                """
                result = session.run(query)
                record = result.single()
                
                if record:
                    print(f"\n{record['from_label']} -[{rel_type}]-> {record['to_label']}")
                    
                    # Show relationship properties
                    rel = record['r']
                    if dict(rel):
                        print("  Properties:")
                        for key, value in dict(rel).items():
                            print(f"    - {key}: {value} ({type(value).__name__})")
                    else:
                        print("  (No properties)")
                    
                    # Count
                    count_query = f"MATCH ()-[r:{rel_type}]->() RETURN count(r) as count"
                    count = session.run(count_query).single()["count"]
                    print(f"  Total: {count:,}")
            
            # Explore PLAYED_IN statistics (most important for FPL)
            print(f"\n{'=' * 80}")
            print("PLAYED_IN RELATIONSHIP DETAILS (Player Performance Stats)")
            print("=" * 80)
            
            played_in_query = """
            MATCH (p:Player)-[r:PLAYED_IN]->(f:Fixture)
            RETURN r
            LIMIT 1
            """
            result = session.run(played_in_query)
            record = result.single()
            
            if record:
                rel = record['r']
                print("\nAvailable statistics per game:")
                for key, value in sorted(dict(rel).items()):
                    print(f"  - {key}: {value} ({type(value).__name__})")
            
            # Sample query: Top scorers
            print(f"\n{'=' * 80}")
            print("SAMPLE QUERY: Top 10 Goal Scorers (All Time)")
            print("=" * 80)
            
            top_scorers_query = """
            MATCH (p:Player)-[r:PLAYED_IN]->()
            WITH p.name as player, sum(r.goals_scored) as total_goals
            ORDER BY total_goals DESC
            LIMIT 10
            RETURN player, total_goals
            """
            
            for rec in session.run(top_scorers_query):
                print(f"  {rec['player']}: {rec['total_goals']} goals")
            
            print("\n" + "=" * 80)
            
    finally:
        driver.close()


if __name__ == "__main__":
    explore_schema()
