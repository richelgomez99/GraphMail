# Feature Specification: Data-Driven Trust Score

**Feature ID**: 011  
**Status**: Draft  
**Created**: November 17, 2025  
**Priority**: MEDIUM (Week 5)

---

## Overview

The system's trust score currently uses arbitrary weights (35% traceability, 25% completeness, 20% phase accuracy, 20% anti-hallucination) and heuristics ("expect 4 facts per email") that are not validated. This feature replaces arbitrary decisions with machine learning on labeled data, resulting in a scientifically validated, reliable quality metric.

**Business Value**: Trust score is the system's primary quality indicator. An unvalidated metric undermines confidence. A data-driven approach ensures the score accurately predicts intelligence quality and guides improvement efforts.

---

## User Story

**As a** consultant evaluating system quality  
**I want** a scientifically validated trust score that accurately reflects intelligence reliability  
**So that** I can confidently use the score to assess which projects have high-quality intelligence and which need review

---

## Functional Requirements

### FR-1: Labeled Dataset Collection
**Description**: Collect 100+ examples with human-annotated quality scores  
**Acceptance Criteria**:
- 100+ extracted intelligence examples
- Each example has human quality score (0-100%)
- Quality criteria documented (accuracy, completeness, etc.)
- Inter-rater reliability >85% (multiple reviewers agree)

### FR-2: Weight Optimization
**Description**: Learn optimal component weights from data  
**Method**: Linear regression on labeled examples  
**Acceptance Criteria**:
- Regression model trained on 70% of data
- Weights optimized for prediction accuracy
- Model validated on held-out 30% test set
- R² score >0.8 (strong predictive power)

### FR-3: Heuristic Replacement
**Description**: Replace "4 facts per email" with learned model  
**Method**: Train regression on email features → fact count  
**Features**: email length, keyword density, participant count, reply depth  
**Acceptance Criteria**:
- Model predicts expected facts per email type
- Confidence intervals provided (lower, expected, upper)
- Model accuracy >80% on test set

### FR-4: Per-Fact Quality Metadata
**Description**: Add quality scores to individual facts  
**Attributes**:
- fact_confidence (0-100%)
- evidence_quality (0-100%)
- extraction_confidence
- verification_confidence
- risk_level (low, medium, high)

**Acceptance Criteria**:
- Every fact has quality metadata
- Metadata used in aggregate trust score
- Low-quality facts flagged for review

### FR-5: Methodology Documentation
**Description**: Document training process for transparency  
**Acceptance Criteria**:
- Data collection process documented
- Model training steps documented
- Weight justifications explained
- Validation results published
- Reproducibility verified (can retrain and get similar results)

---

## Success Criteria

1. **Validation**: Trust score predicts human quality assessment with R² >0.8
2. **Transparency**: All weights justified by data (not arbitrary)
3. **Reliability**: Score variance <10% on similar inputs
4. **Accuracy**: High trust scores (>80%) correspond to 95%+ human-assessed quality
5. **Per-Fact**: Every fact has quality metadata enabling granular analysis

---

## Acceptance Criteria

- [ ] 100+ labeled examples collected with human quality scores
- [ ] Weights optimized using regression (R² >0.8)
- [ ] Heuristics replaced with learned models (80%+ accuracy)
- [ ] Per-fact quality metadata implemented
- [ ] Methodology documented for reproducibility
- [ ] Validation performed on held-out test set
- [ ] Trust score predicts human assessment with R² >0.8
- [ ] High trust scores (>80%) are correct 95%+ of time

---

**Next Steps**: Create implementation plan and task breakdown
