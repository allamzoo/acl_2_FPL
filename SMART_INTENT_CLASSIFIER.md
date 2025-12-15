# Smart Hybrid Intent Classifier

## Overview

A smart agent that combines **fast rule-based classification** with **intelligent LLM fallback** for uncertain cases.

## How It Works

### Architecture

```
User Query
    ↓
[Rule-Based Classification]
    ↓
High Confidence (≥0.85)?
    ↓                ↓
   YES              NO
    ↓                ↓
Return Result   [Smart LLM Agent]
                     ↓
                Uses Groq API
                     ↓
                Return Result
```

### Key Features

1. **Fast First**: Uses rule-based keyword matching for clear queries
2. **Smart Fallback**: Groq LLM (llama-3.3-70b-versatile) handles ambiguous cases
3. **Context-Aware**: LLM sees the rule-based attempt and uses it as context
4. **Efficient**: Only calls LLM when necessary (saves costs and time)

## Implementation

### HybridIntentClassifier

```python
classifier = HybridIntentClassifier(
    confidence_threshold=0.85,  # Minimum confidence for rule-based
    model_name="llama-3.3-70b-versatile"  # Groq model
)

result = classifier.classify("Who are the best players?")
```

### Result Structure

```python
{
    "intent": Intent.TOP_SCORERS,
    "confidence": 0.92,
    "reasoning": "LLM understood context",
    "method": "llm",  # or "rule_based"
    "llm_used": True,  # or False
    "rule_based_suggestion": {  # Only if LLM was used
        "intent": "unknown",
        "confidence": 0.3
    }
}
```

## Examples

### Clear Query (Rule-Based)

**Query**: "Who are the top scorers?"

- **Rule-Based**: top_scorers (confidence: 0.95)
- **Result**: Uses rule-based (fast, no LLM call)
- **Time**: ~1ms

### Ambiguous Query (LLM Agent)

**Query**: "Show me the best players"

- **Rule-Based**: unknown (confidence: 0.3)
- **LLM Agent**: Analyzes context → top_scorers (confidence: 0.88)
- **Result**: Uses LLM classification
- **Time**: ~500ms

### Vague Query (LLM Agent)

**Query**: "Who's on fire?"

- **Rule-Based**: player_form (confidence: 0.75) - uncertain
- **LLM Agent**: Understands "on fire" = recent form → player_form (confidence: 0.92)
- **Result**: Uses LLM classification
- **Time**: ~500ms

## Benefits

1. **Performance**: Fast for 70% of queries (rule-based)
2. **Intelligence**: Smart for 30% of queries (LLM)
3. **Cost-Effective**: Only uses Groq API when needed
4. **Accurate**: LLM sees rule-based context for better decisions
5. **Graceful Degradation**: Falls back to rules if LLM unavailable

## Configuration

### In UI (app.py)

Users can choose:
- **Rule-Based**: Fast, keyword-based only
- **Smart Hybrid**: Rules + intelligent LLM agent

### Default Settings

- Confidence threshold: 0.85
- LLM model: llama-3.3-70b-versatile (Groq)
- Temperature: 0.1 (consistent classification)
- Max tokens: 150

## Testing

### Quick Test

```bash
python test_smart_intent.py
```

### Comprehensive Test

```bash
python test_hybrid_intent.py
```

## Available Intents

1. **player_search** - Find specific player by name
2. **player_stats** - Get player statistics for season
3. **top_scorers** - Top goal scorers by position
4. **top_assisters** - Top assist providers
5. **team_analysis** - Team players and performance
6. **gameweek_performers** - Top performers in gameweek
7. **player_comparison** - Compare multiple players
8. **high_performers** - Players exceeding thresholds
9. **player_form** - Recent player form analysis
10. **ict_analysis** - Best ICT scores

## Integration

### With HybridRetriever

The classifier is used in the retrieval pipeline:

```python
# In hybrid_retriever.py
result = intent_classifier.classify(query)
intent = result["intent"]
confidence = result["confidence"]

# Route to appropriate retriever method
cypher_results = self._execute_intent_query(intent, entities, season)
```

### Performance Metrics

- **Rule-Based Success**: ~70% of queries
- **LLM Fallback**: ~30% of queries
- **Average Response Time**: ~150ms (mixed)
- **Rule-Only Time**: ~1ms
- **LLM Time**: ~500ms

## Future Improvements

1. **Caching**: Cache LLM results for similar queries
2. **Learning**: Track which intents need LLM most often
3. **Adaptive Threshold**: Adjust confidence threshold based on accuracy
4. **Multi-Intent**: Support queries with multiple intents
5. **Confidence Calibration**: Fine-tune confidence scores

## Notes

- Uses same rule-based logic as SimpleIntentClassifier
- LLM is a smart agent that understands context
- No local models - uses fast Groq API
- Graceful degradation if API unavailable
- Cost-effective (only calls API when needed)
