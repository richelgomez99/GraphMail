"""Graph visualization utilities."""

import networkx as nx
import matplotlib.pyplot as plt
from typing import Optional


def visualize_graph(
    graph: nx.DiGraph,
    output_path: Optional[str] = None,
    figsize: tuple = (16, 12)
):
    """Visualize the knowledge graph using matplotlib.
    
    Args:
        graph: NetworkX directed graph
        output_path: Optional path to save figure
        figsize: Figure size (width, height)
    """
    plt.figure(figsize=figsize)
    
    # Position nodes using spring layout
    pos = nx.spring_layout(graph, k=2, iterations=50, seed=42)
    
    # Color nodes by type
    node_colors = []
    for node in graph.nodes():
        node_type = graph.nodes[node].get('node_type', 'Unknown')
        color_map = {
            'Project': '#FF6B6B',      # Red
            'Topic': '#4ECDC4',        # Teal
            'Challenge': '#FFE66D',    # Yellow
            'Resolution': '#95E1D3',   # Green
        }
        node_colors.append(color_map.get(node_type, '#CCCCCC'))
    
    # Draw nodes
    nx.draw_networkx_nodes(
        graph,
        pos,
        node_color=node_colors,
        node_size=3000,
        alpha=0.8
    )
    
    # Draw edges with different colors by type
    edge_colors = []
    for u, v in graph.edges():
        edge_type = graph[u][v].get('edge_type', 'Unknown')
        color_map = {
            'HAS_TOPIC': '#4ECDC4',
            'FACED_CHALLENGE': '#FFE66D',
            'RESOLVED_BY': '#95E1D3',
        }
        edge_colors.append(color_map.get(edge_type, '#CCCCCC'))
    
    nx.draw_networkx_edges(
        graph,
        pos,
        edge_color=edge_colors,
        arrows=True,
        arrowsize=20,
        width=2,
        alpha=0.6
    )
    
    # Draw labels
    labels = {}
    for node in graph.nodes():
        node_data = graph.nodes[node]
        name = node_data.get('name', node_data.get('description', node))
        # Truncate long names
        if len(name) > 30:
            name = name[:27] + '...'
        labels[node] = name
    
    nx.draw_networkx_labels(
        graph,
        pos,
        labels,
        font_size=9,
        font_weight='bold'
    )
    
    # Add title
    plt.title('Project Intelligence Knowledge Graph', fontsize=16, fontweight='bold')
    
    # Add legend
    legend_elements = [
        plt.Line2D([0], [0], marker='o', color='w', label='Project',
                   markerfacecolor='#FF6B6B', markersize=10),
        plt.Line2D([0], [0], marker='o', color='w', label='Topic',
                   markerfacecolor='#4ECDC4', markersize=10),
        plt.Line2D([0], [0], marker='o', color='w', label='Challenge',
                   markerfacecolor='#FFE66D', markersize=10),
        plt.Line2D([0], [0], marker='o', color='w', label='Resolution',
                   markerfacecolor='#95E1D3', markersize=10),
    ]
    plt.legend(handles=legend_elements, loc='upper left', fontsize=10)
    
    plt.axis('off')
    plt.tight_layout()
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"✅ Graph visualization saved to {output_path}")
    else:
        plt.show()


def print_graph_summary(graph: nx.DiGraph):
    """Print a text summary of the graph structure.
    
    Args:
        graph: NetworkX directed graph
    """
    print("\n" + "="*60)
    print("KNOWLEDGE GRAPH SUMMARY")
    print("="*60)
    
    # Node counts by type
    node_types = {}
    for node in graph.nodes():
        node_type = graph.nodes[node].get('node_type', 'Unknown')
        node_types[node_type] = node_types.get(node_type, 0) + 1
    
    print("\nNodes by Type:")
    for node_type, count in sorted(node_types.items()):
        print(f"  {node_type}: {count}")
    
    # Edge counts by type
    edge_types = {}
    for u, v in graph.edges():
        edge_type = graph[u][v].get('edge_type', 'Unknown')
        edge_types[edge_type] = edge_types.get(edge_type, 0) + 1
    
    print("\nEdges by Type:")
    for edge_type, count in sorted(edge_types.items()):
        print(f"  {edge_type}: {count}")
    
    # Projects detail
    print("\nProjects:")
    project_nodes = [n for n in graph.nodes() if graph.nodes[n].get('node_type') == 'Project']
    for node in project_nodes:
        node_data = graph.nodes[node]
        print(f"\n  📁 {node_data.get('name', node)}")
        print(f"     Type: {node_data.get('project_type', 'N/A')}")
        print(f"     Phase: {node_data.get('phase', 'N/A')}")
        
        # Count connected entities
        topics = [n for n in graph.neighbors(node) if graph.nodes[n].get('node_type') == 'Topic']
        challenges = [n for n in graph.neighbors(node) if graph.nodes[n].get('node_type') == 'Challenge']
        
        print(f"     Topics: {len(topics)}")
        print(f"     Challenges: {len(challenges)}")
    
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    # Test with a simple graph
    G = nx.DiGraph()
    
    # Add nodes
    G.add_node('proj_001', node_type='Project', name='Test Project')
    G.add_node('topic_api', node_type='Topic', name='API Integration')
    G.add_node('proj_001_ch_001', node_type='Challenge', description='API Security')
    G.add_node('proj_001_res_001', node_type='Resolution', description='Use OAuth')
    
    # Add edges
    G.add_edge('proj_001', 'topic_api', edge_type='HAS_TOPIC')
    G.add_edge('proj_001', 'proj_001_ch_001', edge_type='FACED_CHALLENGE')
    G.add_edge('proj_001_ch_001', 'proj_001_res_001', edge_type='RESOLVED_BY')
    
    print_graph_summary(G)
    visualize_graph(G, output_path='test_graph.png')
