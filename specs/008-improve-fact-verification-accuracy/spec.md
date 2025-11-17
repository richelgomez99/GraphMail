# Feature Specification: Robust Fact Verification

**Feature ID**: 008  
**Status**: Draft  
**Created**: November 17, 2025  
**Priority**: CRITICAL (Week 3)

---

## Overview

The system currently verifies extracted facts with only 70% accuracy, truncating email context to 600 characters and using binary YES/NO decisions. This feature upgrades verification to 90%+ accuracy using full email context, confidence scoring, multi-hop reasoning, and robust error handling.

**Business Value**: Verification is the final quality gate before facts enter the knowledge graph. Low verification accuracy means the system either rejects valid facts (false negatives) or accepts hallucinations (false positives), undermining the zero-hallucination guarantee.

---

## User Story

**As a** consultant relying on extracted project intelligence  
**I want** the system to accurately verify that every fact is supported by email evidence  
**So that** I can trust all information in the knowledge graph is real and traceable

---

## Functional Requirements

### FR-1: Full Context Verification
- Use complete email content (not truncated to 600 chars)
- Include all relevant emails cited as evidence
- Preserve email structure (subject, body, metadata)

### FR-2: Confidence Scoring
- Assign confidence score (0-100%) to every verification
- Score factors: evidence strength, context clarity, contradictions
- Flag verifications <70% for review

### FR-3: Chain-of-Thought Reasoning
- Show step-by-step reasoning process
- Quote specific evidence supporting claim
- Identify contradictions or ambiguities
- Justify final verification decision

### FR-4: Multi-Hop Reasoning
- Support claims requiring multiple emails
- Example: "Project took 3 months" requires checking start (email 1) and end (email 50)
- Link evidence across email chain
- Track causal relationships

### FR-5: Retry Logic
- Implement exponential backoff for verification failures
- Retry up to 3 times with increasing delays (1s, 2s, 4s)
- Log all retry attempts
- Return "unverified" status (not rejected) after max retries

---

## Success Criteria

1. **Accuracy**: 90%+ verification accuracy (validated against 200+ labeled facts)
2. **Context Usage**: 100% of email context used (no truncation)
3. **Confidence Calibration**: High-confidence verifications (>80%) are correct 95%+ of the time
4. **False Negative Rate**: <10% (valid facts incorrectly rejected)
5. **False Positive Rate**: <5% (invalid facts incorrectly accepted)
6. **Processing Time**: <3 seconds per fact verification
7. **Retry Success**: 60%+ of initial failures succeed on retry

---

## Edge Cases

1. **Ambiguous Evidence**: Claim partially supported → Low confidence score (40-60%)
2. **Contradictory Evidence**: Multiple emails conflict → Flag for review, cite contradictions
3. **Verification Service Failures**: Retry with exponential backoff, mark "unverified" after 3 failures
4. **Very Long Emails**: Prioritize relevant sections, include full context in verification

---

## Acceptance Criteria

- [ ] 90%+ verification accuracy on test set (200+ facts)
- [ ] Full email context used (no 600-char truncation)
- [ ] Every verification includes confidence score (0-100%)
- [ ] Chain-of-thought reasoning included
- [ ] Multi-hop reasoning supported (claims spanning multiple emails)
- [ ] Retry logic implemented (3 attempts with exponential backoff)
- [ ] High-confidence verifications (>80%) are correct 95%+ of time
- [ ] False negative rate <10%, false positive rate <5%
- [ ] Processing time <3 seconds per fact
- [ ] Edge cases handled gracefully

---

**Next Steps**: Create implementation plan and task breakdown
