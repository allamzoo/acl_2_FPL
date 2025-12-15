"""Test to understand team schema in Neo4j."""

from src.retrieval.baseline_retriever import BaselineRetriever

br = BaselineRetriever()

# Test 1: Check which teams Bukayo Saka played for/against
query1 = """
MATCH (p:Player)-[r:PLAYED_IN]->(f:Fixture)-[rel]->(t:Team)
WHERE p.player_name = $name
RETURN t.name as team, type(rel) as rel_type, COUNT(*) as games
ORDER BY games DESC
LIMIT 5
"""
result1 = br._execute_query(query1, {'name': 'Bukayo Saka'})
print("Bukayo Saka's fixtures:")
for row in result1:
    print(f"  {row['team']}: {row['games']} games (relationship: {row['rel_type']})")

# Test 2: Get Arsenal players by finding most common team per player
print("\n\nTesting Arsenal query:")
query2 = """
MATCH (p:Player)-[played:PLAYED_IN]->(f:Fixture)-[rel:HAS_HOME_TEAM]->(t:Team)
WHERE t.name = $team_name
WITH p, played, f, t
MATCH (f)-[:HAS_AWAY_TEAM]->(away:Team)
RETURN p.player_name as player, COUNT(*) as home_games, COLLECT(DISTINCT away.name)[0..3] as opponents
ORDER BY home_games DESC
LIMIT 10
"""
result2 = br._execute_query(query2, {'team_name': 'Arsenal'})
print("Players in Arsenal HOME fixtures (they are Arsenal players):")
for row in result2:
    print(f"  {row['player']}: {row['home_games']} home games")

br.close()
