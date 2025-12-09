"""
Test ONE corrected query to verify it works
"""
from src.retrieval.baseline_retriever import BaselineRetriever

r = BaselineRetriever()

# Corrected query for top scorers
query = """
MATCH (p:Player)-[played:PLAYED_IN]->(gw:Gameweek)
WHERE gw.season = $season
WITH p.player_name AS player,
     SUM(played.goals_scored) AS total_goals,
     SUM(played.assists) AS total_assists,
     SUM(played.total_points) AS total_points,
     SUM(played.minutes) AS total_minutes
WHERE total_minutes > 0
ORDER BY total_goals DESC
LIMIT $limit
RETURN player, total_goals, total_assists, total_points, total_minutes
"""

result = r._execute_query(query, {"season": "2022-23", "limit": 10})

print("TOP SCORERS 2022-23:")
print("="*80)
for i, rec in enumerate(result, 1):
    print(f"{i}. {rec['player']:25} - {rec['total_goals']} goals, {rec['total_points']} pts, {rec['total_minutes']} mins")

r.close()
