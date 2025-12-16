"""
Player Comparison Component

Advanced player comparison with side-by-side stats and visualizations.
"""

import streamlit as st
import pandas as pd
from typing import List, Dict, Any, Optional
import logging
from .stats_viz import (
    create_player_stats_radar,
    create_multi_metric_comparison,
    create_value_analysis_scatter
)
from src.retrieval.baseline_retriever import BaselineRetriever

logger = logging.getLogger(__name__)

# FPL Colors
FPL_COLORS = {
    'primary': '#37003c',
    'secondary': '#00ff87',
    'accent': '#e90052',
    'blue': '#3949ab',
    'orange': '#ff9800',
}


def fetch_player_data(player_name: str, season: str = "2022-23") -> Optional[Dict[str, Any]]:
    """
    Fetch player data from Neo4j database.
    
    Args:
        player_name: Player name to search for
        season: Season to get stats from (default: 2022-23)
        
    Returns:
        Player data dictionary or None if not found
    """
    try:
        retriever = BaselineRetriever()
        
        # Capitalize first letter of each word for better matching
        player_name = player_name.title()
        
        # Get player season stats
        results = retriever.get_player_season_stats(player_name, season)
        
        if results and len(results) > 0:
            player_data = results[0]
            
            # Ensure this is a dictionary
            if not isinstance(player_data, dict):
                logger.error(f"Invalid player data type: {type(player_data)}")
                retriever.close()
                return None
            
            # Log the retrieved data for debugging
            logger.info(f"Retrieved player data keys: {player_data.keys()}")
            
            # Ensure 'name' field exists - map from Neo4j field names
            if 'name' not in player_data:
                player_data['name'] = player_data.get('player', player_data.get('player_name', player_name))
            
            # Ensure position and team exist
            if 'position' not in player_data or not player_data['position']:
                player_data['position'] = 'N/A'
            
            if 'team' not in player_data or not player_data['team']:
                player_data['team'] = 'N/A'
            
            # Add field aliases for compatibility with visualization components
            if 'total_minutes' in player_data and 'minutes' not in player_data:
                player_data['minutes'] = player_data['total_minutes']
            
            # Ensure cost field exists (may not be in season stats)
            if 'cost' not in player_data:
                player_data['cost'] = 7.5  # Default placeholder cost
            
            # Ensure required fields exist with defaults
            defaults = {
                'team': 'Unknown',
                'position': 'Unknown',
                'goals': 0,
                'assists': 0,
                'total_points': 0,
                'bonus': 0,
                'bps': 0,
                'clean_sheets': 0,
                'ict_index': 0
            }
            
            for key, default_value in defaults.items():
                if key not in player_data:
                    player_data[key] = default_value
                
            retriever.close()
            return player_data
        
        retriever.close()
        return None
        
    except Exception as e:
        logger.error(f"Error fetching player data for {player_name}: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None


def render_player_comparison_ui():
    """Render the player comparison interface."""
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(255,255,255,0.1) 0%, rgba(255,255,255,0.05) 100%); 
                padding: 2rem; border-radius: 16px; margin: 2rem 0; border: 2px solid rgba(255,255,255,0.2);">
        <h2 style="color: #00ff87; margin-top: 0;">🔄 Player Comparison Tool</h2>
        <p style="color: white; font-size: 1.1rem;">
            Compare multiple players side-by-side with interactive charts and detailed statistics.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state for player comparison
    if 'comparison_players' not in st.session_state:
        st.session_state.comparison_players = []
    if 'comparison_season' not in st.session_state:
        st.session_state.comparison_season = "2022-23"
    
    # Clean up old string-based data (compatibility fix)
    if st.session_state.comparison_players:
        # Filter out any non-dictionary entries
        valid_players = [p for p in st.session_state.comparison_players if isinstance(p, dict)]
        if len(valid_players) != len(st.session_state.comparison_players):
            st.session_state.comparison_players = valid_players
            if valid_players:
                st.info("🔄 Cleaned up invalid player data. Valid players retained.")
            else:
                st.info("🔄 Player comparison data has been reset. Please add players again.")
    
    # Season selector
    season = st.selectbox(
        "📅 Select Season",
        ["2022-23", "2021-22"],
        key="player_comparison_season_selector"
    )
    
    st.session_state.comparison_season = season
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        player_name = st.text_input(
            "🔍 Search for a player to add",
            placeholder="Enter player name...",
            label_visibility="collapsed",
            key="player_search_input"
        )
    
    with col2:
        add_button = st.button("➕ Add Player", use_container_width=True)
    
    if add_button and player_name:
        # Fetch player data from database
        with st.spinner(f"Searching for {player_name}..."):
            player_data = fetch_player_data(player_name, st.session_state.comparison_season)
            
            if player_data:
                # Check if player already added
                player_names = [p.get('name', p.get('player', '')) for p in st.session_state.comparison_players]
                current_player_name = player_data.get('name', player_data.get('player', ''))
                
                if current_player_name in player_names:
                    st.warning(f"⚠️ {current_player_name} is already in the comparison!")
                else:
                    st.session_state.comparison_players.append(player_data)
                    st.success(f"✅ Added {current_player_name} to comparison!")
                    st.rerun()
            else:
                st.error(f"❌ Player '{player_name}' not found in {st.session_state.comparison_season} season. Try a different name or check spelling.")
    
    # Display current players in comparison
    if st.session_state.comparison_players:
        st.markdown("### 📊 Players in Comparison")
        
        # Safety: ensure all players are dictionaries
        st.session_state.comparison_players = [
            p for p in st.session_state.comparison_players 
            if isinstance(p, dict)
        ]
        
        if not st.session_state.comparison_players:
            st.info("👆 Enter a player name above to start building your comparison.")
            return
        
        cols = st.columns(min(len(st.session_state.comparison_players), 5))
        for i, (col, player) in enumerate(zip(cols, st.session_state.comparison_players)):
            with col:
                # Safety check: ensure player is a dict (double-check)
                if not isinstance(player, dict):
                    logger.error(f"Invalid player data at position {i}: {type(player)}")
                    continue
                    
                player_name = player.get('name', player.get('player', player.get('player_name', 'Unknown')))
                player_position = player.get('position', 'N/A')
                player_team = player.get('team', 'N/A')
                total_points = player.get('total_points', 0)
                
                st.markdown(f"""
                <div class="player-card" style="text-align: center; padding: 1rem; background: rgba(0,255,135,0.1); border-radius: 8px; border: 2px solid rgba(0,255,135,0.3);">
                    <h4 style="margin: 0; color: #00ff87;">{player_name}</h4>
                    <p style="margin: 0.25rem 0; color: #999; font-size: 0.85rem;">{player_position} • {player_team}</p>
                    <p style="margin: 0; color: #e90052; font-weight: bold; font-size: 1.2rem;">{total_points} pts</p>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"❌ Remove", key=f"remove_{i}"):
                    st.session_state.comparison_players.pop(i)
                    st.rerun()
        
        col_a, col_b = st.columns([1, 1])
        with col_a:
            if st.button("🗑️ Clear All", key="clear_all", use_container_width=True):
                st.session_state.comparison_players = []
                st.rerun()
        
        # Actually compare the players if we have at least 2
        if len(st.session_state.comparison_players) >= 2:
            compare_players(st.session_state.comparison_players)
        else:
            st.info("ℹ️ Add at least one more player to start comparing!")
    else:
        st.info("👆 Enter a player name above to start building your comparison.")


def compare_players(players_data: List[Dict[str, Any]], comparison_type: str = "stats"):
    """
    Compare multiple players with various visualization types.
    
    Args:
        players_data: List of player dictionaries with statistics
        comparison_type: Type of comparison ('stats', 'performance', 'value')
    """
    if not players_data or len(players_data) < 2:
        st.warning("⚠️ Add at least 2 players to compare!")
        return
    
    st.markdown("---")
    
    # Comparison type selector
    comparison_tabs = st.tabs(["📊 Statistics", "📈 Performance", "💰 Value Analysis", "🎯 Head-to-Head"])
    
    with comparison_tabs[0]:
        render_stats_comparison(players_data)
    
    with comparison_tabs[1]:
        render_performance_comparison(players_data)
    
    with comparison_tabs[2]:
        render_value_comparison(players_data)
    
    with comparison_tabs[3]:
        render_head_to_head(players_data)


def render_stats_comparison(players_data: List[Dict[str, Any]]):
    """Render statistical comparison of players."""
    st.markdown("### 📊 Statistical Comparison")
    
    # Select metrics to compare
    available_metrics = ['goals', 'assists', 'clean_sheets', 'bonus', 'minutes', 
                        'total_points', 'bps', 'ict_index']
    
    selected_metrics = st.multiselect(
        "Select metrics to compare",
        available_metrics,
        default=['goals', 'assists', 'total_points']
    )
    
    if selected_metrics:
        # Multi-metric comparison chart
        fig = create_multi_metric_comparison(players_data, selected_metrics)
        if fig:
            st.plotly_chart(fig, use_container_width=True)
        
        # Detailed stats table
        st.markdown("#### Detailed Statistics")
        df = pd.DataFrame(players_data)
        
        # Format columns for display
        display_cols = ['name', 'team', 'position'] + selected_metrics
        available_cols = [col for col in display_cols if col in df.columns]
        
        if available_cols:
            # Try to use styling, fallback to plain dataframe if matplotlib not available
            try:
                import matplotlib
                styled_df = df[available_cols].style.background_gradient(
                    subset=selected_metrics,
                    cmap='RdYlGn'
                )
                st.dataframe(styled_df, use_container_width=True)
            except ImportError:
                # Fallback: highlight max values instead
                st.dataframe(
                    df[available_cols].style.highlight_max(
                        subset=selected_metrics,
                        color='lightgreen'
                    ),
                    use_container_width=True
                )


def render_performance_comparison(players_data: List[Dict[str, Any]]):
    """Render performance comparison with radar charts."""
    st.markdown("### 📈 Performance Comparison")
    
    # Radar charts for each player
    cols = st.columns(min(len(players_data), 3))
    
    for i, (col, player) in enumerate(zip(cols, players_data)):
        with col:
            st.markdown(f"#### {player.get('name', 'Player')}")
            fig = create_player_stats_radar(player)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
    
    # Performance metrics cards
    st.markdown("#### 🏆 Key Performance Indicators")
    
    metrics_cols = st.columns(len(players_data))
    
    for col, player in zip(metrics_cols, players_data):
        with col:
            st.markdown(f"""
            <div class="fpl-card" style="text-align: center;">
                <h4>{player.get('name', 'Player')}</h4>
                <div style="margin: 1rem 0;">
                    <div style="font-size: 2rem; color: {FPL_COLORS['accent']}; font-weight: bold;">
                        {player.get('total_points', 0)}
                    </div>
                    <div style="color: #6c757d;">Total Points</div>
                </div>
                <div style="margin: 0.5rem 0;">
                    <span style="color: {FPL_COLORS['primary']}; font-weight: bold;">⚽ {player.get('goals', 0)}</span>
                    <span style="margin: 0 1rem; color: {FPL_COLORS['blue']}; font-weight: bold;">🎯 {player.get('assists', 0)}</span>
                </div>
                <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid #e0e0e0;">
                    <small style="color: #6c757d;">£{player.get('cost', 0)}m • {player.get('position', 'N/A')}</small>
                </div>
            </div>
            """, unsafe_allow_html=True)


def render_value_comparison(players_data: List[Dict[str, Any]]):
    """Render value-for-money comparison."""
    st.markdown("### 💰 Value Analysis")
    
    # Calculate value metrics
    for player in players_data:
        if 'cost' in player and player['cost'] > 0:
            player['points_per_million'] = player.get('total_points', 0) / player['cost']
            player['goals_per_million'] = player.get('goals', 0) / player['cost']
    
    # Value scatter plot
    fig = create_value_analysis_scatter(players_data)
    if fig:
        st.plotly_chart(fig, use_container_width=True)
    
    # Value metrics table
    st.markdown("#### 📊 Value Metrics")
    
    df = pd.DataFrame(players_data)
    value_cols = ['name', 'cost', 'total_points', 'points_per_million']
    
    available_cols = [col for col in value_cols if col in df.columns]
    
    if available_cols:
        # Only sort if points_per_million exists
        if 'points_per_million' in df.columns:
            sorted_df = df[available_cols].sort_values(
                'points_per_million', 
                ascending=False
            )
        else:
            sorted_df = df[available_cols]
        
        # Try to use styling, fallback to simple format if matplotlib not available
        try:
            import matplotlib
            styled_df = sorted_df.style.background_gradient(
                subset=['points_per_million'],
                cmap='RdYlGn'
            ).format({
                'cost': '£{:.1f}m',
                'points_per_million': '{:.2f}'
            })
            st.dataframe(styled_df, use_container_width=True)
        except ImportError:
            # Fallback: just format without gradient
            styled_df = sorted_df.style.format({
                'cost': '£{:.1f}m',
                'points_per_million': '{:.2f}'
            })
            st.dataframe(styled_df, use_container_width=True)


def render_head_to_head(players_data: List[Dict[str, Any]]):
    """Render head-to-head comparison matrix."""
    st.markdown("### 🎯 Head-to-Head Comparison")
    
    if len(players_data) != 2:
        st.info("ℹ️ Head-to-head comparison works best with exactly 2 players. Showing general comparison.")
    
    # Create comparison matrix
    metrics = ['goals', 'assists', 'clean_sheets', 'bonus', 'total_points', 
              'minutes', 'bps', 'ict_index']
    
    comparison_data = []
    
    for metric in metrics:
        row = {'Metric': metric.replace('_', ' ').title()}
        
        for player in players_data[:2]:  # Only compare first 2 players
            player_name = player.get('name', 'Player')
            value = player.get(metric, 0)
            row[player_name] = value
        
        # Add winner column
        if len(players_data) >= 2:
            values = [players_data[0].get(metric, 0), players_data[1].get(metric, 0)]
            if values[0] > values[1]:
                row['Winner'] = players_data[0].get('name', 'Player 1')
            elif values[1] > values[0]:
                row['Winner'] = players_data[1].get('name', 'Player 2')
            else:
                row['Winner'] = 'Draw'
        
        comparison_data.append(row)
    
    df_comparison = pd.DataFrame(comparison_data)
    
    # Style the dataframe
    def highlight_winner(row):
        if len(players_data) >= 2:
            p1_name = players_data[0].get('name', 'Player')
            p2_name = players_data[1].get('name', 'Player')
            
            if p1_name in row.values and p2_name in row.values:
                styles = [''] * len(row)
                p1_idx = list(row.index).index(p1_name)
                p2_idx = list(row.index).index(p2_name)
                
                if row[p1_name] > row[p2_name]:
                    styles[p1_idx] = 'background-color: #d4edda; font-weight: bold'
                elif row[p2_name] > row[p1_name]:
                    styles[p2_idx] = 'background-color: #d4edda; font-weight: bold'
                
                return styles
        return [''] * len(row)
    
    # Apply styling if possible, fallback to plain dataframe
    try:
        st.dataframe(
            df_comparison.style.apply(highlight_winner, axis=1),
            use_container_width=True
        )
    except Exception:
        # Fallback: show plain dataframe
        st.dataframe(df_comparison, use_container_width=True)
    
    # Summary
    if len(players_data) >= 2:
        p1_wins = sum(1 for row in comparison_data if row.get('Winner') == players_data[0].get('name'))
        p2_wins = sum(1 for row in comparison_data if row.get('Winner') == players_data[1].get('name'))
        draws = sum(1 for row in comparison_data if row.get('Winner') == 'Draw')
        
        cols = st.columns(3)
        with cols[0]:
            st.metric(players_data[0].get('name', 'Player 1'), f"{p1_wins} wins")
        with cols[1]:
            st.metric("Draws", draws)
        with cols[2]:
            st.metric(players_data[1].get('name', 'Player 2'), f"{p2_wins} wins")
