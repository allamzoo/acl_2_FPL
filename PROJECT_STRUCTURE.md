# FPL Graph-RAG Project Structure

## Directory Overview

```
fpl-graph-rag/
│
├── src/                           # Source code
│   ├── preprocessing/             # Input preprocessing layer
│   │   ├── __init__.py
│   │   ├── intent_classifier.py   # Classify user query intent
│   │   ├── entity_extractor.py    # Extract entities (players, teams, etc.)
│   │   └── input_embedder.py      # Convert queries to embeddings
│   │
│   ├── retrieval/                 # Graph retrieval layer
│   │   ├── __init__.py
│   │   ├── cypher_queries.py      # 10+ Cypher query templates
│   │   ├── baseline_retriever.py  # Cypher-based retrieval
│   │   ├── embedding_retriever.py # Embedding-based retrieval
│   │   └── hybrid_retriever.py    # Combined approach
│   │
│   ├── embeddings/                # Embedding generation
│   │   ├── __init__.py
│   │   ├── node_embeddings.py     # Player node embeddings
│   │   └── feature_embeddings.py  # Feature vector embeddings
│   │
│   ├── llm/                       # LLM integration layer
│   │   ├── __init__.py
│   │   ├── models.py              # 3+ LLM model integrations
│   │   ├── prompts.py             # Structured prompt templates
│   │   ├── generator.py           # Response generation
│   │   └── evaluator.py           # Model comparison & evaluation
│   │
│   ├── ui/                        # Streamlit UI
│   │   ├── __init__.py
│   │   ├── app.py                 # Main Streamlit application
│   │   ├── graph_viz.py           # Graph visualization
│   │   └── stats_viz.py           # Statistics charts
│   │
│   ├── utils/                     # Utility functions
│   │   ├── __init__.py
│   │   ├── neo4j_utils.py         # Neo4j connection helpers
│   │   ├── logger.py              # Logging configuration
│   │   └── text_utils.py          # Text processing utilities
│   │
│   ├── __init__.py
│   └── main.py                    # Main entry point
│
├── data/
│   ├── raw/                       # Raw FPL data from Milestone 2
│   └── processed/                 # Processed data
│
├── cypher_queries/
│   └── queries.cypher             # Cypher query templates
│
├── config/
│   └── config.py                  # Configuration management
│
├── tests/                         # Unit tests
│   ├── test_intent_classifier.py
│   ├── test_entity_extractor.py
│   ├── test_retrieval.py
│   └── test_llm.py
│
├── notebooks/                     # Jupyter notebooks for experiments
│
├── docs/                          # Documentation
│   ├── architecture.md            # System architecture
│   ├── retrieval_strategy.md     # Retrieval approach docs
│   ├── llm_comparison.md         # LLM comparison results
│   ├── error_analysis.md         # Error analysis
│   └── limitations.md            # Limitations & future work
│
├── .env.example                   # Environment variables template
├── .env                          # Your environment variables (not in git)
├── .gitignore                    # Git ignore rules
├── requirements.txt              # Python dependencies
├── setup.ps1                     # Setup script
└── README.md                     # Project documentation
```

## Implementation Checklist

### 1. Input Preprocessing (Requirement 1)
- [ ] Intent classification (rule-based or LLM)
- [ ] Entity extraction using spaCy NER
- [ ] Input embedding for semantic search

### 2. Graph Retrieval Layer (Requirement 2)
- [ ] **Baseline**: 10+ Cypher query templates
- [ ] **Embeddings**: Node OR feature embeddings
- [ ] Test 2+ embedding models
- [ ] Hybrid retrieval combining both approaches

### 3. LLM Layer (Requirement 3)
- [ ] Combine baseline + embedding results
- [ ] Structured prompts (context, persona, task)
- [ ] Integrate 3+ LLM models
- [ ] Quantitative & qualitative comparison

### 4. UI (Requirement 4)
- [ ] Streamlit application
- [ ] Display KG-retrieved context
- [ ] Display LLM final answer
- [ ] Optional: Show Cypher queries
- [ ] Optional: Graph visualization
- [ ] Optional: Model selection dropdown
- [ ] Optional: Retrieval method selection

### 5. Experiments & Documentation
- [ ] System architecture diagrams
- [ ] Retrieval strategy documentation
- [ ] LLM comparison report
- [ ] Error analysis
- [ ] Improvements implemented
- [ ] Remaining limitations

## Next Steps

1. **Set up environment**:
   ```powershell
   .\setup.ps1
   ```

2. **Install Neo4j Desktop**:
   - Download from https://neo4j.com/download/
   - Create database
   - Install GDS plugin

3. **Configure .env**:
   - Add Neo4j credentials
   - Add LLM API keys

4. **Import Milestone 2 data**:
   - Copy data to `data/raw/`
   - Load into Neo4j

5. **Start implementing**:
   - Begin with preprocessing
   - Then retrieval
   - Then embeddings
   - Then LLM integration
   - Finally UI

6. **Run the app**:
   ```powershell
   streamlit run src/ui/app.py
   ```
