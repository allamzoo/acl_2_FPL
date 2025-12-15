"""Quick test to verify think tag removal"""

from src.llm.generator import strip_think_tags

# Test with complete think tags
test1 = """<think>
This is reasoning
More reasoning
</think>
Final answer here"""

print("Test 1 - Complete tags:")
print("Original:", repr(test1))
result1 = strip_think_tags(test1)
print("Cleaned:", repr(result1))
print()

# Test with truncated think
test2 = """<think>
Some reasoning that doesn't finish"""

print("Test 2 - Truncated think:")
print("Original:", repr(test2))
result2 = strip_think_tags(test2)
print("Cleaned:", repr(result2))
print()

# Test with content after think
test3 = """<think>
Reasoning here
</think>

The answer is: This is the final answer."""

print("Test 3 - Complete with answer:")
print("Original:", repr(test3))
result3 = strip_think_tags(test3)
print("Cleaned:", repr(result3))
