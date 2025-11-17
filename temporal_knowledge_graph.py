#!/usr/bin/env python3
"""
TEMPORAL KNOWLEDGE GRAPH - Track 9 Complete Solution
Focus: Time-aware relationships, calendar integration, verifiable facts
"""

import json
import networkx as nx
from datetime import datetime
from collections import defaultdict
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
import re

load_dotenv()

def parse_date(date_str):
    """Parse email date to datetime"""
    try:
        # Common email date format
        return datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S %z')
    except:
        try:
            return datetime.strptime(date_str, '%Y-%m-%d')
        except:
            return None

def extract_email_address(text):
    """Extract email from 'Name <email>' format"""
    if not text:
        return None
    match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', str(text))
    return match.group(0).lower() if match else None

def clean_subject(subject):
    """Remove Re:, Fwd: prefixes"""
    if not subject:
        return None
    cleaned = re.sub(r'^(Re|Fwd|RE|FW|Fw):\s*', '', subject, flags=re.IGNORECASE)
    cleaned = re.sub(r'^(Re|Fwd|RE|FW|Fw):\s*', '', cleaned, flags=re.IGNORECASE)
    return cleaned.strip() if len(cleaned.strip()) > 5 else None

def build_temporal_knowledge_graph(email_data, calendar_data=None):
    """
    Build complete temporal knowledge graph
    Nodes: People, Organizations, Topics, Events
    Edges: COMMUNICATED_AT(time), MET_AT(time), DISCUSSED(topic, time), WORKS_AT
    """
    
    print("🌐 BUILDING TEMPORAL KNOWLEDGE GRAPH")
    print("=" * 70)
    
    G = nx.MultiDiGraph()  # MultiDiGraph to allow multiple edges with timestamps
    
    # Storage for entities
    people = {}
    organizations = set()
    topics = {}
    
    # Process emails for temporal relationships
    print("\n📧 Processing emails...")
    all_emails = []
    for thread in email_data:
        all_emails.extend(thread.get('emails', []))
    
    for email_idx, email in enumerate(all_emails):
        msg_id = email.get('message_id', f"msg_{email_idx}")
        
        # Extract sender
        sender_email = extract_email_address(email.get('from', ''))
        if not sender_email:
            continue
        
        sender_name = email.get('from', '').split('<')[0].strip().replace('"', '') or sender_email.split('@')[0]
        sender_org = sender_email.split('@')[1].split('.')[0] if '@' in sender_email else 'Unknown'
        
        # Skip generic/invalid organizations
        if sender_org.lower() in ['genericemail', 'example', 'test', 'unknown']:
            continue
        
        # Add/update sender node
        if sender_email not in people:
            people[sender_email] = {
                'name': sender_name,
                'email': sender_email,
                'organization': sender_org,
                'first_contact': email.get('date'),
                'last_contact': email.get('date'),
                'message_count': 0,
                'evidence': []
            }
            G.add_node(sender_email,
                      node_type='Person',
                      name=sender_name,
                      organization=sender_org,
                      email=sender_email)
        
        people[sender_email]['message_count'] += 1
        people[sender_email]['last_contact'] = email.get('date')
        people[sender_email]['evidence'].append(msg_id)
        
        # Add organization node
        organizations.add(sender_org)
        org_node = f"org_{sender_org}"
        if not G.has_node(org_node):
            G.add_node(org_node,
                      node_type='Organization',
                      name=sender_org)
        
        # Add WORKS_AT edge
        if not G.has_edge(sender_email, org_node):
            G.add_edge(sender_email, org_node,
                      edge_type='WORKS_AT',
                      evidence=[msg_id])
        
        # Extract recipients
        recipients = []
        for field in ['to', 'cc']:
            recip_list = email.get(field, [])
            if recip_list:
                for r in (recip_list if isinstance(recip_list, list) else [recip_list]):
                    recip_email = extract_email_address(r)
                    if recip_email:
                        recipients.append(recip_email)
                        
                        # Add recipient node
                        if recip_email not in people:
                            recip_name = r.split('<')[0].strip().replace('"', '') or recip_email.split('@')[0]
                            recip_org = recip_email.split('@')[1].split('.')[0] if '@' in recip_email else 'Unknown'
                            
                            people[recip_email] = {
                                'name': recip_name,
                                'email': recip_email,
                                'organization': recip_org,
                                'first_contact': email.get('date'),
                                'last_contact': email.get('date'),
                                'message_count': 0,
                                'evidence': []
                            }
                            G.add_node(recip_email,
                                      node_type='Person',
                                      name=recip_name,
                                      organization=recip_org,
                                      email=recip_email)
        
        # Add temporal COMMUNICATED edges
        email_date = parse_date(email.get('date', ''))
        for recipient in recipients:
            G.add_edge(sender_email, recipient,
                      edge_type='COMMUNICATED',
                      timestamp=email.get('date'),
                      datetime=email_date.isoformat() if email_date else None,
                      subject=clean_subject(email.get('subject')),
                      message_id=msg_id)
        
        # Extract topic and add DISCUSSED edges
        topic = clean_subject(email.get('subject', ''))
        if topic and len(topic) > 10:
            topic_id = f"topic_{hash(topic) % 10000}"
            
            if topic_id not in topics:
                topics[topic_id] = topic
                G.add_node(topic_id,
                          node_type='Topic',
                          name=topic,
                          evidence=[msg_id])
            else:
                if 'evidence' in G.nodes[topic_id]:
                    G.nodes[topic_id]['evidence'].append(msg_id)
            
            # Person DISCUSSED topic at time
            G.add_edge(sender_email, topic_id,
                      edge_type='DISCUSSED',
                      timestamp=email.get('date'),
                      datetime=email_date.isoformat() if email_date else None,
                      message_id=msg_id)
    
    print(f"   ✅ Processed {len(all_emails)} emails")
    print(f"   ✅ Identified {len(people)} people")
    print(f"   ✅ Identified {len(organizations)} organizations")
    print(f"   ✅ Extracted {len(topics)} topics")
    
    # Process calendar events for MET_AT temporal relationships
    if calendar_data:
        print("\n📅 Processing calendar events...")
        
        for event_idx, event in enumerate(calendar_data):
            event_id = f"event_{event_idx}"
            event_summary = event.get('summary', 'Meeting')
            event_start = event.get('start', '')
            
            # Add event node
            G.add_node(event_id,
                      node_type='Event',
                      summary=event_summary,
                      start=event_start,
                      description=event.get('description', ''))
            
            # Extract attendees
            attendees = event.get('attendees', [])
            attendee_emails = [extract_email_address(a) for a in attendees if extract_email_address(a)]
            
            # Add MET_AT edges between all pairs of attendees
            for i, attendee1 in enumerate(attendee_emails):
                if attendee1 in G:
                    # Person attended event
                    G.add_edge(attendee1, event_id,
                              edge_type='ATTENDED',
                              timestamp=event_start,
                              evidence=event.get('uid'))
                    
                    # Person met with other attendees
                    for attendee2 in attendee_emails[i+1:]:
                        if attendee2 in G:
                            G.add_edge(attendee1, attendee2,
                                      edge_type='MET_AT',
                                      timestamp=event_start,
                                      event=event_summary,
                                      evidence=event.get('uid'))
        
        print(f"   ✅ Processed {len(calendar_data)} calendar events")
    
    # Calculate graph statistics
    stats = {
        'total_nodes': G.number_of_nodes(),
        'total_edges': G.number_of_edges(),
        'node_types': {},
        'edge_types': {},
        'temporal_edges': 0
    }
    
    for node in G.nodes():
        node_type = G.nodes[node].get('node_type', 'Unknown')
        stats['node_types'][node_type] = stats['node_types'].get(node_type, 0) + 1
    
    for u, v, data in G.edges(data=True):
        edge_type = data.get('edge_type', 'Unknown')
        stats['edge_types'][edge_type] = stats['edge_types'].get(edge_type, 0) + 1
        if 'timestamp' in data:
            stats['temporal_edges'] += 1
    
    print("\n📊 TEMPORAL KNOWLEDGE GRAPH STATISTICS:")
    print(f"   Nodes: {stats['total_nodes']}")
    for ntype, count in stats['node_types'].items():
        print(f"      {ntype}: {count}")
    print(f"   Edges: {stats['total_edges']}")
    for etype, count in stats['edge_types'].items():
        print(f"      {etype}: {count}")
    print(f"   Temporal edges: {stats['temporal_edges']} (with timestamps)")
    
    return G, people, topics, stats

def save_temporal_knowledge_graph(G, people, topics, stats, output_dir='./output_hackathon'):
    """Save graph and entities"""
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    # Save graph as JSON (node-link format)
    graph_data = nx.node_link_data(G)
    with open(f"{output_dir}/temporal_knowledge_graph.json", 'w') as f:
        json.dump(graph_data, f, indent=2, default=str)
    
    # Save people profiles
    with open(f"{output_dir}/people_profiles_temporal.json", 'w') as f:
        json.dump(people, f, indent=2, default=str)
    
    # Save topics
    with open(f"{output_dir}/topics.json", 'w') as f:
        json.dump(topics, f, indent=2)
    
    # Save statistics
    with open(f"{output_dir}/graph_statistics.json", 'w') as f:
        json.dump(stats, f, indent=2)
    
    print(f"\n💾 SAVED:")
    print(f"   {output_dir}/temporal_knowledge_graph.json")
    print(f"   {output_dir}/people_profiles_temporal.json")
    print(f"   {output_dir}/topics.json")
    print(f"   {output_dir}/graph_statistics.json")

def main():
    # Load email data
    print("📂 Loading data...")
    with open('Antler_Hackathon_Email_Data_fixed.json', 'r') as f:
        email_data = json.load(f)
    
    # Load calendar data
    try:
        with open('Antler_Hackathon_Calendar_Data.json', 'r') as f:
            cal_obj = json.load(f)
            # Extract events array if it's wrapped
            calendar_data = cal_obj.get('events', cal_obj) if isinstance(cal_obj, dict) else cal_obj
    except:
        print("⚠️  Calendar data not found")
        calendar_data = None
    
    # Build temporal knowledge graph
    G, people, topics, stats = build_temporal_knowledge_graph(email_data, calendar_data)
    
    # Save
    save_temporal_knowledge_graph(G, people, topics, stats)
    
    print("\n" + "=" * 70)
    print("✅ TEMPORAL KNOWLEDGE GRAPH COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    main()
