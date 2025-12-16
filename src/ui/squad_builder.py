"""
Squad Builder UI Component

Interactive FPL Squad Builder with pitch visualization matching official FPL design.
"""

import streamlit as st
import pandas as pd
from typing import Dict, List, Any, Optional
from neo4j import GraphDatabase
from config.config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, NEO4J_DATABASE
import logging

# Import player photos module
from src.ui.player_photos import find_player_photo, get_player_initials

logger = logging.getLogger(__name__)

# Team abbreviations mapping
TEAM_ABBREVIATIONS = {
    'Arsenal': 'ARS', 'Aston Villa': 'AVL', 'Bournemouth': 'BOU', 'Brentford': 'BRE',
    'Brighton': 'BHA', 'Burnley': 'BUR', 'Chelsea': 'CHE', 'Crystal Palace': 'CRY',
    'Everton': 'EVE', 'Fulham': 'FUL', 'Liverpool': 'LIV', 'Luton': 'LUT',
    'Man City': 'MCI', 'Man Utd': 'MUN', 'Newcastle': 'NEW', 'Nott\'m Forest': 'NFO',
    'Sheffield Utd': 'SHU', 'Spurs': 'TOT', 'West Ham': 'WHU', 'Wolves': 'WOL',
    'Leeds': 'LEE', 'Leicester': 'LEI', 'Southampton': 'SOU', 'Watford': 'WAT',
    'Norwich': 'NOR'
}

# Formation layouts for pitch visualization
FORMATION_LAYOUTS = {
    '4-4-2': {
        'GK': [(0.5, 0.95)],
        'DEF': [(0.2, 0.75), (0.4, 0.75), (0.6, 0.75), (0.8, 0.75)],
        'MID': [(0.2, 0.45), (0.4, 0.45), (0.6, 0.45), (0.8, 0.45)],
        'FWD': [(0.35, 0.15), (0.65, 0.15)]
    },
    '3-4-3': {
        'GK': [(0.5, 0.95)],
        'DEF': [(0.25, 0.75), (0.5, 0.75), (0.75, 0.75)],
        'MID': [(0.2, 0.45), (0.4, 0.45), (0.6, 0.45), (0.8, 0.45)],
        'FWD': [(0.25, 0.15), (0.5, 0.15), (0.75, 0.15)]
    },
    '3-5-2': {
        'GK': [(0.5, 0.95)],
        'DEF': [(0.25, 0.75), (0.5, 0.75), (0.75, 0.75)],
        'MID': [(0.15, 0.45), (0.35, 0.45), (0.5, 0.45), (0.65, 0.45), (0.85, 0.45)],
        'FWD': [(0.35, 0.15), (0.65, 0.15)]
    },
    '4-3-3': {
        'GK': [(0.5, 0.95)],
        'DEF': [(0.2, 0.75), (0.4, 0.75), (0.6, 0.75), (0.8, 0.75)],
        'MID': [(0.25, 0.45), (0.5, 0.45), (0.75, 0.45)],
        'FWD': [(0.25, 0.15), (0.5, 0.15), (0.75, 0.15)]
    },
    '4-5-1': {
        'GK': [(0.5, 0.95)],
        'DEF': [(0.2, 0.75), (0.4, 0.75), (0.6, 0.75), (0.8, 0.75)],
        'MID': [(0.15, 0.45), (0.35, 0.45), (0.5, 0.45), (0.65, 0.45), (0.85, 0.45)],
        'FWD': [(0.5, 0.15)]
    },
    '5-4-1': {
        'GK': [(0.5, 0.95)],
        'DEF': [(0.15, 0.75), (0.35, 0.75), (0.5, 0.75), (0.65, 0.75), (0.85, 0.75)],
        'MID': [(0.2, 0.45), (0.4, 0.45), (0.6, 0.45), (0.8, 0.45)],
        'FWD': [(0.5, 0.15)]
    }
}


def get_available_players(season: str = "2022-23", min_points: int = 30, min_games: int = 10) -> Dict[str, List[Dict]]:
    """Fetch all available players from Neo4j organized by position."""
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    
    query = """
    MATCH (p:Player)-[r:PLAYED_IN]->(f:Fixture)<-[:HAS_FIXTURE]-(gw:Gameweek)-[:HAS_GW]->(s:Season)
    WHERE gw.season = $season AND r.minutes > 0
    WITH p.player_name AS player_name,
         r.position AS position,
         SUM(r.total_points) AS total_points,
         SUM(r.goals_scored) AS goals,
         SUM(r.assists) AS assists,
         AVG(r.value) / 10.0 AS price,
         COUNT(DISTINCT f) AS games_played,
         SUM(r.clean_sheets) AS clean_sheets,
         SUM(r.minutes) AS total_minutes
    WHERE total_points >= $min_points
      AND games_played >= $min_games
      AND price IS NOT NULL
    WITH position, player_name, total_points, goals, assists, price, 
         clean_sheets, games_played,
         toFloat(total_points) / (price * 10.0) AS value_ratio
    ORDER BY position, value_ratio DESC
    RETURN position, player_name, total_points, goals, assists, 
           price, clean_sheets, games_played, value_ratio
    """
    
    players_by_position = {'GK': [], 'DEF': [], 'MID': [], 'FWD': []}
    
    try:
        with driver.session(database=NEO4J_DATABASE) as session:
            results = session.run(query, {
                "season": season,
                "min_points": min_points,
                "min_games": min_games
            })
            
            for record in results:
                pos = record['position']
                if pos in players_by_position:
                    players_by_position[pos].append({
                        'name': record['player_name'],
                        'position': pos,
                        'price': round(record['price'], 1),
                        'points': record['total_points'],
                        'goals': record['goals'],
                        'assists': record['assists'],
                        'clean_sheets': record['clean_sheets'],
                        'games': record['games_played'],
                        'value_ratio': round(record['value_ratio'], 2),
                        'team': 'TBD',  # We'll get this from another query if needed
                        'fixture_difficulty': 'H'  # Default to Home
                    })
    
    finally:
        driver.close()
    
    return players_by_position


def get_player_team(player_name: str, season: str = "2022-23") -> str:
    """Get the most common team a player played for in a season."""
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD))
    
    query = """
    MATCH (p:Player)-[r:PLAYED_IN]->(f:Fixture)<-[:HAS_FIXTURE]-(gw:Gameweek)
    WHERE p.player_name = $player_name AND gw.season = $season
    MATCH (f)-[:HAS_HOME_TEAM|HAS_AWAY_TEAM]->(t:Team)
    RETURN t.name AS team_name, COUNT(*) AS appearances
    ORDER BY appearances DESC
    LIMIT 1
    """
    
    try:
        with driver.session(database=NEO4J_DATABASE) as session:
            result = session.run(query, {"player_name": player_name, "season": season})
            record = result.single()
            if record:
                return record['team_name']
            return 'Unknown'
    finally:
        driver.close()


def initialize_session_state():
    """Initialize session state for squad builder."""
    if 'squad' not in st.session_state:
        st.session_state.squad = {
            'GK': [],
            'DEF': [],
            'MID': [],
            'FWD': []
        }
    
    if 'bench' not in st.session_state:
        st.session_state.bench = []
    
    if 'budget' not in st.session_state:
        st.session_state.budget = 100.0
    
    if 'formation' not in st.session_state:
        st.session_state.formation = '4-4-2'
    
    if 'transfers_made' not in st.session_state:
        st.session_state.transfers_made = 0
    
    if 'wildcards_used' not in st.session_state:
        st.session_state.wildcards_used = 0
    
    # Check if squad is empty and auto-generate using baseline retriever
    total_players = sum(len(st.session_state.squad[pos]) for pos in st.session_state.squad)
    if total_players == 0:
        from src.retrieval.baseline_retriever import BaselineRetriever
        
        retriever = BaselineRetriever()
        squad_data = retriever.build_squad_under_budget(
            season="2022-23",
            budget=st.session_state.budget,
            min_points=30,
            min_games=10
        )
        
        # Populate squad with players
        for player in squad_data['squad']:
            pos = player['position']
            st.session_state.squad[pos].append({
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
            })
        
        retriever.close()


def calculate_squad_stats() -> Dict[str, Any]:
    """Calculate current squad statistics."""
    total_cost = 0.0
    total_points = 0
    player_count = 0
    
    for position in st.session_state.squad:
        for player in st.session_state.squad[position]:
            total_cost += player['price']
            total_points += player['points']
            player_count += 1
    
    return {
        'total_cost': round(total_cost, 1),
        'remaining_budget': round(st.session_state.budget - total_cost, 1),
        'total_points': total_points,
        'player_count': player_count,
        'squad_complete': player_count == 15
    }


def render_pitch_header(stats: Dict[str, Any]):
    """Render the header with gameweek info and stats."""
    status_class = 'complete' if stats['squad_complete'] else 'incomplete'
    player_count = stats['player_count']
    remaining_budget = stats['remaining_budget']
    
    st.markdown(f"""
        <style>
        .pitch-header {{
            background: linear-gradient(135deg, #37003c 0%, #2d0035 100%);
            padding: 1rem;
            border-radius: 10px 10px 0 0;
            margin-bottom: 0;
        }}
        .pitch-header-row {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            color: white;
        }}
        .header-item {{
            text-align: center;
            flex: 1;
        }}
        .header-label {{
            font-size: 0.75rem;
            opacity: 0.8;
            margin-bottom: 0.25rem;
        }}
        .header-value {{
            font-size: 1.2rem;
            font-weight: 700;
        }}
        .header-value.complete {{
            color: #00ff87;
        }}
        .header-value.incomplete {{
            color: #ff9800;
        }}
        .chip-container {{
            display: flex;
            gap: 1rem;
            margin-top: 1rem;
        }}
        .chip-btn {{
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.3);
            padding: 0.5rem 1rem;
            border-radius: 5px;
            color: white;
            font-size: 0.85rem;
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        .chip-btn:hover {{
            background: rgba(255, 255, 255, 0.2);
        }}
        .chip-btn.active {{
            background: #00ff87;
            color: #37003c;
            border-color: #00ff87;
        }}
        </style>
        
        <div class="pitch-header">
            <div class="pitch-header-row">
                <div class="header-item">
                    <div class="header-label">Gameweek 17</div>
                    <div class="header-value">Deadline: Sat 20 Dec, 13:00</div>
                </div>
            </div>
            <div class="pitch-header-row" style="margin-top: 1rem;">
                <div class="header-item">
                    <div class="header-label">Players Selected</div>
                    <div class="header-value {status_class}">{player_count}/15</div>
                </div>
                <div class="header-item">
                    <div class="header-label">Budget</div>
                    <div class="header-value">£{remaining_budget:.1f}m</div>
                </div>
                <div class="header-item">
                    <div class="header-label">Free Transfers</div>
                    <div class="header-value">1</div>
                </div>
                <div class="header-item">
                    <div class="header-label">Cost</div>
                    <div class="header-value">0 pts</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)


def render_player_card(player: Optional[Dict[str, Any]], position_index: int, position: str, editable: bool = True):
    """Render a single player card on the pitch."""
    if player:
        team_abbr = TEAM_ABBREVIATIONS.get(player.get('team', 'Unknown'), 'UNK')
        player_name = player.get('name', 'Player')
        player_price = player.get('price', 0.0)
        
        # Get player photo URL using the same approach as season leaders
        photo_url = find_player_photo(player_name)
        initials = get_player_initials(player_name)
        
        # Render complete player card with photo and fallback to initials
        st.markdown(f"""
            <div style="background: rgba(55, 0, 60, 0.7); backdrop-filter: blur(5px); border-radius: 10px; padding: 0.8rem; box-shadow: 0 4px 12px rgba(0,0,0,0.3); position: relative; text-align: center; min-width: 95px; margin: 0 auto; border: 2px solid rgba(0, 255, 135, 0.5);">
                <div style="position: absolute; top: 5px; right: 5px; background: #00ff87; color: #37003c; padding: 3px 8px; border-radius: 5px; font-size: 0.75rem; font-weight: 800; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
                    £{player_price}m
                </div>
                <div style="margin: 1.5rem auto 0.6rem; width: 70px; height: 70px; border-radius: 50%; overflow: hidden; border: 3px solid #00ff87; box-shadow: 0 4px 8px rgba(0,255,135,0.3); background: linear-gradient(135deg, #37003c 0%, #e90052 100%); display: flex; align-items: center; justify-content: center;">
                    <img src="{photo_url}" 
                         style="width: 100%; height: 100%; object-fit: cover;" 
                         onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';"
                         alt="{player_name}"/>
                    <span style="display: none; color: white; font-size: 1.4rem; font-weight: 700; text-shadow: 0 2px 3px rgba(0,0,0,0.4); position: absolute;">{initials}</span>
                </div>
                <div style="font-size: 0.85rem; font-weight: 800; color: #ffffff; margin-top: 0.5rem; padding: 0 0.3rem; text-shadow: 0 1px 2px rgba(0,0,0,0.5); line-height: 1.2;">
                    {player_name[:25]}
                </div>
                <div style="font-size: 0.7rem; color: #00ff87; margin-top: 0.3rem; font-weight: 700; letter-spacing: 0.5px;">
                    {team_abbr}
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div style="background: rgba(255, 255, 255, 0.1); border: 2px dashed rgba(255, 255, 255, 0.3); color: rgba(255, 255, 255, 0.5); min-height: 120px; display: flex; align-items: center; justify-content: center; border-radius: 8px; font-size: 2rem;">
                +
            </div>
        """, unsafe_allow_html=True)


def render_football_pitch(formation: str):
    """Render the football pitch with players in formation."""
    stats = calculate_squad_stats()
    
    # More specific CSS - only apply to pitch area in container
    st.markdown("""
        <style>
        /* Very specific selector - only in squad builder context */
        [data-testid="stVerticalBlock"] > div > [data-testid="stVerticalBlock"]:has(.pitch-marker-unique-xyz) {
            background: repeating-linear-gradient(
                90deg,
                #00a650 0px,
                #00a650 80px,
                #008f43 80px,
                #008f43 160px
            ) !important;
            border: 4px solid rgba(255, 255, 255, 0.4);
            border-radius: 10px;
            padding: 2.5rem 2rem !important;
            position: relative;
            min-height: 750px;
            box-shadow: inset 0 0 50px rgba(0, 0, 0, 0.1);
            margin-bottom: 2rem;
        }
        
        /* Pitch lines */
        [data-testid="stVerticalBlock"] > div > [data-testid="stVerticalBlock"]:has(.pitch-marker-unique-xyz)::before {
            content: '';
            position: absolute;
            top: 50%;
            left: 0;
            right: 0;
            height: 3px;
            background: rgba(255, 255, 255, 0.4);
            transform: translateY(-50%);
            z-index: 1;
        }
        
        /* Center circle */
        [data-testid="stVerticalBlock"] > div > [data-testid="stVerticalBlock"]:has(.pitch-marker-unique-xyz)::after {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 120px;
            height: 120px;
            border: 3px solid rgba(255, 255, 255, 0.4);
            border-radius: 50%;
            z-index: 1;
        }
        
        /* Make columns appear above pitch lines */
        [data-testid="stVerticalBlock"] > div > [data-testid="stVerticalBlock"]:has(.pitch-marker-unique-xyz) div[data-testid="column"] {
            z-index: 100 !important;
            position: relative !important;
        }
        </style>
        <div class="pitch-marker-unique-xyz" style="position:absolute;width:1px;height:1px;opacity:0;"></div>
    """, unsafe_allow_html=True)
    
    layout = FORMATION_LAYOUTS.get(formation, FORMATION_LAYOUTS['4-4-2'])
    
    # Render each position row with actual players
    for position in ['FWD', 'MID', 'DEF', 'GK']:
        squad_players = st.session_state.squad[position]
        
        if squad_players:
            num_players = len(squad_players)
            cols = st.columns(num_players)
            
            for i, player in enumerate(squad_players):
                with cols[i]:
                    render_player_card(player, i, position, editable=False)


def render_action_buttons():
    """Render action buttons below the pitch."""
    st.markdown("""
        <style>
        .action-buttons {{
            display: flex;
            justify-content: center;
            margin-top: 1.5rem;
            margin-bottom: 1.5rem;
        }}
        </style>
    """, unsafe_allow_html=True)
    
    # Center column for regenerate button
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("🔄 REGENERATE SQUAD", use_container_width=True, type="primary", key="regenerate_btn"):
            # Clear session state and regenerate
            st.session_state.squad = {'GK': [], 'DEF': [], 'MID': [], 'FWD': []}
            auto_pick_squad()


def auto_pick_squad():
    """Automatically pick the best squad within budget using baseline retriever."""
    from src.retrieval.baseline_retriever import BaselineRetriever
    
    with st.spinner("🤖 Building optimal squad..."):
        retriever = BaselineRetriever()
        
        squad_data = retriever.build_squad_under_budget(
            season="2022-23",
            budget=st.session_state.budget,
            min_points=30,
            min_games=10,
            randomize=True  # Enable randomization for different squads
        )
        
        # Clear current squad
        st.session_state.squad = {'GK': [], 'DEF': [], 'MID': [], 'FWD': []}
        
        # Populate with optimal players from retriever
        for player in squad_data['squad']:
            pos = player['position']
            st.session_state.squad[pos].append({
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
            })
        
        retriever.close()
    
    st.rerun()


def reset_squad():
    """Reset the squad to empty."""
    st.session_state.squad = {'GK': [], 'DEF': [], 'MID': [], 'FWD': []}
    st.session_state.bench = []
    st.session_state.transfers_made = 0
    st.rerun()


def render_player_selection_panel():
    """Render the player selection/transfer panel."""
    st.markdown("### 🔍 Find Players")
    
    col1, col2 = st.columns(2)
    
    with col1:
        position_filter = st.selectbox(
            "Position",
            options=['All', 'GK', 'DEF', 'MID', 'FWD'],
            index=0
        )
    
    with col2:
        max_price = st.slider(
            "Max Price (£m)",
            min_value=4.0,
            max_value=15.0,
            value=10.0,
            step=0.5
        )
    
    search_query = st.text_input("Search player name...", placeholder="e.g., Salah")
    
    # Get available players
    if st.button("🔎 Search Players", type="primary"):
        with st.spinner("Loading players..."):
            all_players = get_available_players(season="2022-23")
            
            # Filter players
            filtered_players = []
            for pos, players in all_players.items():
                if position_filter == 'All' or position_filter == pos:
                    for player in players:
                        if player['price'] <= max_price:
                            if not search_query or search_query.lower() in player['name'].lower():
                                filtered_players.append(player)
            
            # Display results
            if filtered_players:
                st.markdown(f"**Found {len(filtered_players)} players**")
                
                # Show players in a table
                df = pd.DataFrame(filtered_players)
                df = df[['name', 'position', 'price', 'points', 'goals', 'assists', 'value_ratio']]
                df = df.sort_values('value_ratio', ascending=False)
                
                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "name": "Player",
                        "position": st.column_config.TextColumn("Pos", width="small"),
                        "price": st.column_config.NumberColumn("Price", format="£%.1fm"),
                        "points": st.column_config.NumberColumn("Points"),
                        "goals": st.column_config.NumberColumn("Goals", width="small"),
                        "assists": st.column_config.NumberColumn("Assists", width="small"),
                        "value_ratio": st.column_config.NumberColumn("Value", format="%.2f")
                    }
                )
                
                # Add player selection
                selected_player_name = st.selectbox(
                    "Select player to add",
                    options=[p['name'] for p in filtered_players]
                )
                
                if st.button("➕ Add to Squad", type="primary"):
                    selected = next(p for p in filtered_players if p['name'] == selected_player_name)
                    pos = selected['position']
                    
                    # Check squad limits
                    max_players = {'GK': 2, 'DEF': 5, 'MID': 5, 'FWD': 3}
                    if len(st.session_state.squad[pos]) >= max_players[pos]:
                        st.error(f"❌ Already have maximum {max_players[pos]} {pos} players!")
                    else:
                        stats = calculate_squad_stats()
                        if stats['total_cost'] + selected['price'] > st.session_state.budget:
                            st.error(f"❌ Not enough budget! Need £{selected['price']}m, have £{stats['remaining_budget']}m")
                        else:
                            st.session_state.squad[pos].append(selected)
                            st.success(f"✅ Added {selected['name']} to squad!")
                            st.rerun()
            else:
                st.info("No players found matching your criteria.")


def render_squad_builder():
    """Main squad builder interface."""
    initialize_session_state()
    
    st.markdown("""
        <style>
        .squad-builder-container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        </style>
    """, unsafe_allow_html=True)
    
    # Show info if squad is being auto-generated
    stats = calculate_squad_stats()
    if stats['player_count'] == 0:
        st.info("🤖 Generating your squad... Click 'Regenerate Squad' if you don't see players.")
    
    # Render header
    render_pitch_header(stats)
    
    # Formation selector
    formation_col1, formation_col2 = st.columns([1, 4])
    with formation_col1:
        st.session_state.formation = st.selectbox(
            "Formation",
            options=list(FORMATION_LAYOUTS.keys()),
            index=0
        )
    
    # Render pitch
    render_football_pitch(st.session_state.formation)
    
    # Action buttons - only regenerate
    render_action_buttons()
    
    # Squad stats summary
    st.markdown("---")
    st.markdown("### 📊 Squad Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Cost", f"£{stats['total_cost']}m")
    with col2:
        st.metric("Remaining", f"£{stats['remaining_budget']}m")
    with col3:
        st.metric("Total Points", stats['total_points'])
    with col4:
        st.metric("Players", f"{stats['player_count']}/15")
