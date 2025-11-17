"""Agent 2: Project Intelligence Extractor
Extracts structured project data using LLMs.
"""

import json
from typing import List, Dict
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
import os


def get_llm():
    """Get LLM instance (OpenAI or Anthropic based on available key)."""
    if os.getenv('OPENAI_API_KEY'):
        # Using latest GPT-4o for better intelligence extraction
        return ChatOpenAI(model="gpt-4o", temperature=0)
    elif os.getenv('ANTHROPIC_API_KEY'):
        return ChatAnthropic(model="claude-3-5-sonnet-20241022", temperature=0)
    else:
        raise ValueError("No API key found. Set OPENAI_API_KEY or ANTHROPIC_API_KEY")


def extract_project_intelligence_llm(
    project_id: str,
    project_name: str,
    emails: List[Dict],
    calendar_events: List[Dict] = None
) -> Dict:
    """Extract structured project intelligence using LLM.
    
    Args:
        project_id: Unique project identifier
        project_name: Project name from clustering
        emails: List of emails for this project
        calendar_events: Optional calendar events
        
    Returns:
        ProjectIntelligence dict
    """
    llm = get_llm()
    
    # Format emails for prompt (limit to avoid context overflow)
    email_context = format_emails_for_prompt(emails[:15])
    
    # Build extraction prompt
    prompt = build_extraction_prompt(project_id, project_name, email_context)
    
    # Invoke LLM
    print(f"[Agent 2] Extracting intelligence for {project_name}...")
    response = llm.invoke(prompt)
    
    # Parse response
    try:
        result = json.loads(response.content)
        return result
    except json.JSONDecodeError:
        # Fallback: extract JSON from markdown code blocks
        content = response.content
        if '```json' in content:
            json_str = content.split('```json')[1].split('```')[0]
            return json.loads(json_str)
        elif '```' in content:
            json_str = content.split('```')[1].split('```')[0]
            return json.loads(json_str)
        else:
            raise ValueError(f"Could not parse LLM response as JSON: {content[:200]}")


def format_emails_for_prompt(emails: List[Dict]) -> str:
    """Format emails into readable context for LLM."""
    formatted = []
    for email in emails:
        formatted.append(
            f"Email {email['message_id']}:\n"
            f"From: {email['from']}\n"
            f"Date: {email['date']}\n"
            f"Subject: {email['subject']}\n"
            f"Body: {email['body_clean'][:800]}...\n"
        )
    return "\n\n".join(formatted)


def build_extraction_prompt(project_id: str, project_name: str, email_context: str) -> str:
    """Build prompt for project intelligence extraction."""
    return f"""Extract project intelligence from these consultant-client emails.

Project Name (from clustering): {project_name}

Emails:
{email_context}

Extract the following information:

1. **Project Name**: Refine the project name from email subjects/content (use clustering name as fallback)
2. **Project Type**: Categorize as one of: Design/Branding, Financial Systems, Strategy Consulting, Operations, Market Research, Technology/Engineering, Other
3. **Topics**: List specific themes within project (e.g., "API Integration", "Payment Gateway", "Brand Guidelines")
4. **Scope**: High-level description of what's being built/delivered. Quote key scope statements.
5. **Timeline**: Extract start date (first email), end date (last email or mentioned deadline), duration
6. **Challenges**: Look for problems, issues, blockers, concerns. Categorize as: Technical, Budget, Timeline, Scope, Communication
7. **Resolutions**: Look for solutions, fixes, decisions. Link to specific challenges if possible.
8. **Phase**: Infer project phase from communication patterns:
   - Scoping: Requirements gathering, "what do you need?", questions about scope
   - Execution: Progress updates, "here's what we've done", active work
   - Challenge Resolution: Problem discussions, debugging, "let's figure this out"
   - Delivery: Final deliverables, "ready for review", handoff language

CRITICAL RULES:
- Every extracted fact MUST include evidence (message_ids where it appears)
- If a fact appears in multiple emails, list all message_ids
- Be specific: "API integration for payment processing" not just "API work"
- For challenges/resolutions, extract WHO raised it, WHEN, and WHAT it was

Output JSON format:
{{
  "project_id": "{project_id}",
  "project_name": "Refined Project Name",
  "evidence": ["msg_X", "msg_Y"],
  "project_type": "Design/Branding",
  "topics": [
    {{"topic": "API Integration", "evidence": ["msg_X"]}},
    {{"topic": "Brand Guidelines", "evidence": ["msg_Y", "msg_Z"]}}
  ],
  "scope": {{
    "description": "Create online brand book with API access for dynamic content",
    "evidence": ["msg_X"]
  }},
  "timeline": {{
    "start": "2026-03-25",
    "end": "2026-04-22",
    "evidence": ["msg_X", "msg_Y"]
  }},
  "challenges": [
    {{
      "id": "ch_001",
      "description": "Client uncertain about API key sharing for security reasons",
      "category": "Technical",
      "raised_date": "2026-03-26",
      "evidence": ["msg_X"]
    }}
  ],
  "resolutions": [
    {{
      "id": "res_001",
      "resolves": "ch_001",
      "description": "Decided to use hosted solution instead of direct API access",
      "resolved_date": "2026-03-27",
      "methodology": "Switched to managed service approach",
      "evidence": ["msg_Y"]
    }}
  ],
  "phase": "Execution",
  "phase_reasoning": "Emails show active work and progress updates rather than scoping questions"
}}

Output ONLY the JSON, no additional text.
"""


def extract_challenges(email_group: List[Dict]) -> List[Dict]:
    """Extract challenges using keyword detection + LLM.
    
    Args:
        email_group: List of emails for a project
        
    Returns:
        List of challenge dicts
    """
    challenge_keywords = [
        'issue', 'problem', 'concern', 'blocker', 'delay',
        'confused', 'unclear', 'stuck', 'challenge', 'trouble',
        'difficulty', 'complication'
    ]
    
    challenges = []
    llm = get_llm()
    
    for email in email_group:
        body_lower = email['body_clean'].lower()
        
        # Check for challenge indicators
        if any(keyword in body_lower for keyword in challenge_keywords):
            # Use LLM to extract structured challenge
            prompt = f"""Extract the challenge/problem mentioned in this email.

Email:
From: {email['from']}
Date: {email['date']}
Subject: {email['subject']}
Body: {email['body_clean']}

If a problem or challenge is mentioned, extract it. Otherwise return null.

Output JSON:
{{"text": "description of challenge", "category": "Technical|Budget|Timeline|Scope|Communication"}}

Output ONLY the JSON, no additional text.
"""
            
            try:
                response = llm.invoke(prompt)
                challenge_data = json.loads(response.content)
                
                if challenge_data and 'text' in challenge_data:
                    challenges.append({
                        'description': challenge_data['text'],
                        'category': challenge_data.get('category', 'Other'),
                        'raised_date': email['date'],
                        'evidence': [email['message_id']]
                    })
            except:
                continue
    
    return challenges


def extract_resolutions(email_group: List[Dict]) -> List[Dict]:
    """Extract resolutions using keyword detection + LLM."""
    resolution_keywords = [
        'solution', 'resolved', 'fixed', 'decided', 'agreed',
        'sorted', 'addressed', 'settled', 'concluded'
    ]
    
    resolutions = []
    llm = get_llm()
    
    for email in email_group:
        body_lower = email['body_clean'].lower()
        
        if any(keyword in body_lower for keyword in resolution_keywords):
            prompt = f"""Extract the resolution/solution mentioned in this email.

Email:
From: {email['from']}
Date: {email['date']}
Subject: {email['subject']}
Body: {email['body_clean']}

If a solution or resolution is mentioned, extract it. Otherwise return null.

Output JSON:
{{"text": "description of resolution", "methodology": "how was it solved"}}

Output ONLY the JSON, no additional text.
"""
            
            try:
                response = llm.invoke(prompt)
                resolution_data = json.loads(response.content)
                
                if resolution_data and 'text' in resolution_data:
                    resolutions.append({
                        'description': resolution_data['text'],
                        'resolved_date': email['date'],
                        'methodology': resolution_data.get('methodology', ''),
                        'evidence': [email['message_id']]
                    })
            except:
                continue
    
    return resolutions


def agent_2_extractor(state: Dict) -> Dict:
    """Agent 2: Extract project intelligence from grouped emails.
    
    Args:
        state: ProjectGraphState dict
        
    Returns:
        Updated state with project_intelligence
    """
    print("[Agent 2] Starting project intelligence extraction...")
    
    intelligence = []
    
    cleaned_emails = state['cleaned_emails']
    project_groups = state['project_groups']
    
    for project_id, project_data in project_groups.items():
        # Get emails for this project
        emails = [
            e for e in cleaned_emails
            if e['message_id'] in project_data['email_ids']
        ]
        
        if not emails:
            continue
        
        # Extract using LLM
        try:
            project_intel = extract_project_intelligence_llm(
                project_id=project_id,
                project_name=project_data['project_name'],
                emails=emails,
                calendar_events=[]
            )
            intelligence.append(project_intel)
            print(f"[Agent 2] Extracted: {project_intel['project_name']}")
        except Exception as e:
            print(f"[Agent 2] Error extracting {project_id}: {str(e)}")
            continue
    
    print(f"[Agent 2] Extracted intelligence for {len(intelligence)} projects")
    print("[Agent 2] Complete")
    
    return {"project_intelligence": intelligence}
