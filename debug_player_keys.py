"""Debug script to check what keys are in player dictionaries."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.retrieval.hybrid_retriever import HybridRetriever

def main():
    # Initialize retriever
    retriever = HybridRetriever()
    
    query = "Who were the best performing midfielders in gameweek 5 season 2021-22?"
    
    print("Testing Baseline + Embedding1 mode:")
    print("=" * 80)
    
    results = retriever.retrieve(
        query=query,
        retrieval_mode="baseline+embedding1",
        season="2021-22"
    )
    
    players = results.get('unified_players', [])
    
    if players:
        print(f"\nTotal players: {len(players)}")
        print("\nFirst player's keys:")
        print(players[0].keys())
        print("\nFirst player's data:")
        for key, value in list(players[0].items())[:15]:
            print(f"  {key}: {value}")
        
        if len(players) > 1:
            print("\n\nSecond player's keys:")
            print(players[1].keys())
            print("\nSecond player's data:")
            for key, value in list(players[1].items())[:15]:
                print(f"  {key}: {value}")
    else:
        print("No players found!")

if __name__ == "__main__":
    main()
