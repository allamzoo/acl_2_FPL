"""
Check all properties in Neo4j database
"""

from src.retrieval.baseline_retriever import BaselineRetriever

retriever = BaselineRetriever()

# Get all unique property keys
result = retriever.driver.session().run("""
    MATCH (p:Player)
    WITH p LIMIT 5
    UNWIND keys(p) as key
    RETURN DISTINCT key
    ORDER BY key
""")

print("Available Player properties:")
for record in result:
    print(f"  - {record['key']}")

print("\n" + "="*80)
print("Sample player with values:")
print("="*80)

# Get a complete player with actual stats
result = retriever.driver.session().run("""
    MATCH (p:Player)
    WHERE p.player_name IS NOT NULL
    RETURN p
    LIMIT 1
""")

player = result.single()['p']
for key in sorted(dict(player).keys()):
    value = player[key]
    if isinstance(value, list):
        print(f"{key}: [array with {len(value)} elements]")
    else:
        print(f"{key}: {value}")

retriever.close()
