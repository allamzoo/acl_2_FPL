"""
Check Neo4j schema - node types and relationships
"""

from src.retrieval.baseline_retriever import BaselineRetriever

retriever = BaselineRetriever()

# Check node types
print("="*80)
print("NODE TYPES:")
print("="*80)
result = retriever.driver.session().run("""
    CALL db.labels()
""")
for record in result:
    label = record['label']
    # Count nodes of this type
    count_result = retriever.driver.session().run(f"""
        MATCH (n:{label})
        RETURN count(n) as count
    """)
    count = count_result.single()['count']
    print(f"  {label}: {count} nodes")

print("\n" + "="*80)
print("RELATIONSHIP TYPES:")
print("="*80)
result = retriever.driver.session().run("""
    CALL db.relationshipTypes()
""")
for record in result:
    print(f"  {record['relationshipType']}")

print("\n" + "="*80)
print("SAMPLE SCHEMA:")
print("="*80)
result = retriever.driver.session().run("""
    CALL db.schema.visualization()
""")

# Check if there are connected nodes
print("\n" + "="*80)
print("CHECKING FOR PLAYER STATS:")
print("="*80)
result = retriever.driver.session().run("""
    MATCH (p:Player)
    OPTIONAL MATCH (p)-[r]->(related)
    RETURN p.player_name as player, 
           type(r) as relationship, 
           labels(related) as related_labels,
           related
    LIMIT 5
""")

for record in result:
    print(f"\nPlayer: {record['player']}")
    print(f"  Relationship: {record['relationship']}")
    print(f"  Connected to: {record['related_labels']}")
    if record['related']:
        print(f"  Data: {dict(record['related'])[:200] if record['related'] else 'None'}...")

retriever.close()
