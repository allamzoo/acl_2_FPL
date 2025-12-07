# FPL Graph-RAG System

End-to-end Graph-RAG Travel Assistant for Fantasy Premier League using Neo4j Knowledge Graph and LLMs.

## Project Structure

```
fpl-graph-rag/
├── src/
│   ├── preprocessing/       # Input preprocessing (intent classification, NER, embeddings)
│   ├── retrieval/          # Graph retrieval (Cypher queries, embeddings search)
│   ├── llm/                # LLM integration and prompt management
│   ├── embeddings/         # Node and feature embeddings
│   ├── ui/                 # Streamlit UI components
│   └── utils/              # Utility functions
├── data/
│   ├── raw/                # Raw FPL data
│   └── processed/          # Processed data
├── cypher_queries/         # Cypher query templates
├── config/                 # Configuration files
├── notebooks/              # Jupyter notebooks for experiments
├── tests/                  # Unit tests
└── docs/                   # Documentation

## Requirements

- Python 3.11+
- Neo4j Database
- All dependencies in requirements.txt

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
python -m spacy download en_core_web_sm
```

2. Set up Neo4j Database
3. Configure environment variables in `.env`

## Usage

```bash
streamlit run src/ui/app.py
```

## Features

- Intent Classification
- Entity Extraction (Players, Teams, Positions, Seasons)
- Cypher-based Retrieval
- Embedding-based Semantic Search
- Multi-LLM Support
- Interactive UI with Graph Visualization
