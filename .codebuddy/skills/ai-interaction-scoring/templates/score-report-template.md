# AI Interaction Quality Scoring Report

## Task: {{taskDescription}}
## Scoring Date: {{scoringDate}}
## Conversation Source: {{conversationSource}}

---

## Score Overview

| Dimension | Max Score | Actual Score | Score Rate | Evidence Summary |
|-----------|-----------|--------------|------------|-----------------|
| Spec-Coding Compliance | 10 | {{dim1Score}} | {{dim1Rate}} | {{dim1Summary}} |
| Skills/Agent Usage | 5 | {{dim2Score}} | {{dim2Rate}} | {{dim2Summary}} |
| Project Completion | 10 | {{dim3Score}} | {{dim3Rate}} | {{dim3Summary}} |
| Extended Features & UI | 5 | {{dim4Score}} | {{dim4Rate}} | {{dim4Summary}} |
| **Total** | **30** | **{{totalScore}}** | **{{totalRate}}** | |

### Score Level

| Level | Range | Description |
|-------|-------|-------------|
| Excellent | 25-30 | Process-compliant, feature-complete, well-polished |
| Good | 19-24 | Mostly compliant, core features work, minor gaps |
| Acceptable | 13-18 | Partial compliance, some features work, notable gaps |
| Needs Improvement | 0-12 | Significant gaps in process, features, or both |

**Current Level: {{scoreLevel}}**

---

## Detailed Analysis

### 1. Spec-Coding Compliance ({{dim1Score}}/10)

#### Breakdown

| Item | Points | Awarded | Evidence |
|------|--------|---------|----------|
| Requirement Clarification | 2 | {{specItem1}} | {{specEvidence1}} |
| Technical Direction Evaluation | 2 | {{specItem2}} | {{specEvidence2}} |
| Formal Spec Document | 2 | {{specItem3}} | {{specEvidence3}} |
| Implementation Plan | 2 | {{specItem4}} | {{specEvidence4}} |
| Persistent Documentation | 1 | {{specItem5}} | {{specEvidence5}} |
| Quality Gates | 1 | {{specItem6}} | {{specEvidence6}} |

#### Deduction Reasons
{{dim1Deductions}}

---

### 2. Skills/Agent Usage ({{dim2Score}}/5)

#### Skills Used

| # | Skill/Agent | Usage Context |
|---|-------------|---------------|
{{skillsList}}

**Distinct skills count: {{skillsCount}}**

#### Deduction Reasons
{{dim2Deductions}}

---

### 3. Project Completion ({{dim3Score}}/10)

#### Task-Specific Deliverables

| # | Deliverable | Status | Evidence Level | Score |
|---|-------------|--------|---------------|-------|
{{deliverablesList}}

#### Supplementary Evidence
{{supplementaryEvidence}}

#### Negative Evidence (if any)
{{negativeEvidence}}

#### Deduction Reasons
{{dim3Deductions}}

---

### 4. Extended Features & UI Beautification ({{dim4Score}}/5)

#### Extended Features
{{extendedFeatures}}

#### UI Beautification
{{uiBeautification}}

#### Deduction Reasons
{{dim4Deductions}}

---

## Anti-Patterns Detected

| Anti-Pattern | Detected | Occurrences | Impact |
|-------------|----------|-------------|--------|
| False Completion | {{ap1Detected}} | {{ap1Count}} | {{ap1Impact}} |
| Premature Coding | {{ap2Detected}} | {{ap2Count}} | {{ap2Impact}} |
| Bug Fix Loop | {{ap3Detected}} | {{ap3Count}} | {{ap3Impact}} |
| Ignored User Feedback | {{ap4Detected}} | {{ap4Count}} | {{ap4Impact}} |

---

## Highlights

### Strengths
{{strengths}}

### Weaknesses
{{weaknesses}}

---

## Improvement Recommendations

{{recommendations}}

---

## Scoring Methodology

This report was generated using the `ai-interaction-scoring` skill (v1.0.0).

- Scoring is based on conversation evidence (proxy indicators)
- User statements about functionality override code analysis
- Each dimension is scored independently
- Conservative scoring when evidence is ambiguous
- Anti-pattern detection applied as negative modifiers
