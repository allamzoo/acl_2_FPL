# Quick Start Guide

## Prerequisites
- ✅ Python 3.11+ installed
- ✅ All packages installed (from requirements.txt)
- ⚠️ Neo4j Desktop (needs to be installed)
- ⚠️ FPL data from Milestone 2

## Step 1: Environment Setup

1. **Copy environment file**:
   ```powershell
   Copy-Item .env.example .env
   ```

2. **Edit .env file** with your credentials:
   - Neo4j connection details
   - LLM API keys (OpenAI, HuggingFace, etc.)

## Step 2: Neo4j Setup

1. **Download Neo4j Desktop**: https://neo4j.com/download/
2. **Create a new database**
3. **Install GDS plugin** (from plugins section)
4. **Start the database**
5. **Import your Milestone 2 data**

## Step 3: Implementation Order

### Phase 1: Preprocessing (Week 1)
1. `src/preprocessing/intent_classifier.py`
2. `src/preprocessing/entity_extractor.py`
3. `src/preprocessing/input_embedder.py`

### Phase 2: Retrieval (Week 1)
1. `src/retrieval/cypher_queries.py` (10+ queries)
2. `src/retrieval/baseline_retriever.py`
3. `src/embeddings/node_embeddings.py` OR `feature_embeddings.py`
4. `src/retrieval/embedding_retriever.py`
5. `src/retrieval/hybrid_retriever.py`

### Phase 3: LLM Integration (Week 2)
1. `src/llm/models.py` (3+ models)
2. `src/llm/prompts.py`
3. `src/llm/generator.py`
4. `src/llm/evaluator.py`

### Phase 4: UI & Testing (Week 2)
1. `src/ui/app.py`
2. `src/ui/graph_viz.py`
3. `src/ui/stats_viz.py`
4. Write tests
5. Document results

## Step 4: Running the Application

```powershell
# Activate virtual environment (if using)
.\venv\Scripts\Activate.ps1

# Run Streamlit app
streamlit run src/ui/app.py
```

## Step 5: Testing

```powershell
# Run all tests
pytest tests/

# Run specific test
pytest tests/test_retrieval.py
```

## Step 6: Documentation

Before presentation, complete:
- [ ] `docs/architecture.md` - System design
- [ ] `docs/retrieval_strategy.md` - Query examples
- [ ] `docs/llm_comparison.md` - Model comparison results
- [ ] `docs/error_analysis.md` - Failure cases
- [ ] `docs/limitations.md` - Current limitations

## Milestone 3 Requirements Checklist

### System Requirements
- [ ] 1.a: Intent Classification
- [ ] 1.b: Entity Extraction
- [ ] 1.c: Input Embedding
- [ ] 2.a: Baseline (10+ Cypher queries)
- [ ] 2.b: Embeddings (node OR feature, 2+ models)
- [ ] 3.a: Combine results
- [ ] 3.b: Structured prompts
- [ ] 3.c: 3+ LLM models
- [ ] 3.d: Quantitative & qualitative comparison

### UI Requirements
- [ ] 4.a: Display KG context
- [ ] 4.b: Display LLM answer
- [ ] Optional: Show Cypher queries
- [ ] Optional: Graph visualization
- [ ] Optional: Model selection
- [ ] Optional: Retrieval method selection

### Documentation
- [ ] System architecture
- [ ] Retrieval strategy & examples
- [ ] LLM comparison (quantitative + qualitative)
- [ ] Error analysis
- [ ] Improvements
- [ ] Limitations

## Tips

1. **Start small**: Implement basic functionality first
2. **Test frequently**: Test each component as you build
3. **Use free models**: Start with HuggingFace free models
4. **Keep it simple**: Don't overcomplicate the UI
5. **Document as you go**: Add comments and notes while coding
6. **Backup your work**: Commit to GitHub regularly

## Troubleshooting

### Neo4j Connection Issues
- Check if database is running
- Verify credentials in .env
- Test connection with Neo4j Browser

### Import Errors
- Ensure all packages are installed
- Activate virtual environment
- Check Python path

### LLM API Errors
- Verify API keys in .env
- Check API rate limits
- Use free alternatives (HuggingFace)

## Deadline: December 15, 2025 at 23:59

Good luck! 🚀
