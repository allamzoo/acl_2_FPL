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

from src.preprocessing.intent_classifier import SimpleIntentClassifier, Intent
from src.preprocessing.entity_extractor import EntityExtractor
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
            color: white;
        }}
        
        /* Text colors for dark theme */
        .stApp *, .stMarkdown, .stMarkdown p, .stMarkdown li, .stMarkdown span {{
            color: white !important;
        }}
        
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
        
        .fpl-card p, .fpl-card span, .fpl-card li, .fpl-card div {{
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
        
        .player-card p, .player-card span {{
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
            color: #2d2d2d;
            font-weight: 600;
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
        div[data-testid="stVerticalBlock"] p,
        div[data-testid="stVerticalBlock"] li,
        div[data-testid="stVerticalBlock"] span {{
            color: #2d2d2d;
        }}
        
        /* Headers in main content */
        div[data-testid="stVerticalBlock"] h1,
        div[data-testid="stVerticalBlock"] h2,
        div[data-testid="stVerticalBlock"] h3 {{
            color: {FPL_COLORS['primary']};
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
            color: #2d2d2d;
            font-weight: 600;
        }}
        
        .stTabs [aria-selected="true"] {{
            background: linear-gradient(135deg, {FPL_COLORS['primary']} 0%, #580064 100%);
            color: white;
            border-color: {FPL_COLORS['primary']};
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
    if 'entity_extractor' not in st.session_state:
        try:
            st.session_state.entity_extractor = EntityExtractor()
        except:
            st.session_state.entity_extractor = None
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
            ["Baseline (Cypher)", "LLM-Powered", "Hybrid (Advanced)"],
            index=0,
            help="Choose how to retrieve information from the knowledge graph"
        )
        
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
    
    # Check if LLM-powered mode is enabled
    use_llm = config['retrieval_method'] in ['Hybrid (Recommended)', 'LLM-Powered']
    
    # Initialize LLM manager on first use (lightweight, no model downloads)
    if use_llm and st.session_state.answer_generator is None:
        try:
            with st.spinner("🔄 Initializing LLM system..."):
                st.session_state.answer_generator = create_llm_manager(backend='groq')
        except Exception as e:
            st.session_state.generator_error = str(e)
            st.error(f"Failed to initialize LLM: {e}")
            use_llm = False
    
    if use_llm and st.session_state.answer_generator:
        # Use LLM with baseline retrieval (no embeddings needed)
        try:
            # Step 1: Get context from baseline retriever
            retriever = BaselineRetriever()
            
            # Classify intent to choose right retrieval method
            intent_result = st.session_state.intent_classifier.classify(query)
            method_name = st.session_state.intent_classifier.get_query_mapping(intent_result['intent'])
            
            # Extract entities for better retrieval
            entities = {}
            if st.session_state.entity_extractor:
                try:
                    entities = st.session_state.entity_extractor.extract(query)
                except:
                    pass
            
            # Retrieve context
            context_data = []
            if hasattr(retriever, method_name) and method_name != "unknown":
                method = getattr(retriever, method_name)
                
                # Call method with appropriate parameters based on intent
                try:
                    from src.preprocessing.intent_classifier import Intent
                    
                    if intent_result['intent'] == Intent.TOP_SCORERS:
                        position = None
                        if config.get('position_filter') and len(config['position_filter']) > 0:
                            position = config['position_filter'][0]
                        elif 'positions' in entities and entities['positions']:
                            position = entities['positions'][0]
                        context_data = method(position=position, season=config.get('season', '2022-23'), limit=config['max_results'])
                    
                    elif intent_result['intent'] == Intent.TOP_ASSISTERS:
                        position = None
                        if config.get('position_filter') and len(config['position_filter']) > 0:
                            position = config['position_filter'][0]
                        elif 'positions' in entities and entities['positions']:
                            position = entities['positions'][0]
                        context_data = method(position=position, season=config.get('season', '2022-23'), limit=config['max_results'])
                    
                    elif intent_result['intent'] == Intent.PLAYER_SEARCH and 'players' in entities and entities['players']:
                        context_data = method(entities['players'][0])
                    
                    elif intent_result['intent'] == Intent.TEAM_ANALYSIS and 'teams' in entities and entities['teams']:
                        context_data = method(entities['teams'][0])
                    
                    else:
                        # Try generic call
                        try:
                            context_data = method(limit=config['max_results'])
                        except TypeError:
                            try:
                                context_data = method()
                            except:
                                context_data = []
                except Exception as e:
                    # Fallback to generic call
                    try:
                        context_data = method(limit=config['max_results'])
                    except:
                        try:
                            context_data = method()
                        except:
                            context_data = []
            
            # Debug: Show what we retrieved
            if config.get('show_debug', False):
                st.write(f"🔍 Debug - Retrieved {len(context_data) if context_data else 0} items")
                if context_data:
                    st.write("Sample data:", context_data[:2])
            
            # Step 2: Build structured prompt
            # Format context data for LLM - convert list to unified_players format
            formatted_context = {
                'unified_players': [],
                'baseline_results': {}
            }
            
            # Convert context_data to player format
            if context_data and isinstance(context_data, list) and len(context_data) > 0:
                for item in context_data:
                    if isinstance(item, dict):
                        # Normalize field names
                        player_entry = {
                            'player_name': item.get('player', item.get('player_name', 'Unknown')),
                            'position': item.get('position', 'N/A'),
                            'total_goals': item.get('total_goals', item.get('goals', 0)),
                            'total_assists': item.get('total_assists', item.get('assists', 0)),
                            'total_points': item.get('total_points', item.get('points', 0)),
                            'source': 'baseline'
                        }
                        # Add any additional fields from the original item
                        for key, value in item.items():
                            if key not in player_entry:
                                player_entry[key] = value
                        formatted_context['unified_players'].append(player_entry)
            
            # If no data retrieved, show warning
            if not formatted_context['unified_players']:
                st.warning(f"⚠️ No data retrieved for intent: {intent_result['intent']} (method: {method_name})")
                st.info("💡 Tip: Try using 'Baseline (Cypher)' retrieval method instead")
            
            task_type = 'answer'
            if 'recommend' in query.lower() or 'suggest' in query.lower():
                task_type = 'recommend'
            elif 'compare' in query.lower() or 'vs' in query.lower():
                task_type = 'compare'
            elif 'explain' in query.lower() or 'why' in query.lower():
                task_type = 'explain'
            
            prompt = build_fpl_prompt(query, formatted_context, task=task_type)
            
            # Step 3: Generate answer with LLM
            llm_response = st.session_state.answer_generator.generate(
                prompt=prompt,
                model=config['model_name'],
                max_tokens=512,
                temperature=config['temperature']
            )
            
            return {
                'intent': intent_result,
                'entities': {},
                'context': context_data[:10],  # Show top 10
                'response': llm_response['response'],
                'retrieval_method': config['retrieval_method'],
                'model': llm_response['model'],
                'tokens': llm_response['tokens'],
                'cost': llm_response.get('cost', 0.0),
                'backend': llm_response.get('backend', 'unknown'),
                'cypher_query': '',
                'llm_result': llm_response
            }
        except Exception as e:
            st.error(f"LLM generation failed: {str(e)}")
            # Fallback to baseline
            use_llm = False
    
    # Fallback: Use baseline retrieval
    retriever = BaselineRetriever()
    
    # Intent classification
    intent_result = st.session_state.intent_classifier.classify(query)
    
    # Entity extraction
    entities = {}
    if st.session_state.entity_extractor:
        try:
            entities = st.session_state.entity_extractor.extract(query)
        except Exception as e:
            pass
    
    # Get retriever method based on intent
    method_name = st.session_state.intent_classifier.get_query_mapping(intent_result['intent'])
    
    # Retrieve context
    context = []
    cypher_query = ""
    
    try:
        if hasattr(retriever, method_name) and method_name != "unknown":
            method = getattr(retriever, method_name)
            
            # Try to call the method with appropriate parameters
            if intent_result['intent'] == Intent.PLAYER_SEARCH and 'players' in entities and entities['players']:
                context = method(entities['players'][0])
            elif intent_result['intent'] == Intent.TOP_SCORERS:
                # Get position if available, default to FWD
                position = "FWD"
                if 'positions' in entities and entities['positions'] and len(entities['positions']) > 0:
                    position = entities['positions'][0]
                # Apply position filter if set
                if config.get('position_filter') and len(config['position_filter']) > 0:
                    position = config['position_filter'][0]
                context = method(position=position, season=config.get('season', '2022-23'), limit=config['max_results'])
            elif intent_result['intent'] == Intent.TOP_ASSISTERS:
                # Get position if available, default to MID
                position = "MID"
                if 'positions' in entities and entities['positions'] and len(entities['positions']) > 0:
                    position = entities['positions'][0]
                # Apply position filter if set
                if config.get('position_filter') and len(config['position_filter']) > 0:
                    position = config['position_filter'][0]
                context = method(position=position, season=config.get('season', '2022-23'), limit=config['max_results'])
            elif intent_result['intent'] == Intent.TEAM_ANALYSIS and 'teams' in entities and entities['teams']:
                context = method(entities['teams'][0])
            else:
                # Generic call
                try:
                    context = method(limit=config['max_results'])
                except TypeError:
                    context = method()
        else:
            # For unknown intents, try to get top scorers as a default
            try:
                context = retriever.get_top_scorers(position="FWD", season="2022-23", limit=config['max_results'])
            except:
                context = []
            
            if not context:
                context = [{
                    "message": "I couldn't determine the specific query type. Please try:",
                    "examples": [
                        "Who are the top scorers?",
                        "Show me the best assisters",
                        "Find player Haaland",
                        "Show me Arsenal players"
                    ]
                }]
            
    except Exception as e:
        context = [{"error": f"Retrieval failed: {str(e)}"}]
    
    # Generate simple response
    response = format_simple_response(query, context, intent_result, config.get('season', '2022-23'))
    
    return {
        'intent': intent_result,
        'entities': entities,
        'context': context,
        'response': response,
        'retrieval_method': config['retrieval_method'],
        'cypher_query': cypher_query,
        'season': config.get('season', '2022-23')
    }


def format_simple_response(query: str, context: list, intent_result: dict, season: str = "2022-23") -> str:
    """Format a simple response without LLM."""
    
    if not context or (isinstance(context, list) and len(context) == 0):
        return "❌ No results found for your query."
    
    if isinstance(context, list) and len(context) > 0 and 'error' in context[0]:
        return f"❌ {context[0]['error']}"
    
    intent = intent_result['intent']
    
    # Format based on intent
    if intent == Intent.TOP_SCORERS:
        response = f"## ⚽ Top Scorers ({season} Season)\n\n"
        for i, player_data in enumerate(context[:10], 1):
            name = player_data.get('player', player_data.get('player_name', 'Unknown'))
            goals = player_data.get('total_goals', 0)
            assists = player_data.get('total_assists', 0)
            points = player_data.get('total_points', 0)
            response += f"{i}. **{name}** - ⚽ {goals} goals, 🎯 {assists} assists, 📊 {points} points\n"
        return response
    
    elif intent == Intent.TOP_ASSISTERS:
        response = f"## 🎯 Top Assist Providers ({season} Season)\n\n"
        for i, player_data in enumerate(context[:10], 1):
            name = player_data.get('player', player_data.get('player_name', 'Unknown'))
            assists = player_data.get('total_assists', 0)
            goals = player_data.get('total_goals', 0)
            points = player_data.get('total_points', 0)
            response += f"{i}. **{name}** - 🎯 {assists} assists, ⚽ {goals} goals, 📊 {points} points\n"
        return response
    
    elif intent == Intent.PLAYER_SEARCH or intent == Intent.PLAYER_STATS:
        if context:
            player = context[0]
            name = player.get('player_name', player.get('name', 'Unknown'))
            response = f"## 👤 {name}\n\n"
            for key, value in player.items():
                if key != 'player_name' and key != 'name':
                    response += f"**{key.replace('_', ' ').title()}:** {value}\n"
            return response
    
    elif intent == Intent.TEAM_ANALYSIS:
        if context:
            response = "## 👥 Team Players\n\n"
            for i, player in enumerate(context, 1):
                name = player.get('player_name', player.get('name', 'Unknown'))
                position = player.get('position', 'Unknown')
                response += f"{i}. **{name}** - {position}\n"
            return response
    
    # Generic response
    response = f"## 📊 Results ({len(context)} found)\n\n"
    for i, item in enumerate(context[:10], 1):
        response += f"### Result {i}\n"
        for key, value in item.items():
            response += f"**{key.replace('_', ' ').title()}:** {value}\n"
        response += "\n"
    
    return response


def render_results(results: dict, config: dict):
    """Render query results."""
    
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
            st.write(f"**Intent:** {results['intent']['intent']}")
            st.write(f"**Confidence:** {results['intent']['confidence']:.2%}")
        
        with col2:
            st.markdown("**Extracted Entities:**")
            if results['entities']:
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
            st.markdown("**Retrieval Method:**")
            st.code(results['retrieval_method'])
            
            if 'model' in results and results.get('retrieval_method') != 'Baseline (Cypher)':
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Model", results.get('model', 'N/A'))
                with col2:
                    st.metric("Tokens", results.get('tokens', 0))
                with col3:
                    st.metric("Backend", results.get('backend', 'N/A'))
            
            if config.get('show_cypher', False) and 'cypher_query' in results and results['cypher_query']:
                st.markdown("**Executed Cypher Query:**")
                st.code(results['cypher_query'], language='cypher')
            
            if 'llm_result' in results:
                with st.expander("🔍 Full LLM Response Details"):
                    st.json({
                        'prompt_tokens': results['llm_result'].get('prompt_tokens', 0),
                        'completion_tokens': results['llm_result'].get('completion_tokens', 0),
                        'total_tokens': results['llm_result'].get('tokens', 0),
                        'cost': results['llm_result'].get('cost', 0.0),
                        'num_players_retrieved': results['llm_result'].get('context', {}).get('num_players', 0)
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
