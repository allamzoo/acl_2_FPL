from neo4j import GraphDatabase
from config.config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, NEO4J_DATABASE

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

with driver.session(database=NEO4J_DATABASE) as session:
    result = session.run("MATCH (p:Player) WHERE p.player_name IS NOT NULL RETURN p LIMIT 1").single()
    
    if result:
        player = dict(result['p'])
        print("ALL Player properties:")
        for key in sorted(player.keys()):
            value = player[key]
            if isinstance(value, list):
                print(f"  {key}: list with {len(value)} items")
            elif isinstance(value, str):
                print(f"  {key}: '{value[:50]}...' (string)")
            else:
                print(f"  {key}: {value} ({type(value).__name__})")

driver.close()
