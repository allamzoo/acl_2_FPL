from src.retrieval.baseline_retriever import BaselineRetriever

r = BaselineRetriever()

# Check each node type
print("POSITION NODE:")
result = r.driver.session().run("MATCH (n:Position) RETURN n LIMIT 1")
rec = result.single()
if rec:
    for k, v in dict(rec['n']).items():
        print(f"  {k}: {v}")

print("\nTEAM NODE:")
result = r.driver.session().run("MATCH (n:Team) RETURN n LIMIT 1")
rec = result.single()
if rec:
    for k, v in dict(rec['n']).items():
        print(f"  {k}: {v}")

print("\nSEASON NODE:")
result = r.driver.session().run("MATCH (n:Season) RETURN n LIMIT 1")
rec = result.single()
if rec:
    for k, v in dict(rec['n']).items():
        print(f"  {k}: {v}")

print("\nGAMEWEEK NODE:")
result = r.driver.session().run("MATCH (n:Gameweek) RETURN n LIMIT 1")
rec = result.single()
if rec:
    for k, v in dict(rec['n']).items():
        print(f"  {k}: {v}")

print("\nPLAYED_IN RELATIONSHIP:")
result = r.driver.session().run("MATCH ()-[r:PLAYED_IN]->() RETURN r LIMIT 1")
rec = result.single()
if rec:
    stats = dict(rec['r'])
    for k in sorted(stats.keys())[:30]:
        print(f"  {k}: {stats[k]}")

r.close()
