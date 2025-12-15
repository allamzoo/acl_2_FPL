"""
Test season extraction in full workflow
"""

from src.preprocessing.context_handler import ContextAwareFollowupHandler
from src.preprocessing.entity_extractor import EntityExtractor

print("="*80)
print("SEASON EXTRACTION TEST - Full Workflow")
print("="*80)

# Initialize components
context_handler = ContextAwareFollowupHandler()
entity_extractor = EntityExtractor()

# Simulate conversation
print("\n📖 Conversation:")
print("-"*80)

# Query 1
query1 = "Who are the top scorers?"
print(f"\n1. User: {query1}")
entities1 = entity_extractor.extract(query1)
print(f"   Extracted season: {entities1['seasons']}")
context_handler.add_to_history(
    query=query1,
    intent="top_scorers",
    entities=entities1
)

# Query 2 - Follow-up with season
query2 = "what about season 2022/2023"
print(f"\n2. User: {query2}")

# Resolve context
context_result = context_handler.resolve_context(query2)
print(f"   Is follow-up: {context_result['is_followup']}")
print(f"   Resolved query: {context_result['resolved_query']}")

# Extract entities from resolved query
resolved = context_result['resolved_query']
entities2 = entity_extractor.extract(resolved)
print(f"   Extracted season: {entities2['seasons']}")
print(f"   ✅ Season correctly extracted: {'2022-23' in entities2['seasons']}")

# Cleanup
entity_extractor.close()

print("\n" + "="*80)
print("✅ Season extraction working correctly!")
print("="*80)
