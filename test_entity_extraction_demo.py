"""
Entity Extraction Demo for Presentation

Tests entity extraction with diverse FPL queries to showcase capabilities.
"""

import sys
from src.preprocessing.entity_extractor import EntityExtractor


def tabulate(data, headers=None, tablefmt="grid"):
    """Simple tabulate replacement for formatting tables."""
    if not data:
        return ""
    
    # Calculate column widths
    if headers:
        all_rows = [headers] + data
    else:
        all_rows = data
    
    col_widths = []
    for col_idx in range(len(all_rows[0])):
        max_width = max(len(str(row[col_idx])) for row in all_rows)
        col_widths.append(max_width)
    
    # Build table
    lines = []
    separator = "+" + "+".join(["-" * (w + 2) for w in col_widths]) + "+"
    
    lines.append(separator)
    
    if headers:
        header_line = "|"
        for i, cell in enumerate(headers):
            header_line += f" {str(cell).ljust(col_widths[i])} |"
        lines.append(header_line)
        lines.append(separator)
    
    for row in data:
        row_line = "|"
        for i, cell in enumerate(row):
            row_line += f" {str(cell).ljust(col_widths[i])} |"
        lines.append(row_line)
    
    lines.append(separator)
    
    return "\n".join(lines)


def print_section(title):
    """Print formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def print_entities(query, entities):
    """Print extracted entities in a formatted table."""
    print(f"📝 Query: \"{query}\"\n")
    
    # Prepare data for tabulation
    data = []
    
    if entities.get("player_names"):
        data.append(["👤 Players", ", ".join(entities["player_names"])])
    
    if entities.get("team_names"):
        data.append(["⚽ Teams", ", ".join(entities["team_names"])])
    
    if entities.get("positions"):
        data.append(["🎯 Positions", ", ".join(entities["positions"])])
    
    if entities.get("seasons"):
        data.append(["📅 Seasons", ", ".join(entities["seasons"])])
    
    if entities.get("gameweeks"):
        data.append(["🗓️  Gameweeks", ", ".join(map(str, entities["gameweeks"]))])
    
    if entities.get("thresholds"):
        threshold_str = ", ".join([f"{k}: {v}" for k, v in entities["thresholds"].items()])
        data.append(["📊 Thresholds", threshold_str])
    
    if entities.get("stats_mentioned"):
        data.append(["📈 Stats", ", ".join(entities["stats_mentioned"])])
    
    if entities.get("limit"):
        data.append(["🔢 Limit", str(entities["limit"])])
    
    if not data:
        data.append(["ℹ️  Status", "No entities extracted"])
    
    print(tabulate(data, headers=["Entity Type", "Extracted Values"], tablefmt="grid"))
    print()


def run_demo():
    """Run entity extraction demo with various query types."""
    
    print_section("ENTITY EXTRACTION DEMONSTRATION")
    print("Testing FPL Query Understanding with Real Examples\n")
    
    # Test queries covering different entity types
    test_queries = [
        # Simple team + position queries
        "best arsenal midfielders",
        "top liverpool defenders season 2022",
        "manchester city forwards",
        
        # Player-specific queries
        "compare salah and son",
        "kane vs haaland stats",
        "how did bruno fernandes perform",
        
        # Queries with thresholds
        "players with more than 200 points",
        "defenders with over 5 goals",
        "midfielders scoring above 150 points under 8 million",
        
        # Season-specific queries
        "top scorers in 2021-22 season",
        "best players 2020/21",
        "season 2022-23 defenders",
        
        # Gameweek queries
        "gameweek 10 top performers",
        "best players in gw 25",
        "top scorers between gameweek 15 and 20",
        
        # Complex multi-entity queries
        "top 5 chelsea forwards with more than 10 goals in season 2022",
        "compare trent alexander-arnold and andrew robertson",
        "which arsenal midfielder scored the most between gw 1 and 10",
        
        # Value-based queries
        "best value forwards under 7 million",
        "cheap midfielders with good points",
        
        # Statistical queries
        "highest assists in premier league",
        "most clean sheets by goalkeepers",
        "players with best points per game",
    ]
    
    extractor = EntityExtractor()
    
    try:
        # Group queries by type for presentation
        query_groups = {
            "Team + Position Queries": test_queries[0:3],
            "Player Comparison Queries": test_queries[3:6],
            "Threshold-Based Queries": test_queries[6:9],
            "Season-Specific Queries": test_queries[9:12],
            "Gameweek Queries": test_queries[12:15],
            "Complex Multi-Entity Queries": test_queries[15:18],
            "Value-Based Queries": test_queries[18:20],
            "Statistical Queries": test_queries[20:23],
        }
        
        for group_name, queries in query_groups.items():
            print_section(group_name)
            
            for query in queries:
                entities = extractor.extract(query)
                print_entities(query, entities)
        
        # Summary statistics
        print_section("EXTRACTION CAPABILITIES SUMMARY")
        
        all_entities = [extractor.extract(q) for q in test_queries]
        
        stats = {
            "Total Queries Tested": len(test_queries),
            "Queries with Players Extracted": sum(1 for e in all_entities if e.get("player_names")),
            "Queries with Teams Extracted": sum(1 for e in all_entities if e.get("team_names")),
            "Queries with Positions Extracted": sum(1 for e in all_entities if e.get("positions")),
            "Queries with Seasons Extracted": sum(1 for e in all_entities if e.get("seasons")),
            "Queries with Gameweeks Extracted": sum(1 for e in all_entities if e.get("gameweeks")),
            "Queries with Thresholds Extracted": sum(1 for e in all_entities if e.get("thresholds")),
            "Queries with Stats Mentioned": sum(1 for e in all_entities if e.get("stats_mentioned")),
        }
        
        stats_data = [[k, v] for k, v in stats.items()]
        print(tabulate(stats_data, headers=["Metric", "Count"], tablefmt="grid"))
        print()
        
        # Entity type distribution
        print("\n📊 ENTITY TYPE DISTRIBUTION:\n")
        
        entity_counts = {
            "👤 Player Names": sum(len(e.get("player_names", [])) for e in all_entities),
            "⚽ Team Names": sum(len(e.get("team_names", [])) for e in all_entities),
            "🎯 Positions": sum(len(e.get("positions", [])) for e in all_entities),
            "📅 Seasons": sum(len(e.get("seasons", [])) for e in all_entities),
            "🗓️  Gameweeks": sum(len(e.get("gameweeks", [])) for e in all_entities),
            "📊 Thresholds": sum(len(e.get("thresholds", {})) for e in all_entities),
            "📈 Stats": sum(len(e.get("stats_mentioned", [])) for e in all_entities),
        }
        
        count_data = [[k, v] for k, v in entity_counts.items()]
        print(tabulate(count_data, headers=["Entity Type", "Total Extracted"], tablefmt="grid"))
        print()
        
        # Key Features
        print_section("KEY FEATURES")
        
        features = [
            ["✅", "Database-backed validation", "Player and team names verified against Neo4j"],
            ["✅", "Position normalization", "Maps variants (e.g., 'striker' → 'FWD')"],
            ["✅", "Season format flexibility", "Handles '2022', '2021-22', '2020/21'"],
            ["✅", "Gameweek extraction", "Supports ranges and single GWs"],
            ["✅", "Threshold parsing", "Extracts numerical filters (e.g., '>200 points')"],
            ["✅", "Multi-entity queries", "Handles complex queries with multiple entities"],
            ["✅", "Player name fuzzy matching", "Matches full names and last names"],
            ["✅", "Statistical keyword detection", "Identifies mentioned stats (goals, assists, etc.)"],
        ]
        
        print(tabulate(features, headers=["", "Feature", "Description"], tablefmt="grid"))
        print()
        
        print("\n✅ Entity extraction demo completed successfully!")
        print("=" * 80 + "\n")
        
    finally:
        extractor.close()


if __name__ == "__main__":
    try:
        run_demo()
    except KeyboardInterrupt:
        print("\n\n⚠️  Demo interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
