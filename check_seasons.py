"""Check what seasons are available in the database"""

from neo4j import GraphDatabase
from config.config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD

# Neo4j connection details
URI = NEO4J_URI
AUTH = (NEO4J_USERNAME, NEO4J_PASSWORD)

driver = GraphDatabase.driver(URI, auth=AUTH)

with driver.session(database="neo4j") as session:
    # Get all unique seasons
    result = session.run("""
        MATCH (s:Season)
        RETURN s.season_name AS season
        ORDER BY s.season_name
    """)
    
    seasons = [record["season"] for record in result]
    
    print("=" * 80)
    print("AVAILABLE SEASONS IN DATABASE")
    print("=" * 80)
    for i, season in enumerate(seasons, 1):
        print(f"{i}. {season}")
    
    print(f"\nTotal: {len(seasons)} seasons")
    print("=" * 80)

driver.close()
