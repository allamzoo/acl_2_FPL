from src.retrieval.baseline_retriever import BaselineRetriever
r = BaselineRetriever()

# Check ANY PLAYED_IN relationship
result = r.driver.session().run("""
    MATCH (p:Player)-[played:PLAYED_IN]->(gw:Gameweek)
    RETURN p.player_name as player,
           gw,
           played.goals_scored as goals
    LIMIT 5
""")

print("Sample PLAYED_IN data:")
for i, rec in enumerate(result, 1):
    print(f"\n{i}. Player: {rec['player']}")
    print(f"   Goals: {rec['goals']}")
    print(f"   Gameweek properties: {dict(rec['gw'])}")

r.close()
