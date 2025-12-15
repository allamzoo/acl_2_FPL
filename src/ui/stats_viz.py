"""
Statistics Visualization Component

Creates interactive charts for player statistics and comparisons using Plotly.
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import streamlit as st
import logging

logger = logging.getLogger(__name__)

# FPL Color scheme
FPL_COLORS = {
    'primary': '#37003c',
    'secondary': '#00ff87',
    'accent': '#e90052',
    'blue': '#3949ab',
    'orange': '#ff9800',
    'purple': '#9c27b0',
    'teal': '#009688'
}


def create_player_stats_radar(player_data, metrics=['goals', 'assists', 'minutes', 'bonus', 'bps']):
    """
    Create a radar chart for a player's statistics.
    
    Args:
        player_data: Dictionary containing player statistics
        metrics: List of metrics to include in the radar chart
    
    Returns:
        Plotly figure object
    """
    try:
        # Extract values for each metric
        values = []
        labels = []
        
        for metric in metrics:
            if metric in player_data:
                values.append(player_data[metric])
                labels.append(metric.replace('_', ' ').title())
        
        # Close the radar chart
        values.append(values[0])
        labels.append(labels[0])
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=labels,
            fill='toself',
            fillcolor=f'rgba(233, 0, 82, 0.3)',
            line=dict(color=FPL_COLORS['accent'], width=2),
            name=player_data.get('name', 'Player')
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, max(values) * 1.2] if values else [0, 100]
                ),
                bgcolor='rgba(255, 255, 255, 0.9)'
            ),
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Karla', color=FPL_COLORS['primary']),
            margin=dict(l=80, r=80, t=40, b=40),
            height=400
        )
        
        return fig
        
    except Exception as e:
        logger.error(f"Error creating radar chart: {e}")
        return None


def create_player_comparison_chart(players_data, metric='goals', chart_type='bar'):
    """
    Create a comparison chart for multiple players.
    
    Args:
        players_data: List of dictionaries containing player statistics
        metric: The metric to compare
        chart_type: 'bar', 'line', or 'scatter'
    
    Returns:
        Plotly figure object
    """
    try:
        df = pd.DataFrame(players_data)
        
        if chart_type == 'bar':
            fig = px.bar(
                df,
                x='name',
                y=metric,
                color='team',
                title=f'Player Comparison: {metric.replace("_", " ").title()}',
                color_discrete_sequence=[FPL_COLORS['accent'], FPL_COLORS['secondary'], 
                                        FPL_COLORS['blue'], FPL_COLORS['orange']]
            )
        elif chart_type == 'scatter':
            fig = px.scatter(
                df,
                x='minutes',
                y=metric,
                size='total_points' if 'total_points' in df.columns else None,
                color='position',
                hover_data=['name', 'team'],
                title=f'{metric.replace("_", " ").title()} vs Minutes Played',
                color_discrete_sequence=[FPL_COLORS['accent'], FPL_COLORS['secondary'], 
                                        FPL_COLORS['blue'], FPL_COLORS['orange']]
            )
        
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(255,255,255,0.9)',
            font=dict(family='Karla', color=FPL_COLORS['primary']),
            xaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.1)'),
            yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.1)'),
            hoverlabel=dict(bgcolor='white', font_family='Karla'),
            margin=dict(l=60, r=40, t=60, b=60)
        )
        
        return fig
        
    except Exception as e:
        logger.error(f"Error creating comparison chart: {e}")
        return None


def create_performance_timeline(player_data, metric='total_points'):
    """
    Create a timeline chart showing player performance over gameweeks.
    
    Args:
        player_data: Dictionary with 'gameweek' and metric data
        metric: The metric to plot over time
    
    Returns:
        Plotly figure object
    """
    try:
        if 'gameweek_data' not in player_data:
            return None
        
        df = pd.DataFrame(player_data['gameweek_data'])
        
        fig = go.Figure()
        
        # Add line trace
        fig.add_trace(go.Scatter(
            x=df['gameweek'],
            y=df[metric],
            mode='lines+markers',
            name=metric.replace('_', ' ').title(),
            line=dict(color=FPL_COLORS['accent'], width=3),
            marker=dict(size=8, color=FPL_COLORS['secondary'], 
                       line=dict(width=2, color=FPL_COLORS['accent']))
        ))
        
        # Add moving average if enough data points
        if len(df) >= 3:
            df['moving_avg'] = df[metric].rolling(window=3, center=True).mean()
            fig.add_trace(go.Scatter(
                x=df['gameweek'],
                y=df['moving_avg'],
                mode='lines',
                name='3-Game Average',
                line=dict(color=FPL_COLORS['blue'], width=2, dash='dash'),
                opacity=0.7
            ))
        
        fig.update_layout(
            title=f"{player_data.get('name', 'Player')} - {metric.replace('_', ' ').title()} Over Time",
            xaxis_title='Gameweek',
            yaxis_title=metric.replace('_', ' ').title(),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(255,255,255,0.9)',
            font=dict(family='Karla', color=FPL_COLORS['primary']),
            xaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.1)'),
            yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.1)'),
            hovermode='x unified',
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='right',
                x=1
            ),
            margin=dict(l=60, r=40, t=80, b=60)
        )
        
        return fig
        
    except Exception as e:
        logger.error(f"Error creating timeline chart: {e}")
        return None


def create_position_distribution(players_data):
    """
    Create a pie chart showing distribution of players by position.
    
    Args:
        players_data: List of player dictionaries with 'position' field
    
    Returns:
        Plotly figure object
    """
    try:
        df = pd.DataFrame(players_data)
        position_counts = df['position'].value_counts()
        
        fig = go.Figure(data=[go.Pie(
            labels=position_counts.index,
            values=position_counts.values,
            hole=0.4,
            marker=dict(
                colors=[FPL_COLORS['accent'], FPL_COLORS['secondary'], 
                       FPL_COLORS['blue'], FPL_COLORS['orange']],
                line=dict(color='white', width=2)
            ),
            textfont=dict(size=14, family='Karla', color='white'),
            hovertemplate='<b>%{label}</b><br>Count: %{value}<br>%{percent}<extra></extra>'
        )])
        
        fig.update_layout(
            title='Player Distribution by Position',
            paper_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Karla', color=FPL_COLORS['primary']),
            showlegend=True,
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=-0.2,
                xanchor='center',
                x=0.5
            ),
            margin=dict(l=40, r=40, t=60, b=100),
            height=400
        )
        
        return fig
        
    except Exception as e:
        logger.error(f"Error creating position distribution: {e}")
        return None


def create_team_performance_heatmap(team_data):
    """
    Create a heatmap showing team performance across different metrics.
    
    Args:
        team_data: List of team dictionaries with various metrics
    
    Returns:
        Plotly figure object
    """
    try:
        df = pd.DataFrame(team_data)
        
        # Select numeric columns for heatmap
        numeric_cols = df.select_dtypes(include=['int64', 'float64']).columns.tolist()
        
        if 'team' in df.columns:
            df_pivot = df.set_index('team')[numeric_cols]
        else:
            df_pivot = df[numeric_cols]
        
        # Normalize data
        df_normalized = (df_pivot - df_pivot.min()) / (df_pivot.max() - df_pivot.min())
        
        fig = go.Figure(data=go.Heatmap(
            z=df_normalized.values,
            x=df_normalized.columns,
            y=df_pivot.index,
            colorscale=[[0, FPL_COLORS['primary']], [0.5, FPL_COLORS['blue']], 
                       [1, FPL_COLORS['secondary']]],
            text=df_pivot.values,
            texttemplate='%{text}',
            textfont=dict(size=10, color='white'),
            hoverongaps=False,
            hovertemplate='Team: %{y}<br>Metric: %{x}<br>Value: %{text}<extra></extra>'
        ))
        
        fig.update_layout(
            title='Team Performance Heatmap',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family='Karla', color=FPL_COLORS['primary']),
            xaxis=dict(side='bottom'),
            margin=dict(l=120, r=40, t=60, b=100),
            height=max(400, len(df_pivot) * 40)
        )
        
        return fig
        
    except Exception as e:
        logger.error(f"Error creating heatmap: {e}")
        return None


def create_multi_metric_comparison(players_data, metrics=['goals', 'assists', 'clean_sheets']):
    """
    Create a grouped bar chart comparing multiple metrics for multiple players.
    
    Args:
        players_data: List of player dictionaries
        metrics: List of metrics to compare
    
    Returns:
        Plotly figure object
    """
    try:
        df = pd.DataFrame(players_data)
        
        fig = go.Figure()
        
        colors = [FPL_COLORS['accent'], FPL_COLORS['secondary'], FPL_COLORS['blue'], 
                 FPL_COLORS['orange'], FPL_COLORS['purple']]
        
        for i, metric in enumerate(metrics):
            if metric in df.columns:
                fig.add_trace(go.Bar(
                    name=metric.replace('_', ' ').title(),
                    x=df['name'],
                    y=df[metric],
                    marker_color=colors[i % len(colors)],
                    text=df[metric],
                    textposition='auto',
                ))
        
        fig.update_layout(
            title='Multi-Metric Player Comparison',
            xaxis_title='Player',
            yaxis_title='Value',
            barmode='group',
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(255,255,255,0.9)',
            font=dict(family='Karla', color=FPL_COLORS['primary']),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.1)'),
            legend=dict(
                orientation='h',
                yanchor='bottom',
                y=1.02,
                xanchor='right',
                x=1
            ),
            margin=dict(l=60, r=40, t=80, b=60),
            height=450
        )
        
        return fig
        
    except Exception as e:
        logger.error(f"Error creating multi-metric comparison: {e}")
        return None


def create_value_analysis_scatter(players_data):
    """
    Create a scatter plot analyzing player value (points per cost).
    
    Args:
        players_data: List of player dictionaries with 'total_points', 'cost', 'name'
    
    Returns:
        Plotly figure object
    """
    try:
        df = pd.DataFrame(players_data)
        
        if 'cost' in df.columns and 'total_points' in df.columns:
            df['value'] = df['total_points'] / df['cost']
            
            fig = px.scatter(
                df,
                x='cost',
                y='total_points',
                size='value',
                color='position' if 'position' in df.columns else None,
                hover_data=['name', 'value'],
                title='Player Value Analysis: Points vs Cost',
                labels={'cost': 'Cost (£m)', 'total_points': 'Total Points'},
                color_discrete_sequence=[FPL_COLORS['accent'], FPL_COLORS['secondary'], 
                                        FPL_COLORS['blue'], FPL_COLORS['orange']]
            )
            
            # Add trend line
            z = pd.DataFrame({'x': df['cost'], 'y': df['total_points']}).dropna()
            if len(z) >= 2:
                from sklearn.linear_model import LinearRegression
                model = LinearRegression()
                x_vals = z['x'].values.reshape(-1, 1)
                y_vals = z['y'].values
                model.fit(x_vals, y_vals)
                
                x_range = pd.Series([z['x'].min(), z['x'].max()])
                y_pred = model.predict(x_range.values.reshape(-1, 1))
                
                fig.add_trace(go.Scatter(
                    x=x_range,
                    y=y_pred,
                    mode='lines',
                    name='Trend',
                    line=dict(color=FPL_COLORS['primary'], width=2, dash='dash')
                ))
            
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(255,255,255,0.9)',
                font=dict(family='Karla', color=FPL_COLORS['primary']),
                xaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.1)'),
                yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.1)'),
                hoverlabel=dict(bgcolor='white', font_family='Karla'),
                margin=dict(l=60, r=40, t=60, b=60),
                height=500
            )
            
            return fig
        
        return None
        
    except Exception as e:
        logger.error(f"Error creating value analysis: {e}")
        return None
