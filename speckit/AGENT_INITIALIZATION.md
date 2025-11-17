# AGENT INITIALIZATION: GRAPHMAIL Production Transformation

**Your Mission**: Transform GRAPHMAIL from a hackathon prototype (4/10) into a production-ready system (7/10) in 25 hours

---

## 🎯 What You're Building

**Project**: GRAPHMAIL - Graph-First Project Intelligence System  
**Current State**: 4/10 production readiness (functional prototype)  
**Target State**: 7/10 production readiness (enterprise-grade)  
**Timeline**: 5 days (5 hours/day)  
**Approach**: Test-Driven Development (TDD)

### Why This Matters
GRAPHMAIL demonstrates a novel 3-agent verification pipeline for knowledge extraction with zero hallucination guarantees. However, it has critical production gaps that prevent deployment.

---

## 📋 Your Complete Context Package

All documentation is in the `speckit/` folder. Here's what you have:

### 1. START HERE: Master Guides ⭐

**Primary Reading** (Read in order):
1. `speckit/IMPLEMENTATION_READY.md` (489 lines)
   - Complete overview of all 5 features
   - Week-by-week implementation roadmap
   - Success criteria and expected outcomes
   - Your main reference document

2. `speckit/README.md` (456 lines)
   - Quick start guide for implementation
   - Folder structure explanation
   - TDD workflow overview
   - Quality gates and checkpoints

### 2. Problem Analysis (Understand WHY)

**Comprehensive Audit** (`speckit/audit/speckit-prep/`):
- `AUDIT_REPORT.md` (50 KB) - Complete technical audit
  - Security: OWASP 3/10 (7 major vulnerabilities)
  - Quality: 27.5% code duplication
  - Performance: 5x slower than target
  - Current issues across 8 dimensions

- `constitution.md` (381 lines) - 9 Development Principles
  - Zero-Hallucination Principle
  - Test-Driven Development
  - Security by Default
  - **CRITICAL**: Follow these principles in all code

- `SECURITY_VULNERABILITIES.md` - 7 critical security issues
- `TASK_PRIORITIES.md` - Prioritized by impact/effort
- `QUICK_WINS.md` - 12 fast improvements (3 hours)

### 3. Implementation Specs (Understand WHAT)

**5 Features to Build** (`speckit/implementation/specs/`):

Each feature folder contains:
- `spec.md` - User requirements & acceptance criteria
- `plan.md` - Technical architecture & tech stack
- `research.md` - Technology decisions & rationale
- `data-model.md` - Entity models & validation rules
- `tasks.md` - 24 actionable tasks (15-30 min each)
- `contracts/` - API contracts & interfaces

**Features** (in recommended order):
1. **001-input-sanitization** (CRITICAL - 4h)
   - Security: OWASP 3/10 → 7/10
   - Prevents prompt injection, XSS, data corruption
   
2. **003-retry-logic** (CRITICAL - 3h)
   - Reliability: 60% → 99%+
   - Exponential backoff for LLM API calls
   
3. **002-structured-logging** (HIGH - 6h)
   - Replace 38+ print statements
   - Correlation IDs, JSON formatting
   
4. **004-configuration-management** (HIGH - 4h)
   - Replace 25+ hardcoded values
   - Type-safe, environment-aware config
   
5. **005-code-consolidation** (HIGH - 8h)
   - Reduce duplication: 27.5% → <5%
   - Consolidate 11 demo files → 1

### 4. Configuration

**SpecKit Config** (`speckit/config/.specify-mcp/`):
- `constitution.yaml` - Project constitution (YAML format)
- `templates/` - Spec/plan/task templates

**Environment Setup**:
- `speckit/ENV_TEMPLATE.env` - Template for .env file
- Copy to project root as `.env` and add your API keys

---

## 🚀 How to Start Implementation

### Step 1: Read Context (15 minutes)

```bash
# Essential reading (do this first!)
cat speckit/IMPLEMENTATION_READY.md

# Quick reference
cat speckit/README.md

# Understand the problems
cat speckit/audit/speckit-prep/AUDIT_REPORT.md

# Learn the principles
cat speckit/audit/speckit-prep/constitution.md
```

### Step 2: Set Up Environment (10 minutes)

```bash
# 1. Install dependencies
pip install -r requirements.txt
pip install pytest pytest-cov structlog tenacity bleach email-validator pydantic

# 2. Create .env file
cp speckit/ENV_TEMPLATE.env .env
# Edit .env and add your API keys:
# OPENAI_API_KEY=your_key_here
# ANTHROPIC_API_KEY=your_key_here

# 3. Verify environment
python -c "import structlog, tenacity, bleach; print('✅ Dependencies OK')"

# 4. Run existing tests (will mostly fail - that's expected!)
pytest tests/ -v
```

### Step 3: Choose First Feature (2 minutes)

**Recommended**: Start with Input Sanitization (CRITICAL, blocks all others)

```bash
# Checkout feature branch
git checkout 001-implement-comprehensive-input-sanitization

# Or create it if it doesn't exist
git checkout -b 001-implement-comprehensive-input-sanitization
```

### Step 4: Read Feature Context (10 minutes)

```bash
# Feature specification (what to build)
cat speckit/implementation/specs/001-implement-comprehensive-input-sanitization/spec.md

# Technical plan (how to build)
cat speckit/implementation/specs/001-implement-comprehensive-input-sanitization/plan.md

# Task breakdown (step-by-step)
cat speckit/implementation/specs/001-implement-comprehensive-input-sanitization/tasks.md

# Data models (entities)
cat speckit/implementation/specs/001-implement-comprehensive-input-sanitization/data-model.md
```

### Step 5: Start Implementation Using SpecKit Workflow

**IMPORTANT**: Follow the `/speckit.implement` workflow below.

---

## 📖 SpecKit Implementation Workflow

### Overview

The `/speckit.implement` command executes implementation plans by processing tasks from `tasks.md` in a structured, phase-by-phase approach with TDD.

### Execution Flow

#### 1. **Load Implementation Context**

**Required Files**:
- `tasks.md` - Complete task list and execution plan
- `plan.md` - Tech stack, architecture, file structure

**Optional Files** (read if they exist):
- `data-model.md` - Entities and relationships
- `contracts/` - API specifications and test requirements
- `research.md` - Technical decisions and constraints

**Example**:
```bash
# For Feature 001
cd speckit/implementation/specs/001-implement-comprehensive-input-sanitization/
cat tasks.md  # Your execution plan
cat plan.md   # Technical guidance
cat data-model.md  # Entity models
```

#### 2. **Project Setup Verification**

**Create/Verify Ignore Files**:
- `.gitignore` - Already exists, verify patterns
- Add any missing patterns based on tech stack

**Python Patterns** (from plan.md):
```gitignore
__pycache__/
*.pyc
.venv/
venv/
dist/
*.egg-info/
.pytest_cache/
.coverage
htmlcov/
*.log
.env
```

#### 3. **Parse Task Structure**

Extract from `tasks.md`:
- **Task Phases**: Setup → Tests → Implementation → Integration → Documentation
- **Task Dependencies**: Sequential vs parallel ([P] marker)
- **Task Details**: ID (T001, T002...), description, file paths
- **Execution Flow**: Order requirements

**Example Task**:
```markdown
- [ ] T006 [P] Write contract test for HTML sanitization in tests/test_sanitizer.py
```
- `T006` = Task ID
- `[P]` = Parallelizable (can run with other [P] tasks)
- Clear file path: `tests/test_sanitizer.py`

#### 4. **Execute Implementation (Phase-by-Phase)**

##### Phase 1: Setup (T001-T005)
**Goal**: Initialize project structure and dependencies

Example:
```bash
# T001: Create project structure
mkdir -p src/sanitizer tests/
touch src/sanitizer/__init__.py
touch src/sanitizer/html_sanitizer.py
touch src/sanitizer/email_validator.py

# T002: Initialize configuration
# (Create config files as needed)

# T003-T005: Can run in parallel (different files)
```

**Commit After Phase**:
```bash
git add .
git commit -m "feat(sanitization): Phase 1 - Project setup complete"
```

##### Phase 2: Tests (T006-T010) - TDD CRITICAL
**Goal**: Write failing tests BEFORE implementation

**TDD Workflow**:
1. **Red**: Write failing test
   ```python
   # tests/test_sanitizer.py
   def test_html_sanitization():
       """Test that HTML tags are stripped."""
       dirty_html = "<script>alert('xss')</script>Hello"
       clean = sanitize_html(dirty_html)
       assert clean == "Hello"
       assert "<script>" not in clean
   ```

2. **Verify Failure**:
   ```bash
   pytest tests/test_sanitizer.py::test_html_sanitization
   # Should FAIL (not implemented yet)
   ```

3. **Commit Test**:
   ```bash
   git add tests/test_sanitizer.py
   git commit -m "test(sanitization): T006 - Add HTML sanitization test (RED)"
   ```

**Tasks T006-T010**:
- T006: HTML sanitization test
- T007: Email validation test
- T008: Body truncation test
- T009: Rate limiting test
- T010: Prompt injection detection test

**All marked [P]** = Can write in parallel (different test functions)

##### Phase 3: Implementation (T011-T018)
**Goal**: Implement minimal code to pass tests (GREEN)

**TDD Workflow**:
1. **Green**: Implement minimal code
   ```python
   # src/sanitizer/html_sanitizer.py
   import bleach
   
   def sanitize_html(html_text: str) -> str:
       """Sanitize HTML by removing dangerous tags."""
       # Minimal implementation to pass test
       return bleach.clean(html_text, tags=[], strip=True)
   ```

2. **Verify Pass**:
   ```bash
   pytest tests/test_sanitizer.py::test_html_sanitization
   # Should PASS now
   ```

3. **Refactor** (if needed):
   - Clean up code
   - Add comments
   - Improve naming

4. **Commit Implementation**:
   ```bash
   git add src/sanitizer/html_sanitizer.py
   git commit -m "feat(sanitization): T011 - Implement HTML sanitizer (GREEN)"
   ```

**Tasks T011-T018**:
- T011-T014: Core modules (marked [P] = parallel)
- T015-T018: Integration modules (sequential)

##### Phase 4: Integration (T019-T021)
**Goal**: Integrate all modules and validate

```bash
# T019: Integrate all sanitization modules
# Create unified interface in src/sanitizer/__init__.py

# T020: Run integration tests
pytest tests/ -v

# T021: Performance optimization
# Run benchmarks, optimize bottlenecks
```

##### Phase 5: Documentation (T022-T024)
**Goal**: Document the implementation

All marked [P] = Can write in parallel

```bash
# T022: User documentation
# T023: API documentation (docstrings, etc.)
# T024: Update README
```

**Final Commit**:
```bash
git add .
git commit -m "docs(sanitization): Complete feature documentation"
```

#### 5. **Progress Tracking**

**CRITICAL**: Mark tasks as complete in `tasks.md`

```bash
# After completing T006, edit tasks.md:
# Change: - [ ] T006 [P] Write contract test...
# To:     - [X] T006 [P] Write contract test...

# Commit the update
git add speckit/implementation/specs/001-*/tasks.md
git commit -m "chore: mark T006 complete"
```

**Track Progress**:
```bash
# See completed vs remaining tasks
grep -c "\[ \]" tasks.md  # Remaining
grep -c "\[X\]" tasks.md  # Completed
```

#### 6. **Validation Checkpoints**

**After Each Phase**:
- [ ] All phase tasks marked [X] in tasks.md
- [ ] Tests pass: `pytest tests/ -v`
- [ ] Linting passes: `pylint src/`
- [ ] Type checking passes: `mypy src/`
- [ ] Git commit made with clear message

**After Feature Complete**:
- [ ] All 24 tasks marked [X]
- [ ] Acceptance criteria met (from spec.md)
- [ ] Test coverage >80%: `pytest --cov=src tests/`
- [ ] Integration tests pass
- [ ] Feature branch ready for merge

#### 7. **Error Handling**

**If a task fails**:
1. **Stop immediately** (for sequential tasks)
2. **Report error** with context
3. **Suggest fixes** based on error message
4. **Ask for guidance** if unclear

**For parallel tasks [P]**:
- Continue with successful tasks
- Report failed ones
- User decides whether to fix or continue

---

## 📊 Success Criteria

### Per Feature

**Input Sanitization (001)** - 4 hours:
- [ ] All 24 tasks complete
- [ ] Security tests pass (50+ test cases)
- [ ] OWASP score increases to 7/10
- [ ] 100% prompt injection protection
- [ ] <10ms sanitization latency

### Week 1 Complete (All 5 Features)

**Production Readiness**: 4/10 → 7/10 (+75%)

| Metric | Before | After | Target |
|--------|--------|-------|--------|
| OWASP Security | 3/10 | 7/10 | ✅ |
| Pipeline Reliability | 60% | 99%+ | ✅ |
| Code Duplication | 27.5% | <5% | ✅ |
| Print Statements | 38+ | 0 | ✅ |
| Hardcoded Values | 25+ | 0 | ✅ |
| Test Coverage | 20% | 80%+ | ✅ |
| Processing Speed | 156s | <30s | ✅ |

---

## 🔧 Development Commands

### Testing
```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_sanitizer.py -v

# Run with coverage
pytest --cov=src tests/

# Run specific test function
pytest tests/test_sanitizer.py::test_html_sanitization
```

### Code Quality
```bash
# Linting
pylint src/

# Type checking
mypy src/

# Code formatting
black src/ tests/

# Check code duplication
pylint --disable=all --enable=duplicate-code src/
```

### Git Workflow
```bash
# After each task
git add <changed files>
git commit -m "feat(module): TXX - Task description"

# Examples:
git commit -m "test(sanitization): T006 - Add HTML sanitization test (RED)"
git commit -m "feat(sanitization): T011 - Implement HTML sanitizer (GREEN)"
git commit -m "refactor(sanitization): T011 - Clean up sanitizer code"
```

---

## 💡 TDD Best Practices

### The Red-Green-Refactor Cycle

**Red (Write Failing Test)**:
```python
# tests/test_sanitizer.py
def test_email_validation():
    """Test that invalid emails are rejected."""
    assert validate_email("valid@example.com") == True
    assert validate_email("invalid.email") == False
    assert validate_email("missing@domain") == False
```

```bash
pytest tests/test_sanitizer.py::test_email_validation
# Output: FAILED (ImportError or assertion error)
```

**Green (Implement Minimal Code)**:
```python
# src/sanitizer/email_validator.py
import re

def validate_email(email: str) -> bool:
    """Validate email against RFC 5322."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))
```

```bash
pytest tests/test_sanitizer.py::test_email_validation
# Output: PASSED
```

**Refactor (Clean Up)**:
```python
# src/sanitizer/email_validator.py
import re
from typing import Pattern

# More robust implementation
EMAIL_PATTERN: Pattern = re.compile(
    r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
)

def validate_email(email: str) -> bool:
    """
    Validate email address against RFC 5322 standards.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid, False otherwise
        
    Examples:
        >>> validate_email("user@example.com")
        True
        >>> validate_email("invalid.email")
        False
    """
    if not email or not isinstance(email, str):
        return False
    return bool(EMAIL_PATTERN.match(email.strip()))
```

```bash
pytest tests/test_sanitizer.py::test_email_validation
# Output: Still PASSED (refactor didn't break anything)
```

### TDD Discipline

**NEVER**:
- ❌ Write implementation before tests
- ❌ Skip test verification (must see RED first)
- ❌ Commit without running tests
- ❌ Move to next task with failing tests

**ALWAYS**:
- ✅ Write test first (RED)
- ✅ Verify test fails
- ✅ Implement minimal code (GREEN)
- ✅ Verify test passes
- ✅ Refactor if needed
- ✅ Verify tests still pass
- ✅ Commit with clear message
- ✅ Move to next task

---

## 🚨 Critical Reminders

### Constitutional Principles (MUST FOLLOW)

From `speckit/audit/speckit-prep/constitution.md`:

1. **Zero-Hallucination Principle**: Every fact must have proof
2. **Sequential Processing Integrity**: Respect temporal order
3. **Graph-First Architecture**: Graph is source of truth
4. **LLM Verification Layer**: Trust but verify
5. **Evidence Traceability**: Audit trail for every claim
6. **Test-Driven Development**: No code without tests (80%+ coverage)
7. **API-First Design**: Build for integration
8. **Security by Default**: Fail secure, not open
9. **Performance Budgets**: Speed is a feature

### Task Execution Rules

1. **Phase-by-phase**: Complete setup before tests, tests before implementation
2. **Respect [P] markers**: Parallel tasks can run together, others sequential
3. **TDD always**: Test first (RED), implement (GREEN), refactor
4. **Mark progress**: Update tasks.md after each task ([X])
5. **Commit frequently**: After each task or logical unit
6. **Validate often**: Run tests after each phase

### Quality Gates (MUST PASS)

**Before Moving to Next Phase**:
- [ ] All phase tasks complete
- [ ] Tests pass
- [ ] Linting passes
- [ ] Type checking passes
- [ ] Git committed

**Before Feature Complete**:
- [ ] All 24 tasks marked [X]
- [ ] 80%+ test coverage
- [ ] Acceptance criteria met (from spec.md)
- [ ] No security vulnerabilities
- [ ] Performance benchmarks met

---

## 📞 Support & Reference

### Quick Reference Files

**Implementation**:
- Task breakdown: `speckit/implementation/specs/*/tasks.md`
- Technical plan: `speckit/implementation/specs/*/plan.md`
- Requirements: `speckit/implementation/specs/*/spec.md`

**Context**:
- Master guide: `speckit/IMPLEMENTATION_READY.md`
- Audit details: `speckit/audit/speckit-prep/AUDIT_REPORT.md`
- Constitution: `speckit/audit/speckit-prep/constitution.md`

**Troubleshooting**:
- Quick wins: `speckit/audit/speckit-prep/QUICK_WINS.md`
- Security issues: `speckit/audit/speckit-prep/SECURITY_VULNERABILITIES.md`
- Breaking changes: `speckit/audit/speckit-prep/BREAKING_CHANGES.md`

### Common Issues

**"Test won't fail"**:
- Make sure you're importing correctly
- Check test is actually running (not skipped)
- Verify assertion is meaningful

**"Don't understand entity model"**:
- Read `data-model.md` in feature folder
- Check `spec.md` for entity descriptions
- Look at `contracts/` for API examples

**"Task unclear"**:
- Read full feature `spec.md`
- Check `plan.md` for technical context
- Review `research.md` for decisions

**"Blocked by dependency"**:
- Complete blocking tasks first
- Check tasks.md for dependency order
- Only [P] tasks can run in parallel

---

## 🎯 Your First Steps (Start Now!)

### Immediate Actions (30 minutes)

1. **Read Master Guide** (10 min):
   ```bash
   cat speckit/IMPLEMENTATION_READY.md
   ```

2. **Set Up Environment** (10 min):
   ```bash
   cp speckit/ENV_TEMPLATE.env .env
   # Add your API keys
   pip install -r requirements.txt
   pytest tests/ -v  # See baseline
   ```

3. **Read First Feature** (10 min):
   ```bash
   git checkout 001-implement-comprehensive-input-sanitization
   cat speckit/implementation/specs/001-implement-comprehensive-input-sanitization/tasks.md
   ```

### Start Implementation (4 hours)

4. **Execute Tasks** (following /speckit.implement workflow above):
   ```bash
   # T001-T005: Setup (1 hour)
   # T006-T010: Tests - RED phase (1 hour)
   # T011-T018: Implementation - GREEN phase (1.5 hours)
   # T019-T021: Integration (0.5 hours)
   ```

5. **Validate & Commit**:
   ```bash
   pytest --cov=src tests/
   git add .
   git commit -m "feat(sanitization): Complete input sanitization feature"
   ```

---

## ✅ Ready to Start!

**You have**:
- ✅ Complete context (47 documents, 11,403 lines)
- ✅ Clear tasks (120 total, 24 per feature)
- ✅ Technical plans (architecture, data models, contracts)
- ✅ TDD workflow (test first, then implement)
- ✅ Success criteria (measurable outcomes)
- ✅ Constitutional principles (development guidelines)

**Your mission**:
Transform GRAPHMAIL from 4/10 → 7/10 production readiness in 25 hours

**Start with**:
```bash
cat speckit/IMPLEMENTATION_READY.md
git checkout 001-implement-comprehensive-input-sanitization
cat speckit/implementation/specs/001-implement-comprehensive-input-sanitization/tasks.md
# Begin with T001: Create project structure
```

**Let's build! 🚀**

---

*Document Version: 1.0*  
*Created: November 17, 2025*  
*Status: READY FOR IMPLEMENTATION*

