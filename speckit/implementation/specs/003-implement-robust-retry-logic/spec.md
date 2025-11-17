# Feature Specification: Retry Logic with Exponential Backoff

**Feature Branch**: `003-implement-robust-retry-logic`  
**Created**: 2025-11-17  
**Status**: Ready for Planning  
**Priority**: CRITICAL  
**Effort**: 3 hours  
**Impact**: 9/10 (Prevents pipeline failures from transient API errors)

## Executive Summary

Implement intelligent retry logic with exponential backoff for all LLM API calls to handle transient failures (rate limits, timeouts, network issues) gracefully without manual intervention. This transforms GRAPHMAIL from a fragile prototype that crashes on API errors into a resilient system that automatically recovers from temporary failures.

**Reliability Context**: Current system has zero error handling for LLM APIs. A single rate limit error causes the entire pipeline to fail. This feature increases reliability from 60% to 99%+.

## Constitutional Alignment

This specification adheres to the GRAPHMAIL constitution:

- **Article IV: LLM Verification Layer** - Reliable LLM access is foundational to verification process
- **Article IX: Performance Budgets** - Retry delays must be reasonable (total <10s for 3 retries)
- **Article V: Evidence Traceability** - All retry attempts logged for debugging

## User Scenarios & Testing

### Primary User Story

**As a** system operator running GRAPHMAIL on production data  
**I want** the system to automatically recover from temporary API failures  
**So that** pipelines complete successfully even when LLM providers have transient issues

### Secondary User Story

**As a** developer testing GRAPHMAIL  
**I want** clear feedback when API calls fail and are retried  
**So that** I understand system behavior and can distinguish permanent vs temporary failures

### Acceptance Scenarios

**Scenario 1: Rate Limit Recovery (Happy Path)**
- **Given** Agent 2 makes 60 LLM calls in rapid succession
- **When** the 51st call hits the rate limit (50/min)
- **Then** the system automatically retries after 1 second
- **And** the retry succeeds (rate limit window reset)
- **And** logs show "Rate limit hit, retry 1/3 after 1.0s"
- **And** pipeline continues without manual intervention

**Scenario 2: Network Timeout Recovery**
- **Given** an LLM API call times out after 30 seconds (network issue)
- **When** the system detects the timeout
- **Then** the system retries immediately (no delay needed)
- **And** the retry succeeds
- **And** total time is 30s + 3s = 33s (acceptable)
- **And** logs show "Timeout error, retry 1/3"

**Scenario 3: Exponential Backoff Progression**
- **Given** an LLM API call fails 3 times due to server overload (503 errors)
- **When** each failure occurs
- **Then** retry delays increase exponentially: 1s, 2s, 4s
- **And** logs show attempt number and delay for each retry
- **And** after 3 failures, the system reports permanent failure
- **And** the error includes context about all 3 attempts

**Scenario 4: Permanent Failure Detection**
- **Given** an LLM API call fails with invalid API key (401 error)
- **When** the system detects the error
- **Then** no retries are attempted (not a transient error)
- **And** the error is immediately logged as CRITICAL
- **And** pipeline fails fast (doesn't waste time retrying)
- **And** clear error message explains the API key issue

**Scenario 5: Partial Pipeline Recovery**
- **Given** a pipeline processing 100 emails
- **When** email #47 hits a transient error (rate limit)
- **Then** only email #47 is retried (others continue normally)
- **And** the pipeline completes successfully for all 100 emails
- **And** total time increase is minimal (only affected by one retry)

### Edge Cases and Error Conditions

- **All Retries Exhausted**: System fails gracefully with clear error after 3 attempts
- **Mixed Error Types**: System correctly identifies retryable vs non-retryable errors
- **Rate Limit Window**: System respects provider-specific rate limit reset times
- **Jitter**: Random jitter added to backoff delays to prevent thundering herd
- **Concurrent Retries**: Multiple emails retrying simultaneously don't interfere
- **Maximum Delay**: Total retry time capped at 10 seconds to prevent excessive waits

## Requirements

### Functional Requirements

- **FR-001**: System MUST automatically retry failed LLM API calls up to 3 times before reporting permanent failure
- **FR-002**: System MUST use exponential backoff delays: 1 second (1st retry), 2 seconds (2nd retry), 4 seconds (3rd retry)
- **FR-003**: System MUST distinguish between retryable errors (rate limits, timeouts, 5xx server errors) and non-retryable errors (authentication failures, invalid requests)
- **FR-004**: System MUST log each retry attempt with context: attempt number, error type, delay, correlation ID
- **FR-005**: System MUST add random jitter (±20% of delay) to prevent thundering herd when multiple requests retry simultaneously
- **FR-006**: System MUST respect provider-specific rate limit headers (Retry-After) when available
- **FR-007**: System MUST accumulate total retry time and fail if it exceeds 10 seconds (prevents indefinite hangs)
- **FR-008**: System MUST preserve original error context when all retries fail (includes all 3 error messages)
- **FR-009**: System MUST allow configuration of retry parameters (max attempts, base delay) via settings
- **FR-010**: System MUST fail fast (no retries) for non-retryable errors like authentication failures

### Non-Functional Requirements

- **NFR-001**: **Reliability** - System recovers from 95%+ of transient failures without manual intervention
- **NFR-002**: **Performance** - Total retry overhead for 3 attempts is <10 seconds (1s + 2s + 4s = 7s + API call time)
- **NFR-003**: **Observability** - All retry attempts are logged with structured data (attempt, delay, error, outcome)
- **NFR-004**: **Maintainability** - Retry logic is centralized in a single decorator or wrapper (not duplicated)
- **NFR-005**: **Testability** - Retry behavior can be simulated with mock failures (no real API calls needed)

### Business Rules

- **BR-001**: Maximum 3 retry attempts per API call (prevents infinite loops)
- **BR-002**: Exponential backoff base delay is 1 second (configurable via settings)
- **BR-003**: Jitter range is ±20% of calculated delay (prevents synchronized retries)
- **BR-004**: Non-retryable errors: 400 (Bad Request), 401 (Unauthorized), 403 (Forbidden), 404 (Not Found)
- **BR-005**: Retryable errors: 429 (Rate Limit), 500 (Server Error), 502 (Bad Gateway), 503 (Service Unavailable), 504 (Timeout)
- **BR-006**: If Retry-After header present, use its value instead of calculated backoff
- **BR-007**: Total retry time cap is 10 seconds (after which permanent failure is reported)

### Key Entities

- **RetryContext**: State tracked across retry attempts
  - `attempt_number`: Current attempt (1, 2, or 3)
  - `max_attempts`: Maximum retries allowed (default: 3)
  - `base_delay`: Base delay in seconds (default: 1)
  - `errors_history`: List of errors from previous attempts
  - `total_elapsed_time`: Cumulative time spent retrying
  - `correlation_id`: Links retries to original request
  - `error_classification`: "retryable" or "non_retryable"

- **RetryDecision**: Outcome of retry eligibility check
  - `should_retry`: Boolean indicating if retry is appropriate
  - `delay_seconds`: Calculated delay before next attempt (with jitter)
  - `reason`: Explanation for decision (e.g., "Rate limit detected", "Authentication failure - non-retryable")

### Integration Points

- **Agent 2 (Extractor)**: Wrap all `llm.invoke()` calls with retry decorator
- **Agent 3 (Verifier)**: Wrap all `llm.invoke()` calls with retry decorator
- **Logging System**: Log all retry attempts with structured data
- **Configuration System**: Retry parameters (max attempts, base delay) from settings

## Success Criteria

### Definition of Done

- [ ] Retry decorator created that wraps LLM API calls
- [ ] Exponential backoff implemented with jitter (1s, 2s, 4s ±20%)
- [ ] Error classification logic distinguishes retryable vs non-retryable errors
- [ ] Retry-After header parsing implemented for rate limits
- [ ] All LLM calls in Agent 2 wrapped with retry decorator
- [ ] All LLM calls in Agent 3 wrapped with retry decorator
- [ ] Retry attempts logged with structured data (attempt, delay, error)
- [ ] Configuration via settings (max_attempts, base_delay, jitter_range)
- [ ] Unit tests for retry logic (20+ scenarios including edge cases)
- [ ] Integration tests simulate transient failures and verify recovery

### Measurable Outcomes

| Metric | Current | Target | Success? |
|--------|---------|--------|----------|
| Pipeline Reliability | 60% (fails on API errors) | 99%+ | ✅ Simulated failures validate |
| Transient Error Recovery | 0% | 95%+ | ✅ Retry tests validate |
| Retry Overhead | N/A | <10s total | ✅ Performance tests validate |
| LLM Calls Protected | 0% | 100% | ✅ Code coverage validates |
| Retry Context Logged | 0% | 100% | ✅ Log tests validate |

### Acceptance Tests

**Test Suite 1: Exponential Backoff Behavior**
```
Given: LLM API call fails 3 times with retryable errors (503 Service Unavailable)
When: Retry logic executes
Then: Delays are 1s (±0.2s), 2s (±0.4s), 4s (±0.8s)
And: Total elapsed time is ~7 seconds (plus API call time)
And: Jitter prevents exact timing (prevents thundering herd)
And: All 3 attempts are logged with delays
```

**Test Suite 2: Error Classification**
```
Given: LLM API calls fail with various HTTP status codes
When: Error classification runs
Then: 429, 500, 502, 503, 504 are classified as "retryable"
And: 400, 401, 403, 404 are classified as "non_retryable"
And: Retryable errors trigger retries
And: Non-retryable errors fail immediately (no retries)
```

**Test Suite 3: Retry-After Header Respect**
```
Given: LLM API returns 429 with Retry-After: 5 header
When: Retry logic calculates delay
Then: Delay is 5 seconds (from header, not 1s from exponential backoff)
And: System waits 5 seconds before retry
And: Log shows "Respecting Retry-After: 5s"
```

**Test Suite 4: Permanent Failure Reporting**
```
Given: LLM API call fails 3 times despite retries
When: All retry attempts exhausted
Then: System raises exception with context from all 3 attempts
And: Error message includes: "Failed after 3 attempts: [error1, error2, error3]"
And: Correlation ID links all retry logs
And: CRITICAL log entry created
```

**Test Suite 5: Partial Pipeline Resilience**
```
Given: Pipeline processing 10 emails
And: Email #5 hits rate limit (retryable)
And: Email #8 has invalid API key (non-retryable)
When: Pipeline executes
Then: Emails 1-4, 6-7, 9-10 complete successfully
And: Email #5 completes after 1 retry (1s delay)
And: Email #8 fails immediately with clear error
And: Overall pipeline reports 9/10 success (90%)
```

## Scope

### In Scope
- Exponential backoff with jitter (1s, 2s, 4s ±20%)
- Error classification (retryable vs non-retryable)
- Retry-After header parsing
- Decorator/wrapper for LLM API calls
- Structured logging of retry attempts
- Configuration via settings (max attempts, delays)
- Total retry time cap (10 seconds)
- Unit and integration tests

### Out of Scope (Future Enhancements)
- Circuit breaker pattern (Phase 2 - prevents overwhelming failing service)
- Retry budgets per user (Phase 2 - prevents abuse)
- Adaptive backoff (Phase 3 - adjusts delays based on success rate)
- Bulkhead pattern (Phase 3 - isolates failures)
- Custom retry strategies per LLM provider (Phase 3)

## Dependencies

- **Required Before**: Structured Logging System (for logging retry attempts)
- **Blocks**: None (but increases reliability for all LLM-dependent features)
- **Integrates With**: Agent 2, Agent 3, Configuration System, Logging System

## Assumptions

1. Retry library (tenacity) provides sufficient functionality for exponential backoff
2. 3 retry attempts are sufficient for most transient failures
3. 10-second total retry time is acceptable for user experience
4. LLM providers return standard HTTP status codes (429, 503, etc.)
5. Jitter range of ±20% is sufficient to prevent thundering herd

## Performance Considerations

- **Retry Overhead**: Worst case is 7 seconds (1s + 2s + 4s) plus API call time
- **Jitter Impact**: Random delays prevent synchronized retries across concurrent requests
- **Total Time Cap**: 10-second cap prevents indefinite hangs
- **Concurrency**: Retry logic doesn't block other requests (async-friendly)

## Security Considerations

- **API Key Exposure**: Never log full API keys in retry error messages (only last 4 chars)
- **Rate Limit Abuse**: Respect Retry-After headers to avoid overwhelming providers
- **DoS Prevention**: Max 3 retries prevents infinite retry loops
- **Error Context**: Logged errors must not include sensitive email content (only IDs)

## Success Metrics

- **Reliability**: 95%+ recovery rate for transient failures
- **Performance**: <10s total retry overhead
- **Coverage**: 100% of LLM calls protected by retry logic
- **Observability**: 100% of retry attempts logged with context
- **Maintainability**: Retry logic centralized (not duplicated across code)

---

## Review & Acceptance Checklist

### Constitutional Compliance
- [x] Aligns with Article IV (LLM Verification Layer)
- [x] Supports Article IX (Performance Budgets)
- [x] Follows Article V (Evidence Traceability)

### Content Quality
- [x] No implementation details (tenacity mentioned as example only)
- [x] Focused on reliability outcomes
- [x] Written for stakeholders (explains WHY retries matter)
- [x] All mandatory sections completed

### Requirement Quality
- [x] All 10 functional requirements testable and measurable
- [x] 5 non-functional requirements cover key quality attributes
- [x] Success criteria clearly defined with metrics
- [x] 5 acceptance scenarios cover rate limits, timeouts, failures

### Specification Completeness
- [x] Performance considerations documented (<10s total)
- [x] Security considerations addressed (no API key exposure)
- [x] Integration points identified (Agents 2&3, logging, config)
- [x] Edge cases addressed (all retries exhausted, mixed errors)
- [x] Success criteria measurable (reliability %, overhead, coverage)

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

*This specification follows spec-kit methodology with GRAPHMAIL constitution-driven development. Priority: CRITICAL (increases reliability from 60% to 99%+).*
