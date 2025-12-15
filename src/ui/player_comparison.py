"""
Player Comparison Component

Advanced player comparison with side-by-side stats and visualizations.
"""

import streamlit as st
import pandas as pd
from typing import List, Dict, Any
import logging
from .stats_viz import (
    create_player_stats_radar,
    create_multi_metric_comparison,
    create_value_analysis_scatter
)

logger = logging.getLogger(__name__)

# FPL Colors
FPL_COLORS = {
    'primary': '#37003c',
    'secondary': '#00ff87',
    'accent': '#e90052',
    'blue': '#3949ab',
    'orange': '#ff9800',
}


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
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        player_name = st.text_input(
            "🔍 Search for a player to add",
            placeholder="Enter player name...",
            label_visibility="collapsed"
        )
    
    with col2:
        add_button = st.button("➕ Add Player", use_container_width=True)
    
    if add_button and player_name:
        # Here you would query the database for the player
        st.session_state.comparison_players.append(player_name)
        st.success(f"✅ Added {player_name} to comparison!")
    
    # Display current players in comparison
    if st.session_state.comparison_players:
        st.markdown("### 📊 Players in Comparison")
        
        cols = st.columns(len(st.session_state.comparison_players))
        for i, (col, player) in enumerate(zip(cols, st.session_state.comparison_players)):
            with col:
                st.markdown(f"""
                <div class="player-card" style="text-align: center; padding: 1rem;">
                    <h4 style="margin: 0;">{player}</h4>
                </div>
                """, unsafe_allow_html=True)
                if st.button(f"❌ Remove", key=f"remove_{i}"):
                    st.session_state.comparison_players.pop(i)
                    st.rerun()
        
        if st.button("🗑️ Clear All", key="clear_all"):
            st.session_state.comparison_players = []
            st.rerun()


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
        sorted_df = df[available_cols].sort_values(
            'points_per_million', 
            ascending=False
        )
        
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
