"""Test the complete LLM pipeline with fixed retrieval"""
import sys
sys.path.append('C:\\Users\\Marwan Allam\\fpl-graph-rag')

from src.llm.generator import FPLAnswerGenerator

print("=" * 70)
print("TESTING COMPLETE LLM PIPELINE WITH 3 MODELS")
print("=" * 70)

generator = FPLAnswerGenerator()

# Test query
query = "Who was the top scorer in the 2022-23 season?"

print(f"\nQuery: {query}")
print("\n" + "-" * 70)

# Generate answer with 3-model comparison
print("\n🔍 Generating answers from all 3 models...")
comparison = generator.compare_models(query)

print("\n" + "=" * 70)
print("COMPARISON RESULTS")
print("=" * 70)

# Check if models key exists and is a dict
models = comparison.get('models', {})
for model_name, model_result in models.items():
    if isinstance(model_result, dict):
        answer = model_result.get('answer', model_result.get('response', 'No answer'))
        time = model_result.get('response_time', model_result.get('time', 0))
        tokens = model_result.get('tokens', 'N/A')
    else:
        answer = str(model_result)
        time = 0
        tokens = 'N/A'
    
    print(f"\n{'='*70}")
    print(f"MODEL: {model_name}")
    print(f"Time: {time:.2f}s | Tokens: {tokens}")
    print(f"{'='*70}")
    print(answer)

# Show context that was retrieved
print("\n" + "=" * 70)
print("RETRIEVED CONTEXT")
print("=" * 70)
context = comparison.get('context', 'No context found')
if len(context) > 500:
    print(context[:500] + "...\n[Context truncated for display]")
else:
    print(context)

print("\n" + "=" * 70)
print("✅ 3-MODEL COMPARISON COMPLETE!")
print("=" * 70)
