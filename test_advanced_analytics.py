"""Test advanced analytics queries to ensure they work with real data"""

from neo4j import GraphDatabase
from config.config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, NEO4J_DATABASE

def test_top_performers():
    print("\n" + "="*80)
    print("TEST 1: Top Performers by Metric")
    print("="*80)
    
    with GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD)) as driver:
        with driver.session(database=NEO4J_DATABASE) as session:
            metric = "goals_scored"
            season = "2022-23"
            top_n = 10
            
            query = f"""
            MATCH (p:Player)-[r:PLAYED_IN]->(gw:Gameweek)-[:HAS_GW]->(s:Season)
            WHERE s.season_name = $season AND r.{metric} IS NOT NULL
            WITH p, SUM(r.{metric}) as total_value, 
                 AVG(r.{metric}) as avg_value
            RETURN p.player_name as name, 
                   total_value as value,
                   avg_value,
                   p.position as position
            ORDER BY total_value DESC
            LIMIT $limit
            """
            result = session.run(query, season=season, limit=top_n)
            data = [dict(record) for record in result]
            
            if data:
                print(f"✅ Found {len(data)} top performers for {metric}")
                for i, player in enumerate(data[:5], 1):
                    print(f"  {i}. {player['name']} ({player['position']}): {player['value']} goals")
            else:
                print("❌ No data found")


def test_position_distribution():
    print("\n" + "="*80)
    print("TEST 2: Position Distribution")
    print("="*80)
    
    with GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD)) as driver:
        with driver.session(database=NEO4J_DATABASE) as session:
            season = "2022-23"
            
            query = """
            MATCH (p:Player)-[r:PLAYED_IN]->(gw:Gameweek)-[:HAS_GW]->(s:Season)
            WHERE s.season_name = $season
            WITH DISTINCT p.player_name as player, p.position as position
            WITH position, count(player) as count
            RETURN position, count
            ORDER BY count DESC
            """
            result = session.run(query, season=season)
            data = [dict(record) for record in result]
            
            if data:
                print(f"✅ Found position distribution:")
                for pos in data:
                    print(f"  {pos['position']}: {pos['count']} players")
            else:
                print("❌ No data found")


def test_value_analysis():
    print("\n" + "="*80)
    print("TEST 3: Value Analysis (Points per 90)")
    print("="*80)
    
    with GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD)) as driver:
        with driver.session(database=NEO4J_DATABASE) as session:
            season = "2022-23"
            min_minutes = 500
            
            query = """
            MATCH (p:Player)-[r:PLAYED_IN]->(gw:Gameweek)-[:HAS_GW]->(s:Season)
            WHERE s.season_name = $season AND r.total_points IS NOT NULL 
                  AND r.minutes IS NOT NULL
            WITH p, 
                 SUM(r.total_points) as total_points,
                 SUM(r.minutes) as total_minutes,
                 SUM(r.goals_scored) as goals,
                 SUM(r.assists) as assists
            WHERE total_minutes >= $min_minutes
            WITH p.player_name as name,
                 p.position as position,
                 total_points,
                 total_minutes,
                 goals,
                 assists,
                 toFloat(total_points) / (toFloat(total_minutes) / 90.0) as points_per_90
            RETURN name, position, total_points, total_minutes, 
                   goals, assists, points_per_90
            ORDER BY points_per_90 DESC
            LIMIT 10
            """
            
            result = session.run(query, season=season, min_minutes=min_minutes)
            data = [dict(record) for record in result]
            
            if data:
                print(f"✅ Found {len(data)} value players:")
                for i, player in enumerate(data[:5], 1):
                    print(f"  {i}. {player['name']} ({player['position']}): {player['points_per_90']:.2f} pts/90")
            else:
                print("❌ No data found")


def test_team_performance():
    print("\n" + "="*80)
    print("TEST 4: Team Performance")
    print("="*80)
    
    with GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD)) as driver:
        with driver.session(database=NEO4J_DATABASE) as session:
            season = "2022-23"
            metric = "total_points"
            
            query = f"""
            MATCH (p:Player)-[r:PLAYED_IN]->(gw:Gameweek)-[:HAS_GW]->(s:Season)
            WHERE s.season_name = $season AND r.{metric} IS NOT NULL AND gw.team_h IS NOT NULL
            WITH gw.team_h as team, SUM(r.{metric}) as home_value
            RETURN team, home_value as total_value
            ORDER BY total_value DESC
            """
            result = session.run(query, season=season)
            data = [dict(record) for record in result if record['team']]
            
            if data:
                print(f"✅ Found {len(data)} teams:")
                for i, team in enumerate(data[:5], 1):
                    print(f"  {i}. {team['team']}: {team['total_value']} {metric}")
            else:
                print("❌ No data found")


if __name__ == "__main__":
    print("\n🧪 Testing Advanced Analytics Queries")
    print("="*80)
    
    test_top_performers()
    test_position_distribution()
    test_value_analysis()
    test_team_performance()
    
    print("\n" + "="*80)
    print("✅ All tests completed!")
    print("="*80 + "\n")
