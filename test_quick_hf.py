"""
Quick HuggingFace Test - Single Model
Tests if the API is working with updated model versions
"""

import os
from dotenv import load_dotenv
load_dotenv()

from src.llm.generator import create_answer_generator

print("="*80)
print(" "*20 + "Quick HuggingFace Test")
print("="*80)

# Use HuggingFace
generator = create_answer_generator(llm_backend="huggingface", default_llm="qwen-2.5")

try:
    query = "Who is the top goalscorer?"
    print(f"\nQuery: '{query}'")
    print("Model: Qwen 2.5 7B Instruct")
    print("Backend: HuggingFace")
    print("\nGenerating answer...")
    
    result = generator.answer(
        query=query,
        season="2022-23",
        model="qwen-2.5",
        max_tokens=256,
        temperature=0.3
    )
    
    print(f"\n{'='*80}")
    print("RESULT")
    print(f"{'='*80}")
    
    if 'error' in result and result.get('error'):
        print(f"\n❌ Error: {result.get('answer', result.get('error'))}")
        print("\nPossible reasons:")
        print("  • Model is loading (first request can take 20-30 seconds)")
        print("  • Rate limit reached (free tier limits)")
        print("  • Model version changed/deprecated")
        print("\nTry again in a minute or check: https://huggingface.co/mistralai/Mistral-7B-Instruct-v0.3")
    else:
        print(f"\n✅ Success!")
        print(f"\nAnswer:")
        print("-"*80)
        print(result['answer'])
        print("-"*80)
        
        print(f"\n📊 Stats:")
        print(f"  • Tokens: {result['tokens']}")
        print(f"  • Retrieved players: {result['context']['num_players']}")
        print(f"  • Backend: {result['backend']}")

finally:
    generator.close()

print("\n" + "="*80)
