# Structured Prompt System Implementation

## Overview
Implemented a 3-component structured prompt system for the FPL Graph-RAG to improve answer quality and reduce hallucinations by explicitly grounding the LLM in Knowledge Graph data.

## Prompt Structure

### 1. PERSONA Component
Defines the assistant's role and expertise:

```
You are an expert Fantasy Premier League (FPL) analyst with deep knowledge of:
- Player performance analysis (goals, assists, points, form, consistency)
- Statistical insights (xG, xA, ICT index, bonus points, clean sheets)
- Positional analysis (GK, DEF, MID, FWD roles and requirements)
- Value assessment (budget constraints, price vs. performance)
- Team selection strategy (differentials, captains, enablers)
- Fixture analysis and gameweek planning
```

**Purpose:** Establishes the LLM's role and sets expectations for expert-level FPL advice.

---

### 2. CONTEXT Component
Retrieved Knowledge Graph information formatted for the LLM:

**Player Statistics (ranked by relevance):**
- Player name and position
- Goals, assists, total points
- Advanced metrics (ICT index, influence, creativity, threat)
- Clean sheets, bonus points, minutes played
- Per-90 statistics when available
- Relevance score and source (baseline/semantic/hybrid)

**Additional Structured Query Results:**
- Baseline Cypher query results
- Detailed player comparisons
- Aggregate statistics

**Purpose:** Provides factual, structured data from the Knowledge Graph that the LLM must use exclusively.

---

### 3. TASK Component
Clear instructions on what to do with the context:

#### Available Task Types:

**a) ANSWER (General QA)**
```
Instructions:
1. Base answer exclusively on provided statistics
2. Cite specific numbers to support answer
3. If insufficient information, state clearly
4. Do NOT make up information
5. Do NOT hallucinate player names or stats
6. Be concise but informative
```

**b) RECOMMEND (Player Recommendations)**
```
Instructions:
1. Analyze player data against user requirements
2. Rank by relevance (stats, position, value)
3. Provide top 3-5 recommendations with justification
4. Include key statistics for each
5. Mention trade-offs (price, form, fixtures)
6. Do NOT recommend players not in context
```

**c) COMPARE (Player Comparisons)**
```
Instructions:
1. Identify players to compare from context
2. Present structured comparison
3. Highlight strengths and weaknesses
4. Provide clear conclusion
5. State if any player is missing
6. Use actual numbers from context
7. Consider multiple dimensions
```

**d) EXPLAIN (Statistical Explanations)**
```
Instructions:
1. Identify relevant statistics from context
2. Provide clear explanations
3. Put statistics in context (per 90, percentiles)
4. Highlight notable patterns/trends
5. Only discuss stats present in context
```

**Purpose:** Explicitly instructs the LLM on expected behavior and constraints to prevent hallucinations.

---

## Implementation

### File: `src/llm/prompts.py`

**Class:** `FPLPromptBuilder`

**Key Methods:**

1. **`format_context(retrieval_context)`**
   - Converts hybrid retriever output into structured text
   - Formats unified player statistics with all relevant metrics
   - Includes baseline query results
   - Adds relevance scores and source tags

2. **`build_prompt(query, retrieval_context, task_type)`**
   - Assembles complete prompt: PERSONA + CONTEXT + TASK
   - Supports 4 task types: answer, recommend, compare, explain
   - Returns formatted prompt ready for LLM

3. **`build_simple_prompt(query, retrieval_context)`**
   - Convenience method for common QA use case
   - Default task_type="answer"

**Convenience Function:**
```python
build_fpl_prompt(query, context, task="answer")
```

---

## Example Prompts

### Example 1: Answer Task
**Query:** "Who are the best attacking midfielders with high creativity?"

**Generated Prompt:**
- **PERSONA:** FPL Expert with defined expertise areas
- **CONTEXT:** 7 relevant midfielders with creativity metrics
  - Mohamed Salah: 19G, 13A, 239 pts (Sim: 0.838)
  - Christian Eriksen: 1G, 9A, 103 pts (Sim: 0.839)
  - Dejan Kulusevski: 2G, 7A, 96 pts (Sim: 0.841)
  - etc.
- **TASK:** Answer using only provided information, cite statistics

**Prompt Length:** 3,033 characters

---

### Example 2: Recommend Task
**Query:** "Recommend cheap defenders under 5 million for my FPL team"

**Generated Prompt:**
- **PERSONA:** FPL Expert
- **CONTEXT:** 8 defenders with pricing consideration
  - Trent Alexander-Arnold: 2G, 11A, 156 pts, 10 CS (Sim: 0.838)
  - Andrew Robertson: 0G, 8A, 121 pts, 9 CS (Sim: 0.811)
  - John Stones: 2G, 2A, 93 pts, 7 CS (Sim: 0.786)
  - Plus detailed season stats for top 3
- **TASK:** Provide top 3-5 recommendations with justification

**Prompt Length:** 3,994 characters

---

### Example 3: Compare Task
**Query:** "Compare Mohamed Salah and Kevin De Bruyne"

**Generated Prompt:**
- **PERSONA:** FPL Expert
- **CONTEXT:** 7 players including Salah
  - Mohamed Salah: 19G, 13A, 239 pts, 3290 mins, ICT 9.31
  - (KDB not in top results, but would be included if found)
- **TASK:** Structured comparison with strengths/weaknesses

**Prompt Length:** 3,252 characters

---

## Benefits

### 1. Reduces Hallucinations
- Explicit instruction: "Do NOT make up information"
- "Use ONLY the information provided in the CONTEXT section"
- Clear boundary between what LLM knows and what it should use

### 2. Improves Answer Quality
- Persona sets expert-level expectations
- Structured context makes data easy to parse
- Task instructions guide response format

### 3. Grounds LLM in Knowledge Graph
- All statistics come from Neo4j database
- Hybrid retrieval ensures relevant, accurate data
- Source tags show where information originated

### 4. Flexible Task Types
- Different instructions for different use cases
- Supports QA, recommendations, comparisons, explanations
- Easy to add new task types

### 5. Transparent Data Flow
```
User Query 
  → Hybrid Retriever (Cypher + Embeddings)
  → Context Formatting
  → Structured Prompt (Persona + Context + Task)
  → LLM
  → Grounded Answer
```

---

## Testing

**Test File:** `test_prompt_structure.py`

**Tests:**
1. Individual component display (persona, task templates)
2. Full prompt generation with real KG data
3. Multiple task types (answer, recommend, compare)
4. Prompt length and structure breakdown

**Results:**
✅ All 3 components correctly integrated
✅ Context properly formatted from hybrid retriever
✅ Task-specific instructions included
✅ Prompt lengths reasonable (3,000-4,000 characters)

---

## Next Steps

1. **LLM Integration:** Implement `src/llm/generator.py` with multiple models
2. **Response Evaluation:** Test answer quality across different LLMs
3. **Prompt Tuning:** Refine instructions based on LLM outputs
4. **UI Integration:** Add task type selector in Streamlit app
5. **Caching:** Cache prompts for identical queries

---

## Usage Example

```python
from src.retrieval.hybrid_retriever import HybridRetriever
from src.llm.prompts import build_fpl_prompt

# Initialize retriever
retriever = HybridRetriever()

# Get context from Knowledge Graph
query = "Best midfielders with high creativity?"
context = retriever.retrieve(query, season="2022-23")

# Build structured prompt
prompt = build_fpl_prompt(
    query=query,
    context=context,
    task="answer"  # or "recommend", "compare", "explain"
)

# Send to LLM (next step)
# response = llm.generate(prompt)
```

---

## File Structure

```
src/llm/
├── prompts.py          # ✅ Structured prompt builder
├── generator.py        # TODO: LLM integration
├── evaluator.py        # TODO: Response quality evaluation
└── models.py           # TODO: Multi-model support
```

---

## Summary

The structured prompt system is **fully implemented and tested**. It provides:

✅ **PERSONA:** FPL expert role definition  
✅ **CONTEXT:** Formatted KG data (nodes, relationships, statistics)  
✅ **TASK:** Clear instructions with 4 task types  

This approach explicitly grounds the LLM in Knowledge Graph data and provides clear instructions to prevent hallucinations while improving answer quality.

**Status:** Ready for LLM integration (next milestone step)
