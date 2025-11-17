"""Data models and schemas for the Graph-First Project Intelligence System."""

from typing import TypedDict, List, Dict, Optional
from pydantic import BaseModel, Field
from datetime import datetime
import networkx as nx


# ==================== State Schema ====================
class ProjectGraphState(TypedDict):
    """State object for LangGraph workflow."""
    # Input
    raw_emails: List[Dict]
    raw_calendar: List[Dict]
    
    # Agent 1 outputs
    cleaned_emails: List[Dict]
    project_groups: Dict[str, Dict]
    
    # Agent 2 outputs
    project_intelligence: List[Dict]
    
    # Agent 3 outputs
    verified_graph: nx.DiGraph
    rejected_facts: List[Dict]
    
    # Final outputs
    graph_json: Dict
    evaluation_metrics: Dict


# ==================== Email Models ====================
class CleanedEmail(BaseModel):
    """Cleaned and parsed email structure."""
    message_id: str
    from_: str = Field(alias='from')
    to: List[str]
    cc: Optional[List[str]] = None
    subject: str
    date: str
    body_clean: str
    participants: List[str]
    
    class Config:
        populate_by_name = True


class ProjectGroup(BaseModel):
    """Email group clustered by project."""
    project_id: str
    email_ids: List[str]
    calendar_ids: Optional[List[str]] = []


# ==================== Project Intelligence Models ====================
class Evidence(BaseModel):
    """Evidence linking facts to source emails."""
    message_ids: List[str]


class Topic(BaseModel):
    """Project topic/theme."""
    topic: str
    evidence: List[str]


class Scope(BaseModel):
    """Project scope definition."""
    description: str
    evidence: List[str]


class Timeline(BaseModel):
    """Project timeline."""
    start: str
    end: Optional[str] = None
    evidence: List[str]


class Challenge(BaseModel):
    """Challenge or problem encountered."""
    id: str
    description: str
    category: str  # Technical, Budget, Timeline, Scope, Communication
    raised_date: str
    evidence: List[str]


class Resolution(BaseModel):
    """Resolution to a challenge."""
    id: str
    resolves: str  # Challenge ID
    description: str
    resolved_date: str
    methodology: Optional[str] = None
    evidence: List[str]


class ProjectIntelligence(BaseModel):
    """Complete project intelligence extraction."""
    project_id: str
    project_name: str
    evidence: List[str]
    project_type: str
    topics: List[Topic]
    scope: Scope
    timeline: Timeline
    challenges: List[Challenge]
    resolutions: List[Resolution]
    phase: str  # Scoping, Execution, Challenge Resolution, Delivery
    phase_reasoning: str


# ==================== Graph Node Types ====================
class NodeType:
    """Node type constants."""
    PROJECT = "Project"
    TOPIC = "Topic"
    CHALLENGE = "Challenge"
    RESOLUTION = "Resolution"


class EdgeType:
    """Edge type constants."""
    HAS_TOPIC = "HAS_TOPIC"
    FACED_CHALLENGE = "FACED_CHALLENGE"
    RESOLVED_BY = "RESOLVED_BY"
    LED_BY = "LED_BY"
    FOR_CLIENT = "FOR_CLIENT"


# ==================== Evaluation Models ====================
class TrustScoreMetrics(BaseModel):
    """Trust Score evaluation metrics."""
    trust_score: float
    fact_traceability: float
    extraction_completeness: float
    phase_accuracy: float
    hallucination_rate: float
    hallucinations: List[Dict]
    total_facts: int
    traceable_facts: int
