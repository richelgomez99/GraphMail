# REFACTORING PLAN - Strategic Code Improvement

**Status**: Hackathon → Production  
**Approach**: Incremental refactoring (no big rewrite)  
**Timeline**: 3-4 weeks  
**Philosophy**: "Make it work, make it right, make it fast"

---

## Refactoring Philosophy

### Why NOT a Rewrite?

The codebase has **strong fundamentals**:
- ✅ Clear separation of concerns (3 agents)
- ✅ Well-documented architecture
- ✅ Functional core logic
- ✅ Comprehensive documentation

**Problems are tactical, not strategic**:
- Duplicated code (easy to consolidate)
- Missing error handling (easy to add)
- Hardcoded values (easy to externalize)
- No tests (easy to retrofit)

### Refactoring Strategy

**Strangler Fig Pattern**: Gradually replace old code with new:
1. Add tests around existing code
2. Extract interfaces
3. Implement new version behind interface
4. Switch over incrementally
5. Delete old code

---

## Phase 1: Code Organization (Week 1)

### 1.1 Consolidate Demo Files (Day 1)

**Problem**: 11 demo files with 70% duplication

**Solution**: Single unified demo with feature flags

```bash
# Delete redundant files
rm demo_clear.py demo_collaboration_graph.py demo_final.py \
   demo_final_complete.py demo_simple.py demo_track9.py

# Keep and enhance:
# - demo_dashboard.py (rename to app.py)
# - demo_complete_graph.py (move features into main)
# - demo_human.py (move features into main)
```

**New Structure**:
```
src/
  ui/
    __init__.py
    app.py              # Main Streamlit app
    components/
      metrics.py        # Metrics display
      graph.py          # Graph visualization
      project_list.py   # Project cards
      filters.py        # Search/filter UI
    utils/
      formatting.py     # Data formatting
      colors.py         # Color schemes
```

**Effort**: 8 hours  
**Impact**: -2,500 LOC, easier maintenance

---

### 1.2 Extract Shared Utilities (Day 2)

**Problem**: LLM initialization duplicated 3x, JSON parsing 5x

**Solution**: Create `src/utils/llm.py`:

```python
# src/utils/llm.py
from functools import lru_cache
from typing import Literal
import os
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

LLMProvider = Literal['openai', 'anthropic']

class LLMConfig:
    """Centralized LLM configuration."""
    def __init__(
        self,
        provider: LLMProvider | None = None,
        model: str | None = None,
        temperature: float = 0.0
    ):
        self.provider = provider or self._detect_provider()
        self.model = model or self._get_default_model()
        self.temperature = temperature
    
    def _detect_provider(self) -> LLMProvider:
        """Auto-detect available provider."""
        if os.getenv('OPENAI_API_KEY'):
            return 'openai'
        elif os.getenv('ANTHROPIC_API_KEY'):
            return 'anthropic'
        else:
            raise ValueError("No LLM API key found")
    
    def _get_default_model(self) -> str:
        """Get default model for provider."""
        defaults = {
            'openai': 'gpt-4o',
            'anthropic': 'claude-3-5-sonnet-20241022'
        }
        return defaults[self.provider]

@lru_cache(maxsize=1)
def get_llm(config: LLMConfig | None = None):
    """Get cached LLM instance."""
    if config is None:
        config = LLMConfig()
    
    if config.provider == 'openai':
        return ChatOpenAI(
            model=config.model,
            temperature=config.temperature
        )
    elif config.provider == 'anthropic':
        return ChatAnthropic(
            model=config.model,
            temperature=config.temperature
        )
```

**Usage in agents**:
```python
# Before (duplicated):
if os.getenv('OPENAI_API_KEY'):
    return ChatOpenAI(model="gpt-4o", temperature=0)
elif os.getenv('ANTHROPIC_API_KEY'):
    return ChatAnthropic(model="claude-3-5-sonnet-20241022", temperature=0)

# After (centralized):
from src.utils.llm import get_llm
llm = get_llm()
```

**Effort**: 4 hours  
**Impact**: DRY principle, easier to add new LLMs

---

### 1.3 Create Configuration Module (Day 2)

**Problem**: Hardcoded paths, models, magic numbers

**Solution**: `src/config/settings.py`:

```python
# src/config/settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False
    )
    
    # Paths
    project_root: Path = Path(__file__).parent.parent.parent
    data_dir: Path = project_root / "data"
    output_dir: Path = project_root / "output"
    
    # LLM Configuration
    llm_provider: str = "openai"
    llm_model: str = "gpt-4o"
    llm_temperature: float = 0.0
    llm_max_retries: int = 3
    llm_timeout: int = 60
    
    # API Keys (from environment)
    openai_api_key: str | None = None
    anthropic_api_key: str | None = None
    
    # Agent Configuration
    agent1_max_emails: int = 1000
    agent2_emails_per_project: int = 15
    agent2_context_window_tokens: int = 8000
    agent3_verification_threshold: float = 0.7
    
    # Trust Score Weights
    trust_score_traceability_weight: float = 0.35
    trust_score_completeness_weight: float = 0.25
    trust_score_phase_accuracy_weight: float = 0.20
    trust_score_anti_hallucination_weight: float = 0.20
    
    # Dashboard
    dashboard_port: int = 8501
    dashboard_auto_refresh: bool = True
    dashboard_refresh_interval: int = 5
    
    # Logging
    log_level: str = "INFO"
    log_file: Path | None = project_root / "graphmail.log"
    
    @property
    def has_api_key(self) -> bool:
        """Check if any API key is configured."""
        return bool(self.openai_api_key or self.anthropic_api_key)

# Global settings instance
settings = Settings()
```

**Usage**:
```python
from src.config.settings import settings

# Instead of: output_dir = './output'
output_dir = settings.output_dir

# Instead of: emails[:15]
emails[:settings.agent2_emails_per_project]
```

**Effort**: 3 hours  
**Impact**: Centralized config, environment-aware

---

## Phase 2: Error Handling & Logging (Week 1)

### 2.1 Replace Print with Structured Logging (Day 3)

**Problem**: Print statements everywhere, no log levels

**Solution**: Use `structlog` for structured logging:

```python
# src/utils/logging.py
import structlog
import logging
import sys

def configure_logging(log_level: str = "INFO"):
    """Configure structured logging."""
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level),
    )
    
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.StackInfoRenderer(),
            structlog.dev.set_exc_info,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer()
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=False
    )

def get_logger(name: str):
    """Get a structured logger."""
    return structlog.get_logger(name)
```

**Usage**:
```python
# Before:
print(f"[Agent 1] Parsed {len(cleaned)} emails")

# After:
logger = get_logger(__name__)
logger.info("emails_parsed", count=len(cleaned), agent="1")
```

**Benefits**:
- Searchable logs (can query by field)
- Log levels (DEBUG, INFO, WARNING, ERROR)
- Context propagation
- JSON output for production

**Effort**: 6 hours (replace all prints)  
**Impact**: Production-grade logging

---

### 2.2 Add Retry Logic with Exponential Backoff (Day 3-4)

**Problem**: LLM calls fail without retries

**Solution**: Use `tenacity` library:

```python
# src/utils/retry.py
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)
from langchain_core.exceptions import LangChainException
import structlog

logger = structlog.get_logger(__name__)

def retry_llm_call():
    """Decorator for retrying LLM calls with exponential backoff."""
    return retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
        retry=retry_if_exception_type((
            LangChainException,
            TimeoutError,
            ConnectionError
        )),
        before_sleep=lambda retry_state: logger.warning(
            "llm_call_retry",
            attempt=retry_state.attempt_number,
            exception=str(retry_state.outcome.exception())
        )
    )
```

**Usage**:
```python
@retry_llm_call()
def extract_project_intelligence_llm(...):
    llm = get_llm()
    response = llm.invoke(prompt)
    return json.loads(response.content)
```

**Effort**: 2 hours  
**Impact**: Resilient to transient failures

---

### 2.3 Implement Custom Exceptions (Day 4)

**Problem**: Generic exceptions lose context

**Solution**: Create exception hierarchy:

```python
# src/exceptions.py
class GraphMailException(Exception):
    """Base exception for GRAPHMAIL."""
    pass

class ConfigurationError(GraphMailException):
    """Invalid configuration."""
    pass

class LLMException(GraphMailException):
    """LLM-related errors."""
    pass

class ExtractionError(LLMException):
    """Failed to extract intelligence."""
    def __init__(self, project_id: str, reason: str):
        self.project_id = project_id
        self.reason = reason
        super().__init__(f"Extraction failed for {project_id}: {reason}")

class VerificationError(LLMException):
    """Failed to verify fact."""
    def __init__(self, claim: str, evidence_ids: list[str]):
        self.claim = claim
        self.evidence_ids = evidence_ids
        super().__init__(f"Cannot verify: {claim}")

class GraphBuildError(GraphMailException):
    """Failed to build graph."""
    pass
```

**Usage**:
```python
# Instead of:
raise ValueError("Could not parse LLM response")

# Use:
raise ExtractionError(
    project_id=project_id,
    reason="LLM returned invalid JSON"
)
```

**Effort**: 2 hours  
**Impact**: Better error messages, easier debugging

---

## Phase 3: Add Tests (Week 2)

### 3.1 Test Infrastructure (Day 5)

**Setup**:
```bash
pip install pytest pytest-cov pytest-asyncio pytest-mock

# Create pytest configuration
cat > pytest.ini << 'EOF'
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --cov=src
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80
EOF
```

**Fixtures**:
```python
# tests/conftest.py
import pytest
from unittest.mock import Mock

@pytest.fixture
def sample_emails():
    """Sample email data for testing."""
    return [
        {
            'message_id': 'msg_001',
            'from': 'consultant@example.com',
            'to': ['client@example.com'],
            'subject': 'Project Kickoff',
            'date': '2026-03-25',
            'body_text': 'Starting brand book project...'
        },
        # ... more emails ...
    ]

@pytest.fixture
def mock_llm():
    """Mock LLM for testing."""
    llm = Mock()
    llm.invoke.return_value = Mock(
        content=json.dumps({
            "project_id": "project_001",
            "project_name": "Test Project",
            # ... mock response ...
        })
    )
    return llm

@pytest.fixture
def mock_graph():
    """Mock NetworkX graph."""
    import networkx as nx
    G = nx.DiGraph()
    G.add_node('project_001', node_type='Project', name='Test')
    return G
```

**Effort**: 4 hours

---

### 3.2 Unit Tests (Day 6-7)

**Agent 1 Tests** (expand existing):
```python
# tests/agents/test_agent1_parser.py
def test_parse_email_thread_removes_signature(sample_emails):
    """Test signature removal."""
    email = {
        'from': 'test@example.com',
        'body_text': 'Email body\n\nBest regards,\nJohn'
    }
    result = parse_email_thread(email)
    assert 'Best regards' not in result['body_clean']

def test_group_emails_by_project_clusters_similar_subjects():
    """Test project grouping."""
    emails = [
        {'subject': 'Brand Book - Initial Draft', ...},
        {'subject': 'Re: Brand Book - Initial Draft', ...},
        {'subject': 'Financial Portal Setup', ...}
    ]
    groups = group_emails_by_project(emails)
    assert len(groups) == 2  # 2 distinct projects
```

**Agent 2 Tests** (new):
```python
# tests/agents/test_agent2_extractor.py
from unittest.mock import patch

@patch('src.agents.agent2_extractor.get_llm')
def test_extract_project_intelligence_success(mock_get_llm, sample_emails):
    """Test successful extraction."""
    mock_llm = Mock()
    mock_llm.invoke.return_value = Mock(content=json.dumps({
        "project_id": "project_001",
        "project_name": "Test Project",
        "evidence": ["msg_001"],
        "project_type": "Design/Branding",
        "topics": [{"topic": "API", "evidence": ["msg_001"]}],
        # ... full structure ...
    }))
    mock_get_llm.return_value = mock_llm
    
    result = extract_project_intelligence_llm(
        project_id="project_001",
        project_name="Test",
        emails=sample_emails
    )
    
    assert result['project_name'] == "Test Project"
    assert len(result['topics']) == 1
    mock_llm.invoke.assert_called_once()

@patch('src.agents.agent2_extractor.get_llm')
def test_extract_handles_json_parse_error(mock_get_llm, sample_emails):
    """Test graceful handling of malformed JSON."""
    mock_llm = Mock()
    mock_llm.invoke.return_value = Mock(content="Not JSON")
    mock_get_llm.return_value = mock_llm
    
    with pytest.raises(ExtractionError) as exc_info:
        extract_project_intelligence_llm(
            project_id="project_001",
            project_name="Test",
            emails=sample_emails
        )
    
    assert "project_001" in str(exc_info.value)
```

**Agent 3 Tests** (new):
```python
# tests/agents/test_agent3_verifier.py
@patch('src.agents.agent3_verifier.get_llm')
def test_verify_fact_returns_true_for_supported_claim(mock_get_llm):
    """Test fact verification with valid evidence."""
    mock_llm = Mock()
    mock_llm.invoke.return_value = Mock(
        content='{"supported": true, "reasoning": "Directly stated"}'
    )
    mock_get_llm.return_value = mock_llm
    
    builder = GraphBuilder()
    result = builder.verify_fact(
        claim="Project named StartupCo",
        evidence_ids=["msg_001"],
        source_emails=[
            {'message_id': 'msg_001', 'body_clean': 'StartupCo project...'}
        ]
    )
    
    assert result is True

def test_verify_fact_returns_false_for_missing_evidence():
    """Test that facts without evidence are rejected."""
    builder = GraphBuilder()
    result = builder.verify_fact(
        claim="Some claim",
        evidence_ids=[],  # No evidence
        source_emails=[]
    )
    
    assert result is False
```

**Effort**: 16 hours  
**Coverage Target**: 80%+

---

## Phase 4: Performance Optimization (Week 3)

### 4.1 Async LLM Calls (Day 8-9)

**Problem**: Sequential processing is 5x slower

**Solution**: Async/await with `asyncio`:

```python
# src/agents/agent2_extractor_async.py
from langchain_openai import AsyncChatOpenAI
import asyncio

async def extract_project_intelligence_async(
    project_id: str,
    project_name: str,
    emails: list[dict]
) -> dict:
    """Async version of extraction."""
    llm = AsyncChatOpenAI(model="gpt-4o", temperature=0)
    prompt = build_extraction_prompt(project_id, project_name, emails)
    
    response = await llm.ainvoke(prompt)
    return json.loads(response.content)

async def agent_2_extractor_async(state: dict) -> dict:
    """Process all projects concurrently."""
    tasks = []
    
    for project_id, project_data in state['project_groups'].items():
        emails = [
            e for e in state['cleaned_emails']
            if e['message_id'] in project_data['email_ids']
        ]
        
        task = extract_project_intelligence_async(
            project_id,
            project_data['project_name'],
            emails
        )
        tasks.append(task)
    
    # Run all extractions concurrently
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Filter out failures
    intelligence = [r for r in results if not isinstance(r, Exception)]
    
    logger.info(
        "extraction_complete",
        total=len(tasks),
        successful=len(intelligence),
        failed=len(tasks) - len(intelligence)
    )
    
    return {"project_intelligence": intelligence}
```

**LangGraph Integration**:
```python
# src/workflow_async.py
from langgraph.graph import StateGraph

async def run_pipeline_async(raw_emails, raw_calendar):
    """Async pipeline execution."""
    workflow = StateGraph(ProjectGraphState)
    
    # Agent 1 stays sync (no LLM)
    workflow.add_node("parse", agent_1_parser)
    
    # Agent 2 & 3 are async
    workflow.add_node("extract", agent_2_extractor_async)
    workflow.add_node("verify", agent_3_verifier_async)
    workflow.add_node("evaluate", evaluation_node)
    
    # ... rest of workflow ...
    
    graph = workflow.compile()
    result = await graph.ainvoke({
        "raw_emails": raw_emails,
        "raw_calendar": raw_calendar
    })
    
    return result
```

**Expected Speedup**: 5-6x faster for 50+ projects

**Effort**: 12 hours

---

### 4.2 Add Caching (Day 10)

**Problem**: Re-processing same emails wastes money

**Solution**: Redis-backed LLM response cache:

```python
# src/utils/cache.py
import hashlib
import json
from redis import Redis
from functools import wraps

redis_client = Redis(host='localhost', port=6379, decode_responses=True)

def cache_llm_response(ttl: int = 3600):
    """Cache LLM responses by prompt hash."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key from prompt
            prompt = kwargs.get('prompt') or args[0]
            cache_key = f"llm:{hashlib.sha256(prompt.encode()).hexdigest()}"
            
            # Check cache
            cached = redis_client.get(cache_key)
            if cached:
                logger.debug("cache_hit", key=cache_key)
                return json.loads(cached)
            
            # Call LLM
            result = await func(*args, **kwargs)
            
            # Store in cache
            redis_client.setex(
                cache_key,
                ttl,
                json.dumps(result)
            )
            logger.debug("cache_miss", key=cache_key)
            
            return result
        return wrapper
    return decorator

# Usage
@cache_llm_response(ttl=3600)  # 1 hour
async def extract_project_intelligence_async(...):
    # ... existing code ...
```

**Expected Savings**: 90% reduction for duplicate queries

**Effort**: 6 hours

---

## Phase 5: Database Migration (Week 4)

### 5.1 PostgreSQL Schema (Day 11-12)

**Migration from JSON files → PostgreSQL**:

```python
# src/models/database.py
from sqlalchemy import create_engine, Column, String, JSON, ForeignKey, Table
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

# Association table for many-to-many
project_topics = Table(
    'project_topics',
    Base.metadata,
    Column('project_id', String, ForeignKey('projects.id')),
    Column('topic_id', Integer, ForeignKey('topics.id'))
)

class Project(Base):
    __tablename__ = 'projects'
    
    id = Column(String, primary_key=True)
    name = Column(String, nullable=False, index=True)
    project_type = Column(String, index=True)
    timeline = Column(JSON)
    scope = Column(String)
    phase = Column(String)
    evidence = Column(JSON)  # List of message IDs
    created_at = Column(DateTime, default=datetime.utcnow)
    
    topics = relationship("Topic", secondary=project_topics, back_populates="projects")
    challenges = relationship("Challenge", back_populates="project")
    
class Topic(Base):
    __tablename__ = 'topics'
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True, index=True)
    evidence = Column(JSON)
    
    projects = relationship("Project", secondary=project_topics, back_populates="topics")

class Challenge(Base):
    __tablename__ = 'challenges'
    
    id = Column(Integer, primary_key=True)
    project_id = Column(String, ForeignKey('projects.id'))
    description = Column(String, nullable=False)
    category = Column(String)
    raised_date = Column(Date)
    evidence = Column(JSON)
    
    project = relationship("Project", back_populates="challenges")
    resolutions = relationship("Resolution", back_populates="challenge")

# + Resolution, Edge models...
```

**Migration Script**:
```python
# scripts/migrate_json_to_db.py
from sqlalchemy.orm import Session
import json

def migrate_knowledge_graph(json_path: str, db_session: Session):
    """Migrate JSON knowledge graph to PostgreSQL."""
    with open(json_path) as f:
        graph_data = json.load(f)
    
    # Migrate nodes
    for node in graph_data['nodes']:
        if node['node_type'] == 'Project':
            project = Project(
                id=node['id'],
                name=node['name'],
                project_type=node.get('project_type'),
                # ... map fields ...
            )
            db_session.add(project)
    
    db_session.commit()
```

**Effort**: 16 hours

---

## Phase 6: API Layer (Week 4)

### 6.1 FastAPI Backend (Day 13-14)

**RESTful API**:

```python
# api/main.py
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel

app = FastAPI(
    title="GRAPHMAIL API",
    version="1.0.0",
    description="Extract verifiable knowledge from emails"
)

class ExtractionRequest(BaseModel):
    emails: list[dict]
    calendar_events: list[dict] = []

@app.post("/api/v1/extract", status_code=202)
async def extract_projects(
    request: ExtractionRequest,
    background_tasks: BackgroundTasks
):
    """Start extraction job (async)."""
    job_id = str(uuid.uuid4())
    
    # Queue extraction in background
    background_tasks.add_task(
        run_extraction_job,
        job_id=job_id,
        emails=request.emails,
        calendar_events=request.calendar_events
    )
    
    return {
        "job_id": job_id,
        "status": "queued",
        "message": "Extraction started"
    }

@app.get("/api/v1/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Check extraction job status."""
    job = get_job_from_db(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {
        "job_id": job.id,
        "status": job.status,  # queued, running, complete, failed
        "progress": job.progress,
        "result_url": f"/api/v1/results/{job.result_id}" if job.complete else None
    }

@app.get("/api/v1/projects")
async def list_projects(
    project_type: str | None = None,
    skip: int = 0,
    limit: int = 50
):
    """List all projects with filtering."""
    query = db.query(Project)
    
    if project_type:
        query = query.filter(Project.project_type == project_type)
    
    projects = query.offset(skip).limit(limit).all()
    return [project.to_dict() for project in projects]
```

**Effort**: 16 hours

---

## Summary

### Total Effort by Phase

| Phase | Days | Hours | Priority |
|-------|------|-------|----------|
| Phase 1: Code Organization | 2 | 15 | 🔴 CRITICAL |
| Phase 2: Error Handling | 2 | 10 | 🔴 CRITICAL |
| Phase 3: Tests | 2 | 20 | ⚠️ HIGH |
| Phase 4: Performance | 3 | 18 | ⚠️ HIGH |
| Phase 5: Database | 2 | 16 | 🟡 MEDIUM |
| Phase 6: API Layer | 2 | 16 | 🟡 MEDIUM |
| **TOTAL** | **13 days** | **95 hours** | - |

### Success Metrics

**Before Refactoring**:
- Code duplication: 27.5%
- Test coverage: 20%
- Processing time (100 emails): 156 seconds
- Deployability: 2/10

**After Refactoring**:
- Code duplication: <5%
- Test coverage: 80%+
- Processing time (100 emails): 27 seconds (5.8x faster)
- Deployability: 9/10

### Non-Goals

❌ **Not doing in this phase**:
- Complete UI rewrite (separate project)
- Multi-tenancy (future)
- Advanced analytics (future)
- Real-time collaboration (future)

---

## Implementation Order

**Week 1**: Foundation
1. ✅ Delete demo files
2. ✅ Extract utilities
3. ✅ Add configuration
4. ✅ Replace prints with logging
5. ✅ Add retry logic

**Week 2**: Hardening
1. ✅ Custom exceptions
2. ✅ Test infrastructure
3. ✅ Unit tests for all agents
4. ✅ Integration tests

**Week 3**: Performance
1. ✅ Async LLM calls
2. ✅ Response caching
3. ✅ Optimize graph building

**Week 4**: Persistence
1. ✅ PostgreSQL setup
2. ✅ Migration scripts
3. ✅ FastAPI endpoints

**Outcome**: Production-ready codebase in 4 weeks


