from src.retrieval.baseline_retriever import BaselineRetriever
r = BaselineRetriever()

# Just count
result = r.driver.session().run("MATCH ()-[r:PLAYED_IN]->() RETURN count(r) as c")
print(f"PLAYED_IN count: {result.single()['c']}")

# Get ANY relationship
result = r.driver.session().run("""
    MATCH (p)-[r:PLAYED_IN]->(gw)
    RETURN type(r) as rel_type,
           labels(p) as start_labels,
           labels(gw) as end_labels,
           r
    LIMIT 1
""")

rec = result.single()
if rec:
    print(f"\nRelationship: {rec['rel_type']}")
    print(f"From: {rec['start_labels']}")
    print(f"To: {rec['end_labels']}")
    print(f"Properties: {list(dict(rec['r']).keys())[:10]}")

r.close()
