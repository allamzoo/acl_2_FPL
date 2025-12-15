"""
Graph Visualization Component

Visualizes retrieved subgraphs using pyvis for interactive network graphs.
"""

from pyvis.network import Network
import streamlit.components.v1 as components
import tempfile
import os
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# FPL Color scheme for graph visualization
FPL_COLORS = {
    'Player': '#e90052',       # Pink/magenta
    'Team': '#37003c',         # Deep purple
    'Season': '#00ff87',       # Bright cyan/green
    'Position': '#3949ab',     # Blue
    'Gameweek': '#ff9800',     # Orange
    'default': '#6c757d'       # Grey
}


def create_network_graph(neo4j_results, height='600px', width='100%', physics=True):
    """
    Create an interactive network graph from Neo4j results.
    
    Args:
        neo4j_results: Results from Neo4j query containing nodes and relationships
        height: Height of the visualization
        width: Width of the visualization
        physics: Enable physics simulation for layout
    
    Returns:
        HTML string of the network graph
    """
    try:
        # Create network with FPL styling
        net = Network(
            height=height,
            width=width,
            bgcolor='#ffffff',
            font_color='#37003c',
            directed=True
        )
        
        # Configure physics
        if physics:
            net.set_options("""
            {
                "physics": {
                    "enabled": true,
                    "stabilization": {
                        "enabled": true,
                        "iterations": 200
                    },
                    "barnesHut": {
                        "gravitationalConstant": -8000,
                        "centralGravity": 0.3,
                        "springLength": 150,
                        "springConstant": 0.04,
                        "damping": 0.09
                    }
                },
                "interaction": {
                    "hover": true,
                    "tooltipDelay": 100,
                    "zoomView": true,
                    "dragView": true
                },
                "nodes": {
                    "font": {
                        "size": 14,
                        "face": "Karla"
                    },
                    "borderWidth": 2,
                    "borderWidthSelected": 4
                },
                "edges": {
                    "color": {
                        "inherit": false,
                        "color": "#cccccc",
                        "highlight": "#e90052",
                        "hover": "#00ff87"
                    },
                    "smooth": {
                        "enabled": true,
                        "type": "dynamic"
                    },
                    "arrows": {
                        "to": {
                            "enabled": true,
                            "scaleFactor": 0.5
                        }
                    }
                }
            }
            """)
        
        nodes_added = set()
        
        # Process nodes and relationships from Neo4j results
        if isinstance(neo4j_results, list):
            for record in neo4j_results:
                # Handle different result structures
                if hasattr(record, 'graph'):
                    # Graph projection results
                    for node in record.graph.nodes:
                        add_node_to_network(net, node, nodes_added)
                    for rel in record.graph.relationships:
                        add_relationship_to_network(net, rel)
                        
                elif hasattr(record, 'data'):
                    # Standard Cypher results
                    data = record.data()
                    for key, value in data.items():
                        if hasattr(value, '__class__'):
                            class_name = value.__class__.__name__
                            if class_name == 'Node':
                                add_node_to_network(net, value, nodes_added)
                            elif class_name == 'Relationship':
                                add_relationship_to_network(net, value)
        
        # If no nodes were added, create a simple message
        if len(nodes_added) == 0:
            net.add_node(0, label="No graph data available", color='#cccccc')
        
        # Generate HTML
        html = net.generate_html()
        
        return html
        
    except Exception as e:
        logger.error(f"Error creating network graph: {e}")
        return f"<div style='padding: 20px; color: red;'>Error creating graph: {str(e)}</div>"


def add_node_to_network(net, node, nodes_added):
    """Add a node to the pyvis network."""
    try:
        node_id = node.id if hasattr(node, 'id') else str(node)
        
        if node_id in nodes_added:
            return
        
        # Get node labels and properties
        labels = list(node.labels) if hasattr(node, 'labels') else []
        props = dict(node) if hasattr(node, '__iter__') else {}
        
        # Determine node color based on label
        color = FPL_COLORS.get(labels[0] if labels else 'default', FPL_COLORS['default'])
        
        # Create label
        label = props.get('name') or props.get('web_name') or props.get('id') or str(node_id)
        
        # Create hover title with properties
        title = f"<b>{labels[0] if labels else 'Node'}</b><br>"
        for key, value in props.items():
            if key not in ['embedding', 'vector']:  # Skip large data
                title += f"{key}: {value}<br>"
        
        # Determine node size based on type
        if labels and labels[0] == 'Player':
            size = 25
            shape = 'dot'
        elif labels and labels[0] == 'Team':
            size = 30
            shape = 'square'
        elif labels and labels[0] == 'Season':
            size = 20
            shape = 'diamond'
        else:
            size = 20
            shape = 'dot'
        
        net.add_node(
            node_id,
            label=label,
            color=color,
            size=size,
            shape=shape,
            title=title,
            borderWidth=2,
            borderWidthSelected=4
        )
        
        nodes_added.add(node_id)
        
    except Exception as e:
        logger.error(f"Error adding node to network: {e}")


def add_relationship_to_network(net, rel):
    """Add a relationship to the pyvis network."""
    try:
        start_id = rel.start_node.id if hasattr(rel, 'start_node') else rel.nodes[0].id
        end_id = rel.end_node.id if hasattr(rel, 'end_node') else rel.nodes[1].id
        rel_type = rel.type if hasattr(rel, 'type') else 'RELATED_TO'
        
        # Get relationship properties
        props = dict(rel) if hasattr(rel, '__iter__') else {}
        
        # Create label from relationship type
        label = rel_type.replace('_', ' ').title()
        
        # Create hover title
        title = f"<b>{label}</b><br>"
        for key, value in props.items():
            title += f"{key}: {value}<br>"
        
        net.add_edge(
            start_id,
            end_id,
            title=title,
            label=label,
            color='#cccccc',
            width=2
        )
        
    except Exception as e:
        logger.error(f"Error adding relationship to network: {e}")


def render_graph(neo4j_results, height='600px', width='100%'):
    """
    Render an interactive graph in Streamlit.
    
    Args:
        neo4j_results: Results from Neo4j query
        height: Height of the visualization
        width: Width of the visualization
    """
    try:
        html = create_network_graph(neo4j_results, height, width)
        components.html(html, height=int(height.replace('px', '')), scrolling=False)
    except Exception as e:
        logger.error(f"Error rendering graph: {e}")
        import streamlit as st
        st.error(f"Could not render graph: {str(e)}")
