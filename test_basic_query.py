from src.retrieval.baseline_retriever import BaselineRetriever
r = BaselineRetriever()

# Test basic query
result = r.driver.session().run("""
    MATCH (p:Player)-[played:PLAYED_IN]->(gw:Gameweek)
    WHERE gw.season = '2022-23' AND played.goals_scored > 0
    RETURN p.player_name as player, 
           played.goals_scored as goals,
           gw.GW_number as gameweek
    LIMIT 10
""")

print("Players who scored in 2022-23:")
for rec in result:
    print(f"  GW{rec['gameweek']}: {rec['player']} - {rec['goals']} goals")

r.close()
