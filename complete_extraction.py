#!/usr/bin/env python3
"""
COMPLETE PROJECT INTELLIGENCE EXTRACTION
Combines: Timeline, Stages, Real Topics, AND Insights
"""

import json
import re
from datetime import datetime
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

def clean_subject(subject):
    """Remove Re:, Fwd: and extract actual topic"""
    if not subject:
        return None
    
    cleaned = re.sub(r'^(Re|Fwd|RE|FW|Fw):\s*', '', subject, flags=re.IGNORECASE)
    cleaned = re.sub(r'^(Re|Fwd|RE|FW|Fw):\s*', '', cleaned, flags=re.IGNORECASE)
    cleaned = cleaned.strip()
    
    if len(cleaned) < 5 or cleaned.lower() in ['re', 'fwd', 'fw']:
        return None
    
    return cleaned

def extract_complete_project_intelligence(thread_emails, thread_idx):
    """Extract EVERYTHING: timeline, stages, topics, AND insights"""
    
    # Get project name
    project_name = None
    for email in thread_emails:
        clean_subj = clean_subject(email.get('subject', ''))
        if clean_subj and len(clean_subj) > 10:
            project_name = clean_subj
            break
    
    if not project_name:
        project_name = f"Project {thread_idx}"
    
    print(f"\n📁 Extracting: {project_name}")
    print(f"   Emails: {len(thread_emails)}")
    
    # Prepare email context for LLM
    email_context = ""
    for i, email in enumerate(thread_emails[:10], 1):
        email_context += f"\n--- EMAIL {i} ---\n"
        email_context += f"From: {email.get('from', '')}\n"
        email_context += f"To: {email.get('to', '')}\n"
        email_context += f"Date: {email.get('date', '')}\n"
        email_context += f"Subject: {email.get('subject', '')}\n"
        email_context += f"Body: {email.get('body_text', '')[:600]}\n"
    
    # Use LLM to extract EVERYTHING at once
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    
    prompt = f"""You are analyzing consultant-client emails for project: "{project_name}"

Extract comprehensive project intelligence from these emails:

{email_context}

Return JSON with:
{{
  "project_type": "Client Project" or "Internal" or "Proposal",
  "real_topics": ["API Integration", "Brand Strategy", etc] (3-5 specific topics, NOT "Re", "Fwd", "Update"),
  
  "timeline_stages": [
    {{
      "stage": "Outreach" | "Discovery" | "Proposal" | "Negotiation" | "Kickoff" | "Execution" | "Review" | "Delivery",
      "date": "when this stage occurred",
      "evidence": "which email number shows this"
    }}
  ],
  
  "bottlenecks": [
    {{
      "what": "What slowed the project down?",
      "who": "Who was involved?",
      "why": "Root cause?",
      "duration": "How long?",
      "impact": "What was the impact?"
    }}
  ],
  
  "pain_points": [
    {{
      "what": "What went wrong?",
      "why": "Root cause?",
      "impact": "Effect on project?"
    }}
  ],
  
  "what_worked": [
    {{
      "what": "What went well?",
      "why": "Why was this successful?"
    }}
  ],
  
  "lessons_learned": [
    {{
      "lesson": "What should we do differently next time?",
      "context": "When does this apply?",
      "action": "Specific action to take"
    }}
  ],
  
  "client_concerns": [
    {{
      "concern": "What was the client worried about?",
      "when": "When did this come up?",
      "how_addressed": "How did we handle it?"
    }}
  ]
}}

RULES:
- Be specific and concrete
- Only extract what's clearly in the emails
- Topics should be substantive (NOT "Re", "Fwd", "Meeting", "Update")
- Every insight needs to be grounded in the emails
- If nothing found for a category, return empty array

Return ONLY valid JSON.
"""
    
    try:
        response = llm.invoke(prompt)
        content = response.content.strip()
        
        # Handle markdown code blocks
        if content.startswith('```'):
            content = content.split('```')[1]
            if content.startswith('json'):
                content = content[4:]
            content = content.strip()
        
        extracted = json.loads(content)
        
        # Build complete project object
        project = {
            'project_id': f"project_{thread_idx}",
            'project_name': project_name,
            'project_type': extracted.get('project_type', 'Unknown'),
            'total_emails': len(thread_emails),
            
            # Timeline and stages
            'timeline_stages': extracted.get('timeline_stages', []),
            
            # Topics (real ones!)
            'topics': extracted.get('real_topics', []),
            
            # Insights
            'bottlenecks': extracted.get('bottlenecks', []),
            'pain_points': extracted.get('pain_points', []),
            'what_worked': extracted.get('what_worked', []),
            'lessons_learned': extracted.get('lessons_learned', []),
            'client_concerns': extracted.get('client_concerns', []),
            
            # Evidence
            'evidence': [e.get('message_id', '') for e in thread_emails]
        }
        
        # Print what we found
        if project['topics']:
            print(f"   🏷️  Topics: {', '.join(project['topics'][:3])}")
        if project['timeline_stages']:
            stages = [s['stage'] for s in project['timeline_stages']]
            print(f"   📅 Stages: {' → '.join(stages)}")
        if project['bottlenecks']:
            print(f"   🚧 Bottlenecks: {len(project['bottlenecks'])}")
        if project['lessons_learned']:
            print(f"   💡 Lessons: {len(project['lessons_learned'])}")
        
        return project
        
    except Exception as e:
        print(f"   ⚠️  Error: {e}")
        return None

def main():
    print("=" * 70)
    print("🔬 COMPLETE PROJECT INTELLIGENCE EXTRACTION")
    print("=" * 70)
    print("Extracting:")
    print("  ✅ Real topics (not 'Re', 'Fwd')")
    print("  ✅ Project timeline and stages")
    print("  ✅ Bottlenecks and pain points")
    print("  ✅ What worked well")
    print("  ✅ Lessons learned")
    print("  ✅ Client concerns")
    print()
    
    # Load emails
    with open('Antler_Hackathon_Email_Data_fixed.json', 'r') as f:
        threads = json.load(f)
    
    all_projects = []
    
    # Process ALL threads
    for idx, thread in enumerate(threads):  # ALL threads
        emails = thread.get('emails', [])
        
        if not emails or len(emails) < 2:
            continue
        
        project = extract_complete_project_intelligence(emails, idx)
        
        if project:
            all_projects.append(project)
    
    # Save
    with open('./output_hackathon/complete_project_intelligence.json', 'w') as f:
        json.dump(all_projects, f, indent=2)
    
    print("\n" + "=" * 70)
    print(f"✅ Extracted {len(all_projects)} complete project profiles")
    print(f"📁 Saved to: ./output_hackathon/complete_project_intelligence.json")
    
    # Summary stats
    total_bottlenecks = sum(len(p['bottlenecks']) for p in all_projects)
    total_lessons = sum(len(p['lessons_learned']) for p in all_projects)
    projects_with_timeline = sum(1 for p in all_projects if p['timeline_stages'])
    
    print()
    print("📊 SUMMARY:")
    print(f"   Projects with clear timeline: {projects_with_timeline}/{len(all_projects)}")
    print(f"   Total bottlenecks identified: {total_bottlenecks}")
    print(f"   Total lessons learned: {total_lessons}")
    print(f"   Avg topics per project: {sum(len(p['topics']) for p in all_projects) / len(all_projects):.1f}")
    
    # Show example
    if all_projects:
        print()
        print("📋 EXAMPLE PROJECT:")
        example = all_projects[0]
        print(f"   Name: {example['project_name']}")
        print(f"   Type: {example['project_type']}")
        if example['timeline_stages']:
            print(f"   Timeline: {' → '.join([s['stage'] for s in example['timeline_stages']])}")
        if example['topics']:
            print(f"   Topics: {', '.join(example['topics'])}")
        if example['bottlenecks']:
            print(f"   Bottleneck: {example['bottlenecks'][0]['what']}")
        if example['lessons_learned']:
            print(f"   Lesson: {example['lessons_learned'][0]['lesson']}")
    
    print("=" * 70)

if __name__ == "__main__":
    main()
