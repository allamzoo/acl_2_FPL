"""
Import player value/price data from CSV into Neo4j Player nodes.

This script reads the fpl_two_seasons.csv file and updates the Player nodes
with their price values aggregated per season.
"""

import pandas as pd
from neo4j import GraphDatabase
import os

# Neo4j connection
NEO4J_URI = "neo4j://127.0.0.1:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "Teammm80"
NEO4J_DATABASE = "neo4j"

# CSV file path
CSV_PATH = "data/raw/fpl_two_seasons.csv"

def import_value_to_neo4j():
    """Import value property from CSV to Neo4j Player nodes."""
    
    print("=" * 80)
    print("IMPORTING VALUE DATA FROM CSV TO NEO4J")
    print("=" * 80)
    
    # Load CSV
    print(f"\n1. Loading CSV from: {CSV_PATH}")
    if not os.path.exists(CSV_PATH):
        print(f"❌ ERROR: CSV file not found at {CSV_PATH}")
        return
    
    df = pd.read_csv(CSV_PATH)
    print(f"✓ Loaded {len(df)} gameweek records")
    print(f"✓ Columns: {list(df.columns)}")
    
    # Aggregate value per player-season (use last gameweek value for each season)
    print("\n2. Aggregating value per player-season...")
    
    # Get the last gameweek value for each player in each season
    player_values = df.sort_values('GW').groupby(['name', 'season']).agg({
        'value': 'last',  # Use last gameweek value
        'position': 'first'
    }).reset_index()
    
    print(f"✓ Aggregated to {len(player_values)} player-season records")
    print(f"\nSample data:")
    print(player_values.head(10))
    
    # Calculate average value across both seasons for each player
    print("\n3. Calculating average value across seasons...")
    player_avg_values = player_values.groupby('name').agg({
        'value': 'mean',  # Average across seasons
        'position': 'first'
    }).reset_index()
    
    print(f"✓ Calculated average values for {len(player_avg_values)} unique players")
    
    # Connect to Neo4j
    print("\n4. Connecting to Neo4j...")
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    
    # Update Neo4j with value property
    print("\n5. Updating Player nodes with value property...")
    
    update_query = """
    MATCH (p:Player {player_name: $player_name})
    SET p.value = $value
    RETURN p.player_name AS name, p.value AS value
    """
    
    updated_count = 0
    not_found_count = 0
    
    with driver.session(database=NEO4J_DATABASE) as session:
        for _, row in player_avg_values.iterrows():
            result = session.run(update_query, {
                "player_name": row['name'],
                "value": round(float(row['value']) / 10, 1)  # Convert to £millions (divide by 10)
            })
            
            records = list(result)
            if records:
                updated_count += 1
                if updated_count % 100 == 0:
                    print(f"  Updated {updated_count} players...")
            else:
                not_found_count += 1
    
    print(f"\n✓ Update complete!")
    print(f"  - Updated: {updated_count} players")
    print(f"  - Not found in Neo4j: {not_found_count} players")
    
    # Verify the update
    print("\n6. Verifying update...")
    verify_query = """
    MATCH (p:Player)
    WHERE p.value IS NOT NULL
    RETURN count(p) AS count,
           min(p.value) AS min_value,
           max(p.value) AS max_value,
           avg(p.value) AS avg_value
    """
    
    with driver.session(database=NEO4J_DATABASE) as session:
        result = session.run(verify_query)
        record = result.single()
        print(f"✓ Players with value: {record['count']}")
        print(f"✓ Price range: £{record['min_value']:.1f}m - £{record['max_value']:.1f}m")
        print(f"✓ Average price: £{record['avg_value']:.1f}m")
    
    # Show top 10 most expensive players
    print("\n7. Top 10 most expensive players:")
    top_query = """
    MATCH (p:Player)
    WHERE p.value IS NOT NULL
    RETURN p.player_name AS player, p.value AS value
    ORDER BY p.value DESC
    LIMIT 10
    """
    
    with driver.session(database=NEO4J_DATABASE) as session:
        result = session.run(top_query)
        for i, record in enumerate(result, 1):
            print(f"  {i}. {record['player']}: £{record['value']:.1f}m")
    
    driver.close()
    
    print("\n" + "=" * 80)
    print("✅ VALUE DATA IMPORT COMPLETE!")
    print("=" * 80)

if __name__ == "__main__":
    import_value_to_neo4j()
