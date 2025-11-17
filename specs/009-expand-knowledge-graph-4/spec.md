# Feature Specification: Comprehensive Knowledge Graph

**Feature ID**: 009  
**Status**: Draft  
**Created**: November 17, 2025  
**Priority**: HIGH (Week 4)

---

## Overview

The system currently captures only 40% of valuable project information using 4 entity types (Project, Topic, Challenge, Resolution). This feature expands the graph to 10 entity types with temporal reasoning and rich relationships, increasing information capture to 85% and enabling timeline reconstruction, causality analysis, and comprehensive project intelligence.

**Business Value**: A richer knowledge graph means consultants can answer complex questions like "Who was responsible for this decision?", "What deliverables were produced?", "How long did it take to resolve this challenge?", and "What are the project dependencies?" - currently impossible with limited entity types.

---

## User Story

**As a** consultant reviewing project history  
**I want** the system to capture all important project entities (people, deliverables, milestones, dependencies, decisions, risks)  
**So that** I can reconstruct complete project timelines, understand causality, and extract comprehensive intelligence

---

## Functional Requirements

### FR-1: Expanded Entity Types
**Current**: 4 types (Project, Topic, Challenge, Resolution)  
**New**: 10 types total:
- Project (existing)
- Topic (existing)
- Challenge (existing)
- Resolution (existing)
- **Person** (consultant, client, stakeholder)
- **Deliverable** (document, code, design, report)
- **Milestone** (deadline, checkpoint, phase completion)
- **Dependency** (task dependency, blocking relationship)
- **Decision** (choice made, approval given, direction set)
- **Risk** (identified risk, mitigation strategy)

**Acceptance Criteria**:
- All 10 entity types are extracted from emails
- Each entity type has specific attributes
- Entity relationships are preserved

### FR-2: Temporal Reasoning
**Description**: Add timestamps and temporal relationships  
**Acceptance Criteria**:
- Every node has timestamp (creation_date, first_mentioned, last_mentioned)
- Every edge has timestamp (relationship_established)
- System can answer "What was project status at time T?"
- Timeline reconstruction shows events in chronological order
- Temporal queries work (e.g., "challenges in last week of project")

### FR-3: Entity Deduplication
**Description**: Merge duplicate mentions of same entity  
**Example**: "Stripe API", "Stripe Integration", "Payment Gateway (Stripe)" → ONE node  
**Acceptance Criteria**:
- Entities with 90%+ semantic similarity are merged
- Evidence from all mentions is combined
- Aliases list shows all name variations
- Merge decisions are logged for audit

### FR-4: Rich Relationship Types
**Current**: Simple edges (HAS_TOPIC, FACED_CHALLENGE, RESOLVED_BY)  
**New**: 8 relationship types:
- HAS_TOPIC (Project → Topic)
- FACED_CHALLENGE (Project → Challenge)
- RESOLVED_BY (Challenge → Resolution)
- **CAUSES** (Event → Effect)
- **DEPENDS_ON** (Task → Prerequisite)
- **RESOLVES** (Resolution → Challenge)
- **MENTIONS** (Generic reference)
- **DELIVERED** (Person → Deliverable)
- **OWNED_BY** (Decision → Person)
- **MITIGATES** (Strategy → Risk)

**Acceptance Criteria**:
- All relationship types are extracted
- Relationships include evidence and confidence
- Causal relationships enable "why" queries

### FR-5: Person Entity Extraction
**Description**: Identify and track people in project  
**Attributes**: name, email, role (consultant, client, stakeholder), participation_count  
**Acceptance Criteria**:
- People are extracted from From/To/Cc fields and email mentions
- Roles are inferred from context
- Participation metrics tracked (# emails sent/received)
- Person-deliverable relationships captured

### FR-6: Deliverable Tracking
**Description**: Track documents, code, designs produced  
**Attributes**: deliverable_name, type, delivery_date, owner, status  
**Acceptance Criteria**:
- Deliverables extracted from phrases like "attached", "here's the", "completed"
- Types classified (document, code, design, report, presentation)
- Ownership linked to people
- Delivery timelines tracked

---

## Success Criteria

1. **Information Capture**: 85%+ of project information captured (up from 40%)
2. **Entity Coverage**: All 10 entity types extracted from test emails
3. **Deduplication Accuracy**: 90%+ of duplicate entities correctly merged
4. **Temporal Queries**: System answers "what happened when" questions correctly
5. **Relationship Richness**: 80%+ of entity relationships have evidence and confidence
6. **Processing Time**: Graph construction <10 seconds for 100 emails

---

## Key Entities (New)

### Person
- name, email, role, participation_count, first_seen, last_seen

### Deliverable
- deliverable_name, type, delivery_date, owner_id, status, evidence

### Milestone
- milestone_name, target_date, completion_date, status, dependencies

### Dependency
- source_id, target_id, dependency_type, blocking, evidence

### Decision
- decision_text, decision_date, decision_maker_id, impact, evidence

### Risk
- risk_description, severity, likelihood, mitigation_strategy, status

---

## Edge Cases

1. **Missing Timestamps**: Use email date as fallback
2. **Ambiguous Entity Types**: Classify with confidence scores
3. **Circular Dependencies**: Detect and flag for review
4. **Conflicting Information**: Store both versions with timestamps

---

## Acceptance Criteria

- [ ] All 10 entity types are extracted and stored
- [ ] 85%+ of project information captured (validated on test set)
- [ ] Temporal reasoning enabled (timestamps on all nodes/edges)
- [ ] Entity deduplication implemented (90%+ accuracy)
- [ ] Rich relationships captured (8 relationship types)
- [ ] Timeline reconstruction works correctly
- [ ] Causality analysis supported (CAUSES relationships)
- [ ] Person tracking complete with roles and participation
- [ ] Deliverable tracking complete with ownership
- [ ] Processing time <10 seconds for 100 emails

---

**Next Steps**: Create implementation plan and task breakdown
