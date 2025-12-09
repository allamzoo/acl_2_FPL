"""
Comprehensive Intent Classifier Test
Tests the SimpleIntentClassifier with diverse FPL queries.
"""

from src.preprocessing.intent_classifier import SimpleIntentClassifier, Intent
from colorama import init, Fore, Style

# Initialize colorama for colored output
init(autoreset=True)


def test_intent_classifier():
    """Test intent classification with comprehensive FPL queries."""
    
    classifier = SimpleIntentClassifier()
    
    # Test queries organized by intent
    test_cases = {
        Intent.PLAYER_SEARCH: [
            "Who is Mohamed Salah?",
            "Find player named Harry Kane",
            "Tell me about Kevin De Bruyne",
            "Search for Cristiano Ronaldo",
        ],
        
        Intent.PLAYER_STATS: [
            "What are Salah's stats for 2021-22 season?",
            "Show me Kevin De Bruyne's performance in 2021-22",
            "Get statistics for Harry Kane",
            "Display Bruno Fernandes season stats",
        ],
        
        Intent.TOP_SCORERS: [
            "Who scored the most goals among forwards in 2021-22?",
            "Top 10 goal scorers for midfielders",
            "Best scorers in the league",
            "Leading goal scorers by position",
        ],
        
        Intent.TOP_ASSISTERS: [
            "Who had the most assists in 2021-22?",
            "Best playmakers among midfielders",
            "Top assist providers",
            "Show me the assist leaders",
        ],
        
        Intent.TEAM_ANALYSIS: [
            "Show me Liverpool's squad for 2021-22",
            "Which players played for Arsenal?",
            "Get team roster for Manchester City",
            "Liverpool players and their stats",
        ],
        
        Intent.GAMEWEEK_PERFORMERS: [
            "Who were the best players in gameweek 1?",
            "Top performers in GW 10 of 2021-22",
            "Show me week 5 top scorers",
            "Gameweek 15 best players",
        ],
        
        Intent.PLAYER_COMPARISON: [
            "Compare Salah and Kane in 2021-22",
            "How does Son compare to Mane?",
            "Salah vs De Bruyne statistics",
            "Show me the difference between Ronaldo and Vardy",
        ],
        
        Intent.HIGH_PERFORMERS: [
            "Which players scored more than 15 goals?",
            "Find players with at least 20 goals in 2021-22",
            "Players with over 200 points",
            "Show me forwards with >= 10 assists",
        ],
        
        Intent.PLAYER_FORM: [
            "How has Salah performed in recent gameweeks?",
            "Show me Kane's form over the last 5 games",
            "What's De Bruyne's recent performance?",
            "Salah's form lately",
        ],
        
        Intent.ICT_ANALYSIS: [
            "Who has the best ICT index among midfielders?",
            "Top players by influence, creativity and threat",
            "Show me ICT leaders",
            "Best creativity scores for forwards",
        ],
    }
    
    print("=" * 100)
    print(f"{Fore.CYAN}{Style.BRIGHT}INTENT CLASSIFIER COMPREHENSIVE TEST")
    print("=" * 100)
    
    total_tests = 0
    correct_classifications = 0
    
    for expected_intent, queries in test_cases.items():
        print(f"\n{Fore.YELLOW}{Style.BRIGHT}Testing Intent: {expected_intent.value.upper()}")
        print(f"{Fore.YELLOW}{'─' * 100}")
        
        for query in queries:
            total_tests += 1
            result = classifier.classify(query)
            
            # Check if classification matches expected
            is_correct = result['intent'] == expected_intent
            if is_correct:
                correct_classifications += 1
            
            # Color code the output
            status_color = Fore.GREEN if is_correct else Fore.RED
            status_symbol = "✓" if is_correct else "✗"
            
            print(f"\n{status_color}{status_symbol} Query: {Fore.WHITE}\"{query}\"")
            print(f"   {Fore.CYAN}Classified as: {Fore.WHITE}{result['intent'].value}")
            print(f"   {Fore.CYAN}Confidence: {Fore.WHITE}{result['confidence']:.2f}")
            print(f"   {Fore.CYAN}Reasoning: {Fore.WHITE}{result['reasoning']}")
            print(f"   {Fore.CYAN}Retriever method: {Fore.WHITE}{classifier.get_query_mapping(result['intent'])}")
            
            if not is_correct:
                print(f"   {Fore.RED}Expected: {expected_intent.value}")
    
    # Summary
    accuracy = (correct_classifications / total_tests) * 100
    
    print("\n" + "=" * 100)
    print(f"{Fore.CYAN}{Style.BRIGHT}TEST SUMMARY")
    print("=" * 100)
    print(f"{Fore.WHITE}Total Tests: {total_tests}")
    print(f"{Fore.GREEN}Correct: {correct_classifications}")
    print(f"{Fore.RED}Incorrect: {total_tests - correct_classifications}")
    print(f"{Fore.YELLOW}Accuracy: {accuracy:.1f}%")
    
    if accuracy >= 90:
        print(f"\n{Fore.GREEN}{Style.BRIGHT}✓ EXCELLENT! Classifier performing very well.")
    elif accuracy >= 75:
        print(f"\n{Fore.YELLOW}{Style.BRIGHT}⚠ GOOD! Minor improvements possible.")
    else:
        print(f"\n{Fore.RED}{Style.BRIGHT}✗ NEEDS IMPROVEMENT")
    
    print("=" * 100)
    
    # Test edge cases
    print(f"\n{Fore.MAGENTA}{Style.BRIGHT}EDGE CASE TESTING")
    print(f"{Fore.MAGENTA}{'=' * 100}")
    
    edge_cases = [
        "asdfghjkl random text",
        "What is the weather today?",
        "",
        "FPL",
        "Tell me everything about fantasy football",
    ]
    
    for query in edge_cases:
        result = classifier.classify(query)
        print(f"\n{Fore.WHITE}Query: \"{query}\"")
        print(f"  {Fore.CYAN}→ {result['intent'].value} (confidence: {result['confidence']:.2f})")
        print(f"  {Fore.CYAN}Reasoning: {result['reasoning']}")
    
    print("\n" + "=" * 100)


if __name__ == "__main__":
    test_intent_classifier()
