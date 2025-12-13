"""Quick Neo4j connection test"""
from neo4j import GraphDatabase
from config.config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, NEO4J_DATABASE

print(f"Testing connection to: {NEO4J_URI}")
print(f"Database: {NEO4J_DATABASE}")
print(f"Username: {NEO4J_USERNAME}")

try:
    # Test connection
    driver = GraphDatabase.driver(
        NEO4J_URI,
        auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
    )
    
    print("✓ Driver created successfully")
    
    # Verify connection
    driver.verify_connectivity()
    print("✓ Connectivity verified")
    
    # Test database access
    with driver.session(database=NEO4J_DATABASE) as session:
        result = session.run("RETURN 1 as test")
        record = result.single()
        print(f"✓ Database query successful: {record['test']}")
        
        # Check if data exists
        count_result = session.run("MATCH (n) RETURN count(n) as count")
        count = count_result.single()["count"]
        print(f"✓ Total nodes in database: {count}")
        
        # Check players
        player_result = session.run("MATCH (p:Player) RETURN count(p) as count")
        player_count = player_result.single()["count"]
        print(f"✓ Total players: {player_count}")
    
    driver.close()
    print("\n✅ All tests passed!")
    
except Exception as e:
    print(f"\n❌ Connection failed: {type(e).__name__}")
    print(f"Error: {str(e)}")
    
    # Common fixes
    print("\n🔧 Troubleshooting:")
    print("1. Is Neo4j Desktop/Server running?")
    print("2. Check if the URI is correct (neo4j:// or bolt://)")
    print("3. Verify username/password")
    print("4. Check if database name exists")
