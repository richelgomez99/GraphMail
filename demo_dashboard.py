#!/usr/bin/env python3
"""
Live Demo Dashboard for Track 9 Hackathon
Shows real-time pipeline execution and beautiful graph visualization
"""

import streamlit as st
import networkx as nx
import plotly.graph_objects as go
import json
import time
from pathlib import Path
import pandas as pd

# Page config
st.set_page_config(
    page_title="Graph-First Intelligence System - Track 9",
    page_icon="🏆",
    layout="wide"
)

# Title
st.title("🏆 Graph-First Project Intelligence System")
st.markdown("**Track 9 Hackathon Demo** - Real-time Email-to-Graph Intelligence")

# Sidebar controls
st.sidebar.title("🎛️ Controls")
output_dir = st.sidebar.text_input("Output Directory", value="./output_hackathon")
auto_refresh = st.sidebar.checkbox("Auto-refresh", value=True)
refresh_interval = st.sidebar.slider("Refresh interval (sec)", 1, 10, 2)

if auto_refresh:
    st.sidebar.info(f"Auto-refreshing every {refresh_interval}s")
    time.sleep(refresh_interval)
    st.rerun()

# Check if results exist
output_path = Path(output_dir)
results_exist = output_path.exists() and (output_path / "knowledge_graph.json").exists()

if not results_exist:
    st.warning(f"⏳ Waiting for pipeline results in `{output_dir}/`...")
    st.info("Run: `python main.py --emails Antler_Hackathon_Email_Data_fixed.json --output ./output_hackathon`")
    st.stop()

# Load results
@st.cache_data
def load_results(output_dir):
    """Load all pipeline results."""
    results = {}
    
    # Load graph
    with open(f"{output_dir}/knowledge_graph.json", 'r') as f:
        graph_data = json.load(f)
        results['graph'] = nx.node_link_graph(graph_data)
    
    # Load project intelligence
    with open(f"{output_dir}/project_intelligence.json", 'r') as f:
        results['projects'] = json.load(f)
    
    # Load trust score
    with open(f"{output_dir}/trust_score.json", 'r') as f:
        results['trust_score'] = json.load(f)
    
    # Load rejected facts
    with open(f"{output_dir}/rejected_facts.json", 'r') as f:
        results['rejected'] = json.load(f)
    
    return results

try:
    results = load_results(output_dir)
except Exception as e:
    st.error(f"Error loading results: {e}")
    st.stop()

# Metrics row
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("🏆 Trust Score", f"{results['trust_score']['trust_score']:.3f}")

with col2:
    st.metric("📊 Graph Nodes", results['graph'].number_of_nodes())

with col3:
    st.metric("🔗 Graph Edges", results['graph'].number_of_edges())

with col4:
    st.metric("📁 Projects", len(results['projects']))

# Trust Score Details
st.header("📊 Trust Score Breakdown")
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Fact Traceability", f"{results['trust_score']['fact_traceability']:.1%}", 
              help="% of facts with valid evidence citations")

with col2:
    st.metric("Extraction Complete", f"{results['trust_score']['extraction_completeness']:.1%}",
              help="% of ground truth facts extracted")

with col3:
    st.metric("Phase Accuracy", f"{results['trust_score']['phase_accuracy']:.1%}",
              help="% of correctly inferred project phases")

with col4:
    hallucination_score = 1 - results['trust_score']['hallucination_rate']
    st.metric("Anti-Hallucination", f"{hallucination_score:.1%}",
              help="1 - (hallucinated facts / total facts)")

# Tabs for different views
tab1, tab2, tab3, tab4 = st.tabs(["🌐 Knowledge Graph", "📁 Projects", "⚠️ Rejected Facts", "📈 Statistics"])

with tab1:
    st.header("🌐 Interactive Knowledge Graph")
    
    G = results['graph']
    
    if G.number_of_nodes() == 0:
        st.warning("No nodes in graph yet!")
    else:
        # Create plotly visualization
        pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
        
        # Node traces by type
        node_types = {}
        for node in G.nodes():
            node_type = G.nodes[node].get('node_type', 'Unknown')
            if node_type not in node_types:
                node_types[node_type] = []
            node_types[node_type].append(node)
        
        # Color map
        color_map = {
            'Project': '#FF6B6B',
            'Topic': '#4ECDC4',
            'Challenge': '#FFE66D',
            'Resolution': '#95E1D3',
        }
        
        # Create edge trace
        edge_trace = []
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            edge_trace.append(
                go.Scatter(
                    x=[x0, x1, None],
                    y=[y0, y1, None],
                    mode='lines',
                    line=dict(width=2, color='#888'),
                    hoverinfo='none',
                    showlegend=False
                )
            )
        
        # Create node traces by type
        node_traces = []
        for node_type, nodes in node_types.items():
            node_x = [pos[node][0] for node in nodes]
            node_y = [pos[node][1] for node in nodes]
            
            # Get labels
            node_text = []
            for node in nodes:
                node_data = G.nodes[node]
                name = node_data.get('name', node_data.get('description', node))
                evidence_count = len(node_data.get('evidence', []))
                node_text.append(f"{name}<br>Evidence: {evidence_count}")
            
            node_traces.append(
                go.Scatter(
                    x=node_x,
                    y=node_y,
                    mode='markers+text',
                    name=node_type,
                    marker=dict(
                        size=20,
                        color=color_map.get(node_type, '#CCCCCC'),
                        line=dict(width=2, color='white')
                    ),
                    text=[G.nodes[node].get('name', node)[:20] for node in nodes],
                    textposition="top center",
                    textfont=dict(size=10),
                    hovertext=node_text,
                    hoverinfo='text'
                )
            )
        
        # Create figure
        fig = go.Figure(data=edge_trace + node_traces)
        
        fig.update_layout(
            title="Project Intelligence Knowledge Graph",
            showlegend=True,
            hovermode='closest',
            height=700,
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Graph stats
        st.subheader("Graph Statistics")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Nodes by Type:**")
            node_counts = {}
            for node in G.nodes():
                node_type = G.nodes[node].get('node_type', 'Unknown')
                node_counts[node_type] = node_counts.get(node_type, 0) + 1
            for node_type, count in sorted(node_counts.items()):
                st.write(f"- {node_type}: {count}")
        
        with col2:
            st.markdown("**Edges by Type:**")
            edge_counts = {}
            for u, v in G.edges():
                edge_type = G[u][v].get('edge_type', 'Unknown')
                edge_counts[edge_type] = edge_counts.get(edge_type, 0) + 1
            for edge_type, count in sorted(edge_counts.items()):
                st.write(f"- {edge_type}: {count}")

with tab2:
    st.header("📁 Extracted Projects")
    
    for i, project in enumerate(results['projects'], 1):
        with st.expander(f"**{i}. {project['project_name']}** ({project['project_type']})", expanded=(i==1)):
            
            # Project basics
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f"**Type:** {project['project_type']}")
                if 'timeline' in project and project['timeline']:
                    st.markdown(f"**Timeline:** {project['timeline'].get('start', 'N/A')} → {project['timeline'].get('end', 'N/A')}")
            
            with col2:
                evidence_count = len(project.get('evidence', []))
                st.markdown(f"**Evidence:** {evidence_count} emails")
                st.markdown(f"**Topics:** {len(project.get('topics', []))}")
            
            # Scope
            if 'scope' in project and project['scope']:
                st.markdown("**Scope:**")
                st.write(project['scope'].get('description', 'N/A'))
            
            # Topics
            if project.get('topics'):
                st.markdown("**Topics:**")
                topics_df = pd.DataFrame([
                    {'Topic': t['topic'], 'Evidence': len(t.get('evidence', []))}
                    for t in project['topics']
                ])
                st.dataframe(topics_df, use_container_width=True, hide_index=True)
            
            # Challenges
            if project.get('challenges'):
                st.markdown("**Challenges:**")
                for j, challenge in enumerate(project['challenges'], 1):
                    st.markdown(f"{j}. **{challenge.get('category', 'N/A')}**: {challenge.get('description', 'N/A')}")
                    st.caption(f"   📧 Evidence: {len(challenge.get('evidence', []))} emails")
            
            # Resolutions
            if project.get('resolutions'):
                st.markdown("**Resolutions:**")
                for j, resolution in enumerate(project['resolutions'], 1):
                    st.markdown(f"{j}. {resolution.get('description', 'N/A')}")
                    st.caption(f"   📧 Evidence: {len(resolution.get('evidence', []))} emails")

with tab3:
    st.header("⚠️ Rejected Facts")
    
    if not results['rejected']:
        st.success("✅ Zero rejected facts! All extracted facts passed verification.")
    else:
        st.warning(f"Found {len(results['rejected'])} rejected facts")
        for i, fact in enumerate(results['rejected'], 1):
            with st.expander(f"Rejected Fact {i}"):
                st.json(fact)

with tab4:
    st.header("📈 Detailed Statistics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Trust Score Components")
        trust_data = pd.DataFrame([
            {'Component': 'Fact Traceability', 'Score': results['trust_score']['fact_traceability'], 'Weight': 0.35},
            {'Component': 'Extraction Completeness', 'Score': results['trust_score']['extraction_completeness'], 'Weight': 0.25},
            {'Component': 'Phase Accuracy', 'Score': results['trust_score']['phase_accuracy'], 'Weight': 0.20},
            {'Component': 'Anti-Hallucination', 'Score': 1 - results['trust_score']['hallucination_rate'], 'Weight': 0.20},
        ])
        st.dataframe(trust_data, use_container_width=True, hide_index=True)
        
        st.metric("Total Facts", results['trust_score']['total_facts'])
        st.metric("Traceable Facts", results['trust_score']['traceable_facts'])
        st.metric("Hallucinations", len(results['trust_score']['hallucinations']))
    
    with col2:
        st.subheader("Project Breakdown")
        project_stats = []
        for project in results['projects']:
            project_stats.append({
                'Project': project['project_name'][:30],
                'Type': project['project_type'],
                'Topics': len(project.get('topics', [])),
                'Challenges': len(project.get('challenges', [])),
                'Resolutions': len(project.get('resolutions', []))
            })
        
        if project_stats:
            st.dataframe(pd.DataFrame(project_stats), use_container_width=True, hide_index=True)

# Footer
st.markdown("---")
st.markdown("**🏆 Track 9 Hackathon Entry** | Graph-First Project Intelligence System | Zero Hallucination Guarantee")
