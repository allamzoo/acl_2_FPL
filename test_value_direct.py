"""Direct test of value query with proper relationship access."""

from neo4j import GraphDatabase

NEO4J_URI = "neo4j://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "Teammm80"
NEO4J_DATABASE = "neo4j"

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

query = """
MATCH (p:Player)-[played:PLAYED_IN]->(f:Fixture)<-[:HAS_FIXTURE]-(gw:Gameweek)
WHERE played.position = 'MID' 
  AND gw.season = '2022-23'
  AND played.minutes > 0
  AND played.value IS NOT NULL
WITH p.player_name AS player,
     AVG(played.value) / 10.0 AS price,
     played.position AS position,
     SUM(played.total_points) AS total_points,
     SUM(played.goals_scored) AS total_goals,
     SUM(played.assists) AS total_assists,
     SUM(played.minutes) AS total_minutes
WHERE total_points >= 100
  AND price <= 80
WITH player, price, position, total_points, total_goals, total_assists, total_minutes,
     (total_points * 10.0 / price) AS points_per_million
ORDER BY points_per_million DESC
LIMIT 10
RETURN player, price, position, total_points, total_goals, total_assists, 
       total_minutes, ROUND(points_per_million * 10) / 10 AS value_score
"""

with driver.session(database=NEO4J_DATABASE) as session:
    result = session.run(query, {"position": "MID", "season": "2022-23", "min_points": 100, "limit": 10})
    records = list(result)
    
    print(f"Found {len(records)} players\n")
    
    if records:
        for i, record in enumerate(records, 1):
            print(f"{i}. {record['player']} ({record['position']})")
            print(f"   Price: £{record['price']:.1f}m")
            print(f"   Total Points: {record['total_points']}")
            print(f"   Goals: {record['total_goals']} | Assists: {record['total_assists']}")
            print(f"   Value Score: {record['value_score']:.1f}")
            print()
    else:
        print("No results!")

driver.close()
