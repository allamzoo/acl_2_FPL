"""Quick test for intent classifier"""

# Test without imports from other modules
query = "WHO ARE THE TOP SCORERS"
query_lower = query.lower().strip()

# Test the matching logic
print(f"Query: '{query}'")
print(f"Query lower: '{query_lower}'")
print(f"'top' in query_lower: {'top' in query_lower}")
print(f"'scorer' in query_lower: {'scorer' in query_lower}")

# Test the condition
if "top" in query_lower:
    if any(x in query_lower for x in ["scorer", "goal", "attack", "forward", "striker"]) and not any(x in query_lower for x in ["assist"]):
        print("\n✅ MATCH: Would return Intent.TOP_SCORERS with 0.95 confidence")
    else:
        print("\n❌ NO MATCH on first check")
        
# Test second check
if any(phrase in query_lower for phrase in [
    "topscorers", "top scorers", "top scorer", "topscorer",
    "most goals", "goal scorers", "goalscorers", "goal scorer",
    "best scorers", "leading scorers", "highest scorers",
    "who scored", "top goal", "highest goal", "goals leader",
    "who are the top", "top attackers", "best attackers"
]):
    print("✅ MATCH on detailed phrase check too!")
else:
    print("❌ No match on detailed phrase check")
