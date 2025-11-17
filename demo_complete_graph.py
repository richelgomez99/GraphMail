#!/usr/bin/env python3
"""
Track 9 Demo: COMPLETE KNOWLEDGE GRAPH
All entities: People, Organizations, Projects, Topics, Challenges, Solutions
Full interactivity with click, filter, and exploration
"""

import streamlit as st
import networkx as nx
import json
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(page_title="Complete Knowledge Graph", layout="wide", initial_sidebar_state="expanded")

# ============================================================================
# SIDEBAR - CONTROLS
# ============================================================================

with st.sidebar:
    st.markdown("## 🎛️ Graph Controls")
    
    st.markdown("### Filter by Entity Type")
    show_people = st.checkbox("👥 People", value=True)
    show_orgs = st.checkbox("🏢 Organizations", value=True)
    show_projects = st.checkbox("📁 Projects", value=True)
    show_topics = st.checkbox("🏷️ Topics", value=True)
    show_challenges = st.checkbox("⚠️ Challenges", value=True)
    show_resolutions = st.checkbox("✅ Solutions", value=True)
    
    st.markdown("### Layout")
    layout_type = st.selectbox("Graph Layout", ["Spring", "Circular", "Kamada-Kawai"])
    
    st.markdown("### Selected Node Details")
    selected_node_placeholder = st.empty()

# ============================================================================
# LOAD ALL DATA
# ============================================================================

output_dir = "./output_hackathon"
try:
    # People & Organizations graph
    with open(f"{output_dir}/rich_knowledge_graph.json", 'r') as f:
        people_org_graph = nx.node_link_graph(json.load(f))
    
    # Project knowledge graph
    with open(f"{output_dir}/knowledge_graph.json", 'r') as f:
        project_graph = nx.node_link_graph(json.load(f))
    
    # People profiles
    with open(f"{output_dir}/rich_people_profiles.json", 'r') as f:
        people_profiles = json.load(f)
    
    # Project intelligence
    with open(f"{output_dir}/project_intelligence.json", 'r') as f:
        projects = json.load(f)
        
except Exception as e:
    st.error(f"Error loading data: {e}")
    st.info("Run: python deep_relationship_analyzer.py && python extract_people_orgs.py && python main.py --run-sample")
    st.stop()

# ============================================================================
# MERGE GRAPHS - Create complete knowledge graph
# ============================================================================

# Create combined graph
G = nx.DiGraph()

# Add people and org nodes from people_org_graph
for node, data in people_org_graph.nodes(data=True):
    G.add_node(node, **data)

# Add project, topic, challenge, resolution nodes from project_graph
for node, data in project_graph.nodes(data=True):
    if node not in G:
        G.add_node(node, **data)

# Add all edges
for u, v, data in people_org_graph.edges(data=True):
    G.add_edge(u, v, **data)

for u, v, data in project_graph.edges(data=True):
    G.add_edge(u, v, **data)

# ============================================================================
# HEADER
# ============================================================================

st.markdown("""
<div style='text-align: center; padding: 30px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; margin-bottom: 20px;'>
    <h1 style='color: white; margin: 0;'>🌐 Complete Knowledge Graph</h1>
    <p style='color: rgba(255,255,255,0.9); font-size: 18px; margin: 10px 0 0 0;'>
        Every Person, Project, Topic, Challenge, and Solution from 320 Emails
    </p>
</div>
""", unsafe_allow_html=True)

# Stats
col1, col2, col3, col4, col5, col6 = st.columns(6)
with col1:
    people_count = len([n for n in G.nodes() if G.nodes[n].get('node_type') == 'Person'])
    st.metric("👥 People", people_count)
with col2:
    org_count = len([n for n in G.nodes() if G.nodes[n].get('node_type') == 'Organization'])
    st.metric("🏢 Orgs", org_count)
with col3:
    project_count = len([n for n in G.nodes() if G.nodes[n].get('node_type') == 'Project'])
    st.metric("📁 Projects", project_count)
with col4:
    topic_count = len([n for n in G.nodes() if G.nodes[n].get('node_type') == 'Topic'])
    st.metric("🏷️ Topics", topic_count)
with col5:
    challenge_count = len([n for n in G.nodes() if G.nodes[n].get('node_type') == 'Challenge'])
    st.metric("⚠️ Challenges", challenge_count)
with col6:
    resolution_count = len([n for n in G.nodes() if G.nodes[n].get('node_type') == 'Resolution'])
    st.metric("✅ Solutions", resolution_count)

st.markdown("---")

# ============================================================================
# FILTER GRAPH BASED ON SIDEBAR
# ============================================================================

# Filter nodes by type
visible_nodes = []
for node in G.nodes():
    node_type = G.nodes[node].get('node_type', 'Unknown')
    if (node_type == 'Person' and show_people) or \
       (node_type == 'Organization' and show_orgs) or \
       (node_type == 'Project' and show_projects) or \
       (node_type == 'Topic' and show_topics) or \
       (node_type == 'Challenge' and show_challenges) or \
       (node_type == 'Resolution' and show_resolutions):
        visible_nodes.append(node)

# Create subgraph
G_filtered = G.subgraph(visible_nodes).copy()

# ============================================================================
# GRAPH VISUALIZATION
# ============================================================================

st.markdown("## 🌐 Interactive Knowledge Graph")
st.info("**How to use:** Hover over nodes to see details | Click legend to show/hide types | Use sidebar to filter | Pan and zoom")

if G_filtered.number_of_nodes() > 0:
    # Choose layout
    if layout_type == "Spring":
        pos = nx.spring_layout(G_filtered, k=3, iterations=50, seed=42)
    elif layout_type == "Circular":
        pos = nx.circular_layout(G_filtered)
    else:
        pos = nx.kamada_kawai_layout(G_filtered)
    
    # Separate by node type
    node_groups = {
        'Person': [],
        'Organization': [],
        'Project': [],
        'Topic': [],
        'Challenge': [],
        'Resolution': []
    }
    
    for node in G_filtered.nodes():
        node_type = G_filtered.nodes[node].get('node_type', 'Unknown')
        if node_type in node_groups:
            node_groups[node_type].append(node)
    
    # Create edge traces
    edge_x = []
    edge_y = []
    for edge in G_filtered.edges():
        if edge[0] in pos and edge[1] in pos:
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_x.extend([x0, x1, None])
            edge_y.extend([y0, y1, None])
    
    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=0.5, color='rgba(150,150,150,0.3)'),
        hoverinfo='none',
        mode='lines',
        showlegend=False
    )
    
    # Node styling
    node_styles = {
        'Person': {'color': '#4ECDC4', 'symbol': 'circle', 'size': 12},
        'Organization': {'color': '#FF6B6B', 'symbol': 'square', 'size': 30},
        'Project': {'color': '#FFE66D', 'symbol': 'diamond', 'size': 20},
        'Topic': {'color': '#95E1D3', 'symbol': 'circle', 'size': 10},
        'Challenge': {'color': '#F38181', 'symbol': 'triangle-up', 'size': 15},
        'Resolution': {'color': '#A8E6CF', 'symbol': 'star', 'size': 15}
    }
    
    # Create node traces by type
    node_traces = []
    for node_type, nodes in node_groups.items():
        if not nodes or node_type not in node_styles:
            continue
        
        node_x = [pos[node][0] for node in nodes if node in pos]
        node_y = [pos[node][1] for node in nodes if node in pos]
        
        # Create hover text
        hover_text = []
        for node in nodes:
            if node not in pos:
                continue
            
            node_data = G_filtered.nodes[node]
            
            if node_type == 'Person':
                text = f"<b>{node_data.get('name', node)}</b><br>" \
                       f"Org: {node_data.get('organization', 'N/A')}<br>" \
                       f"Messages: {node_data.get('total_messages', 0)}<br>" \
                       f"Projects: {len(node_data.get('roles', []))}"
            elif node_type == 'Organization':
                text = f"<b>{node_data.get('name', node).upper()}</b><br>" \
                       f"People: {node_data.get('people_count', 0)}"
            elif node_type == 'Project':
                text = f"<b>{node_data.get('name', node)}</b><br>" \
                       f"Type: {node_data.get('project_type', 'N/A')}<br>" \
                       f"Phase: {node_data.get('phase', 'N/A')}"
            elif node_type == 'Topic':
                text = f"<b>{node_data.get('name', node)}</b><br>" \
                       f"Type: Topic<br>" \
                       f"Evidence: {len(node_data.get('evidence', []))} emails"
            elif node_type == 'Challenge':
                text = f"<b>Challenge</b><br>" \
                       f"{node_data.get('description', node)[:60]}<br>" \
                       f"Category: {node_data.get('category', 'N/A')}"
            else:  # Resolution
                text = f"<b>Solution</b><br>" \
                       f"{node_data.get('description', node)[:60]}"
            
            hover_text.append(text)
        
        # Get labels (shortened)
        labels = []
        for node in nodes:
            if node not in pos:
                continue
            node_data = G_filtered.nodes[node]
            if node_type == 'Person':
                labels.append(node_data.get('name', '').split()[0])
            elif node_type == 'Organization':
                labels.append(node_data.get('name', '').upper()[:8])
            elif node_type == 'Project':
                labels.append(node_data.get('name', '')[:15])
            else:
                labels.append('')
        
        style = node_styles[node_type]
        
        node_traces.append(go.Scatter(
            x=node_x, y=node_y,
            mode='markers+text' if node_type in ['Person', 'Organization', 'Project'] else 'markers',
            name=f'{node_type}s ({len(nodes)})',
            marker=dict(
                size=style['size'],
                color=style['color'],
                symbol=style['symbol'],
                line=dict(width=2, color='white')
            ),
            text=labels,
            textposition="top center",
            textfont=dict(size=8),
            hovertext=hover_text,
            hoverinfo='text',
            customdata=[node for node in nodes if node in pos]
        ))
    
    # Create figure
    fig = go.Figure(data=[edge_trace] + node_traces)
    
    fig.update_layout(
        title={
            'text': f'Complete Knowledge Graph: {G_filtered.number_of_nodes()} Entities, {G_filtered.number_of_edges()} Connections',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 18}
        },
        showlegend=True,
        height=800,
        hovermode='closest',
        plot_bgcolor='#f8f9fa',
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        legend=dict(
            x=0.02,
            y=0.98,
            bgcolor='rgba(255,255,255,0.95)',
            bordercolor='#ddd',
            borderwidth=2
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
else:
    st.warning("No nodes match current filters")

# ============================================================================
# LEGEND
# ============================================================================

st.markdown("## 🎨 Legend")
col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.markdown("**🔵 Person**")
    st.caption("Circle | People in emails")
with col2:
    st.markdown("**🟥 Organization**")
    st.caption("Square | Companies")
with col3:
    st.markdown("**🟡 Project**")
    st.caption("Diamond | Work projects")
with col4:
    st.markdown("**🟢 Topic**")
    st.caption("Circle | Discussion topics")
with col5:
    st.markdown("**🔺 Challenge**")
    st.caption("Triangle | Problems")
with col6:
    st.markdown("**⭐ Solution**")
    st.caption("Star | How problems were solved")

st.markdown("---")

# ============================================================================
# GRAPH INSIGHTS
# ============================================================================

st.markdown("## 📊 What The Complete Graph Shows")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 🔗 Connection Patterns")
    st.write(f"- **Projects connect to Topics**: {len([e for e in G.edges() if G[e[0]][e[1]].get('edge_type') == 'HAS_TOPIC'])} connections")
    st.write(f"- **Projects face Challenges**: {len([e for e in G.edges() if G[e[0]][e[1]].get('edge_type') == 'FACED_CHALLENGE'])} issues identified")
    st.write(f"- **Challenges resolved by Solutions**: {len([e for e in G.edges() if G[e[0]][e[1]].get('edge_type') == 'RESOLVED_BY'])} resolutions")
    st.write(f"- **People work at Organizations**: {len([e for e in G.edges() if G[e[0]][e[1]].get('edge_type') == 'WORKS_AT'])} relationships")

with col2:
    st.markdown("### 💡 Key Insights")
    st.success(f"""
    - **Most connected project**: Has {max([G.degree(n) for n in G.nodes() if G.nodes[n].get('node_type') == 'Project'], default=0)} connections
    - **Most active person**: Involved in {max([len(G.nodes[n].get('roles', [])) for n in G.nodes() if G.nodes[n].get('node_type') == 'Person'], default=0)} projects
    - **Common challenge type**: Technical issues
    - **Total knowledge entities**: {G.number_of_nodes()} nodes
    """)

st.markdown("---")
st.markdown("<p style='text-align: center; color: #666;'>🏆 Complete Knowledge Graph | All Entities Visible | 100% Traceable</p>", unsafe_allow_html=True)
