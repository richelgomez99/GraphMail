# Feature Specification: Centralized Configuration Management

**Feature Branch**: `004-implement-centralized-configuration-management`  
**Created**: 2025-11-17  
**Status**: Ready for Planning  
**Priority**: HIGH  
**Effort**: 4 hours  
**Impact**: 7/10 (Enables environment-specific deployments)

## Executive Summary

Implement a centralized, type-safe configuration system that externalizes all hardcoded values (file paths, limits, timeouts, model names) into environment-aware settings. This transforms GRAPHMAIL from a prototype with scattered magic numbers into a professional system that can be deployed across multiple environments (dev, staging, production) without code changes.

**Maintainability Context**: Current code has 25+ hardcoded values (file paths, limits, model names) that must be changed in code for different environments. This feature enables configuration through environment variables and settings files.

## Constitutional Alignment

This specification adheres to the GRAPHMAIL constitution:

- **Article VII: API-First Design** - Configuration enables clean deployment across environments
- **Article VI: Test-Driven Development** - Type-safe config prevents runtime errors
- **Article VIII: Security by Default** - Secrets managed separately from code

## User Scenarios & Testing

### Primary User Story

**As a** DevOps engineer deploying GRAPHMAIL to staging and production  
**I want** environment-specific configuration without code changes  
**So that** I can deploy the same codebase with different settings (API keys, file paths, limits)

### Secondary User Story

**As a** developer working on GRAPHMAIL locally  
**I want** easy configuration with sensible defaults  
**So that** I can run the system without creating complex config files

### Acceptance Scenarios

**Scenario 1: Environment-Specific Deployment (Happy Path)**
- **Given** GRAPHMAIL is deployed to dev, staging, and production environments
- **When** each environment sets ENV=development/staging/production
- **Then** each environment uses appropriate configuration (verbose logging in dev, minimal in prod)
- **And** API rate limits differ (dev: 10/min, staging: 30/min, prod: 50/min)
- **And** file paths differ (dev: ./output, staging: /var/staging/output, prod: /var/prod/output)
- **And** no code changes required between environments

**Scenario 2: Configuration Validation at Startup**
- **Given** a required configuration value is missing (e.g., OPENAI_API_KEY)
- **When** GRAPHMAIL starts
- **Then** startup fails immediately with clear error message
- **And** error message specifies which config value is missing
- **And** error message shows expected format or valid values
- **And** system never enters invalid state

**Scenario 3: Type-Safe Configuration**
- **Given** configuration specifies email_body_max_length="invalid" (string instead of int)
- **When** GRAPHMAIL starts
- **Then** Pydantic validation fails with type error
- **And** error message explains expected type (int) vs received type (str)
- **And** system fails fast before processing any data

**Scenario 4: Defaults for Optional Settings**
- **Given** a developer runs GRAPHMAIL locally without creating .env file
- **When** GRAPHMAIL starts
- **Then** sensible defaults are used (log_level=INFO, max_retries=3, output_dir=./output)
- **And** system runs successfully with defaults
- **And** developer can optionally override any default via .env

**Scenario 5: Secrets Management**
- **Given** production environment uses secrets manager (AWS Secrets Manager, Vault)
- **When** GRAPHMAIL starts in production
- **Then** API keys loaded from secrets manager (not .env file)
- **And** secrets manager takes precedence over environment variables
- **And** no secrets appear in config dumps or logs

### Edge Cases and Error Conditions

- **Invalid Enum Value**: Setting log_level=TRACE (invalid) fails with list of valid values (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- **Path Validation**: Setting output_dir=/root/output (no write permission) fails at startup
- **Integer Range**: Setting max_retries=-1 (invalid) fails with message "must be >= 0"
- **Conflicting Settings**: Setting rate_limit_enabled=false but rate_limit_per_minute=50 logs warning
- **Environment Variable Typo**: OPENAI_API_KEy (typo) doesn't match expected OPENAI_API_KEY, startup fails with "did you mean" suggestion

## Requirements

### Functional Requirements

- **FR-001**: System MUST externalize all hardcoded values (file paths, limits, timeouts, model names) into configuration
- **FR-002**: System MUST support environment-specific configuration files (.env.development, .env.staging, .env.production)
- **FR-003**: System MUST validate all configuration values at startup using Pydantic models with type checking
- **FR-004**: System MUST fail fast with clear error messages when configuration is invalid or missing required values
- **FR-005**: System MUST provide sensible defaults for optional configuration (log_level=INFO, max_retries=3, etc.)
- **FR-006**: System MUST support configuration via environment variables, .env files, and secrets managers (priority: secrets manager > env vars > .env > defaults)
- **FR-007**: System MUST never log or expose sensitive configuration values (API keys, secrets)
- **FR-008**: System MUST document all configuration options with descriptions and examples in .env.example
- **FR-009**: System MUST support hot-reload of non-critical configuration (log level, rate limits) without restart
- **FR-010**: System MUST provide configuration dump command for debugging (with secrets redacted)

### Non-Functional Requirements

- **NFR-001**: **Usability** - Configuration is self-documenting with clear variable names and .env.example
- **NFR-002**: **Reliability** - Type-safe configuration prevents runtime errors from invalid values
- **NFR-003**: **Security** - Secrets loaded from secure storage, never committed to git (.gitignore includes .env)
- **NFR-004**: **Maintainability** - All configuration centralized in src/config/settings.py (single source of truth)
- **NFR-005**: **Performance** - Configuration loading adds <50ms to startup time

### Business Rules

- **BR-001**: Configuration priority (highest to lowest): Secrets Manager > Environment Variables > .env File > Defaults
- **BR-002**: Required configuration (no defaults): OPENAI_API_KEY or ANTHROPIC_API_KEY (at least one)
- **BR-003**: Optional configuration has sensible defaults (log_level=INFO, max_retries=3, email_body_max_length=5000)
- **BR-004**: Environment-specific files loaded based on ENV variable (.env.{ENV} takes precedence over .env)
- **BR-005**: Configuration validation occurs once at startup (not on every access)

### Key Entities

- **Settings**: Pydantic BaseSettings model
  - `environment`: Enum (development, staging, production)
  - `log_level`: Enum (DEBUG, INFO, WARNING, ERROR, CRITICAL)
  - `openai_api_key`: SecretStr (masked in logs)
  - `anthropic_api_key`: SecretStr (optional)
  - `email_body_max_length`: int (default: 5000, min: 1000, max: 10000)
  - `max_retries`: int (default: 3, min: 0, max: 10)
  - `rate_limit_per_minute`: int (default: 50, min: 1, max: 1000)
  - `output_directory`: Path (default: "./output", must be writable)
  - `agent2_model`: str (default: "gpt-4o")
  - `agent3_model`: str (default: "claude-3-5-sonnet-20241022")
  - `enable_rate_limiting`: bool (default: True)
  - `enable_caching`: bool (default: False, for future)

- **ConfigValidationError**: Custom exception for configuration errors
  - `field_name`: Which configuration field failed validation
  - `error_message`: Human-readable explanation
  - `expected_format`: Example or description of valid values
  - `received_value`: What was provided (secrets redacted)

### Integration Points

- **Startup (main.py)**: Load and validate configuration before initializing agents
- **All Modules**: Import settings from src/config/settings.py (singleton pattern)
- **Agent 2**: Use settings.agent2_model instead of hardcoded "gpt-4o"
- **Agent 3**: Use settings.agent3_model instead of hardcoded "claude-3-5-sonnet-20241022"
- **Rate Limiter**: Use settings.rate_limit_per_minute for threshold
- **Sanitizer**: Use settings.email_body_max_length for truncation
- **Logging**: Use settings.log_level for verbosity

## Success Criteria

### Definition of Done

- [ ] Pydantic BaseSettings model created in src/config/settings.py
- [ ] All 25+ hardcoded values externalized to settings
- [ ] Startup validation implemented with clear error messages
- [ ] .env.example documented with all configuration options
- [ ] Environment-specific .env files created (.env.development, .env.staging, .env.production)
- [ ] Secrets manager integration implemented (AWS Secrets Manager or Vault)
- [ ] Configuration dump command implemented (secrets redacted)
- [ ] Unit tests for configuration validation (50+ test cases covering invalid values)
- [ ] Integration tests verify settings used throughout codebase
- [ ] Documentation updated with configuration guide

### Measurable Outcomes

| Metric | Current | Target | Success? |
|--------|---------|--------|----------|
| Hardcoded Values | 25+ | 0 | ✅ Code scan validates |
| Configuration Files | 1 (.env) | 4 (.env, .env.dev, .env.staging, .env.prod) | ✅ File count validates |
| Startup Validation | None | 100% | ✅ Tests validate |
| Type Safety | None | 100% | ✅ Pydantic validates |
| Configuration Errors Caught | 0% | 100% | ✅ Startup tests validate |
| Configuration Load Time | N/A | <50ms | ✅ Benchmark validates |

### Acceptance Tests

**Test Suite 1: Configuration Validation**
```
Given: 50 test cases with invalid configuration values
      (missing API key, wrong type, out of range, invalid enum, non-writable path)
When: Each configuration is loaded
Then: Pydantic validation fails with clear error
And: Error message specifies field name, expected format, received value
And: System never enters invalid state
And: 100% of invalid configs are caught at startup
```

**Test Suite 2: Environment-Specific Config**
```
Given: Three environment files (.env.development, .env.staging, .env.production)
And: Each has different settings (log_level, rate_limit, output_dir)
When: ENV is set to development/staging/production
Then: Appropriate .env file is loaded
And: Settings match expected values for that environment
And: No cross-environment pollution (prod doesn't use dev settings)
```

**Test Suite 3: Default Values**
```
Given: No .env file exists
And: Only required OPENAI_API_KEY is set via environment variable
When: Configuration is loaded
Then: All optional settings use documented defaults
And: System runs successfully with defaults
And: Defaults match .env.example documentation
```

**Test Suite 4: Configuration Priority**
```
Given: Same setting (log_level) defined in 4 places:
      - Default (INFO)
      - .env file (DEBUG)
      - Environment variable (WARNING)
      - Secrets Manager (ERROR)
When: Configuration is loaded
Then: Secrets Manager value (ERROR) is used (highest priority)
And: Priority order respected: Secrets Manager > Env Var > .env > Default
```

**Test Suite 5: Secrets Management**
```
Given: API keys stored in AWS Secrets Manager
When: Configuration is loaded in production
Then: API keys retrieved from Secrets Manager (not .env)
And: Configuration dump shows API keys as [REDACTED]
And: Logs never contain full API keys
And: Secrets never committed to git (.gitignore validation)
```

## Scope

### In Scope
- Pydantic BaseSettings for type-safe configuration
- Environment variable loading with .env support
- Environment-specific config files (.env.{ENV})
- Startup validation with clear error messages
- Sensible defaults for optional settings
- Secrets manager integration (AWS Secrets Manager)
- Configuration dump command (secrets redacted)
- .env.example documentation
- Unit tests for validation logic

### Out of Scope (Future Enhancements)
- Hot-reload for all configuration (Phase 2 - requires restart for most changes)
- Configuration UI/dashboard (Phase 3)
- Remote configuration management (Phase 3 - use external config service)
- Feature flags system (Phase 3)
- Configuration versioning and rollback (Phase 3)

## Dependencies

- **Required Before**: None
- **Blocks**: None (but improves all features by enabling environment-specific settings)
- **Integrates With**: All modules (agents, logging, rate limiter, sanitizer)

## Assumptions

1. Pydantic BaseSettings provides sufficient functionality for validation
2. .env files are acceptable for local development (secrets manager for production)
3. AWS Secrets Manager is available in production (or equivalent like Vault)
4. <50ms configuration load time is acceptable for startup
5. Environment variable names follow SCREAMING_SNAKE_CASE convention

## Performance Considerations

- **Startup Time**: Configuration loading must add <50ms (measured via benchmark)
- **Lazy Loading**: Configuration loaded once at startup (not on every access)
- **Caching**: Settings object is singleton (no repeated parsing)
- **Validation Cost**: Pydantic validation is one-time cost at startup (negligible)

## Security Considerations

- **Secrets in Git**: .env files must be .gitignored (only .env.example committed)
- **Secrets in Logs**: API keys automatically redacted in config dumps and logs
- **Secrets in Memory**: SecretStr type masks secrets in string representations
- **Production Secrets**: Production must use secrets manager (never .env files)
- **Audit Trail**: Configuration changes logged with timestamps (what changed, when, by whom)

## Success Metrics

- **Hardcoded Values**: Zero hardcoded values in production code
- **Type Safety**: 100% of configuration validated at startup
- **Environment Support**: Deploy to dev, staging, prod without code changes
- **Error Detection**: 100% of invalid configs caught before processing data
- **Documentation**: Every configuration option documented in .env.example

---

## Review & Acceptance Checklist

### Constitutional Compliance
- [x] Aligns with Article VII (API-First Design)
- [x] Supports Article VI (Test-Driven Development)
- [x] Follows Article VIII (Security by Default)

### Content Quality
- [x] No implementation details (Pydantic, AWS Secrets Manager mentioned as examples only)
- [x] Focused on maintainability and deployment outcomes
- [x] Written for stakeholders (explains WHY configuration matters)
- [x] All mandatory sections completed

### Requirement Quality
- [x] All 10 functional requirements testable and measurable
- [x] 5 non-functional requirements cover key quality attributes
- [x] Success criteria clearly defined with metrics
- [x] 5 acceptance scenarios cover validation, environments, defaults

### Specification Completeness
- [x] Security considerations documented (no secrets in git/logs)
- [x] Performance considerations addressed (<50ms load time)
- [x] Integration points identified (all modules)
- [x] Edge cases addressed (invalid values, typos, conflicts)
- [x] Success criteria measurable (hardcoded value count, validation %)

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

*This specification follows spec-kit methodology with GRAPHMAIL constitution-driven development. Priority: HIGH (enables environment-specific deployments).*
