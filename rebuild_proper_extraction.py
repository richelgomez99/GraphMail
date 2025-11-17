#!/usr/bin/env python3
"""
PROPER Track 9 Solution - Consultant-Focused
Extracts: Project Lifecycle, Real Topics, Timeline, Stages
"""

import json
import re
from datetime import datetime
from collections import defaultdict
from langchain_openai import ChatOpenAI
import os

def clean_subject(subject):
    """Remove Re:, Fwd: and extract actual topic"""
    if not subject:
        return None
    
    # Remove Re:, Fwd:, etc
    cleaned = re.sub(r'^(Re|Fwd|RE|FW|Fw):\s*', '', subject, flags=re.IGNORECASE)
    cleaned = re.sub(r'^(Re|Fwd|RE|FW|Fw):\s*', '', cleaned, flags=re.IGNORECASE)  # Do it twice for "Re: Re:"
    cleaned = cleaned.strip()
    
    # If it's still garbage, return None
    if len(cleaned) < 5 or cleaned.lower() in ['re', 'fwd', 'fw']:
        return None
    
    return cleaned

def detect_project_stage(email_body, subject):
    """Detect what stage of project lifecycle this email represents"""
    body_lower = email_body.lower() if email_body else ""
    subject_lower = subject.lower() if subject else ""
    combined = body_lower + " " + subject_lower
    
    # Stage keywords
    stages = {
        'Outreach': ['introduction', 'reaching out', 'would love to connect', 'interested in', 'initial contact'],
        'Discovery': ['understand your needs', 'discovery call', 'learn more about', 'what are you looking for'],
        'Proposal': ['proposal', 'quote', 'estimate', 'scope of work', 'pricing', 'our approach'],
        'Negotiation': ['contract', 'agreement', 'terms', 'negotiate', 'pricing discussion'],
        'Kickoff': ['kickoff', 'getting started', 'first meeting', 'onboarding', 'project start'],
        'Execution': ['update', 'progress', 'working on', 'completed', 'delivered', 'milestone'],
        'Review': ['feedback', 'review', 'comments', 'thoughts on', 'looks good'],
        'Delivery': ['final', 'completed', 'delivered', 'handoff', 'closing'],
        'Follow-up': ['following up', 'checking in', 'any updates', 'status']
    }
    
    for stage, keywords in stages.items():
        for keyword in keywords:
            if keyword in combined:
                return stage
    
    return 'Communication'  # Default

def extract_real_topics_from_body(email_body):
    """Extract actual discussion topics from email body using LLM"""
    if not email_body or len(email_body) < 20:
        return []
    
    # Use LLM to extract topics
    try:
        llm = ChatOpenAI(model="gpt-4o", temperature=0)
        
        prompt = f"""Extract 1-3 specific topics discussed in this email. Be concrete and specific.

Email:
{email_body[:500]}

Extract topics like: "API Integration", "Brand Guidelines", "Payment Processing", "Budget Discussion"
NOT topics like: "Re", "Fwd", "Update", "Meeting"

Return ONLY a JSON list of topics, nothing else:
["Topic 1", "Topic 2"]
"""
        
        response = llm.invoke(prompt)
        topics = json.loads(response.content)
        
        # Filter out garbage
        good_topics = []
        for topic in topics:
            if len(topic) > 5 and topic.lower() not in ['re', 'fwd', 'update', 'meeting', 'email']:
                good_topics.append(topic)
        
        return good_topics[:3]  # Max 3 topics
    except:
        return []

def build_project_timeline(thread_emails):
    """Build chronological timeline of project stages"""
    timeline = []
    
    for email in sorted(thread_emails, key=lambda x: x.get('date', '')):
        date = email.get('date', '')
        subject = email.get('subject', '')
        body = email.get('body_text', '')
        message_id = email.get('message_id', '')
        
        stage = detect_project_stage(body, subject)
        
        timeline.append({
            'date': date,
            'stage': stage,
            'subject': clean_subject(subject),
            'message_id': message_id
        })
    
    return timeline

def extract_consultant_project_intelligence(thread_emails, thread_idx):
    """Extract what consultants actually need: lifecycle, stages, timeline"""
    
    print(f"  Analyzing thread {thread_idx}...")
    
    # Get project name from first clean subject
    project_name = None
    for email in thread_emails:
        clean_subj = clean_subject(email.get('subject', ''))
        if clean_subj and len(clean_subj) > 10:
            project_name = clean_subj
            break
    
    if not project_name:
        project_name = f"Project {thread_idx}"
    
    # Build timeline
    timeline = build_project_timeline(thread_emails)
    
    # Extract participants
    participants = set()
    for email in thread_emails:
        sender = email.get('from', '')
        if '@' in sender:
            participants.add(sender.split('<')[-1].replace('>', '').strip())
    
    # Determine project type from participants
    project_type = "Internal" if all('@ConsultingCo' in p for p in participants) else "Client Project"
    
    # Extract stages present
    stages_present = list(set([t['stage'] for t in timeline]))
    
    # Get date range
    dates = [t['date'] for t in timeline if t['date']]
    start_date = min(dates) if dates else None
    end_date = max(dates) if dates else None
    
    # Extract real topics using LLM on a sample of emails
    all_topics = set()
    for email in thread_emails[:5]:  # Sample first 5 emails
        body = email.get('body_text', '')
        topics = extract_real_topics_from_body(body)
        all_topics.update(topics)
    
    return {
        'project_id': f"project_{thread_idx}",
        'project_name': project_name,
        'project_type': project_type,
        'participants': list(participants),
        'timeline': timeline,
        'stages': stages_present,
        'start_date': start_date,
        'end_date': end_date,
        'topics': list(all_topics),
        'total_emails': len(thread_emails),
        'evidence': [e.get('message_id', '') for e in thread_emails]
    }

def main():
    print("🔄 REBUILDING PROPER PROJECT INTELLIGENCE")
    print("=" * 70)
    print("Focus: Project Lifecycle, Timeline, Real Topics")
    print()
    
    # Load emails
    with open('Antler_Hackathon_Email_Data_fixed.json', 'r') as f:
        threads = json.load(f)
    
    print(f"📧 Processing {len(threads)} email threads...")
    print()
    
    all_projects = []
    
    for idx, thread in enumerate(threads[:10]):  # Process first 10 for testing
        thread_emails = thread.get('emails', [])
        
        if not thread_emails:
            continue
        
        project = extract_consultant_project_intelligence(thread_emails, idx)
        all_projects.append(project)
        
        # Show what we found
        print(f"\n📁 {project['project_name']}")
        print(f"   Type: {project['project_type']}")
        print(f"   Timeline: {project['start_date']} → {project['end_date']}")
        print(f"   Stages: {', '.join(project['stages'])}")
        print(f"   Topics: {', '.join(project['topics'][:3]) if project['topics'] else 'None extracted'}")
        print(f"   Participants: {len(project['participants'])}")
    
    # Save
    with open('./output_hackathon/proper_project_intelligence.json', 'w') as f:
        json.dump(all_projects, f, indent=2)
    
    print("\n" + "=" * 70)
    print(f"✅ Saved {len(all_projects)} projects to proper_project_intelligence.json")
    print()
    print("📊 SUMMARY:")
    print(f"   Projects with clear stages: {len([p for p in all_projects if len(p['stages']) > 1])}")
    print(f"   Projects with real topics: {len([p for p in all_projects if p['topics']])}")
    print(f"   Client projects: {len([p for p in all_projects if p['project_type'] == 'Client Project'])}")

if __name__ == "__main__":
    main()
