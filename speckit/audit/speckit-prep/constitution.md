# GRAPHMAIL Development Constitution

**Version**: 1.0  
**Effective Date**: November 17, 2025  
**Status**: IMMUTABLE (changes require full team consensus)

---

## Purpose

This constitution defines the **immutable principles** that govern GRAPHMAIL development. All code, architecture decisions, and features must align with these principles.

---

## Article I: Zero-Hallucination Principle

### **"Every Fact Must Have Proof"**

**Rule**: No extracted fact enters the knowledge graph without verifiable evidence.

**Implementation**:
1. Every node in the graph MUST have an `evidence` field containing message IDs
2. Agent 3 (Verifier) MUST validate every fact before adding to graph
3. Facts without evidence are logged in `rejected_facts.json`
4. Trust Score penalizes hallucinations at 20% weight

**Enforcement**:
```python
# REQUIRED in all agent code
def add_node_to_graph(node_data: dict):
    if not node_data.get('evidence'):
        raise ValueError("Cannot add node without evidence")
    
    # Verify evidence exists in source
    if not verify_evidence_exists(node_data['evidence']):
        log_rejected_fact(node_data)
        return False
    
    graph.add_node(**node_data)
```

**Exceptions**: NONE. This principle is absolute.

---

## Article II: Sequential Processing Integrity

### **"Respect Temporal Order"**

**Rule**: Email processing must preserve chronological order to capture project evolution.

**Implementation**:
1. Agent 1 processes emails in date order
2. Timeline information is preserved in all nodes
3. Challenges are linked to raised_date
4. Resolutions are linked to resolved_date

**Rationale**: Project intelligence emerges over time. Processing out-of-order loses causal relationships.

**Enforcement**:
- Sort emails by date before processing
- Add timestamps to all extracted entities
- Timeline view shows chronological evolution

---

## Article III: Graph-First Architecture

### **"The Graph is the Source of Truth"**

**Rule**: All project intelligence is stored as a queryable knowledge graph, not flat data.

**Implementation**:
1. NetworkX DiGraph is the core data structure
2. Nodes represent entities (Projects, Topics, Challenges, Resolutions)
3. Edges represent relationships (HAS_TOPIC, FACED_CHALLENGE, RESOLVED_BY)
4. Flat exports (JSON, GraphML) are derived FROM the graph

**Anti-Pattern**: ❌ Storing data in disconnected JSON objects

**Correct Pattern**: ✅ Graph with traversable relationships

**Enforcement**:
- Primary storage: NetworkX graph object
- Secondary storage: Graph database (Neo4j for production)
- Exports are read-only views

---

## Article IV: LLM Verification Layer

### **"Trust but Verify"**

**Rule**: LLM outputs are treated as hypotheses until verified.

**Implementation**:
1. Agent 2 (Extractor) generates hypotheses
2. Agent 3 (Verifier) validates each hypothesis
3. Unverified hypotheses are rejected
4. Verification uses a second LLM call to check evidence

**Rationale**: LLMs hallucinate. We prevent this with dual-pass architecture.

**Enforcement**:
```python
# Agent 2: Extract (hypothesis)
extracted_fact = llm.invoke("Extract project name from emails...")

# Agent 3: Verify (validation)
is_valid = verify_llm.invoke(
    f"Does this evidence support: {extracted_fact}?"
)

if not is_valid:
    rejected_facts.append(extracted_fact)
```

---

## Article V: Evidence Traceability

### **"Audit Trail for Every Claim"**

**Rule**: Users must be able to trace any fact back to source emails.

**Implementation**:
1. Every node has `evidence: [message_ids]`
2. Every edge has `evidence: [message_ids]`
3. UI displays evidence chips (click to view source email)
4. Trust Score measures traceability at 35% weight

**User Story**: "As a consultant, I can click any fact and see the email that proves it."

**Enforcement**:
- Schema validation requires `evidence` field
- UI components render evidence citations
- API endpoints return evidence with every fact

---

## Article VI: Test-Driven Development

### **"No Code Without Tests"**

**Rule**: All production code must have corresponding unit tests.

**Implementation**:
1. Minimum 80% code coverage
2. Tests must pass before merging to main
3. Mock LLMs in tests (no real API calls)
4. Integration tests for full pipeline

**Enforcement**:
```yaml
# .github/workflows/ci.yml
- name: Run tests
  run: pytest --cov=src --cov-fail-under=80
```

**Exceptions**:
- Exploratory scripts in `scripts/`
- One-off data analysis notebooks
- Demo code (but dashboard must be tested)

---

## Article VII: API-First Design

### **"Build for Integration"**

**Rule**: Core functionality exposed via clean API, not just CLI.

**Implementation**:
1. FastAPI RESTful endpoints
2. OpenAPI documentation auto-generated
3. Versioned endpoints (`/api/v1/`)
4. JSON request/response format

**User Story**: "As a developer, I can integrate GRAPHMAIL into my app via HTTP API."

**Enforcement**:
- All features accessible via API
- CLI is a thin wrapper around API
- Streamlit dashboard calls API (not direct imports)

---

## Article VIII: Security by Default

### **"Fail Secure, Not Open"**

**Rule**: Security is non-negotiable. Conservative defaults.

**Implementation**:
1. All user inputs sanitized before LLM processing
2. API endpoints require authentication by default
3. Secrets in environment variables (never hardcoded)
4. Rate limiting on all LLM-calling endpoints

**Enforcement**:
```python
# REQUIRED on all public endpoints
@app.post("/api/v1/extract")
@rate_limit(max_calls=10, period=60)  # 10 calls per minute
@require_auth()
async def extract_projects(request: ExtractionRequest):
    # Sanitize input
    request = sanitize_input(request)
    # ... rest of logic
```

**Violations**: Security issues are P0 (highest priority) and block release.

---

## Article IX: Performance Budgets

### **"Speed is a Feature"**

**Rule**: System must process emails at minimum throughput.

**Performance Requirements**:
- 100 emails processed in <30 seconds
- Dashboard loads in <2 seconds
- API response time <500ms (excluding LLM wait)
- Graph with 10K nodes renders in <3 seconds

**Implementation**:
1. Async LLM calls for parallel processing
2. Response caching (Redis)
3. Database indexing on frequently queried fields
4. Graph layout pre-computed and cached

**Enforcement**:
- Benchmark tests in CI
- Performance regression alerts
- Budget violations block merge

---

## Amendments

**Process for Amending Constitution**:
1. Proposal must be written as RFC document
2. Full team review (minimum 1 week)
3. Unanimous approval required
4. Version number incremented (1.0 → 2.0)

**Historical Amendments**: None (initial version)

---

## Enforcement Mechanisms

### Pre-Commit Hooks
```bash
#!/bin/bash
# Check for hardcoded API keys
if git diff --cached | grep -q "sk-"; then
    echo "❌ API key detected!"
    exit 1
fi

# Check for missing tests
changed_files=$(git diff --cached --name-only | grep "^src/.*\.py$")
for file in $changed_files; do
    test_file="tests/test_${file#src/}"
    if [[ ! -f "$test_file" ]]; then
        echo "⚠️  Warning: No test file for $file"
    fi
done
```

### CI/CD Pipeline
```yaml
- name: Validate Constitution
  run: |
    # Check test coverage
    pytest --cov=src --cov-fail-under=80
    
    # Check for hardcoded values
    pylint --disable=all --enable=bad-builtin src/
    
    # Check API documentation
    python -m pytest tests/test_api_docs.py
```

### Code Review Checklist
- [ ] Does this change preserve zero-hallucination guarantee?
- [ ] Are new facts traceable to evidence?
- [ ] Are LLM outputs verified before use?
- [ ] Is there test coverage for new code?
- [ ] Are performance budgets met?
- [ ] Is user input sanitized?

---

## Principles in Action

### Example 1: Adding New Node Type

**Scenario**: Developer wants to add "Person" nodes to graph.

**Constitution Compliance**:
✅ Article I: Person nodes must have `evidence` field  
✅ Article III: Must be graph nodes (not separate collection)  
✅ Article V: Must be traceable to source emails  
✅ Article VI: Must write tests for person extraction  

**Implementation**:
```python
class PersonNode:
    id: str
    name: str
    email: str
    evidence: list[str]  # REQUIRED by Article I
    
    def validate(self):
        if not self.evidence:
            raise ConstitutionViolation("Article I: Missing evidence")

# Tests REQUIRED by Article VI
def test_person_extraction_has_evidence():
    person = extract_person_from_email(sample_email)
    assert len(person.evidence) > 0
```

### Example 2: Optimizing Performance

**Scenario**: Pipeline is slow, developer wants to skip verification.

**Constitution Compliance**:
❌ Article IV: Cannot skip LLM verification layer  
✅ Article IX: Can optimize verification implementation  

**Correct Approach**:
- Keep verification step (Article IV)
- Make verification async (Article IX)
- Cache verification results (Article IX)
- Batch verifications (Article IX)

**Incorrect Approach**:
- ❌ Remove verification entirely
- ❌ Make verification optional
- ❌ Skip verification for "trusted" sources

---

## Living Document

This constitution is **immutable** in spirit but **evolving** in practice. Core principles (Articles I-V) cannot change. Implementation details (Articles VI-IX) can be amended through RFC process.

**Core Principles** (Immutable):
- Zero hallucination
- Graph-first architecture
- Evidence traceability
- LLM verification
- Sequential processing

**Best Practices** (Amendable):
- Test coverage targets
- Performance budgets
- API design patterns
- Security controls

---

## Conclusion

This constitution exists to prevent **architectural drift** and ensure GRAPHMAIL remains true to its core mission: **extracting verifiable knowledge from emails with zero hallucination.**

When in doubt, ask: **"Does this change uphold the zero-hallucination guarantee?"**

If no, don't do it.  
If yes, proceed with tests and verification.

**Signed**,  
The GRAPHMAIL Development Team  
November 17, 2025


