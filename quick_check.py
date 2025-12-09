from src.retrieval.baseline_retriever import BaselineRetriever
r = BaselineRetriever()
result = r.driver.session().run('MATCH ()-[rel]->() RETURN type(rel) as t, count(*) as c ORDER BY c DESC')
for record in result:
    print(f"{record['t']}: {record['c']}")
r.close()
