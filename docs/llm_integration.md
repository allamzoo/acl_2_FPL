# LLM Integration - Three Model Comparison

## ✅ Implementation Complete

The FPL Graph-RAG system now supports **three free LLM models** for answer generation and comparison.

---

## 📋 The Three Models

### 1️⃣ Mistral 7B Instruct ⭐ (Recommended Baseline)

**Model Names:**
- HuggingFace: `mistralai/Mistral-7B-Instruct-v0.2`
- OpenRouter: `mistralai/mistral-7b-instruct`

**Size:** 7 billion parameters

**Strengths:**
- ✅ Very good reasoning capabilities
- ✅ Fast inference speed
- ✅ Excellent instruction following
- ✅ Strong performance on structured tasks

**Best For:** General-purpose baseline (main model for FPL Graph-RAG)

**Why It's Great:**
Mistral 7B offers the best balance of speed, reasoning, and instruction-following. It's particularly good at understanding structured prompts (PERSONA + CONTEXT + TASK) and generating accurate, concise answers.

---

### 2️⃣ Llama 3 8B Instruct

**Model Names:**
- HuggingFace: `meta-llama/Meta-Llama-3-8B-Instruct`
- OpenRouter: `meta-llama/llama-3-8b-instruct`

**Size:** 8 billion parameters

**Strengths:**
- ✅ Strong instruction following
- ✅ Better language quality than Llama 2
- ✅ Excellent at structured output
- ✅ Good reasoning on complex queries

**Best For:** High-quality structured answers and player comparisons

**Why It's Great:**
Llama 3 excels at following detailed instructions and producing well-structured output. It's particularly good for comparison tasks and recommendations where natural language quality matters.

---

### 3️⃣ Gemma 7B Instruct (Google)

**Model Names:**
- HuggingFace: `google/gemma-7b-it`
- OpenRouter: `google/gemma-7b-it`

**Size:** 7 billion parameters

**Strengths:**
- ✅ Lightweight and fast
- ✅ Good for structured tasks
- ✅ Easy to run locally
- ✅ Efficient resource usage

**Best For:** Fast responses and resource-constrained environments

**Why It's Great:**
Gemma is optimized for efficiency, making it ideal for quick responses and situations where computational resources are limited. Good for simple Q&A tasks.

---

## 🏗️ Architecture

### Complete Pipeline:

```
User Question
    ↓
┌─────────────────────────────────────────────┐
│  1. HYBRID RETRIEVER                        │
│     • Cypher Queries (Baseline)             │
│     • Semantic Embeddings                   │
│     • Merge & Deduplicate                   │
└─────────────────────────────────────────────┘
    ↓ (Context: nodes, relationships, data)
┌─────────────────────────────────────────────┐
│  2. STRUCTURED PROMPT BUILDER               │
│     • PERSONA: FPL Expert                   │
│     • CONTEXT: Retrieved KG data            │
│     • TASK: Answer instructions             │
└─────────────────────────────────────────────┘
    ↓ (Formatted prompt)
┌─────────────────────────────────────────────┐
│  3. LLM MODEL (Choose 1 of 3)              │
│     ┌─────────────────────────────────┐    │
│     │ A. Mistral 7B    (Baseline)    │    │
│     │ B. Llama 3 8B    (Quality)     │    │
│     │ C. Gemma 7B      (Speed)       │    │
│     └─────────────────────────────────┘    │
└─────────────────────────────────────────────┘
    ↓ (Generated answer)
Final Answer to User
```

---

## 💻 Implementation Files

### 1. **src/llm/models.py** (378 lines)

**Classes:**

- **`BaseLLM`** (Abstract base class)
  - Abstract method: `generate()`
  - Tracks tokens and cost

- **`HuggingFaceLLM`** (HuggingFace Inference API)
  - Uses: `https://api-inference.huggingface.co/models/{model}`
  - Free tier available
  - Requires: `HUGGINGFACE_API_KEY`

- **`OpenRouterLLM`** (OpenRouter API)
  - Uses: `https://openrouter.ai/api/v1/chat/completions`
  - Many free models
  - Requires: `OPENROUTER_API_KEY`

- **`LLMManager`** (Manages all 3 models)
  - Methods:
    - `generate(prompt, model)` - Generate from one model
    - `generate_all(prompt)` - Generate from all 3 for comparison
    - `list_models()` - List available models
    - `get_all_stats()` - Get usage statistics

**Model Configuration:**
```python
MODELS = {
    'mistral-7b': {
        'huggingface': 'mistralai/Mistral-7B-Instruct-v0.2',
        'openrouter': 'mistralai/mistral-7b-instruct',
        'strengths': ['reasoning', 'speed', 'instruction-following']
    },
    'llama-3-8b': {
        'huggingface': 'meta-llama/Meta-Llama-3-8B-Instruct',
        'openrouter': 'meta-llama/llama-3-8b-instruct',
        'strengths': ['instruction-following', 'language-quality', 'structured-output']
    },
    'gemma-7b': {
        'huggingface': 'google/gemma-7b-it',
        'openrouter': 'google/gemma-7b-it',
        'strengths': ['speed', 'structured-tasks', 'lightweight']
    }
}
```

---

### 2. **src/llm/generator.py** (216 lines)

**Class: `FPLAnswerGenerator`**

**Methods:**

**`answer(query, season, model, task_type)`**
- Complete end-to-end pipeline
- Returns: answer, context, tokens, cost

**`compare_models(query, season, task_type)`**
- Runs all 3 models on same query
- Returns: comparison dict with all results

**Pipeline Steps:**
1. Retrieve context from KG (HybridRetriever)
2. Build structured prompt (build_fpl_prompt)
3. Generate answer with LLM (LLMManager)
4. Return formatted result

**Example Usage:**
```python
from src.llm.generator import create_answer_generator

# Initialize
generator = create_answer_generator(
    llm_backend="openrouter",
    default_llm="mistral-7b"
)

# Single model
result = generator.answer(
    query="Who are the top goalscorers?",
    season="2022-23",
    model="mistral-7b"
)

# Compare all 3 models
comparison = generator.compare_models(
    query="Who are the top goalscorers?",
    season="2022-23"
)
```

---

### 3. **src/llm/prompts.py** (268 lines)

Structured prompt builder (PERSONA + CONTEXT + TASK)
- See: `docs/prompt_structure_verification.md` for full details

---

## 📊 Comparison Criteria

The three models will be evaluated on:

### 1. ✅ Answer Quality
- **Accuracy**: Does it use only KG data?
- **Relevance**: Does it answer the question?
- **Completeness**: Does it cover all important points?

### 2. 📊 Response Accuracy
- **Statistics**: Are numbers correct from context?
- **No Hallucinations**: No made-up players/stats
- **Context Usage**: Proper citations

### 3. 💬 Language Quality
- **Clarity**: Easy to understand
- **Coherence**: Logical flow
- **Terminology**: Proper FPL terms

### 4. 🎯 Instruction Following
- **PERSONA**: Acts as FPL expert
- **CONTEXT**: Uses ONLY provided data
- **TASK**: Follows instructions (cite stats, don't hallucinate)

### 5. ⚡ Performance
- **Speed**: Response time
- **Tokens**: Prompt + completion
- **Cost**: Free models, but tokens matter for rate limits

### 6. 🔧 Use Case Fit
- **Best task types**: answer/recommend/compare?
- **Strengths/weaknesses**: For FPL Graph-RAG

---

## 🚀 Setup Instructions

### Step 1: Get API Keys

**Option A: OpenRouter (Recommended)**
1. Go to: https://openrouter.ai/keys
2. Sign up (free)
3. Create API key
4. Many models are free (including our 3 models)

**Option B: HuggingFace**
1. Go to: https://huggingface.co/settings/tokens
2. Sign up (free)
3. Create access token
4. Free inference API (rate limited)

### Step 2: Configure Environment

```bash
# Copy example file
cp .env.example .env

# Edit .env and add your key
OPENROUTER_API_KEY=your_key_here
# OR
HUGGINGFACE_API_KEY=your_key_here
```

### Step 3: Install Dependencies

```bash
pip install requests python-dotenv
```

### Step 4: Test Integration

```bash
# Test without API (integration check)
python test_llm_integration.py

# Test with API (actual LLM calls)
python test_llm_comparison.py
```

---

## 📝 Test Scripts

### 1. **test_llm_integration.py** (No API Required)
- Tests all components integrate correctly
- Shows model information
- Validates configuration
- Doesn't require API keys

**Run:**
```bash
python test_llm_integration.py
```

### 2. **test_llm_comparison.py** (Requires API Key)

**Three test modes:**

**Mode 1: Single Model Test**
- Quick validation with one model
- Tests full pipeline
- Shows answer, tokens, cost

**Mode 2: Three-Model Comparison**
- Runs all 3 models on same queries
- Side-by-side comparison
- Comparison table

**Mode 3: Task Type Test**
- Tests different task types
- Answer / Recommend / Compare
- Shows versatility

**Run:**
```bash
python test_llm_comparison.py
# Choose: 1, 2, 3, or 'all'
```

---

## 📈 Expected Results

### Response Format:

```python
{
    'query': "Who are the top goalscorers?",
    'season': "2022-23",
    'answer': "Based on the provided data, the top goalscorers are: ...",
    'context': {
        'num_players': 15,
        'unified_players': [...],  # Top 10 players
        'baseline_results': {...},
        'semantic_results': {...}
    },
    'model': 'mistral-7b',
    'model_info': {
        'description': 'Mistral 7B Instruct - Very good reasoning, fast',
        'strengths': ['reasoning', 'speed', 'instruction-following']
    },
    'tokens': 1450,
    'prompt_tokens': 1200,
    'completion_tokens': 250,
    'cost': 0.0,  # Free models
    'backend': 'OpenRouter',
    'task_type': 'answer',
    'prompt_length': 5017
}
```

### Comparison Output:

```python
{
    'query': "Who are the top goalscorers?",
    'context': {...},  # Shared context
    'models': {
        'mistral-7b': {...},   # Response from Mistral
        'llama-3-8b': {...},   # Response from Llama
        'gemma-7b': {...}      # Response from Gemma
    }
}
```

---

## 🎯 Model Selection Guidelines

**Use Mistral 7B when:**
- ✅ General Q&A (default choice)
- ✅ Need good reasoning
- ✅ Want fast responses
- ✅ Baseline for comparison

**Use Llama 3 8B when:**
- ✅ Need high-quality language
- ✅ Complex comparisons
- ✅ Structured recommendations
- ✅ Detailed analysis

**Use Gemma 7B when:**
- ✅ Need fast responses
- ✅ Simple Q&A
- ✅ Resource constraints
- ✅ Testing/prototyping

---

## 🔒 API Safety

**All three models are FREE:**
- ✅ Mistral 7B: Free on both platforms
- ✅ Llama 3 8B: Free on both platforms
- ✅ Gemma 7B: Free on both platforms

**Rate Limits:**
- HuggingFace: ~30 requests/hour (free tier)
- OpenRouter: Varies by model (check current limits)

**Cost Monitoring:**
- LLMManager tracks tokens and cost
- `get_all_stats()` shows cumulative usage
- All responses include token counts

---

## ✅ Integration Status

**Completed:**
- ✅ LLM model integration (3 models)
- ✅ Unified interface (BaseLLM)
- ✅ Two backends (HuggingFace, OpenRouter)
- ✅ Answer generator (full pipeline)
- ✅ Model comparison (side-by-side)
- ✅ Token tracking
- ✅ Error handling
- ✅ Test scripts

**Ready for:**
- ✅ Model comparison experiments
- ✅ Answer quality evaluation
- ✅ Performance benchmarking
- ✅ Streamlit UI integration

---

## 📂 File Structure

```
src/llm/
├── models.py          # ✅ LLM integrations (3 models)
├── generator.py       # ✅ Answer generation pipeline
├── prompts.py         # ✅ Structured prompts
└── evaluator.py       # TODO: Answer quality evaluation

tests/
├── test_llm_integration.py    # ✅ Integration test (no API)
└── test_llm_comparison.py     # ✅ Model comparison (requires API)

.env.example          # ✅ API key template
docs/
└── llm_integration.md  # ✅ This file
```

---

## 🚦 Next Steps

1. **Get API Key**: Sign up for OpenRouter or HuggingFace
2. **Run Comparison**: Test all 3 models on FPL queries
3. **Evaluate Results**: Compare accuracy, quality, performance
4. **Choose Best Model**: Select primary model for production
5. **Document Findings**: Create comparison report
6. **Integrate UI**: Add model selector to Streamlit app

---

## 📚 Summary

**Three-Model Comparison Implementation:**

✅ **Models Integrated:**
- Mistral 7B Instruct (baseline, reasoning, speed)
- Llama 3 8B Instruct (quality, structured output)
- Gemma 7B Instruct (speed, lightweight)

✅ **Backends Supported:**
- HuggingFace Inference API (free tier)
- OpenRouter API (many free models)

✅ **Features:**
- Single model generation
- Three-model comparison
- Token tracking
- Error handling
- Multiple task types (answer/recommend/compare/explain)

✅ **Complete Pipeline:**
User Query → Hybrid Retriever → Structured Prompt → LLM → Answer

**Status: Ready for model comparison experiments! 🎯**
