"""LangGraph workflow orchestration for Graph-First Project Intelligence System.

Three-Agent Sequential Pipeline:
  Agent 1: Email Parser & Project Identifier
     ↓
  Agent 2: Project Intelligence Extractor  
     ↓
  Agent 3: Verification & Graph Builder
     ↓
  OUTPUT: Verified Knowledge Graph + Trust Score
"""

from langgraph.graph import StateGraph, END
from typing import Dict
import sys
import os

# Add src to path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.models.schema import ProjectGraphState
from src.agents.agent1_parser import agent_1_parser
from src.agents.agent2_extractor import agent_2_extractor
from src.agents.agent3_verifier import agent_3_verifier
from src.evaluation.trust_score import calculate_trust_score, print_trust_score_report
from src.logging import get_logger, set_correlation_id, generate_correlation_id

logger = get_logger(__name__)


def build_workflow() -> StateGraph:
    """Build the LangGraph workflow.
    
    Returns:
        Compiled StateGraph
    """
    # Create state graph
    workflow = StateGraph(ProjectGraphState)
    
    # Add nodes (agents)
    workflow.add_node("parse", agent_1_parser)
    workflow.add_node("extract", agent_2_extractor)
    workflow.add_node("verify", agent_3_verifier)
    workflow.add_node("evaluate", evaluation_node)
    
    # Define edges (flow)
    workflow.set_entry_point("parse")
    workflow.add_edge("parse", "extract")
    workflow.add_edge("extract", "verify")
    workflow.add_edge("verify", "evaluate")
    workflow.add_edge("evaluate", END)
    
    # Compile
    return workflow.compile()


def evaluation_node(state: Dict) -> Dict:
    """Evaluation node: Calculate Trust Score.
    
    Args:
        state: ProjectGraphState dict
        
    Returns:
        Updated state with evaluation_metrics
    """
    logger.info("evaluation.started",
                 graph_nodes=state['verified_graph'].number_of_nodes(),
                 graph_edges=state['verified_graph'].number_of_edges())
    
    # Calculate metrics
    metrics = calculate_trust_score(
        extracted_graph=state['verified_graph'],
        ground_truth={},  # Load ground truth if available
        source_emails=state['cleaned_emails']
    )
    
    # Print report
    print_trust_score_report(metrics)
    
    return {"evaluation_metrics": metrics}


def run_pipeline(
    raw_emails: list,
    raw_calendar: list = None,
    verbose: bool = True
) -> Dict:
    """Run the complete pipeline.
    
    Args:
        raw_emails: List of email threads
        raw_calendar: Optional calendar events
        verbose: Print progress
        
    Returns:
        Final state with graph and metrics
    """
    # Generate correlation ID for this pipeline run
    from src.logging import set_correlation_id, generate_correlation_id
    correlation_id = generate_correlation_id()
    set_correlation_id(correlation_id)

    logger.info("pipeline.started",
                correlation_id=correlation_id,
                email_count=len(raw_emails),
                has_calendar=bool(raw_calendar))

    if verbose:
        print("\n" + "="*60)
        print("GRAPH-FIRST PROJECT INTELLIGENCE SYSTEM")
        print("="*60 + "\n")
    
    # Build workflow
    graph_system = build_workflow()
    
    # Prepare input
    input_state = {
        "raw_emails": raw_emails,
        "raw_calendar": raw_calendar or []
    }
    
    # Run pipeline
    result = graph_system.invoke(input_state)
    
    logger.info("pipeline.complete",
                correlation_id=correlation_id,
                projects_extracted=len(result.get('project_intelligence', [])),
                graph_nodes=result['verified_graph'].number_of_nodes(),
                graph_edges=result['verified_graph'].number_of_edges(),
                rejected_facts=len(result['rejected_facts']),
                trust_score=result['evaluation_metrics']['trust_score'])

    if verbose:
        print("\n" + "="*60)
        print("PIPELINE COMPLETE")
        print("="*60)
        print(f"Projects Extracted:    {len(result.get('project_intelligence', []))}")
        print(f"Graph Nodes:           {result['verified_graph'].number_of_nodes()}")
        print(f"Graph Edges:           {result['verified_graph'].number_of_edges()}")
        print(f"Rejected Facts:        {len(result['rejected_facts'])}")
        print(f"Trust Score:           {result['evaluation_metrics']['trust_score']:.3f}")
        print("="*60 + "\n")
    
    return result


def save_results(result: Dict, output_dir: str = "./output"):
    """Save pipeline results to files.
    
    Args:
        result: Pipeline output
        output_dir: Directory to save files
    """
    import os
    import json
    import networkx as nx
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Save graph as JSON
    with open(f"{output_dir}/knowledge_graph.json", 'w') as f:
        json.dump(result['graph_json'], f, indent=2)
    
    # Save graph as GraphML (skip if dict attributes present)
    try:
        nx.write_graphml(result['verified_graph'], f"{output_dir}/knowledge_graph.graphml")
    except TypeError:
        logger.warning("results.graphml_export_skipped",
                      reason="dict attributes not supported")
        print("⚠️  GraphML export skipped (dict attributes not supported)")
    
    # Save project intelligence
    with open(f"{output_dir}/project_intelligence.json", 'w') as f:
        json.dump(result['project_intelligence'], f, indent=2)
    
    # Save rejected facts
    with open(f"{output_dir}/rejected_facts.json", 'w') as f:
        json.dump(result['rejected_facts'], f, indent=2)
    
    # Save evaluation metrics
    with open(f"{output_dir}/trust_score.json", 'w') as f:
        json.dump(result['evaluation_metrics'], f, indent=2)
    
    logger.info("results.saved", output_dir=output_dir)
    print(f"✅ Results saved to {output_dir}/")


if __name__ == "__main__":
    # Test with sample data
    sample_emails = [
        {
            'from': 'sage.harris@consultingco.com',
            'to': ['jamie.adams@startupco.com'],
            'subject': 'StartupCo Brand Book - Project Kickoff',
            'date': '2026-03-25',
            'body_text': '''Hi Jamie,

Great to connect yesterday! I'm excited to work on the StartupCo Online Brand Book project.

Based on our discussion, here's what I understand:
- Scope: Create an online brand book with API access for dynamic content
- Timeline: 4 weeks (deliver by April 22)
- Key deliverables: Brand guidelines, color palette, typography system, logo usage

Let me know if I missed anything!

Best,
Sage'''
        },
        {
            'from': 'jamie.adams@startupco.com',
            'to': ['sage.harris@consultingco.com'],
            'subject': 'Re: StartupCo Brand Book - Project Kickoff',
            'date': '2026-03-26',
            'body_text': '''Hi Sage,

Looks good! One concern: I'm not sure about sharing our API keys for the integration. 
Could we explore other options?

Thanks,
Jamie'''
        },
        {
            'from': 'sage.harris@consultingco.com',
            'to': ['jamie.adams@startupco.com'],
            'subject': 'Re: StartupCo Brand Book - API Solution',
            'date': '2026-03-27',
            'body_text': '''Jamie,

Great question. Instead of direct API integration, we can use a hosted solution. 
This way you don't need to share credentials and we get better security.

Sound good?

Sage'''
        }
    ]
    
    logger.info("demo.test_started")
    print("Running test with sample emails...")
    result = run_pipeline(sample_emails, verbose=True)
