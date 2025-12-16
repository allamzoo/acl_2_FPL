"""Test graph visualization query"""
from neo4j import GraphDatabase
from config.config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, NEO4J_DATABASE

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

# Get some player names first
with driver.session(database=NEO4J_DATABASE) as session:
    result = session.run("""
        MATCH (p:Player)-[r:PLAYED_IN]->()
        RETURN DISTINCT p.player_name AS player_name
        LIMIT 5
    """)
    player_names = [record['player_name'] for record in result]
    
print(f"Testing with players: {player_names}")

# Now test the graph visualization query
query = """
MATCH (p:Player)-[r:PLAYED_IN]->(f:Fixture)
WHERE p.player_name IN $player_names
MATCH (f)<-[:HAS_FIXTURE]-(gw:Gameweek)-[:HAS_GW]->(s:Season)
WHERE gw.season = $season
MATCH (f)-[:HAS_HOME_TEAM|HAS_AWAY_TEAM]->(t:Team)
WITH p, r, f, gw, t
LIMIT $limit
RETURN p, r, f, gw, t
"""

with driver.session(database=NEO4J_DATABASE) as session:
    result = session.run(query, {
        'player_names': player_names[:3],
        'season': '2022-23',
        'limit': 50
    })
    
    nodes = []
    relationships = []
    node_ids_seen = set()
    
    record_count = 0
    for record in result:
        record_count += 1
        print(f"\nRecord {record_count}:")
        for key, value in record.items():
            if value is not None and hasattr(value, '__class__'):
                class_name = value.__class__.__name__
                print(f"  {key}: {class_name}")
                
                if class_name == 'Node':
                    node_id = value.id if hasattr(value, 'id') else id(value)
                    if node_id not in node_ids_seen:
                        nodes.append(value)
                        node_ids_seen.add(node_id)
                        labels = list(value.labels) if hasattr(value, 'labels') else []
                        props = dict(value)
                        print(f"    ID: {node_id}, Labels: {labels}, Sample props: {list(props.keys())[:3]}")
                
                elif class_name == 'Relationship':
                    relationships.append(value)
                    print(f"    Type: {value.type if hasattr(value, 'type') else 'unknown'}")

print(f"\n{'='*50}")
print(f"Total: {len(nodes)} nodes, {len(relationships)} relationships")
print(f"Node types: {set([list(n.labels)[0] if n.labels else 'Unknown' for n in nodes])}")

driver.close()
