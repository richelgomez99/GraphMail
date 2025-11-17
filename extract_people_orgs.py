#!/usr/bin/env python3
"""
Track 9 Direct Solution: Extract People, Organizations, and Relationships
Every fact traceable to message IDs - no hallucinations
"""

import json
import re
from collections import defaultdict
from datetime import datetime
import networkx as nx

def extract_email_address(text):
    """Extract email from format like 'Name <email@domain.com>'"""
    match = re.search(r'[\w\.-]+@[\w\.-]+', text)
    return match.group(0) if match else None

def extract_name(text):
    """Extract name from format like 'Name <email@domain.com>'"""
    if '<' in text:
        name = text.split('<')[0].strip().replace('"', '')
        return name if name else None
    return None

def extract_organization(email):
    """Extract organization from email domain"""
    if '@' in email:
        domain = email.split('@')[1]
        org = domain.split('.')[0]
        return org
    return None

def build_people_org_graph(email_file):
    """
    Build Track 9 compliant graph:
    - People nodes with attributes
    - Organization nodes
    - Relationship edges with evidence
    """
    
    # Load emails
    with open(email_file, 'r') as f:
        threads = json.load(f)
    
    # Storage
    people = {}  # email -> profile
    organizations = {}  # org_name -> profile
    relationships = defaultdict(lambda: defaultdict(list))  # person1 -> person2 -> [interactions]
    
    # Process all threads
    for thread in threads:
        thread_emails = thread.get('emails', [])
        
        for email_obj in thread_emails:
            message_id = email_obj.get('message_id', f"msg_{hash(str(email_obj))}")
            date = email_obj.get('date', '')
            subject = email_obj.get('subject', '')
            
            # Extract sender
            sender_raw = email_obj.get('from', '')
            sender_email = extract_email_address(sender_raw)
            sender_name = extract_name(sender_raw)
            
            if sender_email:
                # Add/update person
                if sender_email not in people:
                    people[sender_email] = {
                        'email': sender_email,
                        'name': sender_name or sender_email.split('@')[0],
                        'organization': extract_organization(sender_email),
                        'first_seen': date,
                        'last_seen': date,
                        'message_count': 0,
                        'topics': set(),
                        'evidence': []
                    }
                
                people[sender_email]['last_seen'] = date
                people[sender_email]['message_count'] += 1
                people[sender_email]['evidence'].append(message_id)
                
                # Extract topics from subject
                if subject:
                    people[sender_email]['topics'].add(subject.split(':')[0].strip())
                
                # Add organization
                org = extract_organization(sender_email)
                if org and org not in organizations:
                    organizations[org] = {
                        'name': org,
                        'people': set(),
                        'first_seen': date,
                        'last_seen': date,
                        'evidence': []
                    }
                
                if org:
                    organizations[org]['people'].add(sender_email)
                    organizations[org]['last_seen'] = date
                    organizations[org]['evidence'].append(message_id)
            
            # Extract recipients
            recipients = []
            for field in ['to', 'cc']:
                if field in email_obj and email_obj[field]:
                    recip_list = email_obj[field] if isinstance(email_obj[field], list) else [email_obj[field]]
                    for r in recip_list:
                        if r:
                            recip_email = extract_email_address(r)
                            if recip_email:
                                recipients.append(recip_email)
                                
                                # Add recipient as person
                                if recip_email not in people:
                                    recip_name = extract_name(r)
                                    people[recip_email] = {
                                        'email': recip_email,
                                        'name': recip_name or recip_email.split('@')[0],
                                        'organization': extract_organization(recip_email),
                                        'first_seen': date,
                                        'last_seen': date,
                                        'message_count': 0,
                                        'topics': set(),
                                        'evidence': []
                                    }
                                
                                people[recip_email]['evidence'].append(message_id)
            
            # Build relationships: sender -> recipients
            if sender_email:
                for recip in recipients:
                    relationships[sender_email][recip].append({
                        'date': date,
                        'subject': subject,
                        'message_id': message_id
                    })
    
    # Convert sets to lists for JSON serialization
    for person in people.values():
        person['topics'] = list(person['topics'])
    
    for org in organizations.values():
        org['people'] = list(org['people'])
    
    # Build NetworkX graph
    G = nx.DiGraph()
    
    # Add person nodes
    for email, profile in people.items():
        G.add_node(email, 
                   node_type='Person',
                   name=profile['name'],
                   organization=profile['organization'],
                   message_count=profile['message_count'],
                   topics=profile['topics'],
                   evidence=profile['evidence'])
    
    # Add organization nodes
    for org_name, profile in organizations.items():
        G.add_node(f"org_{org_name}",
                   node_type='Organization',
                   name=org_name,
                   people_count=len(profile['people']),
                   evidence=profile['evidence'])
    
    # Add person->org edges
    for email, profile in people.items():
        if profile['organization']:
            G.add_edge(email, f"org_{profile['organization']}",
                      edge_type='WORKS_AT',
                      evidence=profile['evidence'][:5])
    
    # Add person->person relationships
    for sender, recipients in relationships.items():
        for recip, interactions in recipients.items():
            G.add_edge(sender, recip,
                      edge_type='COMMUNICATED_WITH',
                      interaction_count=len(interactions),
                      last_interaction=interactions[-1]['date'] if interactions else None,
                      topics=[i['subject'] for i in interactions[:3]],
                      evidence=[i['message_id'] for i in interactions[:5]])
    
    return {
        'people': people,
        'organizations': organizations,
        'relationships': dict(relationships),
        'graph': G,
        'stats': {
            'total_people': len(people),
            'total_organizations': len(organizations),
            'total_relationships': sum(len(r) for r in relationships.values()),
            'total_messages_analyzed': sum(p['message_count'] for p in people.values())
        }
    }

if __name__ == "__main__":
    print("🔍 Extracting People, Organizations & Relationships...")
    print("=" * 60)
    
    result = build_people_org_graph('Antler_Hackathon_Email_Data_fixed.json')
    
    # Print stats
    print(f"\n📊 EXTRACTION RESULTS:")
    print(f"   People: {result['stats']['total_people']}")
    print(f"   Organizations: {result['stats']['total_organizations']}")
    print(f"   Relationships: {result['stats']['total_relationships']}")
    print(f"   Messages analyzed: {result['stats']['total_messages_analyzed']}")
    
    # Print sample people
    print(f"\n👥 SAMPLE PEOPLE (with evidence):")
    for email, profile in list(result['people'].items())[:5]:
        print(f"\n   {profile['name']}")
        print(f"   Email: {email}")
        print(f"   Organization: {profile['organization']}")
        print(f"   Messages: {profile['message_count']}")
        print(f"   Evidence: {len(profile['evidence'])} message IDs")
        print(f"   Topics: {', '.join(list(profile['topics'])[:3])}")
    
    # Print sample organizations
    print(f"\n🏢 ORGANIZATIONS:")
    for org_name, profile in result['organizations'].items():
        print(f"   {org_name}: {len(profile['people'])} people, {len(profile['evidence'])} messages")
    
    # Save outputs
    print(f"\n💾 Saving results...")
    
    # Save people profiles
    with open('./output_hackathon/people_profiles.json', 'w') as f:
        json.dump(result['people'], f, indent=2)
    
    # Save organization profiles
    with open('./output_hackathon/organizations.json', 'w') as f:
        json.dump(result['organizations'], f, indent=2)
    
    # Save relationship graph
    graph_data = nx.node_link_data(result['graph'])
    with open('./output_hackathon/people_org_graph.json', 'w') as f:
        json.dump(graph_data, f, indent=2)
    
    # Save stats
    with open('./output_hackathon/extraction_stats.json', 'w') as f:
        json.dump(result['stats'], f, indent=2)
    
    print(f"\n✅ COMPLETE! Files saved to ./output_hackathon/")
    print(f"   - people_profiles.json")
    print(f"   - organizations.json")  
    print(f"   - people_org_graph.json")
    print(f"   - extraction_stats.json")
    print("=" * 60)
