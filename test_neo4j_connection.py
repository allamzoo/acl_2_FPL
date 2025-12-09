"""
Neo4j Connection Test Script
Tests the connection to Neo4j database and displays basic information.
"""

from neo4j import GraphDatabase
from config.config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, NEO4J_DATABASE
import sys


def test_connection():
    """Test Neo4j connection and retrieve basic database information."""
    
    driver = None
    try:
        print("=" * 60)
        print("Neo4j Connection Test")
        print("=" * 60)
        print(f"\nConnecting to: {NEO4J_URI}")
        print(f"Database: {NEO4J_DATABASE}")
        print(f"Username: {NEO4J_USERNAME}")
        
        # Create driver
        driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
        )
        
        # Verify connectivity
        driver.verify_connectivity()
        print("\n✓ Connection successful!")
        
        # Get database information
        with driver.session(database=NEO4J_DATABASE) as session:
            # Count nodes
            result = session.run("MATCH (n) RETURN count(n) as node_count")
            node_count = result.single()["node_count"]
            
            # Count relationships
            result = session.run("MATCH ()-[r]->() RETURN count(r) as rel_count")
            rel_count = result.single()["rel_count"]
            
            # Get node labels
            result = session.run("CALL db.labels()")
            labels = [record["label"] for record in result]
            
            # Get relationship types
            result = session.run("CALL db.relationshipTypes()")
            rel_types = [record["relationshipType"] for record in result]
            
            # Display information
            print("\n" + "=" * 60)
            print("Database Statistics")
            print("=" * 60)
            print(f"Total Nodes: {node_count:,}")
            print(f"Total Relationships: {rel_count:,}")
            
            print(f"\nNode Labels ({len(labels)}):")
            for label in sorted(labels):
                # Count nodes for each label
                count_result = session.run(f"MATCH (n:{label}) RETURN count(n) as count")
                count = count_result.single()["count"]
                print(f"  - {label}: {count:,}")
            
            print(f"\nRelationship Types ({len(rel_types)}):")
            for rel_type in sorted(rel_types):
                # Count relationships for each type
                count_result = session.run(f"MATCH ()-[r:{rel_type}]->() RETURN count(r) as count")
                count = count_result.single()["count"]
                print(f"  - {rel_type}: {count:,}")
            
        print("\n" + "=" * 60)
        print("✓ All tests passed!")
        print("=" * 60)
        return True
        
    except Exception as e:
        print("\n" + "=" * 60)
        print("✗ Connection failed!")
        print("=" * 60)
        print(f"\nError: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Make sure Neo4j is running")
        print("2. Check your credentials in .env file")
        print("3. Verify the URI is correct")
        print("4. Ensure the database exists")
        return False
        
    finally:
        if driver:
            driver.close()
            print("\nConnection closed.")


if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
