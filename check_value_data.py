"""Check if value property has actual data in Neo4j."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from neo4j import GraphDatabase

# Neo4j connection
NEO4J_URI = "neo4j://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "Teammm80"
NEO4J_DATABASE = "neo4j"

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

def check_value_data():
    """Check if Player nodes have value property with actual data."""
    
    # Check how many players have value property
    query1 = """
    MATCH (p:Player)
    WHERE p.value IS NOT NULL
    RETURN count(p) AS players_with_value
    """
    
    # Get sample players with value
    query2 = """
    MATCH (p:Player)
    WHERE p.value IS NOT NULL
    RETURN p.player_name AS player, 
           p.value AS value
    ORDER BY p.value DESC
    LIMIT 10
    """
    
    # Check Mohamed Salah specifically
    query3 = """
    MATCH (p:Player)
    WHERE p.player_name CONTAINS "Salah"
    RETURN p.player_name AS player,
           p.value AS value,
           p.player_element AS id
    """
    
    with driver.session(database=NEO4J_DATABASE) as session:
        print("=" * 80)
        print("1. COUNT OF PLAYERS WITH VALUE PROPERTY:")
        print("=" * 80)
        result = session.run(query1)
        for record in result:
            print(f"Players with value: {record['players_with_value']}")
        
        print("\n" + "=" * 80)
        print("2. TOP 10 PLAYERS BY VALUE:")
        print("=" * 80)
        result = session.run(query2)
        records = list(result)
        if records:
            for record in records:
                print(f"{record['player']}: £{record['value']}m")
        else:
            print("⚠️  No players found with value data")
        
        print("\n" + "=" * 80)
        print("3. MOHAMED SALAH VALUE:")
        print("=" * 80)
        result = session.run(query3)
        for record in result:
            print(f"{record['player']} (ID: {record['id']}): £{record['value']}m")

if __name__ == "__main__":
    check_value_data()
    driver.close()
