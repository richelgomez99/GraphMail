#!/usr/bin/env python3
"""
Deep Relationship Intelligence Analyzer
Extracts rich profiles, roles, timelines, and communication patterns
"""

import json
import re
from collections import defaultdict
from datetime import datetime
import networkx as nx
from langchain_openai import ChatOpenAI
import os

def parse_date(date_str):
    """Parse various date formats"""
    try:
        # Try common formats
        for fmt in ['%a, %d %b %Y %H:%M:%S %z', '%Y-%m-%d', '%Y-%m-%dT%H:%M:%S']:
            try:
                return datetime.strptime(date_str, fmt)
            except:
                continue
        return None
    except:
        return None

def extract_email_address(text):
    """Extract email from format like 'Name <email@domain.com>'"""
    if not text:
        return None
    match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', str(text))
    return match.group(0).lower() if match else None

def infer_role_from_context(person_email, thread_emails, organizations):
    """Infer person's role in project based on communication patterns"""
    person_org = None
    for org_name, org_data in organizations.items():
        if person_email in org_data.get('people', []):
            person_org = org_name
            break
    
    # Count behaviors
    initiated_count = 0
    responded_count = 0
    cc_count = 0
    
    for email in thread_emails:
        sender = extract_email_address(email.get('from', ''))
        
        if sender == person_email:
            # Check if initiating or responding
            subject = email.get('subject', '')
            if subject.startswith('Re:') or subject.startswith('Fwd:'):
                responded_count += 1
            else:
                initiated_count += 1
        
        # Check if CC'd
        cc_list = email.get('cc', [])
        if cc_list:
            cc_emails = [extract_email_address(c) for c in (cc_list if isinstance(cc_list, list) else [cc_list])]
            if person_email in cc_emails:
                cc_count += 1
    
    # Infer role
    if initiated_count > responded_count * 2:
        role = "Project Lead" if person_org and "Consulting" in person_org else "Client Lead"
    elif cc_count > (initiated_count + responded_count):
        role = "Support/Observer"
    elif responded_count > initiated_count:
        role = "Collaborator"
    else:
        role = "Team Member"
    
    return role

def analyze_meeting_type(event, people_orgs):
    """Determine if meeting is internal or cross-team"""
    attendees = event.get('attendees', [])
    attendee_emails = [extract_email_address(a) for a in attendees if extract_email_address(a)]
    
    # Get organizations
    orgs = set()
    for email in attendee_emails:
        for org_name, org_data in people_orgs.items():
            if email in org_data.get('people', []):
                orgs.add(org_name)
    
    if len(orgs) <= 1:
        return "Internal"
    else:
        return "Cross-Team"

def extract_communication_timeline(emails, person_email):
    """Extract timeline of person's communications"""
    timeline = []
    
    for email in emails:
        sender = extract_email_address(email.get('from', ''))
        date_obj = parse_date(email.get('date', ''))
        
        if sender == person_email and date_obj:
            timeline.append({
                'date': date_obj.isoformat(),
                'subject': email.get('subject', '')[:50],
                'type': 'sent',
                'message_id': email.get('message_id', '')
            })
        else:
            # Check if received
            to_list = email.get('to', [])
            if to_list:
                to_emails = [extract_email_address(t) for t in (to_list if isinstance(to_list, list) else [to_list])]
                if person_email in to_emails and date_obj:
                    timeline.append({
                        'date': date_obj.isoformat(),
                        'subject': email.get('subject', '')[:50],
                        'type': 'received',
                        'from': sender,
                        'message_id': email.get('message_id', '')
                    })
    
    # Sort by date
    timeline.sort(key=lambda x: x['date'])
    return timeline

def build_rich_relationship_graph(email_file, calendar_file=None):
    """Build comprehensive relationship graph with roles, timelines, and patterns"""
    
    print("📧 Loading emails...")
    with open(email_file, 'r') as f:
        threads = json.load(f)
    
    # Initialize storage
    people_profiles = {}
    organizations = {}
    project_roles = defaultdict(lambda: defaultdict(str))  # project_id -> person -> role
    meeting_patterns = defaultdict(list)  # person -> [meetings]
    communication_timeline = defaultdict(list)  # person -> timeline
    
    all_emails = []
    for thread in threads:
        all_emails.extend(thread.get('emails', []))
    
    print("🔍 First pass: Extracting people and organizations...")
    
    # First pass: identify all people and orgs
    for thread in threads:
        for email in thread.get('emails', []):
            # Extract sender
            sender_email = extract_email_address(email.get('from', ''))
            if sender_email and sender_email not in people_profiles:
                name = email.get('from', '').split('<')[0].strip().replace('"', '') or sender_email.split('@')[0]
                org = sender_email.split('@')[1].split('.')[0] if '@' in sender_email else 'Unknown'
                
                people_profiles[sender_email] = {
                    'email': sender_email,
                    'name': name,
                    'organization': org,
                    'messages_sent': 0,
                    'messages_received': 0,
                    'topics': set(),
                    'communication_pattern': [],
                    'roles': {},  # project -> role
                    'evidence': [],
                    'first_contact': None,
                    'last_contact': None
                }
                
                if org not in organizations:
                    organizations[org] = {
                        'name': org,
                        'people': set(),
                        'evidence': []
                    }
                organizations[org]['people'].add(sender_email)
            
            # Extract recipients
            for field in ['to', 'cc']:
                recip_list = email.get(field, [])
                if recip_list:
                    for recip in (recip_list if isinstance(recip_list, list) else [recip_list]):
                        recip_email = extract_email_address(recip)
                        if recip_email and recip_email not in people_profiles:
                            name = recip.split('<')[0].strip().replace('"', '') or recip_email.split('@')[0]
                            org = recip_email.split('@')[1].split('.')[0] if '@' in recip_email else 'Unknown'
                            
                            people_profiles[recip_email] = {
                                'email': recip_email,
                                'name': name,
                                'organization': org,
                                'messages_sent': 0,
                                'messages_received': 0,
                                'topics': set(),
                                'communication_pattern': [],
                                'roles': {},
                                'evidence': [],
                                'first_contact': None,
                                'last_contact': None
                            }
                            
                            if org not in organizations:
                                organizations[org] = {
                                    'name': org,
                                    'people': set(),
                                    'evidence': []
                                }
                            organizations[org]['people'].add(recip_email)
    
    print(f"   Found {len(people_profiles)} people across {len(organizations)} organizations")
    
    print("🎭 Second pass: Analyzing roles and patterns...")
    
    # Second pass: analyze each thread for roles and patterns
    for thread_idx, thread in enumerate(threads):
        thread_emails = thread.get('emails', [])
        project_id = f"project_{thread_idx}"
        
        # Infer project from subject
        first_subject = thread_emails[0].get('subject', '') if thread_emails else ''
        
        # Analyze each person's role in this thread
        thread_participants = set()
        for email in thread_emails:
            sender = extract_email_address(email.get('from', ''))
            if sender:
                thread_participants.add(sender)
            
            for field in ['to', 'cc']:
                recips = email.get(field, [])
                if recips:
                    for r in (recips if isinstance(recips, list) else [recips]):
                        recip_email = extract_email_address(r)
                        if recip_email:
                            thread_participants.add(recip_email)
        
        # Assign roles
        for person in thread_participants:
            if person in people_profiles:
                role = infer_role_from_context(person, thread_emails, organizations)
                people_profiles[person]['roles'][project_id] = role
                project_roles[project_id][person] = role
        
        # Update message counts and topics
        for email in thread_emails:
            msg_id = email.get('message_id', f"msg_{hash(str(email))}")
            sender = extract_email_address(email.get('from', ''))
            subject = email.get('subject', '')
            date = email.get('date', '')
            
            if sender and sender in people_profiles:
                people_profiles[sender]['messages_sent'] += 1
                people_profiles[sender]['evidence'].append(msg_id)
                
                # Extract topic
                topic = subject.split(':')[0].replace('Re:', '').replace('Fwd:', '').strip()
                if topic:
                    people_profiles[sender]['topics'].add(topic)
                
                # Update dates
                date_obj = parse_date(date)
                if date_obj:
                    if not people_profiles[sender]['first_contact']:
                        people_profiles[sender]['first_contact'] = date
                    people_profiles[sender]['last_contact'] = date
            
            # Recipients
            for field in ['to', 'cc']:
                recips = email.get(field, [])
                if recips:
                    for r in (recips if isinstance(recips, list) else [recips]):
                        recip_email = extract_email_address(r)
                        if recip_email and recip_email in people_profiles:
                            people_profiles[recip_email]['messages_received'] += 1
    
    print("📅 Building communication timelines...")
    
    # Build timelines
    for person_email in people_profiles:
        timeline = extract_communication_timeline(all_emails, person_email)
        communication_timeline[person_email] = timeline
    
    print("🤝 Analyzing meeting patterns...")
    
    # Analyze calendar if available
    if calendar_file:
        try:
            with open(calendar_file, 'r') as f:
                calendar_events = json.load(f)
            
            for event in calendar_events:
                attendees = event.get('attendees', [])
                attendee_emails = [extract_email_address(a) for a in attendees]
                
                meeting_type = analyze_meeting_type(event, organizations)
                
                for attendee in attendee_emails:
                    if attendee and attendee in people_profiles:
                        meeting_patterns[attendee].append({
                            'summary': event.get('summary', ''),
                            'start': event.get('start', ''),
                            'type': meeting_type,
                            'attendee_count': len(attendee_emails)
                        })
        except:
            print("   Calendar file not found or invalid")
    
    # Convert sets to lists for JSON
    for profile in people_profiles.values():
        profile['topics'] = list(profile['topics'])
    
    for org in organizations.values():
        org['people'] = list(org['people'])
    
    # Build NetworkX graph
    print("🌐 Building knowledge graph...")
    G = nx.DiGraph()
    
    # Add person nodes with rich attributes
    for email, profile in people_profiles.items():
        G.add_node(email,
                   node_type='Person',
                   name=profile['name'],
                   organization=profile['organization'],
                   messages_sent=profile['messages_sent'],
                   messages_received=profile['messages_received'],
                   total_messages=profile['messages_sent'] + profile['messages_received'],
                   topics=profile['topics'],
                   roles=list(profile['roles'].values()),
                   evidence=profile['evidence'][:10])
    
    # Add organization nodes
    for org_name, org_data in organizations.items():
        G.add_node(f"org_{org_name}",
                   node_type='Organization',
                   name=org_name,
                   people_count=len(org_data['people']))
    
    # Add WORKS_AT edges
    for email, profile in people_profiles.items():
        G.add_edge(email, f"org_{profile['organization']}",
                  edge_type='WORKS_AT')
    
    # Add communication edges
    for thread in threads:
        for email in thread.get('emails', []):
            sender = extract_email_address(email.get('from', ''))
            
            for field in ['to', 'cc']:
                recips = email.get(field, [])
                if recips:
                    for r in (recips if isinstance(recips, list) else [recips]):
                        recip = extract_email_address(r)
                        if sender and recip and sender in G and recip in G:
                            if G.has_edge(sender, recip):
                                G[sender][recip]['weight'] += 1
                            else:
                                G.add_edge(sender, recip,
                                          edge_type='COMMUNICATED_WITH',
                                          weight=1)
    
    return {
        'people': people_profiles,
        'organizations': organizations,
        'project_roles': dict(project_roles),
        'meeting_patterns': dict(meeting_patterns),
        'communication_timeline': dict(communication_timeline),
        'graph': G,
        'stats': {
            'total_people': len(people_profiles),
            'total_organizations': len(organizations),
            'total_projects': len(project_roles),
            'avg_messages_per_person': sum(p['messages_sent'] + p['messages_received'] for p in people_profiles.values()) / len(people_profiles)
        }
    }

if __name__ == "__main__":
    print("🔬 DEEP RELATIONSHIP INTELLIGENCE ANALYZER")
    print("=" * 70)
    
    result = build_rich_relationship_graph(
        'Antler_Hackathon_Email_Data_fixed.json',
        'Antler_Hackathon_Calendar_Data.json'
    )
    
    print(f"\n📊 ANALYSIS COMPLETE:")
    print(f"   People: {result['stats']['total_people']}")
    print(f"   Organizations: {result['stats']['total_organizations']}")
    print(f"   Projects analyzed: {result['stats']['total_projects']}")
    print(f"   Avg messages/person: {result['stats']['avg_messages_per_person']:.1f}")
    
    # Show rich profile example
    print(f"\n👤 SAMPLE RICH PROFILE:")
    sample_person = list(result['people'].values())[0]
    print(f"   Name: {sample_person['name']}")
    print(f"   Organization: {sample_person['organization']}")
    print(f"   Messages: {sample_person['messages_sent']} sent, {sample_person['messages_received']} received")
    print(f"   Topics: {', '.join(sample_person['topics'][:3])}")
    print(f"   Roles: {', '.join(set(sample_person['roles'].values()))}")
    print(f"   First contact: {sample_person['first_contact']}")
    print(f"   Last contact: {sample_person['last_contact']}")
    
    # Save outputs
    print(f"\n💾 Saving rich profiles...")
    
    with open('./output_hackathon/rich_people_profiles.json', 'w') as f:
        json.dump(result['people'], f, indent=2, default=str)
    
    with open('./output_hackathon/project_roles.json', 'w') as f:
        json.dump(result['project_roles'], f, indent=2)
    
    with open('./output_hackathon/communication_timelines.json', 'w') as f:
        json.dump(result['communication_timeline'], f, indent=2, default=str)
    
    with open('./output_hackathon/meeting_patterns.json', 'w') as f:
        json.dump(result['meeting_patterns'], f, indent=2, default=str)
    
    graph_data = nx.node_link_data(result['graph'])
    with open('./output_hackathon/rich_knowledge_graph.json', 'w') as f:
        json.dump(graph_data, f, indent=2)
    
    print(f"\n✅ Files saved:")
    print(f"   - rich_people_profiles.json (detailed profiles)")
    print(f"   - project_roles.json (who did what)")
    print(f"   - communication_timelines.json (chronological interactions)")
    print(f"   - meeting_patterns.json (internal vs cross-team)")
    print(f"   - rich_knowledge_graph.json (complete graph)")
    print("=" * 70)
