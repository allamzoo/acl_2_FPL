"""
Main configuration file for FPL Graph-RAG system.
"""

# TODO: Implement configuration loading from .env
# TODO: Define Neo4j connection settings
# TODO: Define LLM model configurations
# TODO: Define embedding model settings
# TODO: Define system parameters (max_results, temperature, etc.)


import os
from dotenv import load_dotenv
load_dotenv()
NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USERNAME = os.getenv("NEO4J_USERNAME")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE")

