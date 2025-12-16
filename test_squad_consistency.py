#!/usr/bin/env python3
"""Test squad builder consistency with randomization."""

from src.retrieval.baseline_retriever import BaselineRetriever

print("Testing Squad Builder - Ensuring 15 Players & Budget Compliance\n")
print("="*70)

all_success = True

for i in range(10):
    retriever = BaselineRetriever()
    result = retriever.build_squad_under_budget(
        season='2022-23', 
        budget=100.0, 
        randomize=True
    )
    
    squad_size = result['squad_size']
    total_cost = result['total_cost']
    
    status = "✅" if squad_size == 15 and total_cost <= 100.0 else "❌"
    
    if squad_size != 15 or total_cost > 100.0:
        all_success = False
    
    print(f"{status} Test {i+1:2d}: Size={squad_size:2d}/15, Cost=£{total_cost:5.1f}m, Budget OK={total_cost <= 100.0}")
    
    retriever.close()

print("="*70)
if all_success:
    print("\n🎉 SUCCESS: All 10 tests generated exactly 15 players under £100m!")
else:
    print("\n⚠️  ISSUE: Some tests failed to generate 15 players or exceeded budget")
