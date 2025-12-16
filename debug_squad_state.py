#!/usr/bin/env python3
"""Debug squad state to see what data structure looks like."""

import streamlit as st
from src.retrieval.baseline_retriever import BaselineRetriever

# Build a sample squad
retriever = BaselineRetriever()
squad_data = retriever.build_squad_under_budget(
    season="2022-23",
    budget=100.0,
    min_points=30,
    min_games=10,
    randomize=True
)

print("=" * 70)
print("RAW SQUAD DATA FROM RETRIEVER:")
print("=" * 70)
for i, player in enumerate(squad_data['squad'][:3]):  # First 3 players
    print(f"\nPlayer {i+1}:")
    for key, value in player.items():
        print(f"  {key}: {value}")

print("\n" + "=" * 70)
print("TRANSFORMED FOR SESSION STATE:")
print("=" * 70)

# Transform as done in auto_pick_squad
squad = {'GK': [], 'DEF': [], 'MID': [], 'FWD': []}
for player in squad_data['squad'][:3]:
    pos = player['position']
    transformed = {
        'name': player['player_name'],
        'team': player.get('team', 'Unknown'),
        'position': pos,
        'price': player['price'],
        'points': player['total_points'],
        'goals': player.get('goals', 0),
        'assists': player.get('assists', 0),
        'clean_sheets': 0,
        'games': 0,
        'value_ratio': player['value_ratio'],
        'fixture_difficulty': 'H'
    }
    squad[pos].append(transformed)
    print(f"\n{pos} Player:")
    for key, value in transformed.items():
        print(f"  {key}: {value}")

retriever.close()
