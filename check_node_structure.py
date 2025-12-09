"""
Check actual Neo4j node structure
"""

from src.retrieval.baseline_retriever import BaselineRetriever

retriever = BaselineRetriever()

# Get a sample node with ALL its properties
result = retriever.driver.session().run("""
    MATCH (p:Player)
    RETURN p
    LIMIT 1
""")

node = result.single()
if node:
    player = node['p']
    print("Sample Player Node:")
    print(f"Labels: {list(player.labels)}")
    print(f"Properties: {dict(player)}")
    print()
    print("Available properties:")
    for key, value in dict(player).items():
        print(f"  - {key}: {value} ({type(value).__name__})")
else:
    print("No nodes found!")

retriever.close()
