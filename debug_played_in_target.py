"""Debug why PLAYED_IN -> Gameweek isn't working"""
import sys
sys.path.append('C:\\Users\\Marwan Allam\\fpl-graph-rag')

from neo4j import GraphDatabase
from config.config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, NEO4J_DATABASE

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

with driver.session(database=NEO4J_DATABASE) as session:
    # Check what PLAYED_IN connects to
    result = session.run("""
        MATCH (p:Player)-[r:PLAYED_IN]->(target)
        RETURN DISTINCT labels(target) as target_labels, COUNT(*) as count
    """)
    print("PLAYED_IN relationships connect to:")
    for record in result:
        print(f"  {record['target_labels']}: {record['count']} relationships")
    
    # If it's Fixture, let's see a sample
    result = session.run("""
        MATCH (p:Player)-[r:PLAYED_IN]->(f)
        RETURN p.player_name, labels(f) as target_type, r.goals_scored, r.total_points
        LIMIT 5
    """)
    print("\nSample PLAYED_IN data:")
    for record in result:
        print(f"  {record['p.player_name']} -> {record['target_type']}: {record['r.goals_scored']} goals, {record['r.total_points']} pts")
    
    # Check if there's a Fixture -> Gameweek relationship
    result = session.run("""
        MATCH ()-[r]->(:Gameweek)
        RETURN DISTINCT type(r) as rel_type, COUNT(*) as count
    """)
    print("\nRelationships TO Gameweek:")
    for record in result:
        print(f"  {record['rel_type']}: {record['count']}")
    
    # Check Gameweek to other nodes
    result = session.run("""
        MATCH (:Gameweek)-[r]->()
        RETURN DISTINCT type(r) as rel_type, COUNT(*) as count
    """)
    print("\nRelationships FROM Gameweek:")
    for record in result:
        print(f"  {record['rel_type']}: {record['count']}")

driver.close()
