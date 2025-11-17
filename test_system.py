#!/usr/bin/env python3
"""
Test script to validate system components without API calls.
Tests Agent 1 (no LLM needed) and validates structure.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from src.utils.data_loader import load_email_data, load_calendar_data
from src.agents.agent1_parser import agent_1_parser
from src.utils.visualize import print_graph_summary
import networkx as nx


def test_agent1():
    """Test Agent 1: Email Parser & Project Identifier."""
    print("\n" + "="*60)
    print("TESTING AGENT 1: Email Parser & Project Identifier")
    print("="*60 + "\n")
    
    # Load sample data
    print("Loading sample data...")
    raw_emails = load_email_data('./data/sample_emails.json')
    raw_calendar = load_calendar_data('./data/sample_calendar.json')
    
    print(f"Loaded {len(raw_emails)} emails")
    print(f"Loaded {len(raw_calendar)} calendar events\n")
    
    # Create state
    state = {
        'raw_emails': raw_emails,
        'raw_calendar': raw_calendar
    }
    
    # Run Agent 1
    result = agent_1_parser(state)
    
    # Validate results
    assert 'cleaned_emails' in result, "Missing cleaned_emails"
    assert 'project_groups' in result, "Missing project_groups"
    
    cleaned_emails = result['cleaned_emails']
    project_groups = result['project_groups']
    
    print(f"\n✅ Agent 1 Success!")
    print(f"   Cleaned Emails: {len(cleaned_emails)}")
    print(f"   Projects Identified: {len(project_groups)}")
    
    # Show project details
    print("\nProject Groups:")
    for proj_id, proj_data in project_groups.items():
        print(f"\n  {proj_id}:")
        print(f"    Name: {proj_data['project_name']}")
        print(f"    Emails: {len(proj_data['email_ids'])}")
        print(f"    Calendar Events: {len(proj_data.get('calendar_ids', []))}")
    
    return result


def test_graph_structure():
    """Test graph building without LLM."""
    print("\n" + "="*60)
    print("TESTING GRAPH STRUCTURE")
    print("="*60 + "\n")
    
    # Create sample graph
    G = nx.DiGraph()
    
    # Add project node
    G.add_node(
        'project_001',
        node_type='Project',
        name='StartupCo Brand Book',
        project_type='Design/Branding',
        phase='Delivery',
        evidence=['msg_001', 'msg_003']
    )
    
    # Add topic nodes
    G.add_node('topic_api', node_type='Topic', name='API Integration', evidence=['msg_002'])
    G.add_node('topic_brand', node_type='Topic', name='Brand Guidelines', evidence=['msg_001'])
    
    # Add challenge node
    G.add_node(
        'project_001_ch_001',
        node_type='Challenge',
        description='API key security concern',
        category='Technical',
        evidence=['msg_002']
    )
    
    # Add resolution node
    G.add_node(
        'project_001_res_001',
        node_type='Resolution',
        description='Use hosted solution',
        evidence=['msg_003']
    )
    
    # Add edges
    G.add_edge('project_001', 'topic_api', edge_type='HAS_TOPIC')
    G.add_edge('project_001', 'topic_brand', edge_type='HAS_TOPIC')
    G.add_edge('project_001', 'project_001_ch_001', edge_type='FACED_CHALLENGE')
    G.add_edge('project_001_ch_001', 'project_001_res_001', edge_type='RESOLVED_BY')
    
    print("✅ Graph structure created successfully")
    print(f"   Nodes: {G.number_of_nodes()}")
    print(f"   Edges: {G.number_of_edges()}")
    
    print_graph_summary(G)
    
    return G


def test_data_formats():
    """Test that data formats are correct."""
    print("\n" + "="*60)
    print("TESTING DATA FORMATS")
    print("="*60 + "\n")
    
    # Check email format
    emails = load_email_data('./data/sample_emails.json')
    print("✅ Email data loaded")
    
    for email in emails[:2]:
        print(f"\n  Email: {email.get('subject', 'N/A')}")
        assert 'from' in email, "Missing 'from' field"
        assert 'subject' in email, "Missing 'subject' field"
        assert 'date' in email, "Missing 'date' field"
        assert 'body_text' in email, "Missing 'body_text' field"
    
    # Check calendar format
    calendar = load_calendar_data('./data/sample_calendar.json')
    print("\n✅ Calendar data loaded")
    
    for event in calendar:
        print(f"\n  Event: {event.get('summary', 'N/A')}")
        assert 'summary' in event or 'subject' in event, "Missing event name"
    
    print("\n✅ All data formats valid")


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("GRAPH-FIRST PROJECT INTELLIGENCE SYSTEM - TEST SUITE")
    print("="*60)
    
    try:
        # Test 1: Data formats
        test_data_formats()
        
        # Test 2: Agent 1 (no LLM needed)
        agent1_result = test_agent1()
        
        # Test 3: Graph structure
        test_graph_structure()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED")
        print("="*60)
        print("\nSystem is ready! To run the full pipeline with LLM:")
        print("1. Copy .env.example to .env")
        print("2. Add your OPENAI_API_KEY or ANTHROPIC_API_KEY")
        print("3. Run: python main.py --run-sample")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
