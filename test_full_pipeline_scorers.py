"""Test full pipeline for top scorers query."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.retrieval.hybrid_retriever import HybridRetriever
from src.llm.generator import FPLAnswerGenerator
import time

# Test query
query = "top scorers 2021"
season = "2021-22"

print("="*80)
print("TESTING FULL PIPELINE: Top Scorers 2021")
print("="*80)
print(f"\nQuery: {query}")
print(f"Season: {season}")
print("\n" + "="*80 + "\n")

# Step 1: Retrieval
print("🔍 STEP 1: RETRIEVAL")
print("-"*80)
retriever = HybridRetriever()

start = time.time()
retrieval_results = retriever.retrieve(
    query=query,
    retrieval_mode="baseline",
    season=season
)
retrieval_time = time.time() - start

intent = retrieval_results.get('intent', 'N/A')
if hasattr(intent, 'value'):
    intent_str = intent.value
else:
    intent_str = str(intent)

print(f"Intent: {intent_str}")
print(f"Confidence: {retrieval_results.get('confidence', 0):.0%}")
print(f"Retrieval Time: {retrieval_time:.2f}s")

players = retrieval_results.get('unified_players', [])
print(f"Players Retrieved: {len(players)}")

if players:
    print("\nTop 5 Players Retrieved:")
    for i, player in enumerate(players[:5], 1):
        name = player.get('player_name', player.get('player', 'Unknown'))
        goals = player.get('total_goals', player.get('goals', 0))
        points = player.get('total_points', 0)
        print(f"  {i}. {name} - {goals} goals, {points} pts")

print("\n" + "="*80 + "\n")

# Step 2: Generation
print("🤖 STEP 2: LLM GENERATION")
print("-"*80)

generator = FPLAnswerGenerator()

start = time.time()
result = generator.answer(
    query=query,
    season=season,
    model="llama-4-maverick",
    retrieval_mode="baseline"
)
generation_time = time.time() - start

response = result.get('answer', 'No response generated')

print(f"Generation Time: {generation_time:.2f}s")
print(f"Total Pipeline Time: {retrieval_time + generation_time:.2f}s")
print("\n" + "="*80)
print("FINAL RESPONSE:")
print("="*80)
print(response)
print("="*80)

retriever.close()
