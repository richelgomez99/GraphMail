"""Data loading utilities for emails and calendar events."""

import json
import os
from typing import List, Dict


def load_email_data(file_path: str) -> List[Dict]:
    """Load email data from JSON file.
    
    Args:
        file_path: Path to JSON file
        
    Returns:
        List of email threads
    """
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    # Handle different formats
    if isinstance(data, list):
        return data
    elif 'emails' in data:
        return data['emails']
    elif 'threads' in data:
        return data['threads']
    else:
        return [data]


def load_calendar_data(file_path: str) -> List[Dict]:
    """Load calendar event data from JSON file.
    
    Args:
        file_path: Path to JSON file
        
    Returns:
        List of calendar events
    """
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    # Handle different formats
    if isinstance(data, list):
        return data
    elif 'events' in data:
        return data['events']
    elif 'calendar' in data:
        return data['calendar']
    else:
        return [data]


def load_ground_truth(file_path: str) -> Dict:
    """Load ground truth annotations for evaluation.
    
    Args:
        file_path: Path to ground truth JSON
        
    Returns:
        Ground truth dict
    """
    with open(file_path, 'r') as f:
        return json.load(f)


def create_sample_dataset(output_dir: str = "./data"):
    """Create sample dataset for testing.
    
    Args:
        output_dir: Directory to save sample data
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Sample emails
    emails = [
        {
            'message_id': 'msg_001',
            'from': 'sage.harris@consultingco.com',
            'to': ['jamie.adams@startupco.com'],
            'subject': 'StartupCo Brand Book - Project Kickoff',
            'date': '2026-03-25',
            'body_text': '''Hi Jamie,

Great to connect yesterday! I'm excited to work on the StartupCo Online Brand Book project.

Based on our discussion, here's what I understand:
- Scope: Create an online brand book with API access for dynamic content
- Timeline: 4 weeks (deliver by April 22)
- Key deliverables: Brand guidelines, color palette, typography system, logo usage

Let me know if I missed anything!

Best,
Sage Harris
Consulting Lead
ConsultingCo'''
        },
        {
            'message_id': 'msg_002',
            'from': 'jamie.adams@startupco.com',
            'to': ['sage.harris@consultingco.com'],
            'subject': 'Re: StartupCo Brand Book - Project Kickoff',
            'date': '2026-03-26',
            'body_text': '''Hi Sage,

Looks good overall! One concern: I'm not sure about sharing our API keys for the integration. 
Could we explore other options for the dynamic content feature?

Also, can we add social media templates to the scope?

Thanks,
Jamie Adams
CTO, StartupCo'''
        },
        {
            'message_id': 'msg_003',
            'from': 'sage.harris@consultingco.com',
            'to': ['jamie.adams@startupco.com'],
            'subject': 'Re: StartupCo Brand Book - API Solution',
            'date': '2026-03-27',
            'body_text': '''Jamie,

Great question. Instead of direct API integration, we can use a hosted solution. 
This way you don't need to share credentials and we get better security.

Regarding social media templates - yes, we can add that. Should be straightforward.

Sound good?

Sage'''
        },
        {
            'message_id': 'msg_004',
            'from': 'jamie.adams@startupco.com',
            'to': ['sage.harris@consultingco.com'],
            'subject': 'Re: StartupCo Brand Book - Approved!',
            'date': '2026-03-27',
            'body_text': '''Perfect! Let's go with the hosted solution. Approved on my end.

Looking forward to the first draft.

Jamie'''
        },
        {
            'message_id': 'msg_005',
            'from': 'sage.harris@consultingco.com',
            'to': ['jamie.adams@startupco.com', 'quinn.baker@startupco.com'],
            'subject': 'StartupCo Brand Book - First Draft Ready',
            'date': '2026-04-10',
            'body_text': '''Hi Jamie and Quinn,

First draft of the brand book is ready for review:
- Brand guidelines complete
- Color palette: primary, secondary, accent colors defined
- Typography system: headings, body, monospace fonts selected
- Logo usage rules documented
- Social media templates: Twitter, LinkedIn, Instagram

Please review and share feedback by Friday.

Best,
Sage'''
        },
        {
            'message_id': 'msg_006',
            'from': 'quinn.baker@startupco.com',
            'to': ['sage.harris@consultingco.com'],
            'cc': ['jamie.adams@startupco.com'],
            'subject': 'Re: StartupCo Brand Book - Feedback',
            'date': '2026-04-12',
            'body_text': '''Sage,

This looks great! A few minor changes:
- Can we adjust the primary blue to be slightly darker?
- Instagram template needs our new tagline

Otherwise we're good to go!

Quinn Baker
Marketing Director, StartupCo'''
        },
        {
            'message_id': 'msg_007',
            'from': 'sage.harris@consultingco.com',
            'to': ['quinn.baker@startupco.com', 'jamie.adams@startupco.com'],
            'subject': 'StartupCo Brand Book - Final Version',
            'date': '2026-04-20',
            'body_text': '''Quinn, Jamie,

Final version ready with your feedback incorporated:
✓ Primary blue darkened
✓ Instagram template updated with tagline
✓ All assets uploaded to hosted platform

Project complete! Let me know if you need anything else.

Best,
Sage'''
        }
    ]
    
    # Sample calendar events
    calendar = [
        {
            'event_id': 'cal_001',
            'summary': 'StartupCo Brand Book - Kickoff Meeting',
            'start': '2026-03-24T10:00:00',
            'end': '2026-03-24T11:00:00',
            'attendees': [
                'sage.harris@consultingco.com',
                'jamie.adams@startupco.com'
            ]
        },
        {
            'event_id': 'cal_002',
            'summary': 'Brand Book Review',
            'start': '2026-04-10T14:00:00',
            'end': '2026-04-10T15:00:00',
            'attendees': [
                'sage.harris@consultingco.com',
                'jamie.adams@startupco.com',
                'quinn.baker@startupco.com'
            ]
        }
    ]
    
    # Save to files
    with open(f"{output_dir}/sample_emails.json", 'w') as f:
        json.dump(emails, f, indent=2)
    
    with open(f"{output_dir}/sample_calendar.json", 'w') as f:
        json.dump(calendar, f, indent=2)
    
    # Ground truth for evaluation
    ground_truth = {
        'projects': {
            'project_001': {
                'project_name': 'StartupCo Brand Book',
                'project_type': 'Design/Branding',
                'phase': 'Delivery',
                'topics': ['API Integration', 'Brand Guidelines', 'Social Media Templates'],
                'challenges': ['API key security concern'],
                'resolutions': ['Use hosted solution instead']
            }
        }
    }
    
    with open(f"{output_dir}/ground_truth.json", 'w') as f:
        json.dump(ground_truth, f, indent=2)
    
    print(f"✅ Sample dataset created in {output_dir}/")
    print(f"   - sample_emails.json ({len(emails)} emails)")
    print(f"   - sample_calendar.json ({len(calendar)} events)")
    print(f"   - ground_truth.json")


if __name__ == "__main__":
    create_sample_dataset()
