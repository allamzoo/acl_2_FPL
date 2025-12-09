"""Check exact season format in database"""
import sys
sys.path.append('C:\\Users\\Marwan Allam\\fpl-graph-rag')

from neo4j import GraphDatabase
from config.config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, NEO4J_DATABASE

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

with driver.session(database=NEO4J_DATABASE) as session:
    # Check Season nodes
    result = session.run("MATCH (s:Season) RETURN s.season_name LIMIT 5")
    print("Season nodes:")
    for record in result:
        print(f"  - '{record['s.season_name']}'")
    
    # Check Gameweek nodes and their season property
    result = session.run("MATCH (gw:Gameweek) RETURN DISTINCT gw.season ORDER BY gw.season LIMIT 10")
    print("\nGameweek.season values:")
    for record in result:
        print(f"  - '{record['gw.season']}'")
    
    # Check sample PLAYED_IN relationships
    result = session.run("""
        MATCH (p:Player)-[r:PLAYED_IN]->(gw:Gameweek)
        RETURN p.player_name, gw.GW_number, gw.season, r.goals_scored, r.total_points
        LIMIT 5
    """)
    print("\nSample PLAYED_IN data:")
    for record in result:
        print(f"  {record['p.player_name']} - GW{record['gw.GW_number']} ({record['gw.season']}): {record['r.goals_scored']} goals, {record['r.total_points']} pts")

driver.close()
