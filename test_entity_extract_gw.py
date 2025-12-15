"""Test entity extraction for gameweek query"""
from src.preprocessing.entity_extractor import EntityExtractor
from neo4j import GraphDatabase
from config.config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD

# Create simple connection wrapper
class SimpleConn:
    def __init__(self):
        self.driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))

conn = SimpleConn()
ee = EntityExtractor()

query = "Who were the best performing midfielders in gameweek 5 season 2021-22?"
print(f"Query: {query}\n")

entities = ee.extract(query)
print("Extracted Entities:")
print(f"  Gameweeks: {entities.get('gameweeks', [])}")
print(f"  Positions: {entities.get('positions', [])}")
print(f"  Seasons: {entities.get('seasons', [])}")
print(f"  Players: {entities.get('players', [])}")

conn.driver.close()
