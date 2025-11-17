# Initialization Prompt for New Coding Agent

Copy and paste this prompt to your new coding agent:

---

# GRAPHMAIL Production Transformation - Implementation Agent Briefing

## Your Mission
You are implementing a production transformation for GRAPHMAIL, a Graph-First Project Intelligence System. Your goal is to transform this codebase from a hackathon prototype (4/10 production readiness) to an enterprise-grade system (7/10) in 25 hours of focused development.

## Complete Context Package
You have a comprehensive implementation package in the `speckit/` folder with 47 documents (11,403 lines of documentation):

### 1. START HERE - Master Guides (REQUIRED READING)
**Read these first before any implementation**:

1. **`speckit/AGENT_INITIALIZATION.md`** (YOUR PRIMARY GUIDE)
   - Complete implementation workflow
   - SpecKit command reference
   - TDD methodology
   - Quality gates and checkpoints
   - **READ THIS ENTIRE FILE FIRST**

2. **`speckit/IMPLEMENTATION_READY.md`** (489 lines)
   - Overview of all 5 features
   - Week-by-week roadmap
   - Success criteria
   - Expected outcomes

3. **`speckit/README.md`** (456 lines)
   - Quick start guide
   - Folder structure
   - Development workflow

### 2. Problem Context (WHY You're Building This)
**Location**: `speckit/audit/speckit-prep/`

**Critical Files**:
- **`AUDIT_REPORT.md`** (50 KB) - Complete technical audit
  - Current Issues: Security (OWASP 3/10), Quality (27.5% duplication), Performance (5x slow)
  
- **`constitution.md`** (381 lines) - **9 IMMUTABLE DEVELOPMENT PRINCIPLES**
  - Zero-Hallucination Principle
  - Test-Driven Development (80%+ coverage REQUIRED)
  - Security by Default
  - **YOU MUST FOLLOW THESE PRINCIPLES IN ALL CODE**

- `SECURITY_VULNERABILITIES.md` - 7 critical security issues to fix
- `TASK_PRIORITIES.md` - Work prioritized by impact/effort
- `QUICK_WINS.md` - 12 fast improvements (optional, 3 hours)

### 3. Implementation Specs (WHAT You're Building)
**Location**: `speckit/implementation/specs/`

**5 Features** (each has 6 files):
1. **`001-implement-comprehensive-input-sanitization/`** (CRITICAL - 4h)
   - Security: OWASP 3/10 → 7/10
   - Prevents prompt injection, XSS
   
2. **`003-implement-robust-retry-logic/`** (CRITICAL - 3h)
   - Reliability: 60% → 99%+
   - Exponential backoff for API calls
   
3. **`002-replace-all-print-statements/`** (HIGH - 6h)
   - Replace 38+ print statements
   - Structured logging
   
4. **`004-implement-centralized-configuration-management/`** (HIGH - 4h)
   - Replace 25+ hardcoded values
   - Type-safe config
   
5. **`005-consolidate-11-redundant-demo/`** (HIGH - 8h)
   - Reduce duplication: 27.5% → <5%

**Each Feature Folder Contains**:
- `spec.md` - User requirements & acceptance criteria (WHAT to build)
- `plan.md` - Technical architecture & tech stack (HOW to build)
- `tasks.md` - 24 actionable tasks, 15-30 min each (STEP-BY-STEP)
- `data-model.md` - Entity models & validation rules
- `research.md` - Technology decisions & rationale
- `contracts/` - API contracts & interfaces

### 4. SpecKit Configuration
**Location**: `speckit/config/.specify-mcp/`
- `constitution.yaml` - Project constitution (YAML format)
- `templates/` - Spec/plan/task templates

---

## Implementation Workflow (FOLLOW THIS EXACTLY)

### Phase 1: Setup & Context (30 minutes)

**Step 1 - Read Documentation** (15 min):
```bash
# PRIMARY: Your complete implementation guide
cat speckit/AGENT_INITIALIZATION.md

# Master overview
cat speckit/IMPLEMENTATION_READY.md

# Understand the problems
head -200 speckit/audit/speckit-prep/AUDIT_REPORT.md

# Learn the principles (CRITICAL - MUST FOLLOW)
cat speckit/audit/speckit-prep/constitution.md
```

**Step 2 - Environment Setup** (10 min):
```bash
# Install dependencies
pip install -r requirements.txt
pip install pytest pytest-cov structlog tenacity bleach email-validator pydantic

# Create .env file
cp speckit/ENV_TEMPLATE.env .env
# Edit .env and add API keys:
# OPENAI_API_KEY=your_key_here
# ANTHROPIC_API_KEY=your_key_here

# Verify setup
python -c "import structlog, tenacity, bleach; print('✅ Dependencies OK')"
pytest tests/ -v  # See baseline (many will fail - that's OK!)
```

**Step 3 - Choose First Feature** (5 min):
```bash
# Start with Input Sanitization (CRITICAL, blocks production)
git checkout 001-implement-comprehensive-input-sanitization
# Or create if it doesn't exist:
# git checkout -b 001-implement-comprehensive-input-sanitization
```

### Phase 2: Feature Implementation (4 hours per feature)

**Step 1 - Read Feature Context** (10 min):
```bash
# For Feature 001 (Input Sanitization)
cd speckit/implementation/specs/001-implement-comprehensive-input-sanitization/

# MUST READ (in order):
cat spec.md         # What to build (requirements, acceptance criteria)
cat plan.md         # How to build (architecture, tech stack)
cat tasks.md        # Step-by-step (24 tasks, 15-30 min each)
cat data-model.md   # Entity models
```

**Step 2 - Execute Tasks Using TDD** (Follow speckit/AGENT_INITIALIZATION.md):

**CRITICAL TDD Workflow** (for EVERY task):
1. **RED**: Write failing test
2. **Verify**: Test MUST fail
3. **GREEN**: Implement minimal code
4. **Verify**: Test MUST pass
5. **Refactor**: Clean up code
6. **Commit**: With clear message

**Task Phases** (from tasks.md):
- **Phase 1: Setup** (T001-T005) - 1 hour
  - Create project structure
  - Initialize configuration
  - Install dependencies

- **Phase 2: Tests** (T006-T010) - 1 hour
  - Write ALL tests FIRST (RED phase)
  - Tests marked [P] can run in parallel
  - **MUST see tests fail before implementing**

- **Phase 3: Implementation** (T011-T018) - 1.5 hours
  - Implement code to pass tests (GREEN phase)
  - Tasks marked [P] can run in parallel
  - Refactor after tests pass

- **Phase 4: Integration** (T019-T021) - 0.5 hours
  - Integrate all modules
  - Run full test suite
  - Performance optimization

- **Phase 5: Documentation** (T022-T024)
  - Update documentation
  - API docs, README

**Task Execution Example**:
```bash
# T006: Write HTML sanitization test (RED)
# Create tests/test_sanitizer.py with failing test
pytest tests/test_sanitizer.py::test_html_sanitization
# Output: FAILED (expected - not implemented yet)
git add tests/test_sanitizer.py
git commit -m "test(sanitization): T006 - Add HTML sanitization test (RED)"

# T011: Implement HTML sanitizer (GREEN)
# Create src/sanitizer/html_sanitizer.py
pytest tests/test_sanitizer.py::test_html_sanitization
# Output: PASSED (implementation works!)
git add src/sanitizer/html_sanitizer.py
git commit -m "feat(sanitization): T011 - Implement HTML sanitizer (GREEN)"

# Refactor if needed, then move to next task
```

**Step 3 - Track Progress**:
```bash
# After EACH completed task, mark it in tasks.md:
# Change: - [ ] T006 [P] Write test...
# To:     - [X] T006 [P] Write test...

# Commit progress update
git add speckit/implementation/specs/*/tasks.md
git commit -m "chore: mark T006 complete"
```

**Step 4 - Validate Feature**:
```bash
# After all 24 tasks complete:
pytest --cov=src tests/            # Must be >80% coverage
pylint src/                        # Must pass linting
mypy src/                          # Must pass type checking

# If all pass:
git add .
git commit -m "feat(sanitization): Complete input sanitization feature

- All 24 tasks completed
- Test coverage: 85%
- Security: OWASP 3/10 → 7/10
- All acceptance criteria met"
```

### Phase 3: Repeat for Remaining Features

**Feature Order** (recommended):
1. ✅ Input Sanitization (4h) - DONE
2. ⏭️ Retry Logic (3h) - NEXT
3. ⏭️ Structured Logging (6h)
4. ⏭️ Configuration Management (4h)
5. ⏭️ Code Consolidation (8h)

---

## Success Criteria (MUST ACHIEVE)

### Per Feature
- [ ] All 24 tasks completed and marked [X]
- [ ] Test coverage >80%
- [ ] All acceptance criteria met (from spec.md)
- [ ] Linting passes (pylint score >8.0)
- [ ] Type checking passes (mypy)
- [ ] Git commits clean and descriptive

### Week 1 Complete (All 5 Features)
- [ ] Production Readiness: 4/10 → 7/10 (+75%)
- [ ] OWASP Security: 3/10 → 7/10 (+133%)
- [ ] Pipeline Reliability: 60% → 99%+ (+65%)
- [ ] Code Duplication: 27.5% → <5% (-82%)
- [ ] Print Statements: 38+ → 0 (-100%)
- [ ] Hardcoded Values: 25+ → 0 (-100%)
- [ ] Test Coverage: 20% → 80%+ (+300%)
- [ ] Processing Speed: 156s → <30s (5x faster)

---

## Critical Reminders

### MUST FOLLOW
1. **Read `speckit/AGENT_INITIALIZATION.md` FIRST** - Your complete guide
2. **Follow TDD** - Test first (RED), implement (GREEN), refactor
3. **Follow Constitution** - 9 principles in `constitution.md`
4. **Mark Progress** - Update tasks.md after each task
5. **Commit Often** - After each task or logical unit
6. **Validate Often** - Run tests after each phase

### NEVER
- ❌ Write code before tests
- ❌ Skip test verification (must see RED/GREEN)
- ❌ Commit without running tests
- ❌ Violate constitutional principles
- ❌ Skip quality gates (coverage, linting, typing)

### ALWAYS
- ✅ Read full feature context before coding
- ✅ Write test first, verify it fails
- ✅ Implement minimal code to pass
- ✅ Refactor and clean up
- ✅ Mark task complete in tasks.md
- ✅ Commit with clear, conventional message
- ✅ Run validation before moving to next phase

---

## Quick Commands

### Testing
```bash
pytest tests/ -v                   # Run all tests
pytest --cov=src tests/            # With coverage
pytest tests/test_file.py::test_func  # Specific test
```

### Code Quality
```bash
pylint src/                        # Linting
mypy src/                          # Type checking
black src/ tests/                  # Formatting
```

### Task Progress
```bash
# See progress
grep -c "\[X\]" speckit/implementation/specs/001-*/tasks.md  # Completed
grep -c "\[ \]" speckit/implementation/specs/001-*/tasks.md  # Remaining
```

---

## Your First Action

**RIGHT NOW**:
```bash
cat speckit/AGENT_INITIALIZATION.md
```

Read this ENTIRE file before writing any code. It contains your complete implementation workflow, TDD methodology, and all the details you need to succeed.

**THEN**:
```bash
cat speckit/IMPLEMENTATION_READY.md
cat speckit/audit/speckit-prep/constitution.md
```

**FINALLY**:
```bash
git checkout 001-implement-comprehensive-input-sanitization
cat speckit/implementation/specs/001-implement-comprehensive-input-sanitization/tasks.md
# Start with T001: Create project structure
```

---

## You Have Everything You Need

✅ **47 documents** - Complete context  
✅ **120 tasks** - Step-by-step instructions  
✅ **TDD workflow** - Test first, then implement  
✅ **Quality gates** - Validation at every step  
✅ **Constitutional principles** - Development guidelines  
✅ **Success criteria** - Measurable outcomes

**Mission**: Transform GRAPHMAIL from 4/10 → 7/10 in 25 hours

**Start**: Read `speckit/AGENT_INITIALIZATION.md` now

**Let's build! 🚀**

---

*Initialization Package Version: 1.0*  
*Created: November 17, 2025*  
*Status: READY FOR IMPLEMENTATION*

