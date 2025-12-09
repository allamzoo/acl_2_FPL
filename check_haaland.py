from src.retrieval.baseline_retriever import BaselineRetriever

r = BaselineRetriever()

# Get ONE complete example
result = r.driver.session().run("""
    MATCH (p:Player)-[played:PLAYED_IN]->(gw:Gameweek)<-[:HAS_GW]-(s:Season)
    MATCH (p)-[:PLAYS_AS]->(pos:Position)
    WHERE p.player_name CONTAINS 'Haaland'
    RETURN p.player_name as name,
           pos.position_name as position, 
           s.season_name as season,
           played
    LIMIT 1
""")

record = result.single()
if record:
    print(f"Player: {record['name']}")
    print(f"Position: {record['position']}")
    print(f"Season: {record['season']}")
    print(f"\nGameweek Stats (PLAYED_IN properties):")
    stats = dict(record['played'])
    for key, value in sorted(stats.items()):
        print(f"  {key}: {value}")
else:
    print("No Haaland found, trying any player...")
    result = r.driver.session().run("""
        MATCH (p:Player)-[played:PLAYED_IN]->(gw:Gameweek)
        RETURN p.player_name as name, played
        LIMIT 1
    """)
    record = result.single()
    if record:
        print(f"Player: {record['name']}")
        print(f"\nGameweek Stats:")
        for key, value in sorted(dict(record['played']).items()):
            print(f"  {key}: {value}")

r.close()
