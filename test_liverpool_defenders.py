"""Test Liverpool defenders query with full pipeline (retrieval + LLM generation)."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.retrieval.hybrid_retriever import HybridRetriever
from src.llm.generator import FPLAnswerGenerator
from src.llm.prompts import build_fpl_prompt
import time

def test_full_pipeline(query, mode, season="2022-23"):
    """Test full pipeline: retrieval + LLM generation."""
    print(f"\n{'='*80}")
    print(f"MODE: {mode}")
    print(f"{'='*80}")
    
    # Use FPLAnswerGenerator which handles both retrieval and generation
    generator = FPLAnswerGenerator()
    
    # Test all 3 models
    models = [
        ("llama-4-maverick", "Llama 4 Maverick"),
        ("qwen-3-32b", "Qwen 3 32B"),
        ("gpt-oss-20b", "GPT OSS 20B")
    ]
    
    for model_id, model_name in models:
        print(f"\n🤖 {model_name}")
        print("   " + "-" * 76)
        
        start = time.time()
        result = generator.answer(
            query=query,
            season=season,
            model=model_id,
            max_tokens=1024,
            retrieval_mode=mode
        )
        total_time = time.time() - start
        
        response = result.get('answer', 'No response')
        context = result.get('context', {})
        
        # Show retrieval info
        players = context.get('unified_players', [])
        intent = context.get('intent', 'N/A')
        confidence = context.get('intent_confidence', 0)
        
        print(f"   ⏱️  Total Time: {total_time:.2f}s")
        print(f"   📊 Intent: {intent}")
        print(f"   🎯 Confidence: {confidence:.2%}")
        print(f"   👥 Players Retrieved: {len(players)}")
        print(f"   📝 Response Length: {len(response)} chars")
        
        if players:
            print(f"\n   📋 TOP 3 RETRIEVED:")
            for i, player in enumerate(players[:3], 1):
                name = player.get('player_name', player.get('player', 'Unknown'))
                position = player.get('position', 'N/A')
                points = player.get('total_points', 0)
                print(f"      {i}. {name} ({position}) - {points} pts")
        
        print(f"\n   Response:\n")
        
        # Print response with indentation
        for line in response.split('\n'):
            print(f"   {line}")
        
        print()
    
    generator.close()
    
    return result

def main():
    print("=" * 80)
    print("FULL PIPELINE TEST: Liverpool Defenders 2022-23")
    print("=" * 80)
    
    query = "top liverpool defenders season 2022"
    season = "2022-23"
    
    print(f"\n📝 Query: '{query}'")
    print(f"🗓️  Season: {season}")
    
    # Test all 3 retrieval modes
    modes = [
        ("baseline", "Baseline Only (Cypher)"),
        ("baseline+embedding1", "Baseline + Embedding Model 1 (mpnet 768D)"),
        ("baseline+embedding2", "Baseline + Embedding Model 2 (MiniLM 384D)")
    ]
    
    for mode_id, mode_name in modes:
        print(f"\n\n{'#'*80}")
        print(f"# RETRIEVAL MODE: {mode_name}")
        print(f"{'#'*80}")
        
        test_full_pipeline(query, mode_id, season)
        
        print("\n" + "="*80)
        input("\nPress Enter to continue to next mode...")
    
    print("\n✅ Full pipeline test completed!")

if __name__ == "__main__":
    main()
