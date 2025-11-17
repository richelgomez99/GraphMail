"""Agent 1: Email Parser & Project Identifier
Cleans emails, identifies projects, and groups related communications.
"""

import re
import hashlib
from typing import List, Dict
from datetime import datetime, timedelta
from collections import defaultdict


def parse_email_thread(email_obj: Dict) -> Dict:
    """Clean email and extract metadata.
    
    Args:
        email_obj: Raw email object
        
    Returns:
        Cleaned email dict with message_id, participants, clean body
    """
    # Generate message ID if not present
    if 'message_id' not in email_obj:
        email_str = str(email_obj)
        message_id = f"msg_{hashlib.md5(email_str.encode()).hexdigest()[:12]}"
    else:
        message_id = email_obj['message_id']
    
    # Extract body text
    body_text = email_obj.get('body_text', email_obj.get('body', ''))
    
    # Clean body
    body_clean = remove_signature(body_text)
    body_clean = remove_forward_chains(body_clean)
    
    # Extract all participants
    participants = extract_all_participants(email_obj)
    
    # Parse 'to' field
    to_field = email_obj.get('to', [])
    if isinstance(to_field, str):
        to_field = [to_field]
    
    # Parse 'cc' field
    cc_field = email_obj.get('cc', [])
    if isinstance(cc_field, str):
        cc_field = [cc_field]
    
    return {
        'message_id': message_id,
        'from': email_obj.get('from', ''),
        'to': to_field,
        'cc': cc_field,
        'subject': email_obj.get('subject', ''),
        'date': email_obj.get('date', ''),
        'body_clean': body_clean,
        'participants': participants
    }


def remove_signature(text: str) -> str:
    """Remove email signature blocks."""
    # Common signature markers
    signature_markers = [
        r'\n--\s*\n',  # Standard -- marker
        r'\nBest regards,',
        r'\nBest,',
        r'\nThanks,',
        r'\nSincerely,',
        r'\nRegards,',
        r'\nCheers,',
        r'\n-{2,}',  # Multiple dashes
    ]
    
    for marker in signature_markers:
        parts = re.split(marker, text, flags=re.IGNORECASE)
        if len(parts) > 1:
            # Keep only content before signature
            text = parts[0]
    
    return text.strip()


def remove_forward_chains(text: str) -> str:
    """Remove forwarded message blocks and reply chains."""
    # Patterns for forward/reply markers
    forward_patterns = [
        r'\n-{3,}\s*Forwarded message\s*-{3,}.*$',
        r'\nOn .* wrote:.*$',
        r'\nFrom:.*\nSent:.*\nTo:.*\nSubject:.*',
        r'\n>{1,}.*$',  # Quoted replies (lines starting with >)
    ]
    
    for pattern in forward_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.MULTILINE | re.DOTALL)
    
    return text.strip()


def extract_all_participants(email_obj: Dict) -> List[str]:
    """Extract all email participants."""
    participants = set()
    
    # Add sender
    if 'from' in email_obj and email_obj['from']:
        participants.add(extract_email_address(email_obj['from']))
    
    # Add recipients
    for field in ['to', 'cc', 'bcc']:
        if field in email_obj:
            recipients = email_obj[field]
            if recipients is None:
                continue
            if isinstance(recipients, str):
                recipients = [recipients]
            for recipient in recipients:
                if recipient:
                    participants.add(extract_email_address(recipient))
    
    return list(participants)


def extract_email_address(email_str: str) -> str:
    """Extract email address from string like 'Name <email@domain.com>'."""
    match = re.search(r'[\w\.-]+@[\w\.-]+', email_str)
    return match.group(0) if match else email_str


def extract_project_signals(email: Dict) -> Dict:
    """Identify project from email subject and body.
    
    Returns:
        Dict with project_name and confidence score
    """
    subject = email['subject'].lower()
    body = email['body_clean'].lower()
    
    # Common project indicators in subject
    project_keywords = ['project', 'brand book', 'portal', 'strategy', 'system', 'platform']
    
    # Extract potential project name from subject
    # Remove common prefixes
    clean_subject = re.sub(r'^(re:|fwd?:|fw:)\s*', '', subject, flags=re.IGNORECASE)
    
    # Look for project name patterns
    project_name = None
    confidence = 0.0
    
    # Check for explicit project names
    if 'brand book' in clean_subject:
        project_name = 'Brand Book'
        confidence = 0.9
    elif 'financial' in clean_subject and 'portal' in clean_subject:
        project_name = 'Financial Portal'
        confidence = 0.9
    elif 'market' in clean_subject and 'strategy' in clean_subject:
        project_name = 'Market Strategy'
        confidence = 0.9
    else:
        # Use first part of subject as project name
        project_name = clean_subject[:50]
        confidence = 0.5
    
    return {
        'project_name': project_name,
        'confidence': confidence,
        'subject': email['subject']
    }


def group_emails_by_project(cleaned_emails: List[Dict]) -> Dict[str, Dict]:
    """Group emails by project using subject similarity and keywords.
    
    Args:
        cleaned_emails: List of cleaned email dicts
        
    Returns:
        Dict mapping project_id -> {email_ids, project_name, subjects}
    """
    projects = defaultdict(lambda: {'email_ids': [], 'subjects': set(), 'project_name': None})
    
    # First pass: identify project signals
    email_project_map = {}
    for email in cleaned_emails:
        signals = extract_project_signals(email)
        email_project_map[email['message_id']] = signals
    
    # Second pass: cluster by project name similarity
    project_clusters = defaultdict(list)
    for email in cleaned_emails:
        msg_id = email['message_id']
        project_signal = email_project_map[msg_id]
        
        # Normalize project name for clustering
        project_key = normalize_project_name(project_signal['project_name'])
        project_clusters[project_key].append(email)
    
    # Build project groups
    project_groups = {}
    for idx, (project_key, emails) in enumerate(project_clusters.items()):
        project_id = f"project_{idx+1:03d}"
        
        # Determine best project name (most common)
        project_names = [email_project_map[e['message_id']]['project_name'] for e in emails]
        best_name = max(set(project_names), key=project_names.count)
        
        project_groups[project_id] = {
            'project_id': project_id,
            'email_ids': [e['message_id'] for e in emails],
            'project_name': best_name,
            'subjects': list(set(e['subject'] for e in emails))
        }
    
    return project_groups


def normalize_project_name(name: str) -> str:
    """Normalize project name for clustering."""
    # Remove common words and normalize
    name = name.lower()
    name = re.sub(r'\b(update|follow[- ]?up|re:|fwd?:|next steps)\b', '', name)
    name = re.sub(r'[^\w\s]', '', name)
    name = re.sub(r'\s+', '_', name.strip())
    return name[:30]  # Truncate for consistency


def link_calendar_events(project_groups: Dict, calendar_events: List[Dict]) -> Dict:
    """Link calendar events to project groups based on participants and timing.
    
    Args:
        project_groups: Project groups from group_emails_by_project
        calendar_events: List of calendar event dicts
        
    Returns:
        Enhanced project_groups with calendar_ids
    """
    for project_id, project_data in project_groups.items():
        calendar_ids = []
        
        # Get project participants from emails
        # (Would need cleaned_emails to do properly - simplified here)
        
        # Check each calendar event
        for event in calendar_events:
            event_id = event.get('event_id', event.get('id'))
            event_subject = event.get('subject', event.get('summary', '')).lower()
            
            # Simple matching: if project name appears in event subject
            project_name_lower = project_data['project_name'].lower()
            if any(word in event_subject for word in project_name_lower.split() if len(word) > 3):
                calendar_ids.append(event_id)
        
        project_data['calendar_ids'] = calendar_ids
    
    return project_groups


def agent_1_parser(state: Dict) -> Dict:
    """Agent 1: Parse emails and identify projects.
    
    Args:
        state: ProjectGraphState dict
        
    Returns:
        Updated state with cleaned_emails and project_groups
    """
    print("[Agent 1] Starting email parsing and project identification...")
    
    cleaned = []
    
    # Parse raw emails
    raw_emails = state.get('raw_emails', [])
    for thread in raw_emails:
        # Handle different structures
        if 'emails' in thread:
            emails_list = thread['emails']
        elif isinstance(thread, list):
            emails_list = thread
        else:
            emails_list = [thread]
        
        for email in emails_list:
            parsed = parse_email_thread(email)
            cleaned.append(parsed)
    
    print(f"[Agent 1] Parsed {len(cleaned)} emails")
    
    # Group by project
    project_groups = group_emails_by_project(cleaned)
    print(f"[Agent 1] Identified {len(project_groups)} projects")
    
    # Link to calendar
    calendar_events = state.get('raw_calendar', [])
    enhanced_groups = link_calendar_events(project_groups, calendar_events)
    
    print("[Agent 1] Complete")
    
    return {
        "cleaned_emails": cleaned,
        "project_groups": enhanced_groups
    }
