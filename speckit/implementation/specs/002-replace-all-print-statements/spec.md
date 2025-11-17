# Feature Specification: Structured Logging System

**Feature Branch**: `002-replace-all-print-statements`  
**Created**: 2025-11-17  
**Status**: Ready for Planning  
**Priority**: HIGH  
**Effort**: 6 hours  
**Impact**: 8/10 (Critical for debugging and monitoring)

## Executive Summary

Replace all 38+ `print()` statements throughout the codebase with a professional structured logging system that provides consistent log levels, contextual metadata, JSON formatting for machine parsing, and integration with monitoring tools. This transforms GRAPHMAIL from a prototype with scattered print statements into a production system with enterprise-grade observability.

**Maintainability Context**: Current code has print statements mixed with actual output, making debugging impossible in production. This feature enables proper monitoring, debugging, and alerting.

## Constitutional Alignment

This specification adheres to the GRAPHMAIL constitution:

- **Article V: Evidence Traceability** - Structured logs create audit trail for every system action
- **Article IX: Performance Budgets** - Logging overhead must be negligible (<1ms per log)
- **Article VIII: Security by Default** - Logs must not contain sensitive data (API keys, PII)

## User Scenarios & Testing

### Primary User Story

**As a** DevOps engineer monitoring GRAPHMAIL in production  
**I want** structured, searchable logs with consistent formatting and context  
**So that** I can quickly debug issues, track system health, and alert on critical errors

### Secondary User Story

**As a** developer debugging GRAPHMAIL locally  
**I want** verbose logging in development with readable formatting  
**So that** I can understand what the system is doing at each step without littering the code with print statements

### Acceptance Scenarios

**Scenario 1: Development Debugging (Happy Path)**
- **Given** GRAPHMAIL is running in development mode with LOG_LEVEL=DEBUG
- **When** an email is processed through the pipeline
- **Then** detailed logs show each processing step with timing
- **And** logs are human-readable with colored output for different levels
- **And** correlation IDs connect all logs for the same email

**Scenario 2: Production Monitoring**
- **Given** GRAPHMAIL is running in production with LOG_LEVEL=INFO
- **When** the system processes 100 emails
- **Then** logs capture key milestones (started, completed, errors)
- **And** logs are JSON-formatted for ingestion by monitoring tools
- **And** no sensitive data (email content, API keys) appears in logs

**Scenario 3: Error Investigation**
- **Given** an LLM API call fails with a rate limit error
- **When** engineers investigate the logs
- **Then** the error log includes correlation ID, stack trace, retry attempt number, and context
- **And** engineers can trace the full request flow using the correlation ID
- **And** log aggregation tools can alert on the ERROR pattern

**Scenario 4: Performance Analysis**
- **Given** engineers suspect Agent 2 is slow
- **When** they query logs for processing times
- **Then** structured logs show duration_ms for each agent
- **And** percentile calculations (p50, p95, p99) are possible
- **And** performance regressions are detected automatically

**Scenario 5: Security Audit**
- **Given** a security audit requires proof of input sanitization
- **When** auditors review logs
- **Then** all sanitization events are logged with timestamps
- **And** security-relevant actions have AUDIT log level
- **And** logs demonstrate compliance with security policies

### Edge Cases and Error Conditions

- **Log Rotation**: System handles log file growth with automatic rotation (100MB per file, keep 10 files)
- **Disk Full**: Logging gracefully degrades when disk space exhausted (doesn't crash system)
- **Unicode in Logs**: Emoji and non-Latin characters logged correctly
- **Sensitive Data Scrubbing**: API keys and email addresses are automatically redacted
- **High-Volume Logging**: System handles 1000+ logs/second without performance degradation
- **Initialization Failure**: System continues running even if logging setup fails (fallback to stderr)

## Requirements

### Functional Requirements

- **FR-001**: System MUST replace all 38+ print() statements with structured logging calls (logger.info, logger.error, etc.)
- **FR-002**: System MUST support 5 log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **FR-003**: System MUST include context in every log entry: timestamp (ISO 8601), log level, module name, function name, line number, correlation ID
- **FR-004**: System MUST output logs in two formats: human-readable (colored, aligned) for development and JSON for production
- **FR-005**: System MUST support per-module log level configuration (e.g., Agent 2 at DEBUG, others at INFO)
- **FR-006**: System MUST automatically redact sensitive data patterns (API keys, email addresses) from log messages
- **FR-007**: System MUST include correlation IDs that trace a single email through all agents
- **FR-008**: System MUST log performance metrics (duration_ms) for each major operation
- **FR-009**: System MUST support log rotation (100MB per file, keep 10 files) to prevent disk exhaustion
- **FR-010**: System MUST integrate with standard Python logging for third-party library logs

### Non-Functional Requirements

- **NFR-001**: **Performance** - Logging adds <1ms overhead per log entry (measured via benchmarks)
- **NFR-002**: **Reliability** - Logging failures never crash the main application (graceful degradation)
- **NFR-003**: **Usability** - Development logs are colored and readable without tools
- **NFR-004**: **Observability** - Production logs are JSON for ingestion by Datadog, Sentry, or ELK stack
- **NFR-005**: **Security** - Logs never contain raw API keys, passwords, or full email content (only IDs/metadata)

### Business Rules

- **BR-001**: DEBUG logs are only active when LOG_LEVEL=DEBUG (not in production)
- **BR-002**: Correlation IDs are generated once per email and propagated through all agents
- **BR-003**: Log rotation occurs when files reach 100MB (configurable via settings)
- **BR-004**: Sensitive data patterns (regex: `[A-Za-z0-9]{20,}` for API keys, `[\w\.-]+@[\w\.-]+\.\w+` for emails) are automatically replaced with `[REDACTED]`
- **BR-005**: All ERROR and CRITICAL logs trigger alerts in production monitoring system

### Key Entities

- **LogEntry**: Structured log record
  - `timestamp`: ISO 8601 timestamp (e.g., "2025-11-17T15:42:33.123Z")
  - `level`: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
  - `correlation_id`: UUID tracing single email through pipeline
  - `module`: Python module name (e.g., "src.agents.agent2_extractor")
  - `function`: Function name (e.g., "extract_project_intelligence_llm")
  - `line`: Line number in source file
  - `message`: Human-readable log message
  - `context`: Dictionary of additional metadata (e.g., {email_id: "msg_123", agent: "Agent2", duration_ms: 1250})

- **CorrelationID**: UUID linking all logs for single email
  - Generated in Agent 1 when email first enters pipeline
  - Propagated through LangGraph state
  - Included in all log entries
  - Used for distributed tracing

### Integration Points

- **LangGraph State**: Correlation ID stored in state, accessible to all agents
- **All Agents**: Replace print() with logger.info/debug/error calls
- **main.py**: Initialize logging system on startup
- **Monitoring Tools**: JSON logs ingested by Datadog/Sentry/ELK for alerting and dashboards

## Success Criteria

### Definition of Done

- [ ] All 38+ print() statements replaced with structured logging
- [ ] Logging system initialized in main.py with environment-aware configuration
- [ ] Correlation IDs generated and propagated through LangGraph state
- [ ] JSON formatter for production, colored formatter for development
- [ ] Sensitive data scrubber tested with 20+ patterns (API keys, emails, tokens)
- [ ] Log rotation configured and tested (create 100MB log, verify rotation)
- [ ] Performance benchmarks show <1ms overhead per log entry
- [ ] Integration with monitoring tool validated (send sample logs, verify ingestion)
- [ ] All 10 functional requirements have automated tests
- [ ] Documentation updated with logging best practices

### Measurable Outcomes

| Metric | Current | Target | Success? |
|--------|---------|--------|----------|
| Print Statements | 38+ | 0 | ✅ Code scan validates |
| Log Levels Supported | 0 | 5 (DEBUG-CRITICAL) | ✅ Unit tests validate |
| Log Formats | 1 (print to stdout) | 2 (JSON + colored) | ✅ Integration test validates |
| Correlation ID Coverage | 0% | 100% | ✅ All agents have correlation_id |
| Sensitive Data Leaks | Unknown | 0 | ✅ Security scan validates |
| Logging Overhead | Unknown | <1ms/entry | ✅ Benchmark validates |

### Acceptance Tests

**Test Suite 1: Print Statement Removal**
```
Given: Codebase scan for print() calls
When: All code is scanned
Then: Zero print() statements remain (except in test fixtures)
And: All former print() locations use logger.* methods
And: Code review confirms logging is contextual (not "test" or "hello world")
```

**Test Suite 2: Log Formatting**
```
Given: Logging system initialized in development and production modes
When: Each log level is triggered (DEBUG, INFO, WARNING, ERROR, CRITICAL)
Then: Development logs are colored and human-readable
And: Production logs are valid JSON with all required fields
And: JSON logs can be parsed by Datadog/Sentry/ELK
```

**Test Suite 3: Correlation ID Propagation**
```
Given: A single email entering the pipeline
When: The email is processed through Agents 1, 2, and 3
Then: All log entries share the same correlation_id
And: Correlation ID can be used to filter logs for that email
And: Distributed tracing tools can visualize the flow
```

**Test Suite 4: Sensitive Data Scrubbing**
```
Given: Log messages containing API keys, email addresses, and tokens
When: Logs are written
Then: All sensitive patterns are replaced with [REDACTED]
And: Original messages are never written to disk
And: Security scan confirms no leaks
```

**Test Suite 5: Performance and Reliability**
```
Given: 10,000 log entries generated rapidly
When: Logging overhead is measured
Then: Average overhead is <1ms per entry
And: System throughput is unaffected
And: No logs are lost (all 10,000 entries captured)
And: Log rotation triggers at 100MB
```

## Scope

### In Scope
- Replace all print() statements with structured logging
- Implement 5 log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- JSON and colored formatters
- Correlation ID generation and propagation
- Sensitive data scrubbing
- Log rotation (100MB per file, keep 10)
- Performance metrics (duration_ms) logging
- Integration with standard Python logging
- Configuration via environment variables

### Out of Scope (Future Enhancements)
- Real-time log streaming UI (Phase 2)
- Advanced log aggregation and search (use external tools: Datadog, ELK)
- Custom log dashboards (Phase 3)
- Log-based alerting rules (configured in monitoring tool, not code)
- Log encryption at rest (Phase 3)

## Dependencies

- **Required Before**: None
- **Blocks**: None (but improves debugging for all future features)
- **Integrates With**: All agents (Agent 1, 2, 3), main.py, evaluation system

## Assumptions

1. Structured logging library (structlog) provides sufficient functionality
2. JSON logs are compatible with common monitoring tools (Datadog, Sentry, ELK)
3. Correlation IDs can be stored in LangGraph state without conflicts
4. <1ms logging overhead is acceptable for production workloads
5. 100MB log file size is reasonable for rotation (prevents excessive disk I/O)

## Performance Considerations

- **Logging Overhead**: Must be <1ms per entry to avoid slowing pipeline
- **JSON Serialization**: Use fast JSON library (orjson) for production
- **Async Logging**: Consider async handlers for high-volume logging (Phase 2)
- **Log Sampling**: If >1000 logs/second, implement sampling for DEBUG logs

## Security Considerations

- **Sensitive Data**: Never log full email content, API keys, or passwords
- **Regex Patterns**: Scrubber uses patterns to detect API keys (20+ alphanumeric), email addresses, tokens
- **PII Protection**: Email addresses replaced with `[EMAIL_REDACTED]` in logs
- **Audit Trail**: All security-relevant actions logged with AUDIT level (higher than INFO)
- **Log Access**: Production logs should have restricted read access (only DevOps team)

## Success Metrics

- **Code Quality**: Zero print() statements in production code
- **Observability**: 100% of operations have correlation IDs
- **Performance**: <1ms logging overhead validated by benchmarks
- **Security**: Zero sensitive data leaks validated by security scan
- **Reliability**: Logging failures don't crash system (graceful degradation tested)

---

## Review & Acceptance Checklist

### Constitutional Compliance
- [x] Aligns with Article V (Evidence Traceability)
- [x] Supports Article IX (Performance Budgets)
- [x] Follows Article VIII (Security by Default)

### Content Quality
- [x] No implementation details (structlog mentioned as example only)
- [x] Focused on observability outcomes
- [x] Written for stakeholders (explains WHY logging matters)
- [x] All mandatory sections completed

### Requirement Quality
- [x] All 10 functional requirements testable and measurable
- [x] 5 non-functional requirements cover key quality attributes
- [x] Success criteria clearly defined with metrics
- [x] 5 acceptance scenarios cover development, production, debugging

### Specification Completeness
- [x] Performance considerations documented (< 1ms overhead)
- [x] Security considerations addressed (no sensitive data in logs)
- [x] Integration points identified (all agents, main.py)
- [x] Edge cases addressed (disk full, Unicode, high volume)
- [x] Success criteria measurable (print count, overhead, coverage)

### Clarification Assessment
- [x] No [NEEDS CLARIFICATION] markers
- [x] Ready for planning phase
- [x] All requirements unambiguous
- [x] Scope clearly bounded (in/out scope documented)

---

## Next Phase Readiness

**Status**: ✅ **READY FOR PLANNING PHASE**

This specification is complete, unambiguous, and ready for technical planning. All requirements are testable, success criteria are measurable, and constitutional alignment is verified.

**Recommended Next Step**: Run `/speckit.plan` to generate implementation plan

---

*This specification follows spec-kit methodology with GRAPHMAIL constitution-driven development. Priority: HIGH (enables debugging and monitoring).*
