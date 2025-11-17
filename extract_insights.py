#!/usr/bin/env python3
"""
INSIGHT EXTRACTION - What Consultants Actually Need
Extract: Root causes, Pain points, Bottlenecks, Lessons learned
"""

import json
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def extract_project_insights(project_emails, project_name):
    """Use LLM to extract meaningful insights from project emails"""
    
    # Combine email content
    email_context = ""
    for email in project_emails[:10]:  # Use first 10 emails
        email_context += f"\n---\nFrom: {email.get('from', '')}\n"
        email_context += f"Date: {email.get('date', '')}\n"
        email_context += f"Subject: {email.get('subject', '')}\n"
        email_context += f"Body: {email.get('body_text', '')[:500]}\n"
    
    llm = ChatOpenAI(model="gpt-4o", temperature=0)
    
    prompt = f"""You are analyzing consultant-client email communications for the project: "{project_name}"

Based on these emails, extract ACTIONABLE INSIGHTS:

{email_context}

Extract and return JSON with:
{{
  "pain_points": [
    {{
      "what": "What was the pain point?",
      "why": "Why did it happen? (root cause)",
      "impact": "What was the impact?",
      "evidence": "Which message mentioned this?"
    }}
  ],
  "bottlenecks": [
    {{
      "what": "What slowed the project?",
      "cause": "Why was this a bottleneck?",
      "duration": "How long did it delay things?",
      "evidence": "Which message shows this?"
    }}
  ],
  "what_went_well": [
    {{
      "what": "What worked well?",
      "why": "Why was this successful?",
      "evidence": "Which message shows this?"
    }}
  ],
  "lessons_learned": [
    {{
      "lesson": "What should we do differently next time?",
      "context": "In what situation does this apply?",
      "action": "Specific action to take"
    }}
  ],
  "client_concerns": [
    {{
      "concern": "What was the client worried about?",
      "when": "When did this come up?",
      "how_addressed": "How did we handle it?",
      "evidence": "Which message?"
    }}
  ]
}}

IMPORTANT:
- Be specific and concrete
- Focus on ACTIONABLE insights
- Every insight needs evidence (message subject or date)
- Don't make things up - only extract what's clearly stated
- If no clear insights, return empty arrays

Return ONLY valid JSON, nothing else.
"""
    
    try:
        response = llm.invoke(prompt)
        content = response.content.strip()
        
        # Remove markdown code blocks if present
        if content.startswith('```'):
            content = content.split('```')[1]
            if content.startswith('json'):
                content = content[4:]
            content = content.strip()
        
        insights = json.loads(content)
        return insights
    except Exception as e:
        print(f"  ⚠️  Error extracting insights: {e}")
        print(f"  Response was: {response.content[:200] if 'response' in locals() else 'No response'}")
        return {
            "pain_points": [],
            "bottlenecks": [],
            "what_went_well": [],
            "lessons_learned": [],
            "client_concerns": []
        }

def analyze_all_projects(email_file):
    """Extract insights from all projects"""
    
    print("🧠 EXTRACTING ACTIONABLE INSIGHTS")
    print("=" * 70)
    print("What we're looking for:")
    print("  ⚠️  Pain points (what went wrong)")
    print("  🚧 Bottlenecks (what slowed us down)")
    print("  ✅ What worked well (successes)")
    print("  💡 Lessons learned (how to improve)")
    print("  😟 Client concerns (what worried them)")
    print()
    
    with open(email_file, 'r') as f:
        threads = json.load(f)
    
    all_insights = []
    
    for idx, thread in enumerate(threads[:5]):  # Process first 5 for demo
        emails = thread.get('emails', [])
        
        if not emails:
            continue
        
        # Get project name
        first_subject = emails[0].get('subject', '').replace('Re:', '').replace('Fwd:', '').strip()
        project_name = first_subject if len(first_subject) > 10 else f"Project {idx}"
        
        print(f"\n📁 Analyzing: {project_name}")
        print(f"   Emails: {len(emails)}")
        
        insights = extract_project_insights(emails, project_name)
        
        # Display findings
        if insights['pain_points']:
            print(f"   ⚠️  Pain points found: {len(insights['pain_points'])}")
            for pp in insights['pain_points'][:2]:
                print(f"      - {pp['what']}")
        
        if insights['bottlenecks']:
            print(f"   🚧 Bottlenecks found: {len(insights['bottlenecks'])}")
            for bn in insights['bottlenecks'][:2]:
                print(f"      - {bn['what']}")
        
        if insights['lessons_learned']:
            print(f"   💡 Lessons learned: {len(insights['lessons_learned'])}")
            for ll in insights['lessons_learned'][:2]:
                print(f"      - {ll['lesson']}")
        
        # Save
        all_insights.append({
            'project_name': project_name,
            'project_id': f"project_{idx}",
            'insights': insights,
            'email_count': len(emails)
        })
    
    # Save results
    with open('./output_hackathon/project_insights.json', 'w') as f:
        json.dump(all_insights, f, indent=2)
    
    print("\n" + "=" * 70)
    print(f"✅ Extracted insights from {len(all_insights)} projects")
    print(f"📁 Saved to: ./output_hackathon/project_insights.json")
    
    # Summary
    total_pain_points = sum(len(p['insights']['pain_points']) for p in all_insights)
    total_bottlenecks = sum(len(p['insights']['bottlenecks']) for p in all_insights)
    total_lessons = sum(len(p['insights']['lessons_learned']) for p in all_insights)
    
    print()
    print("📊 SUMMARY ACROSS ALL PROJECTS:")
    print(f"   Total pain points identified: {total_pain_points}")
    print(f"   Total bottlenecks found: {total_bottlenecks}")
    print(f"   Total lessons learned: {total_lessons}")
    
    # Cross-project patterns
    print()
    print("🔍 CROSS-PROJECT PATTERNS:")
    all_pain_points = []
    for proj in all_insights:
        all_pain_points.extend([pp['what'] for pp in proj['insights']['pain_points']])
    
    # Look for common themes
    if 'budget' in ' '.join(all_pain_points).lower():
        print("   ⚠️  PATTERN: Budget concerns appear in multiple projects")
    if 'timeline' in ' '.join(all_pain_points).lower() or 'delay' in ' '.join(all_pain_points).lower():
        print("   ⚠️  PATTERN: Timeline/delay issues are recurring")
    if 'communication' in ' '.join(all_pain_points).lower():
        print("   ⚠️  PATTERN: Communication breakdowns detected")
    
    return all_insights

if __name__ == "__main__":
    insights = analyze_all_projects('Antler_Hackathon_Email_Data_fixed.json')
    
    print()
    print("=" * 70)
    print("💡 HOW TO USE THESE INSIGHTS:")
    print()
    print("1. Before starting a new project:")
    print("   → Review lessons learned from similar past projects")
    print("   → Proactively address known pain points")
    print()
    print("2. During project execution:")
    print("   → Watch for common bottlenecks")
    print("   → Apply what worked well before")
    print()
    print("3. Client conversations:")
    print("   → Anticipate concerns based on past client worries")
    print("   → Have solutions ready for common issues")
    print()
    print("=" * 70)
