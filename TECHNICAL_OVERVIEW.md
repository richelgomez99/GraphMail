# 🔬 Technical Overview

**Graph-First Project Intelligence System - Deep Dive**

---

## 📋 System Architecture

### High-Level Flow

```
Input Data
    │
    ├─ Raw Emails (JSON)
    └─ Calendar Events (JSON)
    │
    ▼
┌─────────────────────────────────────┐
│ Agent 1: Email Parser               │
│ - parse_email_thread()              │
│ - remove_signature()                │
│ - remove_forward_chains()           │
│ - group_emails_by_project()         │
│ - link_calendar_events()            │
└─────────────┬───────────────────────┘
              │
              ▼ State: cleaned_emails, project_groups
┌─────────────────────────────────────┐
│ Agent 2: Intelligence Extractor     │
│ - extract_project_intelligence_llm()│
│ - LLM-powered structured extraction │
│ - Attach evidence to every fact     │
└─────────────┬───────────────────────┘
              │
              ▼ State: project_intelligence
┌─────────────────────────────────────┐
│ Agent 3: Verifier & Graph Builder   │
│ - GraphBuilder.verify_and_add_*()   │
│ - verify_fact() for each claim      │
│ - Build NetworkX DiGraph            │
└─────────────┬───────────────────────┘
              │
              ▼ State: verified_graph
┌─────────────────────────────────────┐
│ Evaluation Node                     │
│ - calculate_trust_score()           │
│ - 4 weighted components             │
└─────────────┬───────────────────────┘
              │
              ▼
Output: Graph (JSON/GraphML) + Metrics
```

---

## 🧩 Component Details

### Agent 1: Email Parser & Project Identifier

**Purpose**: Clean and structure raw email data

**Input**:
- `raw_emails`: List[Dict] - Raw email threads
- `raw_calendar`: List[Dict] - Calendar events

**Processing**:

1. **Email Cleaning**
   ```python
   def parse_email_thread(email_obj):
       # Remove signatures (regex patterns)
       body = remove_signature(email_obj['body_text'])
       
       # Remove forward chains
       body = remove_forward_chains(body)
       
       # Extract participants
       participants = extract_all_participants(email_obj)
       
       return cleaned_email_dict
   ```

2. **Project Identification**
   - Extract signals from subject lines
   - Keywords: "project", "brand book", "portal", "strategy"
   - Confidence scoring based on explicitness

3. **Project Clustering**
   ```python
   def group_emails_by_project(cleaned_emails):
       # Normalize project names for clustering
       # Subject similarity + keyword matching
       # Returns: {project_id: {email_ids, project_name}}
   ```

4. **Calendar Linking**
   - Match by: participant overlap + temporal proximity (±2 days)

**Output**:
- `cleaned_emails`: List of parsed, clean emails
- `project_groups`: Dict mapping project_id to email clusters

**Key Design Decision**: No LLM in Agent 1
- **Why**: Deterministic parsing is faster and cheaper
- **Trade-off**: May miss nuanced project boundaries
- **Mitigation**: Agent 2 can refine project identification

---

### Agent 2: Project Intelligence Extractor

**Purpose**: Extract structured project data using LLMs

**Input**:
- `cleaned_emails`: From Agent 1
- `project_groups`: From Agent 1

**LLM Prompt Structure**:

```python
prompt = f"""Extract project intelligence from emails.

Emails:
{formatted_email_context}

Extract:
1. Project Name (refine from clustering)
2. Project Type (Design/Branding, Financial, Strategy, etc.)
3. Topics (specific themes: "API Integration", "Brand Guidelines")
4. Scope (high-level deliverables)
5. Timeline (start/end dates)
6. Challenges (problems, blockers, concerns)
7. Resolutions (solutions, decisions)
8. Phase (Scoping/Execution/Challenge Resolution/Delivery)

CRITICAL: Include evidence (message_ids) for EVERY fact.

Output JSON: {{ project_id, project_name, evidence, ... }}
"""
```

**Evidence Enforcement**:
- Prompt explicitly requires message_ids
- Schema validation ensures evidence fields exist
- Agent 3 will verify these citations

**Extraction Strategy**:
- Process each project group independently
- Limit emails to first 15 (context window management)
- Format emails with message_id, from, date, subject, body preview

**Output**:
- `project_intelligence`: List[ProjectIntelligence] - Structured extraction results

**Key Design Decision**: Structured extraction over free-form
- **Why**: Ensures machine-readable output, enables verification
- **Trade-off**: May miss nuanced information
- **Mitigation**: "Description" fields allow flexibility

---

### Agent 3: Verification & Graph Builder

**Purpose**: Verify facts and build knowledge graph with zero hallucination

**Input**:
- `project_intelligence`: From Agent 2
- `cleaned_emails`: From Agent 1 (for verification)

**Core Algorithm**:

```python
class GraphBuilder:
    def verify_and_add_project(self, project_data, source_emails):
        # 1. Verify project name
        if not self.verify_fact(
            claim=project_data['project_name'],
            evidence_ids=project_data['evidence'],
            source_emails=source_emails
        ):
            self.rejected_facts.append(...)
            return None
        
        # 2. Add verified project node
        self.graph.add_node(project_id, **attributes)
        
        # 3. Verify and add topics, challenges, resolutions
        for topic in project_data['topics']:
            if self.verify_fact(topic):
                self.graph.add_node(topic_id, ...)
                self.graph.add_edge(project_id, topic_id, ...)
        
        return project_id
```

**Verification Process**:

```python
def verify_fact(self, claim, evidence_ids, source_emails):
    # 1. Retrieve evidence emails by ID
    evidence_emails = [e for e in source_emails 
                       if e['message_id'] in evidence_ids]
    
    if not evidence_emails:
        return False  # No evidence = reject
    
    # 2. Use LLM to verify claim against evidence
    prompt = f"""Does this evidence support this claim?
    
    Claim: {claim}
    Evidence: {evidence_emails}
    
    Answer YES only if directly stated or strongly implied.
    Output: {{"supported": true/false, "reasoning": "..."}}
    """
    
    response = llm.invoke(prompt)
    return response['supported']
```

**Graph Schema**:

```
Nodes:
  - Project: {node_type, name, project_type, timeline, scope, phase, evidence}
  - Topic: {node_type, name, evidence}
  - Challenge: {node_type, description, category, raised_date, evidence}
  - Resolution: {node_type, description, methodology, resolved_date, evidence}

Edges:
  - HAS_TOPIC: Project → Topic
  - FACED_CHALLENGE: Project → Challenge
  - RESOLVED_BY: Challenge → Resolution
```

**Output**:
- `verified_graph`: NetworkX DiGraph
- `rejected_facts`: List of claims that failed verification
- `graph_json`: Serialized graph (node-link format)

**Key Design Decision**: Verification layer prevents hallucination
- **Why**: LLMs can hallucinate facts not in source
- **Trade-off**: May reject some valid but weakly-evidenced facts
- **Mitigation**: Conservative threshold (better false negative than false positive)

---

## 📊 Custom Evaluation Metric: Trust Score

### Formula Breakdown

```
Trust Score = Σ (Component_i × Weight_i)

Components:
1. Fact_Traceability       (weight: 0.35)
2. Extraction_Completeness (weight: 0.25)
3. Phase_Inference_Accuracy (weight: 0.20)
4. Anti_Hallucination      (weight: 0.20)
```

### Component Calculations

#### 1. Fact Traceability (35%)

```python
def calculate_fact_traceability(graph, source_emails):
    total_facts = graph.number_of_nodes() + graph.number_of_edges()
    traceable_facts = 0
    
    source_msg_ids = set(e['message_id'] for e in source_emails)
    
    for node in graph.nodes():
        evidence = graph.nodes[node].get('evidence', [])
        if any(eid in source_msg_ids for eid in evidence):
            traceable_facts += 1
    
    # Same for edges...
    
    return traceable_facts / total_facts
```

**Measures**: What % of facts have valid evidence citations?

**Why 35%**: Most critical - production systems need traceability

#### 2. Extraction Completeness (25%)

```python
def calculate_extraction_completeness(graph, ground_truth):
    gt_facts = count_ground_truth_facts(ground_truth)
    correctly_extracted = count_matching_facts(graph, ground_truth)
    
    return correctly_extracted / gt_facts
```

**Measures**: What % of ground truth facts were extracted?

**Why 25%**: Important for coverage, but less critical than traceability

**Note**: Without ground truth, estimated using heuristics (facts per email, evidence coverage)

#### 3. Phase Inference Accuracy (20%)

```python
def calculate_phase_accuracy(graph, ground_truth):
    project_nodes = [n for n in graph.nodes() 
                     if graph.nodes[n]['node_type'] == 'Project']
    
    correct = sum(1 for node in project_nodes
                  if graph.nodes[node]['phase'] == ground_truth[node]['phase'])
    
    return correct / len(project_nodes)
```

**Measures**: What % of project phases correctly inferred?

**Why 20%**: Key value-add for consultants, but subjective

#### 4. Anti-Hallucination (20%)

```python
def detect_hallucinations(graph, source_emails):
    hallucinations = []
    source_msg_ids = set(e['message_id'] for e in source_emails)
    
    for node in graph.nodes():
        evidence = graph.nodes[node].get('evidence', [])
        
        # No evidence = hallucination
        if not evidence:
            hallucinations.append(node)
        
        # Invalid evidence IDs = hallucination
        elif not any(eid in source_msg_ids for eid in evidence):
            hallucinations.append(node)
    
    return hallucinations

hallucination_rate = len(hallucinations) / total_facts
anti_hallucination_score = 1 - hallucination_rate
```

**Measures**: 1 - (hallucinated facts / total facts)

**Why 20%**: Production killer, but Agent 3 should prevent this

### Weight Rationale

| Component | Weight | Rationale |
|-----------|--------|-----------|
| Traceability | 35% | Must-have for production. Every fact needs proof. |
| Completeness | 25% | Important to catch key information. |
| Phase Accuracy | 20% | Consultant-specific value-add. |
| Anti-Hallucination | 20% | Critical for trust, but verification layer handles it. |

---

## 🔧 Implementation Details

### Technology Stack

```
Framework:    LangGraph 0.0.50+
LLMs:         OpenAI GPT-4 / Anthropic Claude-3
Graph:        NetworkX 3.2+
Data:         Pydantic 2.0+ (validation)
Lang:         Python 3.9+
```

### State Management (LangGraph)

```python
class ProjectGraphState(TypedDict):
    # Input
    raw_emails: List[Dict]
    raw_calendar: List[Dict]
    
    # Agent 1 → Agent 2
    cleaned_emails: List[Dict]
    project_groups: Dict[str, Dict]
    
    # Agent 2 → Agent 3
    project_intelligence: List[Dict]
    
    # Agent 3 → Evaluation
    verified_graph: nx.DiGraph
    rejected_facts: List[Dict]
    
    # Final output
    graph_json: Dict
    evaluation_metrics: Dict
```

**State Flow**: Each agent reads previous state, returns updates

### LangGraph Workflow

```python
workflow = StateGraph(ProjectGraphState)

workflow.add_node("parse", agent_1_parser)
workflow.add_node("extract", agent_2_extractor)
workflow.add_node("verify", agent_3_verifier)
workflow.add_node("evaluate", evaluation_node)

workflow.set_entry_point("parse")
workflow.add_edge("parse", "extract")
workflow.add_edge("extract", "verify")
workflow.add_edge("verify", "evaluate")
workflow.add_edge("evaluate", END)

graph_system = workflow.compile()
```

**Execution**: Sequential, no cycles, deterministic flow

---

## 🚀 Performance Characteristics

### Time Complexity

| Component | Complexity | Notes |
|-----------|-----------|-------|
| Agent 1 | O(n) | n = number of emails |
| Agent 2 | O(p × m) | p = projects, m = LLM latency |
| Agent 3 | O(f × v) | f = facts, v = verification latency |
| Total | O(n + p×m + f×v) | Sequential processing |

### Space Complexity

- **O(n)** for cleaned emails
- **O(f)** for graph (f = number of facts)
- **O(1)** for state (constant-size dicts)

### Scalability Strategies

1. **Agent 2 Parallelization**
   - Process project groups concurrently
   - Use async LLM calls

2. **Context Window Management**
   - Limit emails to first 15 per project
   - Truncate long email bodies

3. **Caching**
   - Cache LLM responses for verification
   - Reuse parsed emails across runs

4. **Incremental Updates**
   - New emails trigger only affected project updates
   - Graph merge instead of full rebuild

---

## 🔍 Edge Cases & Handling

### 1. Ambiguous Project Boundaries

**Problem**: Email could belong to multiple projects

**Solution**:
- Agent 1 uses strict clustering (subject-based)
- Agent 2 can re-assign if extraction reveals different project
- Human review for confidence < 0.7

### 2. Missing Evidence

**Problem**: Agent 2 fails to include message_ids

**Solution**:
- Schema validation enforces evidence field
- Agent 3 rejects facts without evidence
- Logged in `rejected_facts`

### 3. LLM Hallucination

**Problem**: LLM invents facts not in emails

**Solution**:
- Agent 3 verification layer
- Conservative threshold (direct statement > strong implication > weak inference)
- Trust Score penalizes hallucinations

### 4. Incomplete Email Threads

**Problem**: Missing emails in conversation

**Solution**:
- Agent 1 doesn't require complete threads
- Agent 2 extracts from available context
- Lower Trust Score reflects incompleteness

### 5. Large Email Volumes

**Problem**: Thousands of emails, context overflow

**Solution**:
- Agent 1 processes incrementally (no limit)
- Agent 2 limits to 15 emails per project (configurable)
- Sampling strategies for large projects

---

## 🏆 Why This Architecture Wins

### 1. Agent-Based Design ✅

- **LangGraph orchestration**: Industry-standard framework
- **Three distinct agents**: Clear separation of concerns
- **Sequential processing**: Handles temporal evolution

### 2. Verifiable Output ✅

- **Evidence citations**: Every fact → message_ids
- **Verification layer**: Agent 3 validates claims
- **Rejected facts log**: Transparency into what didn't pass

### 3. Custom Evaluation ✅

- **Trust Score**: Novel metric, not just accuracy
- **Weighted components**: Prioritizes production needs
- **Interpretable**: Each component independently meaningful

### 4. Production-Ready ✅

- **Error handling**: Try-catch in all agents
- **Logging**: Progress tracking at each step
- **Flexible I/O**: JSON/GraphML export
- **Configurable**: Easy to swap LLMs, adjust thresholds

### 5. Real-World Value ✅

- **Consultant pain point**: Actual user research
- **Queryable intelligence**: Graph enables complex queries
- **Institutional knowledge**: Reusable across projects

---

## 📝 Future Enhancements

### Phase 2 Features

1. **Incremental Updates**
   - Add new emails without full rebuild
   - Graph merge algorithm

2. **Query Interface**
   - Natural language → graph query
   - "Show all Financial projects with API challenges"

3. **Relationship Extraction**
   - Person-to-person connections
   - Company-to-company relationships

4. **Temporal Queries**
   - "What challenges arose in month 2?"
   - Project timeline visualization

5. **Multi-Modal**
   - Extract from attachments (PDFs, presentations)
   - Calendar event notes

---

## 📚 References

- **LangGraph**: https://github.com/langchain-ai/langgraph
- **NetworkX**: https://networkx.org/
- **Graph-First Design**: Inspired by knowledge graph research

---

**Technical reviewers**: See `src/` for implementation details.
