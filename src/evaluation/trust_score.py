"""Custom evaluation metric: Project Intelligence Trust Score

Formula:
Trust Score = (Fact_Traceability × 0.35) + 
              (Extraction_Completeness × 0.25) + 
              (Phase_Inference_Accuracy × 0.20) +
              (1 - Hallucination_Rate) × 0.20
"""

import networkx as nx
from typing import Dict, List


def calculate_trust_score(
    extracted_graph: nx.DiGraph,
    ground_truth: Dict,
    source_emails: List[Dict]
) -> Dict:
    """Calculate comprehensive Trust Score metric.
    
    Args:
        extracted_graph: The knowledge graph built by Agent 3
        ground_truth: Ground truth annotations (if available)
        source_emails: Original source emails
        
    Returns:
        Dict with trust_score and component metrics
    """
    # 1. Fact Traceability
    fact_traceability = calculate_fact_traceability(extracted_graph, source_emails)
    
    # 2. Extraction Completeness (if ground truth available)
    if ground_truth and 'projects' in ground_truth:
        extraction_completeness = calculate_extraction_completeness(extracted_graph, ground_truth)
        phase_accuracy = calculate_phase_accuracy(extracted_graph, ground_truth)
    else:
        # Estimate based on graph density and coverage
        extraction_completeness = estimate_completeness(extracted_graph, source_emails)
        phase_accuracy = 0.0  # Unknown without ground truth
    
    # 3. Hallucination Detection
    hallucinations = detect_hallucinations(extracted_graph, source_emails)
    total_facts = count_extracted_facts(extracted_graph)
    hallucination_rate = len(hallucinations) / total_facts if total_facts > 0 else 0
    
    # Calculate final Trust Score
    trust_score = (
        fact_traceability * 0.35 +
        extraction_completeness * 0.25 +
        phase_accuracy * 0.20 +
        (1 - hallucination_rate) * 0.20
    )
    
    return {
        'trust_score': round(trust_score, 3),
        'fact_traceability': round(fact_traceability, 3),
        'extraction_completeness': round(extraction_completeness, 3),
        'phase_accuracy': round(phase_accuracy, 3),
        'hallucination_rate': round(hallucination_rate, 3),
        'hallucinations': hallucinations,
        'total_facts': total_facts,
        'traceable_facts': int(total_facts * fact_traceability)
    }


def calculate_fact_traceability(
    graph: nx.DiGraph,
    source_emails: List[Dict]
) -> float:
    """Calculate percentage of facts with valid evidence.
    
    Args:
        graph: Knowledge graph
        source_emails: Source emails for validation
        
    Returns:
        Traceability score (0-1)
    """
    total_facts = 0
    traceable_facts = 0
    
    # Get all message IDs from source
    source_message_ids = set(e['message_id'] for e in source_emails)
    
    # Check nodes
    for node in graph.nodes():
        node_data = graph.nodes[node]
        
        # Each node is a fact
        total_facts += 1
        
        # Check if evidence exists and is valid
        evidence = node_data.get('evidence', [])
        if evidence:
            # Verify at least one evidence ID exists in source
            if any(eid in source_message_ids for eid in evidence):
                traceable_facts += 1
    
    # Check edges (relationships are also facts)
    for u, v in graph.edges():
        edge_data = graph[u][v]
        total_facts += 1
        
        evidence = edge_data.get('evidence', [])
        if evidence:
            if any(eid in source_message_ids for eid in evidence):
                traceable_facts += 1
    
    return traceable_facts / total_facts if total_facts > 0 else 0.0


def calculate_extraction_completeness(
    graph: nx.DiGraph,
    ground_truth: Dict
) -> float:
    """Calculate percentage of ground truth facts extracted.
    
    Args:
        graph: Extracted knowledge graph
        ground_truth: Ground truth annotations
        
    Returns:
        Completeness score (0-1)
    """
    if not ground_truth or 'projects' not in ground_truth:
        return 0.0
    
    gt_facts = count_ground_truth_facts(ground_truth)
    correctly_extracted = count_matching_facts(graph, ground_truth)
    
    return correctly_extracted / gt_facts if gt_facts > 0 else 0.0


def count_ground_truth_facts(ground_truth: Dict) -> int:
    """Count total facts in ground truth."""
    total = 0
    
    for project_id, project in ground_truth.get('projects', {}).items():
        # Project itself
        total += 1
        
        # Topics
        total += len(project.get('topics', []))
        
        # Challenges
        total += len(project.get('challenges', []))
        
        # Resolutions
        total += len(project.get('resolutions', []))
    
    return total


def count_matching_facts(graph: nx.DiGraph, ground_truth: Dict) -> int:
    """Count how many ground truth facts were correctly extracted."""
    matching = 0
    
    # Check projects
    project_nodes = [n for n in graph.nodes() if graph.nodes[n].get('node_type') == 'Project']
    
    for gt_project_id, gt_project in ground_truth.get('projects', {}).items():
        # Find matching project node
        for node in project_nodes:
            node_data = graph.nodes[node]
            gt_name = gt_project.get('project_name', '').lower()
            extracted_name = node_data.get('name', '').lower()
            
            # Simple name matching (could be more sophisticated)
            if gt_name in extracted_name or extracted_name in gt_name:
                matching += 1
                
                # Check topics
                gt_topics = set(t.lower() for t in gt_project.get('topics', []))
                # Get connected topic nodes
                topic_neighbors = [
                    n for n in graph.neighbors(node)
                    if graph.nodes[n].get('node_type') == 'Topic'
                ]
                extracted_topics = set(
                    graph.nodes[t].get('name', '').lower()
                    for t in topic_neighbors
                )
                
                # Count matches
                matching += len(gt_topics & extracted_topics)
                
                break
    
    return matching


def calculate_phase_accuracy(graph: nx.DiGraph, ground_truth: Dict) -> float:
    """Calculate accuracy of phase inference.
    
    Args:
        graph: Extracted knowledge graph
        ground_truth: Ground truth with phase labels
        
    Returns:
        Phase accuracy (0-1)
    """
    project_nodes = [n for n in graph.nodes() if graph.nodes[n].get('node_type') == 'Project']
    
    if not project_nodes:
        return 0.0
    
    correct_phases = 0
    total_projects = 0
    
    for node in project_nodes:
        node_data = graph.nodes[node]
        project_name = node_data.get('name', '').lower()
        extracted_phase = node_data.get('phase', '')
        
        # Find in ground truth
        for gt_project_id, gt_project in ground_truth.get('projects', {}).items():
            gt_name = gt_project.get('project_name', '').lower()
            
            if gt_name in project_name or project_name in gt_name:
                gt_phase = gt_project.get('phase', '')
                if extracted_phase == gt_phase:
                    correct_phases += 1
                total_projects += 1
                break
    
    return correct_phases / total_projects if total_projects > 0 else 0.0


def detect_hallucinations(graph: nx.DiGraph, source_emails: List[Dict]) -> List[Dict]:
    """Detect potential hallucinations (facts without evidence).
    
    Args:
        graph: Knowledge graph
        source_emails: Source emails
        
    Returns:
        List of suspected hallucinations
    """
    hallucinations = []
    source_message_ids = set(e['message_id'] for e in source_emails)
    
    # Check nodes
    for node in graph.nodes():
        node_data = graph.nodes[node]
        evidence = node_data.get('evidence', [])
        
        # No evidence = potential hallucination
        if not evidence:
            hallucinations.append({
                'type': 'node',
                'id': node,
                'node_type': node_data.get('node_type', 'Unknown'),
                'name': node_data.get('name', node_data.get('description', '')),
                'reason': 'No evidence provided'
            })
        else:
            # Invalid evidence IDs = hallucination
            valid_evidence = [eid for eid in evidence if eid in source_message_ids]
            if not valid_evidence:
                hallucinations.append({
                    'type': 'node',
                    'id': node,
                    'node_type': node_data.get('node_type', 'Unknown'),
                    'name': node_data.get('name', node_data.get('description', '')),
                    'reason': 'Evidence IDs not found in source emails',
                    'invalid_evidence': evidence
                })
    
    return hallucinations


def count_extracted_facts(graph: nx.DiGraph) -> int:
    """Count total facts in extracted graph."""
    # Nodes + edges = facts
    return graph.number_of_nodes() + graph.number_of_edges()


def estimate_completeness(graph: nx.DiGraph, source_emails: List[Dict]) -> float:
    """Estimate extraction completeness without ground truth.
    
    Uses heuristics:
    - Number of emails vs number of facts extracted
    - Graph density
    - Coverage of source emails
    
    Args:
        graph: Knowledge graph
        source_emails: Source emails
        
    Returns:
        Estimated completeness (0-1)
    """
    num_emails = len(source_emails)
    num_facts = count_extracted_facts(graph)
    
    # Heuristic: expect ~3-5 facts per email on average
    expected_facts = num_emails * 4
    
    # Calculate coverage
    coverage_ratio = min(num_facts / expected_facts, 1.0) if expected_facts > 0 else 0.0
    
    # Calculate evidence coverage (what % of emails were used as evidence)
    source_message_ids = set(e['message_id'] for e in source_emails)
    used_message_ids = set()
    
    for node in graph.nodes():
        evidence = graph.nodes[node].get('evidence', [])
        used_message_ids.update(evidence)
    
    evidence_coverage = len(used_message_ids & source_message_ids) / len(source_message_ids) if source_message_ids else 0.0
    
    # Weighted average
    estimated_completeness = coverage_ratio * 0.6 + evidence_coverage * 0.4
    
    return estimated_completeness


def print_trust_score_report(metrics: Dict):
    """Print formatted Trust Score report."""
    print("\n" + "="*60)
    print("PROJECT INTELLIGENCE TRUST SCORE REPORT")
    print("="*60)
    print(f"\n🏆 TRUST SCORE: {metrics['trust_score']:.3f}")
    print("\nComponent Scores:")
    print(f"  📊 Fact Traceability:      {metrics['fact_traceability']:.3f} (35% weight)")
    print(f"  📋 Extraction Completeness: {metrics['extraction_completeness']:.3f} (25% weight)")
    print(f"  🎯 Phase Accuracy:         {metrics['phase_accuracy']:.3f} (20% weight)")
    print(f"  ✅ Anti-Hallucination:     {1 - metrics['hallucination_rate']:.3f} (20% weight)")
    print(f"\nFacts Statistics:")
    print(f"  Total Facts Extracted: {metrics['total_facts']}")
    print(f"  Traceable Facts:       {metrics['traceable_facts']}")
    print(f"  Hallucinations:        {len(metrics['hallucinations'])}")
    
    if metrics['hallucinations']:
        print(f"\n⚠️  Suspected Hallucinations:")
        for h in metrics['hallucinations'][:5]:  # Show first 5
            print(f"    - {h['type']}: {h.get('name', h.get('id'))} ({h['reason']})")
    
    print("="*60 + "\n")
