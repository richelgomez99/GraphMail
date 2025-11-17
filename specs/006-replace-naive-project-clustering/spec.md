# Feature Specification: Intelligent Project Identification

**Feature ID**: 006  
**Status**: Draft  
**Created**: November 17, 2025  
**Priority**: CRITICAL (Week 2)

---

## Overview

The system currently groups consultant-client emails into projects using basic string matching, achieving only 50-60% accuracy. This causes related emails to be fragmented into separate projects, breaking knowledge graph integrity and losing valuable project context. This feature upgrades project identification to use semantic similarity, improving accuracy to 90%+ and enabling the system to correctly group emails that discuss the same project even when worded differently.

**Business Value**: Accurate project grouping is foundational to the entire intelligence pipeline. Without correct project identification, all downstream analysis (fact extraction, verification, graph construction) operates on fragmented data, producing unreliable insights.

---

## User Story

**As a** consultant or project manager reviewing my email history  
**I want** the system to automatically identify and group all emails related to the same project, regardless of how they're worded  
**So that** I can see complete project timelines, extract comprehensive intelligence, and avoid missing critical project context due to emails being incorrectly separated

---

## User Scenarios & Testing

### Scenario 1: Similar Projects with Different Wording

**Context**: A consultant has two email threads about the same payment integration project:
- Thread 1 subjects: "Payment Gateway Integration", "Stripe Setup Questions", "API Keys Configuration"
- Thread 2 subjects: "Payment Processing Implementation", "Stripe API Documentation", "Gateway Testing"

**Current Behavior**: Creates 2 separate projects due to different wording  
**Expected Behavior**: Groups all emails into 1 project (semantic similarity detected)  
**Success Metric**: 90%+ of semantically related emails grouped correctly

### Scenario 2: Long Project Names

**Context**: Emails with subjects:
- "Q4 Marketing Campaign Dashboard Development Phase 1" (51 chars)
- "Q4 Marketing Campaign Dashboard Development Phase 2" (51 chars)

**Current Behavior**: Both truncated to 30 chars → "q4_marketing_campaign_dashbo" → Incorrectly merged  
**Expected Behavior**: Recognized as 2 distinct projects (Phase 1 vs Phase 2)  
**Success Metric**: No information loss due to truncation

### Scenario 3: Email Thread Continuity

**Context**: A project discussion spans multiple reply threads:
- "Initial Proposal: Website Redesign"
- "Re: Initial Proposal: Website Redesign" (uses In-Reply-To header)
- "Follow-up: Website Redesign Questions"
- "Fwd: Website Redesign Timeline"

**Current Behavior**: May fragment based on subject variations  
**Expected Behavior**: Groups all emails using thread metadata (In-Reply-To, References) + participant overlap  
**Success Metric**: 95%+ of emails in same thread grouped together

### Scenario 4: Participant-Based Grouping

**Context**: Emails with different subjects but same sender-receiver pairs discussing one project:
- "Monday Status Update" (Alice → Bob)
- "Tuesday Deliverables" (Alice → Bob)  
- "Wednesday Blockers" (Bob → Alice)

**Current Behavior**: Creates 3 separate projects  
**Expected Behavior**: Groups into 1 project based on participant overlap + temporal proximity  
**Success Metric**: Emails within 48 hours with 80%+ participant overlap are clustered

---

## Functional Requirements

### FR-1: Semantic Similarity Detection
**Description**: System must detect when emails discuss the same project even with different wording  
**Acceptance Criteria**:
- Emails with subjects "Payment Gateway" and "Stripe Integration" are grouped together
- Semantic similarity threshold is configurable (default: 0.7 cosine similarity)
- No arbitrary character truncation

### FR-2: Thread Continuity Support
**Description**: System must use email threading metadata to group related emails  
**Acceptance Criteria**:
- Emails with matching In-Reply-To or References headers are grouped
- Thread IDs are preserved for audit trail
- Thread depth is tracked (original → reply → reply-to-reply)

### FR-3: Participant Overlap Analysis
**Description**: System must consider sender/receiver patterns in grouping  
**Acceptance Criteria**:
- Emails with 80%+ participant overlap within 48 hours are evaluated for clustering
- Participant overlap score is stored per project group
- Multi-participant threads (>3 people) are weighted higher

### FR-4: Temporal Proximity
**Description**: System must consider email timing in clustering decisions  
**Acceptance Criteria**:
- Emails within 48 hours are given higher clustering weight
- Large time gaps (>30 days) reduce clustering likelihood
- Temporal boundaries are visualized in project timeline

### FR-5: Cluster Confidence Scoring
**Description**: System must provide confidence scores for each project cluster  
**Acceptance Criteria**:
- Each project group has a confidence score (0-100%)
- Scores <70% are flagged for review
- Confidence components (semantic, thread, participant, temporal) are tracked separately

### FR-6: No Data Loss
**Description**: System must not lose information through truncation or simplification  
**Acceptance Criteria**:
- Full project names preserved (no 30-char limit)
- Original email subjects stored for reference
- All clustering metadata retained for debugging

---

## Success Criteria

**Measurable Outcomes**:

1. **Accuracy**: 90%+ of emails are grouped into correct projects (validated against ground truth test set)
2. **Precision**: <5% false positives (emails incorrectly grouped together)
3. **Recall**: >85% of related emails are grouped (emails incorrectly separated)
4. **Performance**: Project clustering completes in <5 seconds for 100 emails
5. **Confidence**: 80%+ of project clusters have confidence score >70%
6. **User Validation**: When users review project groups, 95%+ agree with clustering decisions

**Qualitative Measures**:
- Users can trust project groupings without manual verification
- Downstream intelligence extraction (Agent 2) operates on complete project context
- Knowledge graph integrity improves (fewer fragmented projects)

---

## Key Entities

### ProjectCluster
- **Attributes**:
  - cluster_id (unique identifier)
  - project_name (human-readable name)
  - email_ids (list of message IDs in this cluster)
  - confidence_score (0-100%)
  - confidence_breakdown (semantic, thread, participant, temporal scores)
  - participant_set (unique sender/receiver emails)
  - time_span (first_email_date, last_email_date)
  - thread_ids (list of thread identifiers)
  - subject_variations (list of unique subjects in cluster)

### EmailEmbedding
- **Attributes**:
  - message_id
  - subject_embedding (vector representation)
  - body_summary_embedding (vector for first 500 chars)
  - embedding_model (model name/version)

### ClusteringDecision
- **Attributes**:
  - decision_id
  - email_id
  - assigned_cluster_id
  - decision_confidence
  - decision_reasoning (why this cluster was chosen)
  - alternative_clusters (other possible clusters with scores)
  - decision_timestamp

---

## Edge Cases & Error Handling

### Edge Case 1: Ambiguous Emails
**Scenario**: Email could belong to multiple projects  
**Handling**: 
- Assign to highest-confidence cluster
- Log alternative clusters (confidence >50%) for review
- Flag for user verification if top 2 clusters are close (<10% confidence difference)

### Edge Case 2: Single-Email Projects
**Scenario**: Email doesn't match any existing cluster  
**Handling**:
- Create new cluster if confidence <50% for all existing clusters
- Mark as "singleton" for potential later merging
- Re-evaluate when new emails arrive

### Edge Case 3: Empty or Invalid Subjects
**Scenario**: Email has no subject or subject is "[no subject]"  
**Handling**:
- Use email body for embedding (first 500 chars)
- Weight participant overlap and thread continuity higher
- Never reject or drop email due to missing subject

### Edge Case 4: Very Large Email Batches
**Scenario**: Clustering >1000 emails at once  
**Handling**:
- Process in batches of 200
- Use hierarchical clustering for efficiency
- Show progress indicator to user
- Complete within 2 minutes for 1000 emails

---

## Dependencies

**Upstream**:
- Agent 1 email parser (must provide cleaned email data)
- Email metadata extraction (subject, sender, receiver, date, thread IDs)

**Downstream**:
- Agent 2 intelligence extractor (consumes project groups)
- Graph builder (uses project boundaries)
- Trust score calculator (validates cluster quality)

**External**:
- None (all processing happens within system)

---

## Assumptions

1. **Email Quality**: Emails have been cleaned (signatures removed, forward chains removed) before clustering
2. **Language**: All emails are in English (no multi-language semantic similarity)
3. **Metadata Availability**: Email headers contain standard fields (From, To, Subject, Date)
4. **Volume**: Typical usage involves 50-500 emails per analysis run
5. **Thread Headers**: Most email clients populate In-Reply-To and References headers correctly
6. **Semantic Model**: Pre-trained sentence transformer model is sufficient (no domain-specific fine-tuning required)

---

## Out of Scope

- **Multi-language support**: Non-English emails are not semantically analyzed (future enhancement)
- **Real-time clustering**: Clustering happens during batch processing, not as emails arrive
- **User-defined clusters**: Users cannot manually override or merge clusters (future enhancement)
- **Cross-project relationships**: Identifying dependencies between projects (separate feature)
- **Calendar event integration**: Linking calendar events to projects (handled in Agent 1, not clustering)
- **Machine learning training**: Using user feedback to retrain clustering model (future enhancement)

---

## Open Questions

[NEEDS CLARIFICATION: If an email thread starts as one project but evolves into a different project over time (scope change), should the system:
A) Keep all emails in the original project cluster
B) Split the thread at the transition point and create 2 project clusters
C) Flag for manual review and let user decide]

---

## Acceptance Criteria

- [ ] System groups 90%+ of test emails into correct projects (validated against labeled test set of 200+ emails)
- [ ] No information loss due to truncation (full subject lines preserved)
- [ ] Emails with 70%+ semantic similarity are clustered together
- [ ] Emails in same thread (In-Reply-To match) are clustered together
- [ ] Emails with 80%+ participant overlap within 48 hours are clustered together
- [ ] Each project cluster has confidence score >70% for 80%+ of clusters
- [ ] Clustering completes in <5 seconds for 100 emails, <30 seconds for 500 emails
- [ ] False positive rate (emails incorrectly grouped) is <5%
- [ ] Recall rate (related emails found) is >85%
- [ ] Edge cases (ambiguous emails, empty subjects, large batches) are handled gracefully
- [ ] All clustering decisions are logged with reasoning for debugging
- [ ] Users can review cluster confidence scores and alternatives
- [ ] Downstream agents (Agent 2, Agent 3) successfully consume improved project groups

---

**Next Steps**: 
1. Resolve open question about scope changes
2. Create technical implementation plan (`/speckit.plan`)
3. Generate task breakdown (`/speckit.tasks`)
