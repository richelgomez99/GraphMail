# SpecKit Implementation Package - GRAPHMAIL

**Status**: ✅ READY FOR IMPLEMENTATION  
**Created**: November 17, 2025  
**Total Tasks**: 120 across 5 features  
**Estimated Time**: 25 hours (5 days at 5 hours/day)

---

## 🎯 Quick Start for Implementation Agent

### 1. Read Master Overview
```bash
cat IMPLEMENTATION_READY.md
```
This is your **master guide** - read it first!

### 2. Choose First Feature
Recommended order (by priority):
1. **Input Sanitization** (CRITICAL - 4h) - `implementation/specs/001-*`
2. **Retry Logic** (CRITICAL - 3h) - `implementation/specs/003-*`
3. **Structured Logging** (HIGH - 6h) - `implementation/specs/002-*`
4. **Configuration Management** (HIGH - 4h) - `implementation/specs/004-*`
5. **Code Consolidation** (HIGH - 8h) - `implementation/specs/005-*`

### 3. View Task Breakdown
```bash
cd implementation/specs/001-implement-comprehensive-input-sanitization
cat tasks.md
```

### 4. Start Implementation
Follow the TDD approach:
- ✅ Write failing test (T006-T010)
- ✅ Implement minimal code (T011-T018)
- ✅ Refactor
- ✅ Commit after each task

---

## 📁 Folder Structure

```
speckit/
├── IMPLEMENTATION_READY.md     ⭐ START HERE - Master overview
├── README.md                    ⭐ This file - Quick reference
├── ENV_TEMPLATE.env             Environment variable template
│
├── audit/                       Problem analysis & context
│   └── speckit-prep/
│       ├── AUDIT_REPORT.md      Complete audit (50 KB)
│       ├── SECURITY_VULNERABILITIES.md
│       ├── UI_UX_IMPROVEMENTS.md
│       ├── REFACTORING_PLAN.md
│       ├── TASK_PRIORITIES.md
│       ├── constitution.md      9 development principles
│       ├── QUICK_WINS.md        12 fast improvements
│       ├── BREAKING_CHANGES.md
│       ├── TEST_COVERAGE_GAPS.md
│       ├── EXECUTION_SUMMARY.md
│       ├── DELIVERABLES_INDEX.md
│       ├── SPECIFICATIONS_CREATED.md (379 lines)
│       ├── PLANS_GENERATED.md (387 lines)
│       └── TASKS_GENERATED.md (445 lines)
│
├── implementation/              All specs, plans, and tasks
│   └── specs/
│       ├── 001-implement-comprehensive-input-sanitization/
│       │   ├── spec.md          User requirements (302 lines)
│       │   ├── plan.md          Technical architecture (91 lines)
│       │   ├── research.md      Technology decisions (49 lines)
│       │   ├── data-model.md    Entity models (60 lines)
│       │   ├── tasks.md         24 actionable tasks ⭐
│       │   └── contracts/       API contracts
│       │
│       ├── 002-replace-all-print-statements/
│       │   └── [same structure]
│       │
│       ├── 003-implement-robust-retry-logic/
│       │   └── [same structure]
│       │
│       ├── 004-implement-centralized-configuration-management/
│       │   └── [same structure]
│       │
│       └── 005-consolidate-11-redundant-demo/
│           └── [same structure]
│
└── config/                      SpecKit configuration
    └── .specify-mcp/
        ├── constitution.yaml    Project constitution
        └── templates/           Spec/plan/task templates
```

---

## 📋 5 Features to Implement

### Feature 001: Input Sanitization (CRITICAL - 4h)
**Location**: `implementation/specs/001-implement-comprehensive-input-sanitization/`  
**Branch**: `001-implement-comprehensive-input-sanitization`  
**Tasks**: 24 (5 setup, 5 tests, 8 implementation, 3 integration, 3 docs)  
**Impact**: OWASP 3/10 → 7/10, blocks production deployment

**Key Files**:
- `spec.md` - User requirements & acceptance criteria
- `plan.md` - Technical architecture
- `tasks.md` - 24 actionable tasks
- `data-model.md` - Entity models (SanitizedEmail, ValidationResult)

**What to Build**:
- HTML sanitization (bleach library)
- Email validation (RFC 5322)
- Body truncation (5,000 chars)
- Rate limiting (50/min)
- Prompt injection detection
- Security audit logging

---

### Feature 002: Structured Logging (HIGH - 6h)
**Location**: `implementation/specs/002-replace-all-print-statements/`  
**Branch**: `002-replace-all-print-statements`  
**Tasks**: 24 (5 setup, 5 tests, 8 implementation, 3 integration, 3 docs)  
**Impact**: Enables debugging & monitoring

**What to Build**:
- Replace 38+ print statements
- 5 log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- JSON formatter (production) + colored formatter (dev)
- Correlation IDs for tracing
- Sensitive data auto-redaction
- Log rotation (100MB per file)

---

### Feature 003: Retry Logic (CRITICAL - 3h)
**Location**: `implementation/specs/003-implement-robust-retry-logic/`  
**Branch**: `003-implement-robust-retry-logic`  
**Tasks**: 24 (5 setup, 5 tests, 8 implementation, 3 integration, 3 docs)  
**Impact**: Pipeline reliability 60% → 99%+

**What to Build**:
- Exponential backoff (1s, 2s, 4s)
- Error classification (retryable vs non-retryable)
- Jitter (±20% to prevent thundering herd)
- Retry-After header support
- Wrap all LLM API calls
- Retry attempt logging

---

### Feature 004: Configuration Management (HIGH - 4h)
**Location**: `implementation/specs/004-implement-centralized-configuration-management/`  
**Branch**: `004-implement-centralized-configuration-management`  
**Tasks**: 24 (5 setup, 5 tests, 8 implementation, 3 integration, 3 docs)  
**Impact**: Enables multi-environment deployment

**What to Build**:
- Pydantic BaseSettings models
- Environment-aware config (.env.dev, .env.staging, .env.prod)
- Type-safe validation
- Secrets manager integration (AWS)
- Replace 25+ hardcoded values
- Startup validation

---

### Feature 005: Code Consolidation (HIGH - 8h)
**Location**: `implementation/specs/005-consolidate-11-redundant-demo/`  
**Branch**: `005-consolidate-11-redundant-demo`  
**Tasks**: 24 (5 setup, 5 tests, 8 implementation, 3 integration, 3 docs)  
**Impact**: Code duplication 27.5% → <5%

**What to Build**:
- Consolidate 11 demo files → 1 unified demo.py
- Extract shared utilities to src/utils/demo_helpers.py
- 6 visualization modes (simple, complete, collaboration, human, timeline, all)
- Streamlit tabbed UI
- Feature flags
- Mode switching <1s

---

## 🚀 Implementation Strategy

### Week 1 Daily Plan

**Day 1** (7h): CRITICAL Features
- Morning: Input Sanitization (4h)
  - Setup → Tests → Implementation → Integration
- Afternoon: Retry Logic (3h)
  - Setup → Tests → Implementation → Integration

**Day 2** (6h): Observability
- Structured Logging (6h)
  - Replace all print statements
  - Correlation IDs
  - Log rotation

**Day 3** (4h): Configuration
- Configuration Management (4h)
  - Pydantic settings
  - Environment-aware config
  - Replace hardcoded values

**Day 4-5** (8h): Code Quality
- Code Consolidation (8h)
  - Extract shared utilities
  - Unified demo
  - Feature parity validation

---

## ✅ TDD Workflow (REQUIRED)

For **every** feature:

1. **Red Phase** (T006-T010): Write failing tests
   ```bash
   # Example: Test HTML sanitization
   pytest tests/test_sanitizer.py::test_html_sanitization
   # Should FAIL (not implemented yet)
   ```

2. **Green Phase** (T011-T018): Implement minimal code
   ```bash
   # Implement just enough to pass the test
   # Example: src/sanitizer/html_sanitizer.py
   pytest tests/test_sanitizer.py::test_html_sanitization
   # Should PASS now
   ```

3. **Refactor Phase**: Clean up code
   - Remove duplication
   - Improve naming
   - Add comments
   - Run linters

4. **Commit**:
   ```bash
   git add .
   git commit -m "feat(sanitization): T011 - Implement HTML sanitizer"
   ```

5. **Repeat** for next task

---

## 📊 Success Criteria

### After Week 1 Implementation

| Metric | Before | After | Goal |
|--------|--------|-------|------|
| Production Readiness | 4/10 | 7/10 | ✅ +75% |
| OWASP Security | 3/10 | 7/10 | ✅ +133% |
| Pipeline Reliability | 60% | 99%+ | ✅ +65% |
| Code Duplication | 27.5% | <5% | ✅ -82% |
| Print Statements | 38+ | 0 | ✅ -100% |
| Hardcoded Values | 25+ | 0 | ✅ -100% |
| Test Coverage | 20% | 80%+ | ✅ +300% |
| Processing Speed | 156s | <30s | ✅ 5x faster |

---

## 🔧 Development Environment Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
pip install pytest pytest-cov structlog tenacity bleach email-validator pydantic
```

### 2. Set Up Environment Variables
```bash
cp speckit/ENV_TEMPLATE.env .env
# Edit .env with your API keys
```

### 3. Run Tests (Should Fail Initially)
```bash
pytest tests/
```

### 4. Start Development
```bash
# Checkout first feature branch
git checkout 001-implement-comprehensive-input-sanitization

# View tasks
cat speckit/implementation/specs/001-implement-comprehensive-input-sanitization/tasks.md

# Start with T001
```

---

## 📖 Documentation Roadmap

### For Understanding (Read in Order)
1. **IMPLEMENTATION_READY.md** ⭐ Master overview
2. **audit/speckit-prep/EXECUTION_SUMMARY.md** - Executive summary
3. **audit/speckit-prep/TASK_PRIORITIES.md** - Prioritized work

### For Implementation (Use While Coding)
1. **implementation/specs/*/tasks.md** - Task breakdowns
2. **implementation/specs/*/spec.md** - Acceptance criteria
3. **implementation/specs/*/plan.md** - Technical guidance
4. **implementation/specs/*/data-model.md** - Entity models

### For Reference (Consult When Needed)
1. **audit/speckit-prep/AUDIT_REPORT.md** - Problem analysis
2. **audit/speckit-prep/constitution.md** - Development principles
3. **audit/speckit-prep/REFACTORING_PLAN.md** - Detailed refactoring

---

## 🎯 Quality Gates

### Before Starting
- [x] All documentation reviewed
- [ ] Development environment set up
- [ ] Dependencies installed
- [ ] Git branches created
- [ ] .env configured

### During Implementation (Per Task)
- [ ] Test written first (TDD)
- [ ] Test fails initially (Red)
- [ ] Minimal implementation (Green)
- [ ] Code refactored
- [ ] Git commit made
- [ ] Task marked complete

### After Each Feature
- [ ] All tests passing
- [ ] Code coverage >80%
- [ ] Linters passing (pylint, mypy)
- [ ] Integration tests passing
- [ ] Acceptance criteria met
- [ ] Documentation updated

### After Week 1
- [ ] All 120 tasks complete
- [ ] Production readiness: 7/10
- [ ] OWASP security: 7/10
- [ ] Code duplication: <5%
- [ ] Ready for staging

---

## 🚨 Important Notes

### Constitutional Principles (audit/speckit-prep/constitution.md)

These **9 immutable principles** guide all development:

1. **Zero-Hallucination Principle** - Every fact must have proof
2. **Sequential Processing Integrity** - Respect temporal order
3. **Graph-First Architecture** - Graph is source of truth
4. **LLM Verification Layer** - Trust but verify
5. **Evidence Traceability** - Audit trail for every claim
6. **Test-Driven Development** - No code without tests
7. **API-First Design** - Build for integration
8. **Security by Default** - Fail secure, not open
9. **Performance Budgets** - Speed is a feature

### Git Workflow
```bash
# For each task
git checkout <feature-branch>
# Complete task
git add .
git commit -m "feat(<module>): <task-id> - <description>"

# Example:
git commit -m "feat(sanitization): T006 - Write HTML sanitization test"
git commit -m "feat(sanitization): T011 - Implement HTML sanitizer"
```

### Parallel Development
- Tasks marked **[P]** can run in parallel
- 54% of tasks are parallelizable
- With 4 developers: 25h → 15h (40% savings)

---

## 💡 Tips for Success

### TDD Discipline
- **ALWAYS** write test first
- Test should **FAIL** initially
- Implement **minimal** code to pass
- Then **refactor**
- **Never** skip tests

### Task Size
- Each task: 15-30 minutes max
- If longer, break it down
- Commit after each task
- Track progress

### Code Quality
- Run `pytest --cov=src tests/` after each task
- Run `pylint src/` before committing
- Run `mypy src/` for type checking
- Aim for >80% coverage

### Communication
- Commit messages should be clear
- Reference task IDs (T001, T002, etc.)
- Use conventional commits (feat, fix, docs, test, refactor)

---

## 📞 Support Resources

### Documentation
- **Master Guide**: `IMPLEMENTATION_READY.md`
- **Audit Details**: `audit/speckit-prep/AUDIT_REPORT.md`
- **Task Details**: `implementation/specs/*/tasks.md`

### Technical Specs
- **Architecture**: `implementation/specs/*/plan.md`
- **Data Models**: `implementation/specs/*/data-model.md`
- **Contracts**: `implementation/specs/*/contracts/`

### Development Principles
- **Constitution**: `audit/speckit-prep/constitution.md`
- **Best Practices**: `implementation/specs/*/research.md`

---

## 🎉 You're Ready!

Everything you need is in this `speckit/` folder:
- ✅ 47 documents (11,403 lines)
- ✅ 120 actionable tasks
- ✅ 5 complete feature specs
- ✅ 20 implementation plans
- ✅ 12 audit documents
- ✅ Clear success criteria

**Start with**: `IMPLEMENTATION_READY.md`  
**Then**: `implementation/specs/001-implement-comprehensive-input-sanitization/tasks.md`

**Your mission**: Transform GRAPHMAIL from 4/10 → 7/10 production readiness in 25 hours

**Let's build! 🚀**

---

*Generated: November 17, 2025*  
*Package Version: 1.0*  
*Status: READY FOR IMPLEMENTATION*

