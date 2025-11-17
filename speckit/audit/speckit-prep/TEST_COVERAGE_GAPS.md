# TEST COVERAGE GAPS

**Current Coverage**: ~20% (only Agent 1 tested)  
**Target Coverage**: 80%+ (industry standard)  
**Gap**: 3,500+ lines of untested code

---

## Coverage Analysis

### Tested ✅
- **Agent 1 (Parser)**: 100% covered via `test_system.py`
  - Email parsing
  - Signature removal
  - Project grouping
  - Calendar linking

### Untested ❌
- **Agent 2 (Extractor)**: 0% covered (requires LLM mocking)
- **Agent 3 (Verifier)**: 0% covered (requires LLM mocking)
- **Workflow**: 0% covered (integration tests needed)
- **Trust Score**: 0% covered (metric calculations)
- **Demo Dashboard**: 0% covered (UI testing needed)

---

## Priority Test Suite

### 1. Agent 2 Tests (HIGH PRIORITY)

**File**: `tests/agents/test_agent2_extractor.py`  
**Lines to Cover**: ~307 (agent2_extractor.py)  
**Est. Time**: 12 hours

**Required Tests**:
```python
# Happy path
def test_extract_project_intelligence_success()
def test_extract_handles_multiple_projects()
def test_extract_preserves_evidence_ids()

# Error handling
def test_extract_handles_json_parse_error()
def test_extract_handles_llm_timeout()
def test_extract_handles_invalid_email_format()

# Edge cases
def test_extract_with_empty_email_list()
def test_extract_with_very_long_emails()
def test_extract_with_missing_required_fields()

# Validation
def test_extract_enforces_evidence_requirement()
def test_extract_validates_project_type()
def test_extract_validates_timeline_format()
```

---

### 2. Agent 3 Tests (HIGH PRIORITY)

**File**: `tests/agents/test_agent3_verifier.py`  
**Lines to Cover**: ~340 (agent3_verifier.py)  
**Est. Time**: 12 hours

**Required Tests**:
```python
# Verification logic
def test_verify_fact_returns_true_for_valid_evidence()
def test_verify_fact_returns_false_for_missing_evidence()
def test_verify_fact_returns_false_for_weak_evidence()

# Graph building
def test_add_project_node_success()
def test_add_project_rejects_without_evidence()
def test_add_topic_creates_edge()
def test_add_challenge_links_to_project()
def test_add_resolution_links_to_challenge()

# Error handling
def test_verify_handles_llm_error_gracefully()
def test_graph_building_continues_after_rejection()
def test_rejected_facts_are_logged()
```

---

### 3. Workflow Tests (MEDIUM PRIORITY)

**File**: `tests/test_workflow.py`  
**Lines to Cover**: ~150 (workflow.py)  
**Est. Time**: 8 hours

**Required Tests**:
```python
# Integration tests
def test_full_pipeline_end_to_end()
def test_pipeline_handles_agent_failure()
def test_pipeline_preserves_state_between_agents()

# State management
def test_state_contains_all_required_keys()
def test_state_updates_are_merged_correctly()

# Error propagation
def test_pipeline_stops_on_critical_error()
def test_pipeline_logs_all_errors()
```

---

### 4. Trust Score Tests (MEDIUM PRIORITY)

**File**: `tests/evaluation/test_trust_score.py`  
**Lines to Cover**: ~340 (trust_score.py)  
**Est. Time**: 6 hours

**Required Tests**:
```python
# Component calculations
def test_fact_traceability_calculation()
def test_extraction_completeness_calculation()
def test_phase_accuracy_calculation()
def test_hallucination_detection()

# Edge cases
def test_trust_score_with_zero_facts()
def test_trust_score_with_perfect_traceability()
def test_trust_score_without_ground_truth()

# Weighted formula
def test_trust_score_formula_is_correct()
def test_component_weights_sum_to_one()
```

---

### 5. Utilities Tests (LOW PRIORITY)

**File**: `tests/utils/test_data_loader.py`  
**Lines to Cover**: ~100  
**Est. Time**: 3 hours

**Required Tests**:
```python
def test_load_email_data_valid_json()
def test_load_email_data_invalid_json()
def test_load_calendar_data_valid()
def test_load_handles_missing_files()
```

---

## Test Infrastructure Setup

### pytest Configuration

```ini
# pytest.ini
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
    --tb=short
markers =
    slow: marks tests as slow (deselect with '-m "not slow"')
    integration: integration tests
    unit: unit tests
```

### Fixtures

```python
# tests/conftest.py
import pytest
from unittest.mock import Mock
import json

@pytest.fixture
def sample_emails():
    """Sample email data."""
    return [
        {
            'message_id': 'msg_001',
            'from': 'consultant@example.com',
            'to': ['client@example.com'],
            'subject': 'Project Kickoff',
            'date': '2026-03-25',
            'body_text': 'Starting the brand book project...'
        },
        # ... more samples
    ]

@pytest.fixture
def mock_llm():
    """Mock LLM that returns valid responses."""
    llm = Mock()
    llm.invoke.return_value = Mock(
        content=json.dumps({
            "project_id": "project_001",
            "project_name": "Test Project",
            "evidence": ["msg_001"],
            # ... full structure
        })
    )
    return llm

@pytest.fixture
def mock_verifier_llm():
    """Mock LLM for fact verification."""
    llm = Mock()
    llm.invoke.return_value = Mock(
        content='{"supported": true, "reasoning": "Directly stated"}'
    )
    return llm
```

---

## Coverage Targets by Module

| Module | Current | Target | Tests Needed |
|--------|---------|--------|--------------|
| agent1_parser.py | 100% | 100% | ✅ Done |
| agent2_extractor.py | 0% | 90% | 15 tests |
| agent3_verifier.py | 0% | 90% | 18 tests |
| workflow.py | 0% | 85% | 8 tests |
| trust_score.py | 0% | 90% | 12 tests |
| data_loader.py | 0% | 80% | 6 tests |
| schema.py | 0% | 70% | 5 tests |

**Total**: 64 new tests needed

---

## Testing Strategy

### Unit Tests (Fast, Isolated)
- Mock all LLM calls
- Test individual functions
- Run in < 5 seconds
- Tag with `@pytest.mark.unit`

### Integration Tests (Slow, Real Data)
- Use real sample emails
- Test agent interactions
- May take 10-30 seconds
- Tag with `@pytest.mark.integration`

### Performance Tests (Benchmark)
- Measure processing time
- Check memory usage
- Run separately from CI
- Tag with `@pytest.mark.slow`

---

## CI/CD Integration

```yaml
# .github/workflows/ci.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov pytest-mock
      
      - name: Run unit tests
        run: pytest -m unit --cov=src --cov-report=xml
      
      - name: Run integration tests
        run: pytest -m integration
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage.xml
          fail_ci_if_error: true
```

---

## Test Writing Guidelines

### 1. Test Names Should Be Descriptive
```python
# ❌ Bad
def test_extract():
    pass

# ✅ Good
def test_extract_project_intelligence_returns_valid_structure():
    pass
```

### 2. Follow AAA Pattern
```python
def test_example():
    # Arrange
    email = {'subject': 'Test'}
    llm = Mock()
    
    # Act
    result = extract_project(email, llm)
    
    # Assert
    assert result['project_name'] is not None
```

### 3. Test One Thing at a Time
```python
# ❌ Bad - tests multiple things
def test_extraction():
    result = extract(email)
    assert result['name'] is not None
    assert result['type'] == 'Design'
    assert len(result['topics']) > 0

# ✅ Good - separate tests
def test_extraction_includes_name():
    result = extract(email)
    assert result['name'] is not None

def test_extraction_includes_type():
    result = extract(email)
    assert result['type'] in VALID_TYPES
```

### 4. Use Parametrize for Multiple Cases
```python
@pytest.mark.parametrize("input,expected", [
    ("Design/Branding", True),
    ("Financial Systems", True),
    ("Invalid Type", False),
])
def test_project_type_validation(input, expected):
    assert is_valid_project_type(input) == expected
```

---

## Estimated Timeline

### Week 1: Infrastructure
- Day 1: Set up pytest, fixtures
- Day 2: Write Agent 1 expansion tests
- Day 3: CI/CD integration

### Week 2: Core Agents
- Day 1-2: Agent 2 tests (15 tests)
- Day 3-4: Agent 3 tests (18 tests)

### Week 3: Integration
- Day 1: Workflow tests (8 tests)
- Day 2: Trust Score tests (12 tests)
- Day 3: Utilities tests (6 tests)

**Total**: 15 working days (3 weeks)

---

## Success Criteria

✅ **80%+ code coverage** across all modules  
✅ **All tests pass** in CI  
✅ **< 5 second** test suite runtime (unit tests)  
✅ **Zero flaky tests** (consistent results)  
✅ **Coverage report** generated on every PR

---

## Cost-Benefit Analysis

**Investment**: 40 hours ($6,000 at $150/hr)  
**Benefit**:
- Prevents regressions (value: $20K+ in bug fixes)
- Enables confident refactoring
- Faster onboarding (new devs can learn from tests)
- Production confidence

**ROI**: 3-4x in first year

---

## Next Steps

1. ✅ Read this document
2. ✅ Set up pytest infrastructure
3. ✅ Write first 5 tests for Agent 2
4. ✅ Set up CI/CD
5. ✅ Continue until 80% coverage reached

**Start with**: `tests/agents/test_agent2_extractor.py` (highest priority)


