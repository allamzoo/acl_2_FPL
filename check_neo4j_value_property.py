"""Check what value/price properties exist in Neo4j."""

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

def check_value_property():
    """Check if Player nodes have value property and what it's called."""
    
    # Check all properties on Player nodes
    query1 = """
    MATCH (p:Player)
    RETURN keys(p) AS properties
    LIMIT 1
    """
    
    # Check for any value-related properties
    query2 = """
    MATCH (p:Player)
    WHERE p.value IS NOT NULL OR p.price IS NOT NULL OR p.now_cost IS NOT NULL
    RETURN p.player_name AS player, 
           p.value AS value,
           p.price AS price,
           p.now_cost AS now_cost
    LIMIT 10
    """
    
    # Check sample player
    query3 = """
    MATCH (p:Player)
    WHERE p.player_name CONTAINS "Salah"
    RETURN p
    LIMIT 1
    """
    
    with driver.session(database=NEO4J_DATABASE) as session:
        print("=" * 80)
        print("1. PROPERTIES ON PLAYER NODES:")
        print("=" * 80)
        result = session.run(query1)
        for record in result:
            print(f"Available properties: {record['properties']}")
        
        print("\n" + "=" * 80)
        print("2. PLAYERS WITH VALUE PROPERTY:")
        print("=" * 80)
        result = session.run(query2)
        records = list(result)
        if records:
            for record in records:
                print(f"{record['player']}: value={record['value']}, price={record['price']}, now_cost={record['now_cost']}")
        else:
            print("⚠️  No players found with value, price, or now_cost property")
        
        print("\n" + "=" * 80)
        print("3. SAMPLE PLAYER (SALAH) - ALL PROPERTIES:")
        print("=" * 80)
        result = session.run(query3)
        for record in result:
            player = dict(record['p'])
            for key, val in player.items():
                print(f"  {key}: {val}")

if __name__ == "__main__":
    check_value_property()
    driver.close()
