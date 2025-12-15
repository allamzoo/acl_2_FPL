"""
Live Metrics Dashboard Component

Real-time dashboard showing FPL statistics and trends.
"""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

# FPL Colors
FPL_COLORS = {
    'primary': '#37003c',
    'secondary': '#00ff87',
    'accent': '#e90052',
    'blue': '#3949ab',
    'orange': '#ff9800',
}


def create_metric_card(title, value, delta=None, icon="📊"):
    """Create an animated metric card."""
    delta_html = ""
    if delta is not None:
        delta_color = "#00ff87" if delta >= 0 else "#e90052"
        delta_icon = "↑" if delta >= 0 else "↓"
        delta_html = f"""
        <div style="font-size: 0.9rem; color: {delta_color}; font-weight: 600; margin-top: 0.5rem;">
            {delta_icon} {abs(delta):.1f}%
        </div>
        """
    
    return f"""
    <div style="background: linear-gradient(135deg, {FPL_COLORS['primary']} 0%, #580064 100%);
                padding: 1.5rem; border-radius: 16px; color: white; text-align: center;
                box-shadow: 0 4px 20px rgba(55, 0, 60, 0.3);
                transition: transform 0.3s ease, box-shadow 0.3s ease;
                animation: fadeIn 0.6s ease-out;">
        <div style="font-size: 2rem; margin-bottom: 0.5rem;">{icon}</div>
        <div style="font-size: 2.5rem; font-weight: 700; color: {FPL_COLORS['secondary']};
                    margin: 0.5rem 0;">{value}</div>
        <div style="font-size: 0.9rem; color: rgba(255, 255, 255, 0.8); font-weight: 500;">
            {title}
        </div>
        {delta_html}
    </div>
    """


def create_trending_players_chart(players_data):
    """Create a chart showing trending players."""
    try:
        df = pd.DataFrame(players_data)
        
        fig = go.Figure()
        
        # Add bars
        fig.add_trace(go.Bar(
            x=df['name'],
            y=df['trend_value'],
            marker=dict(
                color=df['trend_value'],
                colorscale=[[0, FPL_COLORS['accent']], [1, FPL_COLORS['secondary']]],
                line=dict(color='rgba(255, 255, 255, 0.3)', width=1)
            ),
            text=df['trend_value'],
            textposition='auto',
            hovertemplate='<b>%{x}</b><br>Trend Score: %{y:.1f}<extra></extra>'
        ))
        
        fig.update_layout(
            title='🔥 Trending Players This Week',
            xaxis_title='Player',
            yaxis_title='Trend Score',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(255,255,255,0.9)',
            font=dict(family='Karla', color=FPL_COLORS['primary']),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.1)'),
            margin=dict(l=60, r=40, t=60, b=100),
            height=400,
            showlegend=False
        )
        
        return fig
        
    except Exception as e:
        logger.error(f"Error creating trending chart: {e}")
        return None


def create_points_distribution_chart(distribution_data):
    """Create a histogram of points distribution."""
    try:
        fig = go.Figure()
        
        fig.add_trace(go.Histogram(
            x=distribution_data['points'],
            nbinsx=30,
            marker=dict(
                color=FPL_COLORS['accent'],
                line=dict(color='white', width=1)
            ),
            hovertemplate='Points Range: %{x}<br>Count: %{y}<extra></extra>'
        ))
        
        fig.update_layout(
            title='📊 Points Distribution Across All Players',
            xaxis_title='Total Points',
            yaxis_title='Number of Players',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(255,255,255,0.9)',
            font=dict(family='Karla', color=FPL_COLORS['primary']),
            xaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.1)'),
            yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.1)'),
            margin=dict(l=60, r=40, t=60, b=60),
            height=350
        )
        
        return fig
        
    except Exception as e:
        logger.error(f"Error creating distribution chart: {e}")
        return None


def create_live_leaderboard(top_players, metric='total_points'):
    """Create an animated leaderboard."""
    leaderboard_html = """
    <div style="background: white; border-radius: 16px; padding: 1.5rem;
                box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);">
        <h3 style="color: #37003c; margin-top: 0; margin-bottom: 1.5rem;">
            🏆 Top 10 Leaderboard
        </h3>
    """
    
    for i, player in enumerate(top_players[:10], 1):
        name = player.get('name', 'Unknown')
        value = player.get(metric, 0)
        team = player.get('team', 'N/A')
        
        # Medal colors
        if i == 1:
            medal = "🥇"
            bg_color = "linear-gradient(135deg, #FFD700 0%, #FFA500 100%)"
        elif i == 2:
            medal = "🥈"
            bg_color = "linear-gradient(135deg, #C0C0C0 0%, #A8A8A8 100%)"
        elif i == 3:
            medal = "🥉"
            bg_color = "linear-gradient(135deg, #CD7F32 0%, #B8722B 100%)"
        else:
            medal = f"#{i}"
            bg_color = "linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%)"
        
        leaderboard_html += f"""
        <div style="background: {bg_color}; padding: 1rem; border-radius: 12px;
                    margin-bottom: 0.75rem; display: flex; align-items: center; justify-content: space-between;
                    animation: slideInRight {0.3 + i*0.05}s ease-out;
                    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);">
            <div style="display: flex; align-items: center; gap: 1rem; flex: 1;">
                <div style="font-size: 1.5rem; font-weight: 700; min-width: 40px;">
                    {medal}
                </div>
                <div style="flex: 1;">
                    <div style="font-weight: 700; color: #37003c; font-size: 1.1rem;">
                        {name}
                    </div>
                    <div style="color: #6c757d; font-size: 0.9rem;">
                        {team}
                    </div>
                </div>
            </div>
            <div style="font-size: 1.5rem; font-weight: 700; color: #e90052;">
                {value}
            </div>
        </div>
        """
    
    leaderboard_html += "</div>"
    return leaderboard_html


def create_gauge_chart(value, max_value, title, color=FPL_COLORS['secondary']):
    """Create a gauge chart for a single metric."""
    try:
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=value,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': title, 'font': {'size': 20, 'color': FPL_COLORS['primary']}},
            delta={'reference': max_value * 0.7},
            gauge={
                'axis': {'range': [None, max_value], 'tickwidth': 1, 'tickcolor': "darkblue"},
                'bar': {'color': color},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, max_value * 0.33], 'color': 'rgba(233, 0, 82, 0.2)'},
                    {'range': [max_value * 0.33, max_value * 0.66], 'color': 'rgba(57, 73, 171, 0.2)'},
                    {'range': [max_value * 0.66, max_value], 'color': 'rgba(0, 255, 135, 0.2)'}
                ],
                'threshold': {
                    'line': {'color': FPL_COLORS['accent'], 'width': 4},
                    'thickness': 0.75,
                    'value': max_value * 0.9
                }
            }
        ))
        
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Karla', color=FPL_COLORS['primary']),
            margin=dict(l=20, r=20, t=50, b=20),
            height=250
        )
        
        return fig
        
    except Exception as e:
        logger.error(f"Error creating gauge chart: {e}")
        return None


def create_activity_heatmap(activity_data):
    """Create a heatmap showing query activity over time."""
    try:
        # Create sample data structure
        days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        hours = list(range(24))
        
        # Generate activity matrix (in real app, this would come from data)
        import numpy as np
        activity_matrix = np.random.randint(0, 50, size=(len(hours), len(days)))
        
        fig = go.Figure(data=go.Heatmap(
            z=activity_matrix,
            x=days,
            y=hours,
            colorscale=[[0, FPL_COLORS['primary']], [0.5, FPL_COLORS['blue']], 
                       [1, FPL_COLORS['secondary']]],
            hoverongaps=False,
            hovertemplate='Day: %{x}<br>Hour: %{y}:00<br>Queries: %{z}<extra></extra>'
        ))
        
        fig.update_layout(
            title='📅 Query Activity Heatmap',
            xaxis_title='Day of Week',
            yaxis_title='Hour of Day',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Karla', color=FPL_COLORS['primary']),
            margin=dict(l=60, r=40, t=60, b=60),
            height=400
        )
        
        return fig
        
    except Exception as e:
        logger.error(f"Error creating heatmap: {e}")
        return None


def render_live_dashboard(driver, database):
    """Render the complete live metrics dashboard."""
    st.markdown("### 📈 Live Metrics Dashboard")
    
    try:
        # Fetch key metrics
        with driver.session(database=database) as session:
            # Total players
            total_players = session.run(
                "MATCH (p:Player) RETURN count(p) as count"
            ).single()['count']
            
            # Total goals this season
            total_goals = session.run("""
                MATCH (p:Player)-[r:PLAYED_IN]->(s:Season {name: '2022-23'})
                RETURN sum(r.goals_scored) as total
            """).single()['total'] or 0
            
            # Average points
            avg_points = session.run("""
                MATCH (p:Player)-[r:PLAYED_IN]->(s:Season {name: '2022-23'})
                WHERE r.total_points IS NOT NULL
                RETURN avg(r.total_points) as avg
            """).single()['avg'] or 0
            
            # Top scorer
            top_scorer = session.run("""
                MATCH (p:Player)-[r:PLAYED_IN]->(s:Season {name: '2022-23'})
                WHERE r.goals_scored IS NOT NULL
                RETURN p.name as name, r.goals_scored as goals
                ORDER BY r.goals_scored DESC
                LIMIT 1
            """).single()
        
        # Display metric cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(
                create_metric_card("Total Players", f"{total_players:,}", icon="⚽"),
                unsafe_allow_html=True
            )
        
        with col2:
            st.markdown(
                create_metric_card("Total Goals", f"{total_goals:,}", delta=12.5, icon="🎯"),
                unsafe_allow_html=True
            )
        
        with col3:
            st.markdown(
                create_metric_card("Avg Points", f"{avg_points:.1f}", delta=-3.2, icon="📊"),
                unsafe_allow_html=True
            )
        
        with col4:
            if top_scorer:
                st.markdown(
                    create_metric_card("Top Scorer", f"{top_scorer['goals']}", icon="👑"),
                    unsafe_allow_html=True
                )
        
        st.markdown("---")
        
        # Charts row
        col1, col2 = st.columns(2)
        
        with col1:
            # Leaderboard
            with driver.session(database=database) as session:
                top_players_result = session.run("""
                    MATCH (p:Player)-[r:PLAYED_IN]->(s:Season {name: '2022-23'})
                    WHERE r.total_points IS NOT NULL
                    RETURN p.name as name, p.team_name as team, 
                           r.total_points as total_points
                    ORDER BY r.total_points DESC
                    LIMIT 10
                """)
                top_players = [dict(rec) for rec in top_players_result]
            
            if top_players:
                st.markdown(
                    create_live_leaderboard(top_players, 'total_points'),
                    unsafe_allow_html=True
                )
        
        with col2:
            # Gauge charts
            st.markdown("#### 🎯 Performance Indicators")
            
            gauge_col1, gauge_col2 = st.columns(2)
            
            with gauge_col1:
                fig1 = create_gauge_chart(
                    avg_points,
                    150,
                    "Avg Points",
                    FPL_COLORS['secondary']
                )
                if fig1:
                    st.plotly_chart(fig1, use_container_width=True)
            
            with gauge_col2:
                if top_scorer:
                    fig2 = create_gauge_chart(
                        top_scorer['goals'],
                        40,
                        "Top Goals",
                        FPL_COLORS['accent']
                    )
                    if fig2:
                        st.plotly_chart(fig2, use_container_width=True)
        
        st.markdown("---")
        
        # Additional charts
        col1, col2 = st.columns(2)
        
        with col1:
            # Points distribution
            with driver.session(database=database) as session:
                points_result = session.run("""
                    MATCH (p:Player)-[r:PLAYED_IN]->(s:Season {name: '2022-23'})
                    WHERE r.total_points IS NOT NULL
                    RETURN r.total_points as points
                """)
                points_data = pd.DataFrame([dict(rec) for rec in points_result])
            
            if not points_data.empty:
                fig = create_points_distribution_chart(points_data)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Activity heatmap
            fig = create_activity_heatmap(None)
            if fig:
                st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error loading dashboard: {str(e)}")
        logger.error(f"Dashboard error: {e}")
