"""
Check PLAYED_IN relationship properties
"""

from src.retrieval.baseline_retriever import BaselineRetriever

retriever = BaselineRetriever()

print("="*80)
print("PLAYER-GAMEWEEK RELATIONSHIPS:")
print("="*80)

result = retriever.driver.session().run("""
    MATCH (p:Player)-[r:PLAYED_IN]->(gw:Gameweek)
    RETURN p.player_name as player,
           gw,
           r
    LIMIT 3
""")

for i, record in enumerate(result, 1):
    print(f"\n{i}. Player: {record['player']}")
    print(f"   Gameweek: {dict(record['gw'])}")
    print(f"   Performance Stats:")
    stats = dict(record['r'])
    for key in sorted(stats.keys())[:20]:  # Show first 20 properties
        print(f"      {key}: {stats[key]}")

retriever.close()
