# FPL Graph-RAG Development Plan

## Current Status
✅ Neo4j database connected (2,377 nodes, 55,825 relationships)
✅ Project structure created
✅ Requirements defined
✅ Schema explored

## Data Schema Summary

### Nodes:
- **Player** (1,513): `player_element`, `player_name`
- **Team** (23): `name`
- **Position** (4): `name` (FWD, MID, DEF, GK)
- **Fixture** (760): `fixture_number`, `kickoff_time`, `season`
- **Gameweek** (75): `GW_number`, `season`
- **Season** (2): `season_name` (2021-22, 2022-23)

### Relationships:
- **PLAYED_IN** (51,952): Player → Fixture
  - Stats: goals_scored, assists, minutes, total_points, bonus, bps, clean_sheets, goals_conceded, yellow_cards, red_cards, saves, penalties_missed, penalties_saved, own_goals
  - Metrics: influence, creativity, threat, ict_index, form
  - Position info
  
- **PLAYS_AS**: Player → Position
- **HAS_FIXTURE**: Gameweek → Fixture
- **HAS_HOME_TEAM**: Fixture → Team
- **HAS_AWAY_TEAM**: Fixture → Team
- **HAS_GW**: Season → Gameweek

## Development Phases

### Phase 1: Input Preprocessing (Days 1-2)
**Priority: HIGH**

#### 1.1 Intent Classifier (`src/preprocessing/intent_classifier.py`)
**Intents for FPL:**
- `player_search`: Find specific players
- `player_stats`: Get player performance statistics
- `team_analysis`: Analyze team performance
- `fixture_query`: Query fixtures and schedules
- `recommendation`: Get player recommendations
- `comparison`: Compare players
- `top_performers`: Find top scorers/assisters
- `gameweek_analysis`: Analyze specific gameweeks

**Implementation options:**
- [ ] Simple keyword-based (fast, good for prototype)
- [ ] LLM-based classification (more accurate)

#### 1.2 Entity Extractor (`src/preprocessing/entity_extractor.py`)
**Entities to extract:**
- Player names (e.g., "Salah", "Kane")
- Team names (e.g., "Liverpool", "Arsenal")
- Positions (FWD, MID, DEF, GK)
- Seasons (2021-22, 2022-23)
- Gameweeks (GW1, GW10, etc.)
- Statistics (goals, assists, points, etc.)
- Numbers (thresholds: ">5 goals", "points > 100")

**Implementation options:**
- [ ] Regex patterns + fuzzy matching
- [ ] spaCy NER (needs custom training)
- [ ] LLM-based extraction

#### 1.3 Input Embedder (`src/preprocessing/input_embedder.py`)
- [ ] Convert user queries to vectors
- [ ] Use same model as node/feature embeddings
- [ ] Test models: sentence-transformers (e.g., `all-MiniLM-L6-v2`)

---

### Phase 2: Graph Retrieval Layer (Days 3-5)
**Priority: CRITICAL**

#### 2.1 Baseline: Cypher Queries (`src/retrieval/baseline_retriever.py`)
**Required: 10+ query templates**

Example queries:
1. Find player by name
2. Get player stats for a season
3. Top scorers in a position
4. Players from a specific team
5. Fixtures for a gameweek
6. Player performance in recent gameweeks
7. Compare two players
8. Team's home/away performance
9. Players with assists > X
10. Best players by ICT index

**Tasks:**
- [ ] Write Cypher query templates in `cypher_queries/queries.cypher`
- [ ] Implement parameterized query execution
- [ ] Map intents to queries

#### 2.2 Embeddings (`src/retrieval/embedding_retriever.py`)
**Choose ONE approach:**

**Option A: Feature Vector Embeddings** (RECOMMENDED for FPL)
- Create text descriptions from player stats
- Example: "Player Salah plays as FWD. Total goals: 23, assists: 13, points: 303"
- Embed these descriptions
- Store in Neo4j vector index

**Option B: Node Embeddings**
- Use numerical feature vectors from PLAYED_IN stats
- Combine: [goals, assists, points, minutes, influence, creativity, threat]
- Use directly or with Node2Vec

**Tasks:**
- [ ] Choose 2+ embedding models (e.g., `all-MiniLM-L6-v2`, `all-mpnet-base-v2`)
- [ ] Generate embeddings for all players
- [ ] Create Neo4j vector index
- [ ] Implement similarity search

#### 2.3 Hybrid Retriever (`src/retrieval/hybrid_retriever.py`)
- [ ] Combine Cypher + embedding results
- [ ] Remove duplicates
- [ ] Rank by relevance

---

### Phase 3: LLM Layer (Days 6-7)
**Priority: HIGH**

#### 3.1 Prompt Engineering (`src/llm/prompts.py`)
**Structured prompt template:**
```
Context: [Retrieved KG data]
Persona: You are an FPL expert assistant...
Task: Answer using only the provided context...
```

**Tasks:**
- [ ] Create prompt templates
- [ ] Format KG results for LLM input
- [ ] Handle different intent types

#### 3.2 LLM Integration (`src/llm/generator.py`)
**Test 3+ models:**
- Free options: Gemma-2-2b, Llama-3-8B, Mistral-7B (via HuggingFace)
- Paid (optional): GPT-3.5, GPT-4, Claude

**Tasks:**
- [ ] Set up HuggingFace API
- [ ] Implement model switching
- [ ] Handle API rate limits

#### 3.3 Evaluation (`src/llm/evaluator.py`)
**Metrics:**
- Quantitative: accuracy, response time, token count, cost
- Qualitative: relevance, correctness, naturalness

**Tasks:**
- [ ] Create test dataset (20+ questions)
- [ ] Implement evaluation metrics
- [ ] Compare models

---

### Phase 4: UI (Days 8-9)
**Priority: MEDIUM**

#### 4.1 Streamlit App (`src/ui/app.py`)
**Features:**
- [ ] User input field
- [ ] Model selection dropdown
- [ ] Retrieval method selection (baseline/embeddings/hybrid)
- [ ] Display KG context
- [ ] Display final answer
- [ ] Optional: Show Cypher queries
- [ ] Optional: Graph visualization

#### 4.2 Visualizations
- [ ] Graph viz of retrieved nodes (`src/ui/graph_viz.py`)
- [ ] Stats charts (`src/ui/stats_viz.py`)

---

### Phase 5: Documentation & Analysis (Days 10-11)
**Priority: HIGH**

- [ ] System architecture diagram
- [ ] Document retrieval strategies
- [ ] LLM comparison report
- [ ] Error analysis
- [ ] Improvements made
- [ ] Known limitations

---

## Suggested Task: Fantasy Team Recommender

**User Input:** "Recommend 3 forwards under 10M budget with good form"

**System Flow:**
1. Intent: `recommendation`
2. Entities: position=FWD, budget=10M, criteria=form
3. Cypher: Query forwards, filter by budget
4. Embeddings: Find similar high-performing players
5. LLM: Synthesize recommendation with explanations

---

## Testing Strategy

### Unit Tests:
- [ ] Intent classifier accuracy
- [ ] Entity extraction coverage
- [ ] Cypher query correctness
- [ ] Embedding similarity

### Integration Tests:
- [ ] End-to-end query flow
- [ ] Different question types

### User Testing:
- [ ] 20+ sample questions
- [ ] Edge cases

---

## Timeline (8 days remaining until Dec 15)

**Dec 7-8:** Preprocessing (intent + entity extraction)
**Dec 9-10:** Retrieval (Cypher + embeddings)
**Dec 11:** LLM integration
**Dec 12:** UI development
**Dec 13:** Testing + evaluation
**Dec 14:** Documentation + polish
**Dec 15:** Final submission

---

## Quick Start Checklist

Before coding:
- [x] Neo4j connection verified
- [x] Schema explored
- [ ] Install all requirements: `pip install -r requirements.txt`
- [ ] Download spaCy model: `python -m spacy download en_core_web_sm`
- [ ] Set up HuggingFace token (if using their API)
- [ ] Create sample test questions

Start with:
1. Intent classifier (simplest: keyword-based)
2. One Cypher query that works
3. Connect to a free LLM
4. Basic Streamlit UI
5. Then iterate and improve!

---

## Notes

- Player nodes are missing `name`, `team`, `position` properties directly - these might be in relationships or need fixing
- Focus on PLAYED_IN relationship - it has all the rich stats
- Start simple, add complexity gradually
- Use free models first to save costs
- Test each component individually before integration
