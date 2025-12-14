"""
Main Streamlit Application

Interactive UI for FPL Graph-RAG system with official FPL theme.
"""

import streamlit as st
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

logger = logging.getLogger(__name__)


# FPL Official Color Scheme
FPL_COLORS = {
    'primary': '#37003c',      # Deep purple (main brand color)
    'secondary': '#00ff87',    # Bright cyan/green
    'accent': '#e90052',       # Pink/magenta
    'background': '#f7f7f7',   # Light grey
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
        /* Global Styles */
        @import url('https://fonts.googleapis.com/css2?family=Karla:wght@400;600;700;800&display=swap');
        
        .stApp {{
            background: linear-gradient(135deg, {FPL_COLORS['primary']} 0%, #580064 100%);
            font-family: 'Karla', sans-serif;
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
        
        /* Header */
        .main-header {{
            background: linear-gradient(135deg, {FPL_COLORS['primary']} 0%, #580064 100%);
            padding: 2rem 2rem 3rem 2rem;
            border-radius: 0 0 20px 20px;
            margin: -6rem -4rem 2rem -4rem;
            color: white;
            box-shadow: 0 4px 20px rgba(55, 0, 60, 0.3);
        }}
        
        .main-header h1 {{
            font-size: 2.5rem;
            font-weight: 700;
            margin: 0;
            color: white;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .main-header p {{
            font-size: 1.1rem;
            margin: 0.5rem 0 0 0;
            color: {FPL_COLORS['secondary']};
            font-weight: 400;
        }}
        
        /* Sidebar */
        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, {FPL_COLORS['primary']} 0%, #580064 100%);
            padding-top: 2rem;
        }}
        
        [data-testid="stSidebar"] .stMarkdown {{
            color: white;
        }}
        
        [data-testid="stSidebar"] label {{
            color: white !important;
            font-weight: 600;
            font-size: 0.95rem;
        }}
        
        [data-testid="stSidebar"] .stSelectbox > div > div {{
            background-color: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.2);
            color: white;
        }}
        
        [data-testid="stSidebar"] .stRadio > label {{
            color: white !important;
        }}
        
        /* Cards */
        .fpl-card {{
            background-color: {FPL_COLORS['card']};
            padding: 2rem;
            border-radius: 16px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
            margin: 1.5rem 0;
            border-left: 5px solid {FPL_COLORS['accent']};
            animation: fadeIn 0.5s ease-out;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .fpl-card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 8px 30px rgba(233, 0, 82, 0.15);
        }}
        
        .fpl-card h1, .fpl-card h2, .fpl-card h3, .fpl-card h4, .fpl-card h5 {{
            color: {FPL_COLORS['primary']} !important;
        }}
        
        .fpl-card p, .fpl-card span, .fpl-card li, .fpl-card div, .fpl-card {{
            color: #2d2d2d !important;
        }}
        
        .fpl-card *, .fpl-card .stMarkdown, .fpl-card .stMarkdown * {{
            color: #2d2d2d !important;
        }}
        
        .player-card {{
            background: linear-gradient(135deg, {FPL_COLORS['card']} 0%, #f9f9f9 100%);
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
            margin: 0.75rem 0;
            border-left: 4px solid {FPL_COLORS['secondary']};
            transition: all 0.3s ease;
        }}
        
        .player-card:hover {{
            transform: translateX(8px);
            box-shadow: 0 4px 16px rgba(0, 255, 135, 0.2);
        }}
        
        .player-card h3, .player-card h4 {{
            color: {FPL_COLORS['primary']} !important;
        }}
        
        .player-card p, .player-card span, .player-card div, .player-card li {{
            color: #2d2d2d !important;
        }}
        
        .player-card *, .player-card .stMarkdown, .player-card .stMarkdown * {{
            color: #2d2d2d !important;
        }}
        
        .stat-card {{
            background: linear-gradient(135deg, {FPL_COLORS['primary']} 0%, #580064 100%);
            padding: 1.5rem;
            border-radius: 12px;
            color: white;
            text-align: center;
            box-shadow: 0 4px 12px rgba(55, 0, 60, 0.3);
        }}
        
        .stat-card h3 {{
            font-size: 2rem;
            margin: 0;
            color: {FPL_COLORS['secondary']};
            font-weight: 700;
        }}
        
        .stat-card p {{
            font-size: 0.9rem;
            margin: 0.5rem 0 0 0;
            color: rgba(255, 255, 255, 0.8);
        }}
        
        /* Query Input */
        .stTextInput > label {{
            color: white !important;
            font-weight: 600;
            font-size: 1rem;
        }}
        
        .stTextInput > div > div > input {{
            border: 2px solid {FPL_COLORS['border']};
            border-radius: 8px;
            padding: 0.75rem;
            font-size: 1rem;
            transition: all 0.3s;
            color: {FPL_COLORS['primary']} !important;
            background-color: white;
        }}
        
        .stTextInput > div > div > input::placeholder {{
            color: {FPL_COLORS['text_light']} !important;
        }}
        
        .stTextInput > div > div > input:focus {{
            border-color: {FPL_COLORS['accent']};
            box-shadow: 0 0 0 3px rgba(233, 0, 82, 0.1);
        }}
        
        /* Buttons */
        .stButton > button {{
            background: white !important;
            color: {FPL_COLORS['primary']} !important;
            border: 2px solid {FPL_COLORS['accent']} !important;
            border-radius: 10px;
            padding: 0.875rem 2.5rem;
            font-weight: 700;
            font-size: 1rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(233, 0, 82, 0.2);
            position: relative;
            overflow: hidden;
        }}
        
        .stButton > button *, .stButton > button p {{
            color: {FPL_COLORS['primary']} !important;
        }}
        
        .stButton > button:hover {{
            transform: translateY(-3px);
            box-shadow: 0 8px 25px rgba(55, 0, 60, 0.3);
            background: {FPL_COLORS['primary']} !important;
            color: white !important;
            animation: pulse 0.6s ease;
        }}
        
        .stButton > button:hover *, .stButton > button:hover p {{
            color: white !important;
        }}
        
        .stButton > button:active {{
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(55, 0, 60, 0.25);
        }}
        
        /* Expander */
        .streamlit-expanderHeader {{
            background-color: {FPL_COLORS['card']};
            border: 1px solid {FPL_COLORS['border']};
            border-radius: 8px;
            color: #2d2d2d !important;
            font-weight: 600;
        }}
        
        .streamlit-expanderHeader * {{
            color: #2d2d2d !important;
        }}
        
        [data-testid="stExpander"] {{
            background-color: {FPL_COLORS['card']};
        }}
        
        [data-testid="stExpander"] .stMarkdown,
        [data-testid="stExpander"] .stMarkdown * {{
            color: #2d2d2d !important;
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
            background-color: rgba(0, 255, 135, 0.1);
            border-left: 4px solid {FPL_COLORS['success']};
            border-radius: 8px;
            padding: 1rem;
        }}
        
        .stInfo {{
            background-color: rgba(57, 73, 171, 0.1);
            border-left: 4px solid {FPL_COLORS['info']};
            border-radius: 8px;
            padding: 1rem;
        }}
        
        .stWarning {{
            background-color: rgba(255, 152, 0, 0.1);
            border-left: 4px solid {FPL_COLORS['warning']};
            border-radius: 8px;
            padding: 1rem;
        }}
        
        /* Main content area text */
        /* Override: Elements directly on purple background should be white */
        div[data-testid="stVerticalBlock"] > div > div > p,
        div[data-testid="stVerticalBlock"] > div > div > h1,
        div[data-testid="stVerticalBlock"] > div > div > h2,
        div[data-testid="stVerticalBlock"] > div > div > h3,
        div[data-testid="stVerticalBlock"] > div > div > label {{
            color: white !important;
        }}
        
        /* Text inside cards should be dark */
        div[data-testid="stVerticalBlock"] .fpl-card p,
        div[data-testid="stVerticalBlock"] .fpl-card li,
        div[data-testid="stVerticalBlock"] .fpl-card span,
        div[data-testid="stVerticalBlock"] .fpl-card div {{
            color: #2d2d2d !important;
        }}
        
        div[data-testid="stVerticalBlock"] .fpl-card h1,
        div[data-testid="stVerticalBlock"] .fpl-card h2,
        div[data-testid="stVerticalBlock"] .fpl-card h3 {{
            color: {FPL_COLORS['primary']} !important;
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
            background-color: {FPL_COLORS['card']};
            border-radius: 8px 8px 0 0;
            padding: 0.75rem 1.5rem;
            border: 1px solid {FPL_COLORS['border']};
            color: #2d2d2d !important;
            font-weight: 600;
        }}
        
        .stTabs [data-baseweb="tab"] * {{
            color: #2d2d2d !important;
        }}
        
        .stTabs [aria-selected="true"] {{
            background: linear-gradient(135deg, {FPL_COLORS['primary']} 0%, #580064 100%);
            color: white !important;
            border-color: {FPL_COLORS['primary']};
        }}
        
        .stTabs [aria-selected="true"] * {{
            color: white !important;
        }}
        
        /* Tab content area */
        .stTabs [data-baseweb="tab-panel"] {{
            background-color: {FPL_COLORS['card']};
            padding: 1.5rem;
            border-radius: 0 0 12px 12px;
        }}
        
        .stTabs [data-baseweb="tab-panel"] * {{
            color: #2d2d2d !important;
        }}
        
        .stTabs [data-baseweb="tab-panel"] h1,
        .stTabs [data-baseweb="tab-panel"] h2,
        .stTabs [data-baseweb="tab-panel"] h3 {{
            color: {FPL_COLORS['primary']} !important;
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
        
        /* Override for white cards - make text dark */
        .main .block-container .fpl-card,
        .main .block-container .fpl-card * {{
            color: #2d2d2d !important;
        }}
        
        .main .block-container .fpl-card h1,
        .main .block-container .fpl-card h2,
        .main .block-container .fpl-card h3 {{
            color: {FPL_COLORS['primary']} !important;
        }}
        
        /* Player cards - dark text on white */
        .main .block-container .player-card,
        .main .block-container .player-card * {{
            color: #2d2d2d !important;
        }}
        
        .main .block-container .player-card h1,
        .main .block-container .player-card h2,
        .main .block-container .player-card h3 {{
            color: {FPL_COLORS['primary']} !important;
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
            color: #2d2d2d !important;
        }}
        
        /* Metric labels and values */
        [data-testid="stMetricLabel"] {{
            color: white !important;
        }}
        
        div[data-testid="stVerticalBlock"] [data-testid="stMetricLabel"] {{
            color: #2d2d2d !important;
        }}
        
        /* Ensure section headings on purple background are white */
        .main h1, .main h2, .main h3 {{
            color: white !important;
        }}
        
        /* But keep headings in cards as purple */
        .main .fpl-card h1, .main .fpl-card h2, .main .fpl-card h3 {{
            color: {FPL_COLORS['primary']} !important;
        }}
        
        /* Markdown headings on main background */
        .main > div > div > div > .stMarkdown h1,
        .main > div > div > div > .stMarkdown h2,
        .main > div > div > div > .stMarkdown h3 {{
            color: white !important;
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
    st.markdown("""
    <div class="main-header">
        <h1>⚽ FPL Knowledge Graph Assistant</h1>
        <p>Ask questions about Premier League players, teams, and statistics</p>
    </div>
    """, unsafe_allow_html=True)


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
    
    st.markdown(f"""
    <div class="fpl-card">
        {results['response']}
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
    """Main application."""
    
    # Page config
    st.set_page_config(
        page_title="FPL Knowledge Graph Assistant",
        page_icon="⚽",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Load custom CSS
    load_custom_css()
    
    # Initialize session state
    initialize_session_state()
    
    # Render header
    render_header()
    
    # Render sidebar and get config
    config = render_sidebar()
    
    # Check for example query
    if 'example_query' in st.session_state:
        query = st.session_state.example_query
        del st.session_state.example_query
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
    
    # Process query
    if search_button and user_query:
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


if __name__ == "__main__":
    main()
