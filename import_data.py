import pandas as pd
from src.utils.neo4j_utils import Neo4jConnection

def import_data():
    print("🚀 Starting data import...")
    
    # 1. Read the downloaded CSV
    try:
        df = pd.read_csv('data/raw/cleaned_players.csv')
        print(f"✅ Loaded CSV with {len(df)} players")
    except FileNotFoundError:
        print("❌ Error: data/raw/cleaned_players.csv not found. Did you run the curl command?")
        return

    # 2. Connect to Neo4j
    conn = Neo4jConnection()
    
    # 3. Upload Data
    print("📤 Uploading to Neo4j... (this might take 30 seconds)")
    
    query = """
    MERGE (p:Player {name: $name})
    SET p.first_name = $first_name,
        p.second_name = $second_name,
        p.goals = toInteger($goals_scored),
        p.assists = toInteger($assists),
        p.total_points = toInteger($total_points),
        p.minutes = toInteger($minutes),
        p.goals_conceded = toInteger($goals_conceded),
        p.creativity = toFloat($creativity),
        p.influence = toFloat($influence),
        p.threat = toFloat($threat),
        p.bonus = toInteger($bonus),
        p.bps = toInteger($bps),
        p.ict_index = toFloat($ict_index),
        p.clean_sheets = toInteger($clean_sheets),
        p.red_cards = toInteger($red_cards),
        p.yellow_cards = toInteger($yellow_cards),
        p.selected_by_percent = toFloat($selected_by_percent),
        p.now_cost = toFloat($now_cost) / 10.0,
        p.team = "Unknown",   
        p.position = CASE $element_type
            WHEN 1 THEN 'GK'
            WHEN 2 THEN 'DEF'
            WHEN 3 THEN 'MID'
            WHEN 4 THEN 'FWD'
            ELSE 'Unknown'
        END
    """
    
    # Run the import for each row
    count = 0
    for index, row in df.iterrows():
        full_name = f"{row['first_name']} {row['second_name']}"
        
        params = {
            'name': full_name,
            'first_name': row['first_name'],
            'second_name': row['second_name'],
            'goals_scored': row['goals_scored'],
            'assists': row['assists'],
            'total_points': row['total_points'],
            'minutes': row['minutes'],
            'goals_conceded': row['goals_conceded'],
            'creativity': row['creativity'],
            'influence': row['influence'],
            'threat': row['threat'],
            'bonus': row['bonus'],
            'bps': row['bps'],
            'ict_index': row['ict_index'],
            'clean_sheets': row['clean_sheets'],
            'red_cards': row['red_cards'],
            'yellow_cards': row['yellow_cards'],
            'selected_by_percent': row['selected_by_percent'],
            'now_cost': row['now_cost'],
            'element_type': row['element_type']
        }
        # FIXED LINE BELOW: used execute_query instead of query
        conn.execute_query(query, params)
        count += 1
        if count % 100 == 0:
            print(f"   Processed {count} players...")

    print(f"✅ Successfully imported {count} players into Neo4j!")
    conn.close()

if __name__ == "__main__":
    import_data()