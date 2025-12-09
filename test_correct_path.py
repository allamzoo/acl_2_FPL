"""Check how to get season from Fixture"""
import sys
sys.path.append('C:\\Users\\Marwan Allam\\fpl-graph-rag')

from neo4j import GraphDatabase
from config.config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, NEO4J_DATABASE

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

with driver.session(database=NEO4J_DATABASE) as session:
    # Check Fixture properties
    result = session.run("""
        MATCH (f:Fixture)
        WITH keys(f) as props
        RETURN DISTINCT props
        LIMIT 1
    """)
    print("Fixture properties:")
    for record in result:
        print(f"  {record['props']}")
    
    # Check if Fixture has season property
    result = session.run("""
        MATCH (f:Fixture)
        RETURN f.season, COUNT(*) as count
        LIMIT 5
    """)
    print("\nFixture.season values:")
    for record in result:
        print(f"  season: {record['f.season']}, count: {record['count']}")
    
    # Check the path from Fixture to Season
    result = session.run("""
        MATCH (f:Fixture)<-[:HAS_FIXTURE]-(gw:Gameweek)
        RETURN gw.season, gw.GW_number, COUNT(f) as fixtures
        LIMIT 5
    """)
    print("\nFixture -> Gameweek path:")
    for record in result:
        print(f"  GW{record['gw.GW_number']} ({record['gw.season']}): {record['fixtures']} fixtures")
    
    # Test the correct query pattern
    result = session.run("""
        MATCH (p:Player)-[r:PLAYED_IN]->(f:Fixture)<-[:HAS_FIXTURE]-(gw:Gameweek)
        WHERE r.position = 'FWD' AND gw.season = '2022-23'
        WITH p.player_name AS player,
             SUM(r.goals_scored) AS total_goals,
             SUM(r.total_points) AS total_points
        WHERE total_goals > 5
        RETURN player, total_goals, total_points
        ORDER BY total_goals DESC
        LIMIT 10
    """)
    print("\nTop scorers (FWD, 2022-23) with correct query:")
    for record in result:
        print(f"  {record['player']}: {record['total_goals']} goals, {record['total_points']} pts")

driver.close()
