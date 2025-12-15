"""
Main Streamlit Application

Interactive UI for FPL Graph-RAG system with official FPL theme.
"""

import streamlit as st
import streamlit.components.v1 as components
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.preprocessing.intent_classifier import SimpleIntentClassifier, HybridIntentClassifier, Intent
from src.preprocessing.entity_extractor import EntityExtractor
from src.preprocessing.context_handler import ContextAwareFollowupHandler
from src.retrieval.baseline_retriever import BaselineRetriever
# Defer hybrid retriever import to avoid loading embedding models on startup
# from src.retrieval.hybrid_retriever import HybridRetriever
from src.llm.models import create_llm_manager
from src.llm.prompts import build_fpl_prompt
from config.config import NEO4J_URI, NEO4J_USERNAME, NEO4J_PASSWORD, NEO4J_DATABASE
from neo4j import GraphDatabase
import time
import logging
import pandas as pd
import json

# Import player photos module
from src.ui.player_photos import (
    find_player_photo, 
    extract_player_names_from_response, 
    get_player_initials
)

# Import new visualization components
from src.ui.graph_viz import render_graph, create_network_graph
from src.ui.stats_viz import (
    create_player_stats_radar,
    create_player_comparison_chart,
    create_performance_timeline,
    create_position_distribution,
    create_multi_metric_comparison,
    create_value_analysis_scatter
)
from src.ui.player_comparison import render_player_comparison_ui, compare_players
from src.ui.live_dashboard import render_live_dashboard

logger = logging.getLogger(__name__)


# FPL Official Color Scheme (Matching Official Website)
FPL_COLORS = {
    'primary': '#37003c',      # Deep purple (main brand color)
    'secondary': '#00ff87',    # Bright cyan/green
    'accent': '#e90052',       # Pink/magenta
    'cyan': '#00ffff',         # Pure cyan (gradient start)
    'purple_light': '#8000ff', # Purple gradient end
    'purple_dark': '#37003c',  # Dark purple
    'background': '#2d0035',   # Dark purple background
    'card': '#ffffff',         # White
    'text': '#37003c',         # Deep purple text
    'text_light': '#6c757d',   # Grey text
    'border': '#e0e0e0',       # Light border
    'success': '#00ff87',      # Success green
    'info': '#3949ab',         # Info blue
    'warning': '#ff9800',      # Warning orange
}

# Custom CSS matching FPL theme
def load_custom_css():
    st.markdown(f"""
    <style>
        /* Hide black header completely */
        header {{
            visibility: hidden;
            height: 0;
            display: none;
        }}
        
        #MainMenu {{
            visibility: hidden;
        }}
        
        footer {{
            visibility: hidden;
        }}
        
        .stDeployButton {{
            visibility: hidden;
        }}
        
        /* Ensure sidebar is always visible */
        [data-testid="stSidebar"] {{
            display: block !important;
        }}
        
        /* Global Styles */
        @import url('https://fonts.googleapis.com/css2?family=Karla:wght@400;600;700;800&display=swap');
        
        .stApp {{
            background: linear-gradient(135deg, #1a0020 0%, #37003c 50%, #2d0035 100%);
            font-family: 'Karla', sans-serif;
        }}
        
        /* Ensure main container doesn't add extra padding that prevents full width */
        section[data-testid="stMain"] {{
            padding-top: 0;
        }}
        
        section[data-testid="stMain"] > div:first-child {{
            padding-top: 0;
        }}
        
        /* Main content area */
        .main .block-container {{
            padding-top: 1rem;
            margin-top: 0;
            max-width: 100%;
        }}
        
        /* Remove global white text override - let specific contexts control their colors */
        
        /* Animations */
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
        
        @keyframes pulse {{
            0%, 100% {{ transform: scale(1); }}
            50% {{ transform: scale(1.05); }}
        }}
        
        /* Header - positioned at absolute top */
        .main-header {{
            background: linear-gradient(135deg, #00ffff 0%, #6e3fff 50%, #37003c 100%);
            padding: 0.75rem 1.5rem;
            margin: -1rem -2rem 1.5rem -2rem;
            width: calc(100% + 4rem);
            color: white;
            box-shadow: 0 4px 20px rgba(0, 255, 255, 0.3);
        }}
        
        .main-header h1 {{
            font-size: 1.4rem;
            font-weight: 700;
            margin: 0;
            color: white;
            text-transform: uppercase;
            letter-spacing: 1px;
            text-shadow: 0 0 20px rgba(0, 255, 255, 0.4), 0 4px 8px rgba(0, 0, 0, 0.5);
        }}
        
        .main-header p {{
            font-size: 0.8rem;
            margin: 0.2rem 0 0 0;
            color: rgba(255, 255, 255, 0.95);
            font-weight: 400;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        }}
        
        /* Push content below fixed header */
        [data-testid="stAppViewContainer"] {{
            padding-top: 0;
        }}
        
        /* Sidebar */
        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, #2d0035 0%, #37003c 50%, #4a0052 100%);
            padding-top: 2rem;
            border-right: 2px solid rgba(0, 255, 255, 0.2);
            margin-top: 0;
            transition: margin-left 0.3s ease;
        }}
        
        /* Menu toggle button */
        .menu-toggle {{
            position: fixed;
            left: 1rem;
            top: 1rem;
            background: linear-gradient(135deg, rgba(0, 255, 255, 0.3) 0%, rgba(110, 63, 255, 0.3) 100%);
            border: 2px solid #00ffff;
            color: white;
            padding: 0.75rem 1.5rem;
            border-radius: 12px;
            cursor: pointer;
            font-size: 1.1rem;
            font-weight: 700;
            transition: all 0.3s ease;
            z-index: 999999;
            user-select: none;
            box-shadow: 0 4px 15px rgba(0, 255, 255, 0.4);
            backdrop-filter: blur(10px);
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .menu-toggle:hover {{
            background: linear-gradient(135deg, rgba(0, 255, 255, 0.5) 0%, rgba(110, 63, 255, 0.5) 100%);
            box-shadow: 0 6px 25px rgba(0, 255, 255, 0.6);
            transform: translateY(-2px);
        }}
        
        .menu-toggle:active {{
            transform: translateY(0);
            box-shadow: 0 2px 10px rgba(0, 255, 255, 0.4);
        }}
        
        [data-testid="stSidebar"] .stMarkdown {{
            color: rgba(255, 255, 255, 0.95);
        }}
        
        [data-testid="stSidebar"] label {{
            color: white !important;
            font-weight: 600;
            font-size: 0.95rem;
            text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
        }}
        
        [data-testid="stSidebar"] .stSelectbox > div > div {{
            background-color: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(0, 255, 255, 0.3);
            color: white;
        }}
        
        [data-testid="stSidebar"] .stRadio > label {{
            color: white !important;
        }}
        
        [data-testid="stSidebar"] small {{
            color: rgba(255, 255, 255, 0.7) !important;
        }}
        
        /* Cards */
        .fpl-card {{
            background: linear-gradient(135deg, rgba(55, 0, 60, 0.6) 0%, rgba(45, 0, 53, 0.8) 100%);
            backdrop-filter: blur(10px);
            padding: 2rem;
            border-radius: 16px;
            box-shadow: 0 4px 20px rgba(0, 255, 255, 0.2);
            margin: 1.5rem 0;
            border: 1px solid rgba(0, 255, 255, 0.3);
            border-left: 4px solid #00ffff;
            animation: fadeIn 0.5s ease-out;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .fpl-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 8px 30px rgba(0, 255, 255, 0.5), 0 0 20px rgba(0, 255, 255, 0.3);
            border-color: rgba(0, 255, 255, 0.6);
        }}
        
        .fpl-card h1, .fpl-card h2, .fpl-card h3, .fpl-card h4, .fpl-card h5 {{
            color: #00ffff !important;
            text-shadow: 0 0 15px rgba(0, 255, 255, 0.5), 0 2px 4px rgba(0, 0, 0, 0.3);
            font-weight: 700;
            margin-bottom: 1rem;
        }}
        
        /* Card text - all content white and visible */
        .fpl-card,
        .fpl-card p,
        .fpl-card span,
        .fpl-card li,
        .fpl-card div,
        .fpl-card strong,
        .fpl-card em,
        .fpl-card a,
        .fpl-card ol,
        .fpl-card ul {{
            color: #ffffff !important;
            line-height: 1.7;
            font-size: 1rem;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.8);
        }}
        
        .fpl-card *,
        .fpl-card .stMarkdown,
        .fpl-card .stMarkdown *,
        .fpl-card > div,
        .fpl-card > div * {{
            color: #ffffff !important;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.8);
        }}
        
        /* Override any markdown color styling */
        .markdown-text-container,
        .markdown-text-container *,
        [data-testid="stMarkdownContainer"],
        [data-testid="stMarkdownContainer"] * {{
            color: inherit !important;
        }}
        
        .player-card {{
            background: linear-gradient(135deg, rgba(55, 0, 60, 0.5) 0%, rgba(74, 0, 82, 0.6) 100%);
            backdrop-filter: blur(8px);
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 2px 12px rgba(0, 255, 255, 0.15);
            margin: 0.75rem 0;
            border: 1px solid rgba(0, 255, 255, 0.2);
            border-left: 4px solid #00ffff;
            transition: all 0.3s ease;
        }}
        
        .player-card:hover {{
            transform: translateX(8px);
            box-shadow: 0 4px 16px rgba(0, 255, 255, 0.4), 0 0 15px rgba(0, 255, 255, 0.2);
            border-color: rgba(0, 255, 255, 0.5);
        }}
        
        .player-card h3, .player-card h4 {{
            color: #00ffff !important;
            text-shadow: 0 0 10px rgba(0, 255, 255, 0.4);
            font-weight: 700;
            margin-bottom: 0.75rem;
        }}
        
        .player-card p, .player-card span, .player-card div, .player-card li {{
            color: #ffffff !important;
            line-height: 1.6;
            text-shadow: 0 1px 3px rgba(0, 0, 0, 0.5);
        }}
        
        .player-card *, .player-card .stMarkdown, .player-card .stMarkdown * {{
            color: #ffffff !important;
            text-shadow: 0 1px 3px rgba(0, 0, 0, 0.5);
        }}
        
        .stat-card {{
            background: linear-gradient(135deg, #00ffff 0%, #8000ff 100%);
            padding: 1.5rem;
            border-radius: 12px;
            color: white;
            text-align: center;
            box-shadow: 0 4px 12px rgba(0, 255, 255, 0.4);
        }}
        
        .stat-card h3 {{
            font-size: 2rem;
            margin: 0;
            color: white;
            font-weight: 700;
            text-shadow: 0 0 15px rgba(0, 255, 255, 0.5), 0 2px 6px rgba(0, 0, 0, 0.5);
        }}
        
        .stat-card p {{
            font-size: 0.9rem;
            margin: 0.5rem 0 0 0;
            color: rgba(255, 255, 255, 0.9);
            text-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
        }}
        
        /* Query Input */
        .stTextInput > label {{
            color: white !important;
            font-weight: 600;
            font-size: 1.05rem;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        }}
        
        .stTextInput > div > div > input {{
            border: 2px solid rgba(0, 255, 255, 0.3);
            border-radius: 8px;
            padding: 0.75rem;
            font-size: 1rem;
            transition: all 0.3s;
            color: white !important;
            background: rgba(55, 0, 60, 0.6);
            backdrop-filter: blur(10px);
        }}
        
        .stTextInput > div > div > input::placeholder {{
            color: rgba(255, 255, 255, 0.5) !important;
        }}
        
        .stTextInput > div > div > input:focus {{
            border-color: #00ffff;
            box-shadow: 0 0 0 3px rgba(0, 255, 255, 0.2);
        }}
        
        /* Buttons - Cyan-Purple gradient background with white text */
        .stButton > button,
        button[kind="primary"],
        button[kind="secondary"],
        button[data-testid="baseButton-primary"],
        button[data-testid="baseButton-secondary"],
        .stButton button,
        div[data-testid="column"] button {{
            background: linear-gradient(135deg, #00ffff 0%, #8000ff 100%) !important;
            background-color: transparent !important;
            color: #ffffff !important;
            border: 2px solid #00ffff !important;
            border-radius: 10px !important;
            padding: 0.875rem 2.5rem !important;
            font-weight: 700 !important;
            font-size: 1rem !important;
            text-transform: uppercase;
            letter-spacing: 1px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(0, 255, 255, 0.3) !important;
        }}
        
        /* Button text - force white with maximum specificity */
        .stButton > button,
        .stButton > button *,
        .stButton > button p,
        .stButton > button div,
        .stButton > button span,
        .stButton button,
        .stButton button *,
        button[kind="primary"],
        button[kind="primary"] *,
        button[kind="secondary"],
        button[kind="secondary"] *,
        button[data-testid="baseButton-primary"],
        button[data-testid="baseButton-primary"] *,
        button[data-testid="baseButton-secondary"],
        button[data-testid="baseButton-secondary"] *,
        div[data-testid="column"] button,
        div[data-testid="column"] button *,
        div[data-testid="column"] button p {{
            color: #ffffff !important;
            font-weight: 700 !important;
        }}
        
        /* Button hover state - brighter gradient and lift */
        .stButton > button:hover,
        button[kind="primary"]:hover,
        button[kind="secondary"]:hover,
        div[data-testid="column"] button:hover {{
            transform: translateY(-3px) !important;
            box-shadow: 0 8px 25px rgba(0, 255, 255, 0.6) !important;
            background: linear-gradient(135deg, #00ffff 0%, #a020ff 100%) !important;
            border-color: #00ffff !important;
        }}
        
        /* Button hover text - keep white */
        .stButton > button:hover,
        .stButton > button:hover *,
        .stButton > button:hover p,
        .stButton > button:hover div,
        .stButton > button:hover span,
        button[kind="primary"]:hover,
        button[kind="primary"]:hover *,
        button[kind="secondary"]:hover,
        button[kind="secondary"]:hover *,
        div[data-testid="column"] button:hover,
        div[data-testid="column"] button:hover * {{
            color: #ffffff !important;
            font-weight: 700 !important;
        }}
        
        .stButton > button:active {{
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(55, 0, 60, 0.25);
        }}
        
        /* Expander */
        .streamlit-expanderHeader {{
            background: linear-gradient(135deg, rgba(55, 0, 60, 0.5) 0%, rgba(45, 0, 53, 0.7) 100%);
            border: 1px solid rgba(0, 255, 255, 0.3);
            border-radius: 8px;
            color: white !important;
            font-weight: 600;
            text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
        }}
        
        .streamlit-expanderHeader * {{
            color: white !important;
        }}
        
        [data-testid="stExpander"] {{
            background: linear-gradient(135deg, rgba(55, 0, 60, 0.4) 0%, rgba(45, 0, 53, 0.6) 100%);
        }}
        
        [data-testid="stExpander"] .stMarkdown,
        [data-testid="stExpander"] .stMarkdown * {{
            color: white !important;
        }}
        
        /* Code blocks */
        .stCodeBlock {{
            border-radius: 8px;
            border: 1px solid {FPL_COLORS['border']};
        }}
        
        /* Metrics */
        [data-testid="stMetricValue"] {{
            color: {FPL_COLORS['primary']};
            font-size: 2rem;
            font-weight: 700;
        }}
        
        /* Success/Info/Warning boxes */
        .stSuccess {{
            background: linear-gradient(135deg, rgba(0, 255, 135, 0.15) 0%, rgba(0, 200, 100, 0.1) 100%);
            border-left: 4px solid {FPL_COLORS['success']};
            border-radius: 8px;
            padding: 1rem;
            border: 1px solid rgba(0, 255, 135, 0.3);
        }}
        
        .stInfo {{
            background: linear-gradient(135deg, rgba(0, 255, 255, 0.15) 0%, rgba(0, 200, 255, 0.1) 100%);
            border-left: 4px solid #00ffff;
            border-radius: 8px;
            padding: 1rem;
            border: 1px solid rgba(0, 255, 255, 0.3);
        }}
        
        .stWarning {{
            background: linear-gradient(135deg, rgba(255, 152, 0, 0.15) 0%, rgba(255, 120, 0, 0.1) 100%);
            border-left: 4px solid {FPL_COLORS['warning']};
            border-radius: 8px;
            padding: 1rem;
            border: 1px solid rgba(255, 152, 0, 0.3);
        }}
        
        /* Main content area text */
        /* Override: Elements directly on purple background should be white */
        div[data-testid="stVerticalBlock"] > div > div > p,
        div[data-testid="stVerticalBlock"] > div > div > h1,
        div[data-testid="stVerticalBlock"] > div > div > h2,
        div[data-testid="stVerticalBlock"] > div > div > h3,
        div[data-testid="stVerticalBlock"] > div > div > label {{
            color: #ffffff !important;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.8);
        }}
        
        /* Text inside cards should be WHITE not dark */
        div[data-testid="stVerticalBlock"] .fpl-card p,
        div[data-testid="stVerticalBlock"] .fpl-card li,
        div[data-testid="stVerticalBlock"] .fpl-card span,
        div[data-testid="stVerticalBlock"] .fpl-card div,
        div[data-testid="stVerticalBlock"] .response-container p,
        div[data-testid="stVerticalBlock"] .response-container li,
        div[data-testid="stVerticalBlock"] .response-container span,
        div[data-testid="stVerticalBlock"] .response-container div {{
            color: #ffffff !important;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.8);
        }}
        
        div[data-testid="stVerticalBlock"] .fpl-card h1,
        div[data-testid="stVerticalBlock"] .fpl-card h2,
        div[data-testid="stVerticalBlock"] .fpl-card h3 {{
            color: #00ffff !important;
            text-shadow: 0 0 15px rgba(0, 255, 255, 0.6);
        }}
        
        /* Loading spinner */
        .stSpinner > div {{
            border-top-color: {FPL_COLORS['accent']} !important;
        }}
        
        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {{
            gap: 8px;
        }}
        
        .stTabs [data-baseweb="tab"] {{
            background: linear-gradient(135deg, rgba(55, 0, 60, 0.4) 0%, rgba(45, 0, 53, 0.6) 100%);
            border-radius: 8px 8px 0 0;
            padding: 0.75rem 1.5rem;
            border: 1px solid rgba(0, 255, 255, 0.2);
            color: rgba(255, 255, 255, 0.7) !important;
            font-weight: 600;
        }}
        
        .stTabs [data-baseweb="tab"] * {{
            color: rgba(255, 255, 255, 0.7) !important;
        }}
        
        .stTabs [aria-selected="true"] {{
            background: linear-gradient(135deg, #00ffff 0%, #8000ff 100%);
            color: white !important;
            border-color: #00ffff;
        }}
        
        .stTabs [aria-selected="true"] * {{
            color: white !important;
        }}
        
        /* Tab content area */
        .stTabs [data-baseweb="tab-panel"] {{
            background: linear-gradient(135deg, #2d0035 0%, #37003c 100%);
            padding: 1.5rem;
            border-radius: 0 0 12px 12px;
        }}
        
        .stTabs [data-baseweb="tab-panel"] * {{
            color: white !important;
        }}
        
        .stTabs [data-baseweb="tab-panel"] h1,
        .stTabs [data-baseweb="tab-panel"] h2,
        .stTabs [data-baseweb="tab-panel"] h3 {{
            color: white !important;
        }}
        
        /* JSON viewer inside tabs - white text on dark background */
        .stTabs [data-baseweb="tab-panel"] .stJson {{
            background-color: #1e1e1e !important;
            border: 1px solid rgba(255, 255, 255, 0.1);
            padding: 1rem;
            border-radius: 8px;
        }}
        
        .stTabs [data-baseweb="tab-panel"] .stJson * {{
            color: white !important;
        }}
        
        /* Main container text colors - White on purple background by default */
        .main .block-container {{
            color: white;
        }}
        
        .main .block-container *,
        .main .block-container h1,
        .main .block-container h2, 
        .main .block-container h3,
        .main .block-container h4,
        .main .block-container h5,
        .main .block-container p,
        .main .block-container span,
        .main .block-container label {{
            color: white !important;
        }}
        
        /* Override for dark cards - make text white with cyan headings */
        .main .block-container .fpl-card,
        .main .block-container .fpl-card * {{
            color: white !important;
        }}
        
        .main .block-container .fpl-card h1,
        .main .block-container .fpl-card h2,
        .main .block-container .fpl-card h3 {{
            color: #00ffff !important;
        }}
        
        /* Player cards - white text with cyan headings */
        .main .block-container .player-card,
        .main .block-container .player-card * {{
            color: white !important;
        }}
        
        .main .block-container .player-card h1,
        .main .block-container .player-card h2,
        .main .block-container .player-card h3 {{
            color: #00ffff !important;
        }}
        
        /* JSON viewer text */
        .stJson {{
            background-color: #1e1e1e;
            padding: 1rem;
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }}
        
        .stJson * {{
            color: white !important;
        }}
        
        .stJson .json-key {{
            color: {FPL_COLORS['secondary']} !important;
        }}
        
        .stJson .json-string {{
            color: #ce9178 !important;
        }}
        
        .stJson .json-number {{
            color: #b5cea8 !important;
        }}
        
        /* Info/Success/Warning boxes text */
        .stSuccess *, .stInfo *, .stWarning * {{
            color: white !important;
        }}
        
        /* Metric labels and values */
        [data-testid="stMetricLabel"] {{
            color: white !important;
        }}
        
        [data-testid="stMetricValue"] {{
            color: #00ffff !important;
        }}
        
        div[data-testid="stVerticalBlock"] [data-testid="stMetricLabel"] {{
            color: white !important;
        }}
        
        /* Ensure section headings on purple background are white with glow */
        .main h1, .main h2, .main h3 {{
            color: white !important;
            text-shadow: 0 0 10px rgba(0, 255, 255, 0.3), 0 2px 4px rgba(0, 0, 0, 0.5);
        }}
        
        /* Headings in cards use cyan with glow */
        .main .fpl-card h1, .main .fpl-card h2, .main .fpl-card h3 {{
            color: #00ffff !important;
            text-shadow: 0 0 15px rgba(0, 255, 255, 0.5);
        }}
        
        /* Markdown headings on main background */
        .main > div > div > div > .stMarkdown h1,
        .main > div > div > div > .stMarkdown h2,
        .main > div > div > div > .stMarkdown h3 {{
            color: white !important;
        }}
        
        /* Regular text paragraphs */
        .main > div > div > div > .stMarkdown p {{
            color: rgba(255, 255, 255, 0.95) !important;
            line-height: 1.7;
        }}
        
        /* Strong and emphasis text */
        .main strong, .main b {{
            color: #00ffff !important;
            font-weight: 700;
        }}
        
        .main em, .main i {{
            color: rgba(255, 255, 255, 0.9) !important;
        }}
        
        /* List styling */
        .main ul, .main ol {{
            color: rgba(255, 255, 255, 0.95) !important;
        }}
        
        .main li {{
            line-height: 1.6;
            margin-bottom: 0.5rem;
        }}
        
        /* Code blocks */
        .main code {{
            background: rgba(0, 255, 255, 0.1) !important;
            color: #00ffff !important;
            padding: 0.2rem 0.4rem;
            border-radius: 4px;
            font-family: 'Courier New', monospace;
        }}
    </style>
    """, unsafe_allow_html=True)


def initialize_session_state():
    """Initialize session state variables."""
    if 'query_history' not in st.session_state:
        st.session_state.query_history = []
    if 'driver' not in st.session_state:
        st.session_state.driver = None
    if 'intent_classifier' not in st.session_state:
        st.session_state.intent_classifier = SimpleIntentClassifier()
    if 'classifier_type' not in st.session_state:
        st.session_state.classifier_type = "Rule-Based"
    if 'entity_extractor' not in st.session_state:
        try:
            st.session_state.entity_extractor = EntityExtractor()
        except:
            st.session_state.entity_extractor = None
    if 'context_handler' not in st.session_state:
        st.session_state.context_handler = None
    if 'use_context' not in st.session_state:
        st.session_state.use_context = True
    if 'answer_generator' not in st.session_state:
        st.session_state.answer_generator = None
        st.session_state.generator_error = None


def get_neo4j_driver():
    """Get or create Neo4j driver."""
    if st.session_state.driver is None:
        st.session_state.driver = GraphDatabase.driver(
            NEO4J_URI,
            auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
        )
    return st.session_state.driver


def get_database_stats():
    """Get database statistics."""
    driver = get_neo4j_driver()
    with driver.session(database=NEO4J_DATABASE) as session:
        node_count = session.run("MATCH (n) RETURN count(n) as count").single()["count"]
        rel_count = session.run("MATCH ()-[r]->() RETURN count(r) as count").single()["count"]
        player_count = session.run("MATCH (p:Player) RETURN count(p) as count").single()["count"]
        team_count = session.run("MATCH (t:Team) RETURN count(t) as count").single()["count"]
    
    return {
        'nodes': node_count,
        'relationships': rel_count,
        'players': player_count,
        'teams': team_count
    }


def render_header():
    """Render the main header."""
    # Load and encode the PL logo
    import base64
    from pathlib import Path
    
    logo_path = Path(__file__).parent.parent.parent / "assets" / "fpl-logg.png"
    
    # Try to read the logo, fallback to emoji if file doesn't exist
    try:
        with open(logo_path, "rb") as f:
            logo_bytes = f.read()
        # Encode to base64 for embedding
        logo_base64 = base64.b64encode(logo_bytes).decode()
        logo_html = f'<img src="data:image/png;base64,{logo_base64}" style="width: 140px; height: 140px; margin-right: 1.5rem; vertical-align: middle; background: transparent !important; mix-blend-mode: multiply; filter: drop-shadow(0 6px 20px rgba(0, 255, 255, 0.5)) contrast(1.2);"/>'
    except:
        # Fallback also uses the logo if available, otherwise empty
        logo_html = ''
    
    # Main header
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #00ffff 0%, #6e3fff 50%, #37003c 100%);
        padding: 0.75rem 1.5rem;
        margin: -1rem -2rem 1.5rem -2rem;
        width: calc(100% + 4rem);
        color: white;
        box-shadow: 0 4px 20px rgba(0, 255, 255, 0.3);
    ">
        <h1 style="
            font-size: 1.4rem;
            font-weight: 700;
            margin: 0;
            color: white;
            text-transform: uppercase;
            letter-spacing: 1px;
            text-shadow: 0 0 20px rgba(0, 255, 255, 0.4), 0 4px 8px rgba(0, 0, 0, 0.5);
        ">{logo_html} FPL KNOWLEDGE GRAPH ASSISTANT</h1>
        <p style="
            font-size: 0.8rem;
            margin: 0.2rem 0 0 0;
            color: rgba(255, 255, 255, 0.95);
            font-weight: 400;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        ">Ask questions about Premier League players, teams, and statistics</p>
    </div>
    """, unsafe_allow_html=True)


def render_top_stats_cards():
    """Render cards showing top players for goals, clean sheets, and points."""
    try:
        driver = get_neo4j_driver()
        
        # Query for top stats
        with driver.session(database=NEO4J_DATABASE) as session:
            # Top scorer - sum all goals across fixtures for 2022-23 season
            top_scorer_result = session.run("""
                MATCH (p:Player)-[r:PLAYED_IN]->(f:Fixture)
                WHERE f.season = '2022-23'
                WITH p, SUM(r.goals_scored) as total_goals
                WHERE total_goals > 0
                RETURN p.player_name as name, total_goals as goals
                ORDER BY total_goals DESC
                LIMIT 1
            """).single()
            
            # Top clean sheets - GOALKEEPERS ONLY, sum across fixtures for 2022-23
            top_cs_result = session.run("""
                MATCH (p:Player)-[r:PLAYED_IN]->(f:Fixture)
                WHERE f.season = '2022-23' AND r.position = 'GK'
                WITH p, SUM(r.clean_sheets) as total_cs
                WHERE total_cs > 0
                RETURN p.player_name as name, total_cs as clean_sheets
                ORDER BY total_cs DESC
                LIMIT 1
            """).single()
            
            # Top points - sum all points across fixtures for 2022-23 season
            top_points_result = session.run("""
                MATCH (p:Player)-[r:PLAYED_IN]->(f:Fixture)
                WHERE f.season = '2022-23'
                WITH p, SUM(r.total_points) as total_pts
                WHERE total_pts > 0
                RETURN p.player_name as name, total_pts as points
                ORDER BY total_pts DESC
                LIMIT 1
            """).single()
    except Exception as e:
        st.error(f"Unable to load season leaders: {str(e)}")
        return
    
    # Render cards
    st.markdown("""
    <style>
        .stat-leader-card {
            background: linear-gradient(135deg, rgba(55, 0, 60, 0.9) 0%, rgba(74, 0, 82, 0.9) 100%);
            border-radius: 16px;
            padding: 1.5rem;
            text-align: center;
            border: 1px solid rgba(0, 255, 255, 0.3);
            border-left: 4px solid #00ffff;
            box-shadow: 0 4px 15px rgba(0, 255, 255, 0.2);
            transition: all 0.3s ease;
        }
        
        .stat-leader-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 8px 25px rgba(0, 255, 255, 0.4);
        }
        
        .stat-leader-title {
            color: rgba(255, 255, 255, 0.7);
            font-size: 0.9rem;
            margin-bottom: 0.5rem;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        .stat-leader-name {
            color: #ffffff;
            font-size: 1.8rem;
            font-weight: 700;
            margin: 0.5rem 0;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.8);
        }
        
        .stat-leader-value {
            color: #00ffff;
            font-size: 2.5rem;
            font-weight: 800;
            text-shadow: 0 0 20px rgba(0, 255, 255, 0.6);
        }
        
        .stat-leader-photo {
            width: 80px;
            height: 80px;
            border-radius: 50%;
            margin: 0 auto 1rem;
            border: 3px solid #00ffff;
            box-shadow: 0 0 15px rgba(0, 255, 255, 0.5);
        }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown("### 🏆 Season Leaders")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if top_scorer_result and top_scorer_result.get('name'):
            player_name = top_scorer_result['name']
            goals = top_scorer_result['goals']
            photo_url = find_player_photo(player_name)
            
            st.markdown(f"""
            <div class="stat-leader-card">
                <div class="stat-leader-title">⚽ Most Goals</div>
                <img src="{photo_url}" class="stat-leader-photo" onerror="this.src='https://via.placeholder.com/80/37003c/00ffff?text={get_player_initials(player_name)}'"/>
                <div class="stat-leader-name">{player_name}</div>
                <div class="stat-leader-value">{int(goals)}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="stat-leader-card">
                <div class="stat-leader-title">⚽ Most Goals</div>
                <div class="stat-leader-name">No Data</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        if top_cs_result and top_cs_result.get('name'):
            player_name = top_cs_result['name']
            clean_sheets = top_cs_result['clean_sheets']
            photo_url = find_player_photo(player_name)
            
            st.markdown(f"""
            <div class="stat-leader-card">
                <div class="stat-leader-title">🧤 Most Clean Sheets</div>
                <img src="{photo_url}" class="stat-leader-photo" onerror="this.src='https://via.placeholder.com/80/37003c/00ffff?text={get_player_initials(player_name)}'"/>
                <div class="stat-leader-name">{player_name}</div>
                <div class="stat-leader-value">{int(clean_sheets)}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="stat-leader-card">
                <div class="stat-leader-title">🧤 Most Clean Sheets</div>
                <div class="stat-leader-name">No Data</div>
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        if top_points_result and top_points_result.get('name'):
            player_name = top_points_result['name']
            points = top_points_result['points']
            photo_url = find_player_photo(player_name)
            
            st.markdown(f"""
            <div class="stat-leader-card">
                <div class="stat-leader-title">⭐ Most Points</div>
                <img src="{photo_url}" class="stat-leader-photo" onerror="this.src='https://via.placeholder.com/80/37003c/00ffff?text={get_player_initials(player_name)}'"/>
                <div class="stat-leader-name">{player_name}</div>
                <div class="stat-leader-value">{int(points)}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="stat-leader-card">
                <div class="stat-leader-title">⭐ Most Points</div>
                <div class="stat-leader-name">No Data</div>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<br/>", unsafe_allow_html=True)


def render_sidebar():
    """Render the sidebar with configuration options."""
    with st.sidebar:
        st.markdown("### ⚙️ Configuration")
        
        # Model selection
        model_name = st.selectbox(
            "LLM Model",
            [
                "llama-4-maverick",
                "qwen-3-32b", 
                "gpt-oss-20b"
            ],
            index=0,
            help="Select the language model for generating responses"
        )
        
        st.markdown("""
        <small style='color: rgba(255,255,255,0.7);'>
        • Llama 4 Maverick - Fast & Balanced<br>
        • Qwen 3 32B - Powerful & Detailed<br>
        • GPT OSS 20B - Efficient & Quick
        </small>
        """, unsafe_allow_html=True)
        
        # Retrieval method
        retrieval_method = st.radio(
            "Retrieval Method",
            ["Baseline Only", "Baseline + Embedding Model 1", "Baseline + Embedding Model 2"],
            index=1,
            help="Choose retrieval strategy:\n• Baseline Only - Pure Cypher queries\n• Model 1 - all-mpnet-base-v2 (more accurate)\n• Model 2 - all-MiniLM-L6-v2 (faster)"
        )
        
        # Intent Classifier Selection
        st.markdown("### 🎯 Intent Classifier")
        classifier_type = st.radio(
            "Classifier Type",
            ["Rule-Based", "Smart Hybrid"],
            index=1,
            help="• Rule-Based - Fast keyword matching only\n• Smart Hybrid - Rules first, then smart LLM agent for uncertain cases"
        )
        
        # Context-Aware Follow-up
        st.markdown("### 💬 Conversation Context")
        use_context = st.checkbox(
            "Remember conversation context",
            value=True,
            help="Smart follow-up handling - understands references to previous queries"
        )
        
        if use_context and st.session_state.context_handler:
            history_count = len(st.session_state.context_handler.history)
            if history_count > 0:
                st.caption(f"📝 {history_count} quer{'y' if history_count == 1 else 'ies'} in context")
                if st.button("Clear Context", use_container_width=True):
                    st.session_state.context_handler.clear_history()
                    st.rerun()
        
        st.markdown("---")
        
        # Temperature
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=1.0,
            value=0.3,
            step=0.1,
            help="Controls randomness in responses. Lower = more focused, Higher = more creative"
        )
        
        # Max results
        max_results = st.slider(
            "Max Results",
            min_value=5,
            max_value=50,
            value=10,
            step=5,
            help="Maximum number of results to retrieve"
        )
        
        st.markdown("---")
        
        # Season selection
        st.markdown("### 📅 Season")
        season = st.selectbox(
            "Select Season",
            ["2022-23", "2021-22"],
            index=0,
            help="Choose the FPL season",
            label_visibility="collapsed"
        )
        
        # Position filter
        st.markdown("### 🎯 Position Filter")
        position_filter = st.multiselect(
            "Filter by Position",
            ["FWD", "MID", "DEF", "GK"],
            default=[],
            help="Filter players by position",
            label_visibility="collapsed"
        )
        
        # Advanced options
        with st.expander("⚙️ Advanced Options"):
            show_debug = st.checkbox("Show Debug Info", value=False)
            show_cypher = st.checkbox("Show Cypher Queries", value=False)
            auto_llm = st.checkbox("Auto-use LLM for complex queries", value=True)
        
        st.markdown("---")
        
        # Database stats
        st.markdown("### 📊 Database Stats")
        try:
            stats = get_database_stats()
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Players", f"{stats['players']:,}")
                st.metric("Nodes", f"{stats['nodes']:,}")
            with col2:
                st.metric("Teams", f"{stats['teams']:,}")
                st.metric("Relations", f"{stats['relationships']:,}")
        except Exception as e:
            st.error("Unable to fetch stats")
        
        st.markdown("---")
        
        # Example queries
        st.markdown("### 💡 Example Queries")
        examples = [
            "Who scored the most goals?",
            "Show me midfielders from Arsenal",
            "Compare Salah and Haaland",
            "Top defenders by clean sheets",
            "Best value players under 7M"
        ]
        
        for example in examples:
            if st.button(example, key=f"example_{example}", use_container_width=True):
                st.session_state.example_query = example
                st.session_state.auto_search = True
    
    return {
        'model_name': model_name,
        'retrieval_method': retrieval_method,
        'classifier_type': classifier_type,
        'use_context': use_context,
        'temperature': temperature,
        'max_results': max_results,
        'season': season,
        'position_filter': position_filter,
        'show_debug': show_debug,
        'show_cypher': show_cypher,
        'auto_llm': auto_llm
    }


def process_query(query: str, config: dict):
    """Process user query and return results."""
    
    # Initialize context handler if enabled
    if config.get('use_context') and st.session_state.context_handler is None:
        with st.spinner("🔄 Initializing context handler..."):
            st.session_state.context_handler = ContextAwareFollowupHandler()
    
    # Update intent classifier based on user selection
    if config.get('classifier_type') != st.session_state.classifier_type:
        st.session_state.classifier_type = config['classifier_type']
        if config['classifier_type'] == "Smart Hybrid":
            with st.spinner("🔄 Loading Smart Hybrid Classifier with Groq..."):
                st.session_state.intent_classifier = HybridIntentClassifier()
        else:
            st.session_state.intent_classifier = SimpleIntentClassifier()
    
    # Handle context-aware follow-up
    original_query = query
    context_info = None
    if config.get('use_context') and st.session_state.context_handler:
        context_result = st.session_state.context_handler.resolve_context(query)
        query = context_result['resolved_query']
        context_info = context_result
        
        # Show context resolution if it's a follow-up
        if context_result['is_followup']:
            st.info(f"💬 **Follow-up detected!** Resolved to: *{query}*")

    
    # Map UI retrieval method to hybrid retriever mode
    mode_mapping = {
        "Baseline Only": "baseline",
        "Baseline + Embedding Model 1": "baseline+embedding1",
        "Baseline + Embedding Model 2": "baseline+embedding2"
    }
    retrieval_mode = mode_mapping.get(config['retrieval_method'], "baseline+embedding1")
    
    # Initialize LLM manager on first use (lightweight, no model downloads)
    if st.session_state.answer_generator is None:
        try:
            with st.spinner("🔄 Initializing LLM system..."):
                st.session_state.answer_generator = create_llm_manager(backend='groq')
        except Exception as e:
            st.session_state.generator_error = str(e)
            st.error(f"Failed to initialize LLM: {e}")
            return None
    
    # Always use LLM with hybrid retriever
    if st.session_state.answer_generator:
        try:
            # Initialize hybrid retriever (handles intent classification and entity extraction internally)
            from src.retrieval.hybrid_retriever import HybridRetriever
            retriever = HybridRetriever(use_llm_intent=False)
            
            # Extract entities for season detection
            entities = {}
            if st.session_state.entity_extractor:
                try:
                    entities = st.session_state.entity_extractor.extract(query)
                    # Debug: show extracted season
                    if config.get('show_debug', False) and entities.get('seasons'):
                        st.write(f"🔍 Extracted seasons from '{query}': {entities['seasons']}")
                except:
                    pass
            
            # Determine actual season to use: prioritize extracted season from query over UI dropdown
            actual_season = config.get('season', '2022-23')
            if entities.get('seasons') and len(entities['seasons']) > 0:
                actual_season = entities['seasons'][0]  # Use season from query if explicitly mentioned
                if config.get('show_debug', False):
                    st.write(f"🔍 Using season from query: {actual_season}")
            else:
                if config.get('show_debug', False):
                    st.write(f"🔍 Using default season from UI: {actual_season}")
            
            # Step 1: Retrieve context using hybrid retriever
            retrieval_result = retriever.retrieve(
                query=query,
                season=actual_season,
                retrieval_mode=retrieval_mode
            )
            
            # Debug: Show retrieval info
            if config.get('show_debug', False):
                st.write(f"🔍 Debug - Retrieval Mode: {retrieval_mode}")
                st.write(f"🔍 Intent: {retrieval_result.get('intent_enum', 'N/A')} (confidence: {retrieval_result.get('intent_confidence', 0):.2f})")
                st.write(f"🔍 Retrieved {len(retrieval_result.get('unified_players', []))} players")
            
            # If no data retrieved, show warning
            if not retrieval_result.get('unified_players'):
                st.warning(f"⚠️ No data retrieved for query")
                st.info("💡 Tip: Try rephrasing your question")
            
            # Step 2: Determine task type for prompt building
            task_type = 'answer'
            if 'recommend' in query.lower() or 'suggest' in query.lower():
                task_type = 'recommend'
            elif 'compare' in query.lower() or 'vs' in query.lower():
                task_type = 'compare'
            elif 'explain' in query.lower() or 'why' in query.lower():
                task_type = 'explain'
            
            # Build prompt with hybrid retrieval results
            prompt = build_fpl_prompt(query, retrieval_result, task=task_type)
            
            # Step 3: Generate answer with LLM
            llm_response = st.session_state.answer_generator.generate(
                prompt=prompt,
                model=config['model_name'],
                max_tokens=512,
                temperature=config['temperature']
            )
            
            # Add to context history if enabled
            if config.get('use_context') and st.session_state.context_handler:
                intent_str = str(retrieval_result.get('intent_enum', 'unknown'))
                st.session_state.context_handler.add_to_history(
                    query=original_query,
                    intent=intent_str,
                    entities=entities,
                    response_summary=llm_response['response'][:200]  # First 200 chars
                )
            
            return {
                'intent': retrieval_result.get('intent_enum'),
                'entities': entities,
                'context': retrieval_result.get('unified_players', [])[:10],  # Show top 10
                'response': llm_response['response'],
                'retrieval_method': config['retrieval_method'],
                'retrieval_mode': retrieval_mode,
                'model': llm_response['model'],
                'tokens': llm_response['tokens'],
                'cost': llm_response.get('cost', 0.0),
                'backend': llm_response.get('backend', 'unknown'),
                'season': actual_season,
                'cypher_query': '',
                'llm_result': llm_response,
                'retrieval_details': retrieval_result,
                'context_info': context_info,
                'original_query': original_query
            }
        except Exception as e:
            st.error(f"Error during retrieval or LLM generation: {str(e)}")
            import traceback
            if config.get('show_debug', False):
                st.code(traceback.format_exc())
            return {
                'intent': None,
                'entities': {},
                'context': [],
                'response': f"Sorry, I encountered an error: {str(e)}",
                'retrieval_method': config['retrieval_method'],
                'error': str(e)
            }
    
    # If LLM initialization failed, return error
    return {
        'intent': None,
        'entities': {},
        'context': [],
        'response': "LLM system is not initialized. Please refresh the page.",
        'retrieval_method': config['retrieval_method'],
        'error': 'LLM not initialized'
    }


def render_results(results: dict, config: dict):
    """Render query results."""
    
    # Show context resolution if it was a follow-up
    context_info = results.get('context_info')
    if context_info and context_info.get('is_followup'):
        original = results.get('original_query', '')
        resolved = context_info.get('resolved_query', '')
        if original != resolved:
            st.info(f"💬 **Follow-up detected!** Understood as: *\"{resolved}\"*")
    
    # Main response with enhanced styling
    st.markdown("### 🎯 Answer")
    
    # Show season badge
    season = results.get('season', '2022-23')
    st.markdown(f"<span style='background: linear-gradient(135deg, #37003c 0%, #580064 100%); color: white; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.85rem; font-weight: 600;'>📅 {season}</span>", unsafe_allow_html=True)
    
    # Render response inside a styled card - all in one markdown call
    response_text = results['response'].replace('\n', '<br/>')
    
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, rgba(55, 0, 60, 0.95) 0%, rgba(45, 0, 53, 0.95) 100%);
        padding: 2rem;
        border-radius: 16px;
        border-left: 4px solid #00ffff;
        box-shadow: 0 4px 20px rgba(0, 255, 255, 0.2);
        margin: 1rem 0;
        border: 1px solid rgba(0, 255, 255, 0.3);
    ">
        <div style="
            color: #ffffff !important;
            line-height: 1.8;
            font-size: 1.05rem;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.8);
        ">
            {response_text}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Show top players in card format if available
    if results.get('context') and len(results['context']) > 0:
        st.markdown("### 👥 Top Players from Results")
        
        # Extract player names from the LLM response text
        response_text = results.get('response', '')
        mentioned_names = extract_player_names_from_response(response_text)
        
        # Match mentioned players with context data
        players_to_show = []
        context_players = results['context']
        used_indices = set()
        
        for mentioned_name in mentioned_names[:5]:  # Max 5 players
            best_match = None
            best_score = 0
            best_idx = -1
            
            for idx, player in enumerate(context_players):
                if idx in used_indices:
                    continue
                    
                # Get all possible name fields
                player_names = []
                
                # Build full name from first + last
                if 'first_name' in player and 'second_name' in player:
                    full_name = f"{player.get('first_name', '')} {player.get('second_name', '')}".strip()
                    if full_name:
                        player_names.append(full_name)
                
                # Add other name fields
                for key in ['name', 'player_name', 'web_name', 'full_name']:
                    if key in player and player[key]:
                        name_val = str(player[key]).strip()
                        if name_val and name_val not in player_names:
                            player_names.append(name_val)
                
                if not player_names:
                    continue
                
                # Calculate match score
                mentioned_lower = mentioned_name.lower().strip()
                mentioned_parts = mentioned_lower.split()
                
                for player_name in player_names:
                    player_lower = player_name.lower().strip()
                    player_parts = player_lower.split()
                    
                    current_score = 0
                    
                    # Exact match
                    if mentioned_lower == player_lower:
                        current_score = 100
                    # First and last name match
                    elif (len(mentioned_parts) >= 2 and len(player_parts) >= 2 and
                          mentioned_parts[0] == player_parts[0] and 
                          mentioned_parts[-1] == player_parts[-1]):
                        current_score = 98
                    # Last name exact match
                    elif len(mentioned_parts) >= 2 and len(player_parts) >= 2 and mentioned_parts[-1] == player_parts[-1]:
                        current_score = 90
                    # Full contains
                    elif mentioned_lower in player_lower:
                        current_score = 85
                    elif player_lower in mentioned_lower:
                        current_score = 80
                    
                    if current_score > best_score:
                        best_score = current_score
                        best_match = player
                        best_idx = idx
                
                if best_score >= 98:
                    break
            
            if best_match and best_score >= 80:
                player_display_name = best_match.get('name') or best_match.get('web_name') or best_match.get('player_name', 'Unknown')
                logger.info(f"  ✓ '{mentioned_name}' → '{player_display_name}' (score: {best_score})")
                players_to_show.append(best_match)
                used_indices.add(best_idx)
            else:
                logger.warning(f"  ✗ '{mentioned_name}' no match (best: {best_score})")
        
        # Fallback to context if no names extracted
        if not players_to_show:
            logger.warning("⚠️ No matches found, using first 3 from context")
            players_to_show = context_players[:3]
        else:
            logger.info(f"✓ Matched {len(players_to_show)} players from response")
        
        # Display up to 5 players in cards
        display_count = min(5, len(players_to_show))
        
        # Create rows of 3 columns each for better layout
        for row_start in range(0, display_count, 3):
            row_players = players_to_show[row_start:row_start + 3]
            cols = st.columns(len(row_players))
            for col_idx, player in enumerate(row_players):
                idx = row_start + col_idx
                with cols[col_idx]:
                    # Smart name extraction
                    player_name = 'Unknown'
                    for key in ['name', 'player_name', 'web_name', 'full_name', 'first_name']:
                        if key in player and player[key]:
                            player_name = str(player[key])
                            break
                    
                    # Smart team extraction
                    team = None
                    for key in ['team', 'team_name', 'team_short_name', 'club']:
                        if key in player and player[key]:
                            team = str(player[key])
                            break
                    
                    # Smart position extraction
                    position = None
                    for key in ['position', 'element_type', 'singular_name_short', 'pos']:
                        if key in player and player[key]:
                            position = str(player[key])
                            break
                    
                    # Get relevant stats
                    goals = 0
                    for key in ['goals_scored', 'goals', 'total_goals']:
                        if key in player and player[key] is not None:
                            goals = int(player[key])
                            break
                    
                    assists = 0
                    for key in ['assists', 'total_assists']:
                        if key in player and player[key] is not None:
                            assists = int(player[key])
                            break
                    
                    clean_sheets = 0
                    for key in ['clean_sheets', 'total_clean_sheets']:
                        if key in player and player[key] is not None:
                            clean_sheets = int(player[key])
                            break
                    
                    # Build info text
                    info_parts = []
                    if team:
                        info_parts.append(team)
                    if position:
                        info_parts.append(position)
                    info_text = ' • '.join(info_parts) if info_parts else 'Premier League Player'
                    
                    # Get player photo
                    photo_url = find_player_photo(player_name)
                    initials = get_player_initials(player_name)
                    is_generated_avatar = photo_url and 'ui-avatars.com' in photo_url
                    
                    # Build stats badges HTML
                    stats_badges = f'''<span style="background: linear-gradient(135deg, #e90052 0%, #ff4081 100%); 
                                 color: white; padding: 0.4rem 0.8rem; border-radius: 12px; 
                                 font-size: 0.85rem; font-weight: 600;
                                 box-shadow: 0 2px 8px rgba(233, 0, 82, 0.3);">⚽ {goals}</span>
                        <span style="background: linear-gradient(135deg, #3949ab 0%, #5e35b1 100%); 
                                 color: white; padding: 0.4rem 0.8rem; border-radius: 12px; 
                                 font-size: 0.85rem; font-weight: 600;
                                 box-shadow: 0 2px 8px rgba(57, 73, 171, 0.3);">🎯 {assists}</span>'''
                    
                    if clean_sheets > 0:
                        stats_badges += f'''
                        <span style="background: linear-gradient(135deg, #00ff87 0%, #00d9a8 100%); 
                                 color: #37003c; padding: 0.4rem 0.8rem; border-radius: 12px; 
                                 font-size: 0.85rem; font-weight: 600;
                                 box-shadow: 0 2px 8px rgba(0, 255, 135, 0.3);">🛡️ {clean_sheets}</span>'''
                    
                    # Create player card
                    st.markdown(f"""
                    <div class="player-card" style="animation: fadeIn {0.6 + idx*0.2}s ease-out; 
                         box-shadow: 0 4px 20px rgba(0, 255, 135, 0.3);
                         border: 1px solid rgba(0, 255, 135, 0.2);
                         transition: all 0.3s ease;
                         text-align: center;">
                        <div style="margin-bottom: 1rem;">
                            <img src="{photo_url}" 
                                 alt="{player_name}"
                                 style="width: 110px; height: 140px; 
                                        border-radius: {'50%' if is_generated_avatar else '12px'}; 
                                        border: 3px solid rgba(0, 255, 135, 0.4);
                                        box-shadow: 0 4px 15px rgba(0, 255, 135, 0.3);
                                        object-fit: cover;"
                                 onerror="this.onerror=null; this.src='https://ui-avatars.com/api/?name={player_name.replace(' ', '+')}&size=140&background=37003c&color=00ff87&bold=true&font-size=0.4&rounded=true';">
                        </div>
                        <h4 style="margin: 0; color: #37003c; font-size: 1.2rem; font-weight: 700;">{player_name}</h4>
                        <p style="margin: 0.5rem 0; color: #6c757d; font-size: 0.9rem; font-weight: 500;">{info_text}</p>
                        <div style="margin-top: 1rem; display: flex; gap: 0.75rem; flex-wrap: wrap; justify-content: center;">
                            {stats_badges}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
    
    # Detailed information in tabs (conditional based on settings)
    tabs = ["📋 Context", "🔍 Analysis"]
    if config.get('show_debug', False):
        tabs.append("⚙️ Debug")
    
    tab_objects = st.tabs(tabs)
    tab1 = tab_objects[0]
    tab2 = tab_objects[1]
    tab3 = tab_objects[2] if len(tab_objects) > 2 else None
    
    with tab1:
        st.markdown("**Retrieved Context:**")
        if results['context']:
            st.json(results['context'])
        else:
            st.info("No context retrieved")
    
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Intent Classification:**")
            intent = results.get('intent')
            if intent:
                # Handle both dict and enum formats
                if isinstance(intent, dict):
                    st.write(f"**Intent:** {intent.get('intent', 'N/A')}")
                    st.write(f"**Confidence:** {intent.get('confidence', 0):.2%}")
                else:
                    # It's an enum
                    st.write(f"**Intent:** {intent.value if hasattr(intent, 'value') else str(intent)}")
            else:
                st.write("No intent classification available")
        
        with col2:
            st.markdown("**Extracted Entities:**")
            if results.get('entities'):
                for entity_type, entities in results['entities'].items():
                    if entities:
                        # Ensure entities is a list
                        if isinstance(entities, list):
                            st.write(f"**{entity_type.title()}:** {', '.join(str(e) for e in entities)}")
                        else:
                            st.write(f"**{entity_type.title()}:** {entities}")
            else:
                st.write("No entities extracted")
    
    if tab3:
        with tab3:
            st.markdown("**Retrieval Configuration:**")
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Method:** {results.get('retrieval_method', 'N/A')}")
            with col2:
                st.write(f"**Mode:** {results.get('retrieval_mode', 'N/A')}")
            
            if 'model' in results:
                st.markdown("**LLM Details:**")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Model", results.get('model', 'N/A'))
                with col2:
                    st.metric("Tokens", results.get('tokens', 0))
                with col3:
                    st.metric("Backend", results.get('backend', 'N/A'))
            
            if 'retrieval_details' in results:
                with st.expander("📊 Retrieval Details"):
                    details = results['retrieval_details']
                    st.write(f"**Players Retrieved:** {len(details.get('unified_players', []))}")
                    st.write(f"**Intent Confidence:** {details.get('intent_confidence', 0):.2%}")
                    if 'baseline_results' in details:
                        st.write(f"**Baseline Results:** {len(details.get('baseline_results', {}).get('results', []))} items")
                    if 'semantic_results' in details:
                        st.write(f"**Semantic Results:** {len(details.get('semantic_results', {}).get('results', []))} items")
            
            if 'llm_result' in results:
                with st.expander("🔍 Full LLM Response Details"):
                    st.json({
                        'prompt_tokens': results['llm_result'].get('prompt_tokens', 0),
                        'completion_tokens': results['llm_result'].get('completion_tokens', 0),
                        'total_tokens': results['llm_result'].get('tokens', 0),
                        'cost': results['llm_result'].get('cost', 0.0),
                    })


def main():
    """Main application with tab-based navigation."""
    
    # Page config
    st.set_page_config(
        page_title="FPL Knowledge Graph Assistant",
        page_icon="https://www.premierleague.com/resources/rebrand/v7.129.2/i/elements/pl-main-logo.png",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Load custom CSS
    load_custom_css()
    
    # Initialize session state
    initialize_session_state()
    
    # Render header
    render_header()
    
    # Render top stats cards
    render_top_stats_cards()
    
    # Render sidebar and get config
    config = render_sidebar()
    
    # Main tabs
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "💬 Chat Assistant",
        "📈 Live Dashboard",
        "🔄 Player Comparison",
        "📊 Advanced Analytics",
        "🌐 Graph Explorer",
        "⚙️ Settings & Export"
    ])
    
    # Tab 1: Chat Assistant (Original functionality)
    with tab1:
        render_chat_interface(config)
    
    # Tab 2: Live Dashboard
    with tab2:
        with GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD)) as driver:
            render_live_dashboard(driver, NEO4J_DATABASE)
    
    # Tab 3: Player Comparison
    with tab3:
        render_player_comparison_tab(config)
    
    # Tab 4: Advanced Analytics
    with tab4:
        render_analytics_tab(config)
    
    # Tab 5: Graph Explorer
    with tab5:
        render_graph_explorer_tab(config)
    
    # Tab 6: Settings & Export
    with tab6:
        render_settings_export_tab()


def render_chat_interface(config):
    """Render the original chat interface."""
    # Check for example query
    auto_search = False
    if 'example_query' in st.session_state:
        query = st.session_state.example_query
        del st.session_state.example_query
        if 'auto_search' in st.session_state:
            auto_search = st.session_state.auto_search
            del st.session_state.auto_search
    else:
        query = None
    
    # Main content
    st.markdown("### 💬 Ask Your Question")
    
    # Query input
    user_query = st.text_input(
        "Enter your question about FPL...",
        value=query or "",
        placeholder="e.g., Who are the top scorers in the Premier League?",
        label_visibility="collapsed"
    )
    
    col1, col2, col3 = st.columns([1, 1, 3])
    with col1:
        search_button = st.button("SEARCH", type="primary", use_container_width=True)
    with col2:
        clear_button = st.button("CLEAR", use_container_width=True)
    
    if clear_button:
        st.rerun()
    
    # Process query (either from button click or auto-search from example)
    if (search_button or auto_search) and user_query:
        with st.spinner("🔄 Processing your query..."):
            try:
                results = process_query(user_query, config)
                
                # Add to history
                st.session_state.query_history.insert(0, {
                    'query': user_query,
                    'results': results,
                    'timestamp': time.time()
                })
                
                # Render results
                render_results(results, config)
                
            except Exception as e:
                st.error(f"❌ Error processing query: {str(e)}")
                st.exception(e)
    
    elif search_button:
        st.warning("⚠️ Please enter a question first!")
    
    # Query history
    if st.session_state.query_history:
        st.markdown("---")
        st.markdown("### 📜 Recent Queries")
        
        for i, item in enumerate(st.session_state.query_history[:5]):
            with st.expander(f"🔹 {item['query']}", expanded=(i == 0)):
                render_results(item['results'], config)


def render_player_comparison_tab(config):
    """Render the player comparison tab."""
    render_player_comparison_ui()
    
    # Sample data for demo
    if st.button("🎯 Load Sample Comparison"):
        sample_players = [
            {
                'name': 'Erling Haaland',
                'team': 'Man City',
                'position': 'Forward',
                'goals': 36,
                'assists': 8,
                'clean_sheets': 0,
                'bonus': 30,
                'minutes': 2880,
                'total_points': 272,
                'bps': 820,
                'ict_index': 280,
                'cost': 12.0
            },
            {
                'name': 'Mohamed Salah',
                'team': 'Liverpool',
                'position': 'Midfielder',
                'goals': 19,
                'assists': 12,
                'clean_sheets': 0,
                'bonus': 25,
                'minutes': 3000,
                'total_points': 225,
                'bps': 750,
                'ict_index': 260,
                'cost': 13.0
            },
            {
                'name': 'Harry Kane',
                'team': 'Spurs',
                'position': 'Forward',
                'goals': 30,
                'assists': 3,
                'clean_sheets': 0,
                'bonus': 20,
                'minutes': 3100,
                'total_points': 219,
                'bps': 690,
                'ict_index': 240,
                'cost': 11.0
            }
        ]
        
        compare_players(sample_players)


def render_analytics_tab(config):
    """Render the advanced analytics tab."""
    st.markdown("### 📊 Advanced Analytics")
    
    # Analysis type selector
    analysis_type = st.selectbox(
        "Select Analysis Type",
        ["Top Performers by Metric", "Position Distribution", "Value Analysis", "Team Performance"]
    )
    
    if analysis_type == "Top Performers by Metric":
        col1, col2, col3 = st.columns(3)
        with col1:
            metric = st.selectbox(
                "Select Metric",
                ["goals", "assists", "total_points", "clean_sheets", "bonus"]
            )
        with col2:
            season = st.selectbox("Season", ["2022-23", "2021-22", "2020-21"])
        with col3:
            top_n = st.number_input("Number of Players", 5, 50, 10)
        
        if st.button("🔍 Analyze", use_container_width=True):
            with st.spinner("Loading data..."):
                with GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD)) as driver:
                    with driver.session(database=NEO4J_DATABASE) as session:
                        query = f"""
                        MATCH (p:Player)-[r:PLAYED_IN]->(s:Season {{name: $season}})
                        WHERE r.{metric} IS NOT NULL
                        RETURN p.name as name, p.team_name as team, p.position as position, 
                               r.{metric} as value
                        ORDER BY r.{metric} DESC
                        LIMIT $limit
                        """
                        result = session.run(query, season=season, limit=top_n)
                        data = [dict(record) for record in result]
                
                if data:
                    # Create dataframe
                    df = pd.DataFrame(data)
                    df.columns = ['name', 'team', 'position', metric]
                    
                    # Create bar chart
                    fig = create_player_comparison_chart(data, metric=metric, chart_type='bar')
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                    
                    # Display table
                    st.dataframe(df, use_container_width=True)
                else:
                    st.warning("No data found for the selected criteria.")
    
    elif analysis_type == "Position Distribution":
        season = st.selectbox("Season", ["2022-23", "2021-22", "2020-21"])
        
        if st.button("🔍 Analyze", use_container_width=True):
            with st.spinner("Loading data..."):
                with GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD)) as driver:
                    with driver.session(database=NEO4J_DATABASE) as session:
                        query = """
                        MATCH (p:Player)-[:PLAYED_IN]->(s:Season {name: $season})
                        RETURN p.position as position, count(p) as count
                        """
                        result = session.run(query, season=season)
                        data = [{'position': r['position'], 'count': r['count']} for r in result]
                
                if data:
                    fig = create_position_distribution(data)
                    if fig:
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning("No data found.")


def render_graph_explorer_tab(config):
    """Render the graph explorer tab."""
    st.markdown("### 🌐 Interactive Graph Explorer")
    
    query_type = st.selectbox(
        "Select Query Type",
        ["Player Connections", "Team Network", "Custom Cypher Query"]
    )
    
    if query_type == "Player Connections":
        player_name = st.text_input("Enter Player Name", "Erling Haaland")
        depth = st.slider("Connection Depth", 1, 3, 1)
        
        if st.button("🔍 Explore Connections"):
            with st.spinner("Fetching graph data..."):
                with GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD)) as driver:
                    with driver.session(database=NEO4J_DATABASE) as session:
                        query = """
                        MATCH path = (p:Player {name: $name})-[*1..%d]-(connected)
                        RETURN path
                        LIMIT 50
                        """ % depth
                        
                        result = session.run(query, name=player_name)
                        neo4j_results = list(result)
                
                if neo4j_results:
                    render_graph(neo4j_results, height='700px')
                    st.success(f"✅ Found {len(neo4j_results)} connections for {player_name}")
                else:
                    st.warning(f"No connections found for {player_name}")
    
    elif query_type == "Custom Cypher Query":
        st.markdown("#### Execute Custom Cypher Query")
        cypher_query = st.text_area(
            "Enter Cypher Query",
            value="MATCH (p:Player)-[r:PLAYED_IN]->(s:Season) RETURN p, r, s LIMIT 25",
            height=150
        )
        
        if st.button("▶️ Execute"):
            with st.spinner("Executing query..."):
                with GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USERNAME, NEO4J_PASSWORD)) as driver:
                    with driver.session(database=NEO4J_DATABASE) as session:
                        try:
                            result = session.run(cypher_query)
                            neo4j_results = list(result)
                            
                            if neo4j_results:
                                render_graph(neo4j_results, height='700px')
                                st.success(f"✅ Retrieved {len(neo4j_results)} records")
                            else:
                                st.info("Query returned no results")
                        except Exception as e:
                            st.error(f"Query error: {str(e)}")


def render_settings_export_tab():
    """Render the settings and export tab."""
    st.markdown("### ⚙️ Settings & Export")
    
    # Export section
    st.markdown("#### 📤 Export Data")
    
    col1, col2 = st.columns(2)
    
    with col1:
        export_format = st.selectbox(
            "Export Format",
            ["JSON", "CSV", "Excel"]
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)  # Spacing
        if st.button("📥 Export Query History", use_container_width=True):
            if st.session_state.query_history:
                # Prepare export data
                export_data = []
                for item in st.session_state.query_history:
                    export_data.append({
                        'query': item['query'],
                        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(item['timestamp'])),
                        'results_summary': str(item['results'])[:200]
                    })
                
                if export_format == "JSON":
                    json_str = json.dumps(export_data, indent=2)
                    st.download_button(
                        label="Download JSON",
                        data=json_str,
                        file_name=f"fpl_query_history_{int(time.time())}.json",
                        mime="application/json"
                    )
                
                elif export_format == "CSV":
                    df = pd.DataFrame(export_data)
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="Download CSV",
                        data=csv,
                        file_name=f"fpl_query_history_{int(time.time())}.csv",
                        mime="text/csv"
                    )
                
                elif export_format == "Excel":
                    df = pd.DataFrame(export_data)
                    # Use xlsxwriter engine
                    from io import BytesIO
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine='openpyxl') as writer:
                        df.to_excel(writer, index=False, sheet_name='Query History')
                    output.seek(0)
                    
                    st.download_button(
                        label="Download Excel",
                        data=output,
                        file_name=f"fpl_query_history_{int(time.time())}.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
            else:
                st.warning("No query history to export.")
    
    st.markdown("---")
    
    # Cache management
    st.markdown("#### 🗄️ Cache Management")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Clear Cache", use_container_width=True):
            st.cache_data.clear()
            st.success("✅ Cache cleared successfully!")
    
    with col2:
        if st.button("🔁 Reset Session", use_container_width=True):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.success("✅ Session reset successfully!")
            st.rerun()
    
    st.markdown("---")
    
    # App info
    st.markdown("#### ℹ️ Application Info")
    st.info("""
    **FPL Knowledge Graph Assistant v2.0**
    
    Enhanced with:
    - 📈 Live Metrics Dashboard
    - 🔄 Player Comparison Tool
    - 📊 Advanced Analytics
    - 🌐 Interactive Graph Explorer
    - 📤 Data Export (JSON/CSV/Excel)
    
    Built with Streamlit, Neo4j, and Plotly
    """)


if __name__ == "__main__":
    main()
