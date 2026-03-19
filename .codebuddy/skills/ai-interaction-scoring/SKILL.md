---
name: ai-interaction-scoring
description: "AI interaction quality scoring skill. Evaluates AI coding assistant conversations across 4 dimensions: spec-coding compliance, skills/agent usage, project completion, and extended features/UI quality. Outputs structured scoring reports in MD and XLSX formats."
---

# AI Interaction Quality Scoring

## Purpose

Evaluate the quality of AI coding assistant conversations by analyzing dialogue content, code artifacts, and process compliance. Since direct project execution is not always possible, scoring relies on **proxy indicators** extracted from conversation evidence.

## Input Parameters

`/score-interaction <conversation> [task=<task-description>] [outputDir=<path>]`

| Parameter | Required | Default | Description |
|-----------|----------|---------|-------------|
| conversation | Yes | - | Conversation content (text/JSON) or file path |
| task | No | Auto-detect | Task description for context |
| outputDir | No | `docs/scoring/` | Output directory for reports |

## Scoring Dimensions (Total: 30 Points)

### Dimension 1: Spec-Coding Compliance (10 Points)

Evaluates whether the conversation follows a structured specification-first approach before coding.

| Score | Evidence Criteria |
|-------|-------------------|
| 0 | Coding starts immediately with no planning discussion |
| 3 | Simple requirement description exists but no structured document |
| 5 | Partial spec: has requirement analysis OR interface design, but not both |
| 7 | Has requirement analysis + interface design + technical direction, but missing formal spec document |
| 10 | Full spec-coding workflow: requirement clarification + direction evaluation + formal spec document + implementation plan |

**Detection Patterns:**

1. Spec-related keywords: `spec`, `plan`, `design`, `interface definition`, `data structure`, `technical direction`, `API design`
2. Spec-related commands: `/spec-lite`, `/write-plan`, `/brainstorm`, `/Featureflow`, `/research`
3. Spec document artifacts: files under `docs/specs/`, `docs/plans/`, `spec/` directories
4. Requirement clarification evidence: multi-round Q&A before implementation
5. Direction evaluation evidence: multiple implementation approaches compared with trade-offs
6. Plan document artifacts: batch/phase planning with task breakdown

**Scoring Rules:**

- +2: Requirement clarification phase exists (multi-round Q&A)
- +2: Technical direction evaluation with multiple options
- +2: Formal spec document generated (spec-lite or equivalent)
- +2: Implementation plan with task breakdown and batches
- +1: Persistent documentation maintained (findings.md, progress.md)
- +1: Gate checks or quality gates referenced

### Dimension 2: Skills/Agent Usage (5 Points)

Evaluates the breadth of skill and agent utilization during the conversation.

| Score | Evidence Criteria |
|-------|-------------------|
| 0 | No `/` commands or agent invocations used |
| 2 | 1 skill or agent used |
| 3 | 2 skills or agents used |
| 4 | 3 skills or agents used |
| 5 | 4 or more distinct skills or agents used |

**Detection Method:**

1. Count distinct `/xxx` slash command invocations in the conversation
2. Detect agent calls (code-reviewer, task-implementer, etc.)
3. Reference skill list from `.codebuddy/commands/` and `.codebuddy/skills/`
4. Common skills: `/Featureflow`, `/spec-lite`, `/write-plan`, `/execute-plan`, `/code-review`, `/unified-test`, `/test-gen`, `/fix-bug`, `/simplify`, `/brainstorm`, `/extend`, `/research`, `/status`, `/doc-sync`, `/pua`
5. De-duplicate: same skill invoked multiple times counts as 1

### Dimension 3: Project Completion (10 Points)

Evaluates whether the delivered project actually works, using proxy indicators when direct execution is not possible.

**Evaluation is task-specific.** The scoring system adapts to the actual task requirements. For each task, identify 5 core deliverables and score 2 points each.

**Generic Deliverable Assessment Template (2 Points Each):**

| Assessment Item | Evidence Sources |
|----------------|-----------------|
| Core Feature 1 | API endpoint + handler code + frontend integration |
| Core Feature 2 | API endpoint + handler code + frontend integration |
| Core Feature 3 | API endpoint + handler code + frontend integration |
| Core Feature 4 | API endpoint + handler code + frontend integration |
| UI/UX Completeness | UI framework + layout components + structured styles |

**For each deliverable, apply the following scoring:**

| Evidence Level | Points | Criteria |
|---------------|--------|----------|
| Full evidence | 2 | Code exists + tests pass + runtime verification shown |
| Partial evidence | 1 | Code exists + compiles/builds, but no runtime verification |
| No evidence | 0 | Code missing or broken, no compilation evidence |

**Supplementary Evidence (Strengthens or Weakens Score):**

- Startup command (`npm start`, `go run`, etc.) with successful output log
- Test execution records with pass/fail results
- Screenshots or `localhost:xxx` access descriptions
- User confirmation that feature works
- User reports of bugs or failures (negative evidence)

**Critical Rule:** If the user explicitly reports that a feature does not work (e.g., "page shows no files"), that feature scores 0 regardless of code existence.

### Dimension 4: Extended Features & UI Beautification (5 Points)

Evaluates whether the project goes beyond basic requirements.

| Score | Evidence Criteria |
|-------|-------------------|
| 0 | Only basic requirements fulfilled, no extras |
| 2 | Has extended features OR UI beautification (one of the two) |
| 3 | Has both, but with known bugs or incomplete implementation |
| 4 | Has both with mostly working implementation |
| 5 | Has both with verified working implementation |

**Extended Feature Keywords:**

- Category/tags, priority levels, search/filter, drag-and-drop sorting
- Completion statistics, local storage/localStorage, dark mode
- File preview, batch operations, real-time sync, notifications
- Pagination, export, import, keyboard shortcuts

**UI Beautification Keywords:**

- Responsive/responsive design, animation/transition, theme/dark mode
- Icons/icon library, mobile adaptation/media query
- UI component library (Ant Design, Element Plus, Naive UI, etc.)
- Layout components, grid system, card/panel design

## Execution Flow

1. **Parse Input**: Extract conversation content and optional parameters
2. **Task Identification**: Determine the task type and core deliverables
3. **Evidence Collection**: Scan conversation for scoring evidence across all 4 dimensions
4. **Score Calculation**: Apply scoring rules with evidence mapping
5. **Highlight Analysis**: Identify strengths and weaknesses
6. **Report Generation**: Output MD report + XLSX summary

## Output Artifacts

### Primary: `ai-interaction-scoring-report.md`

Generated in `outputDir` using the template at `templates/score-report-template.md`.

### Secondary: `ai-interaction-scoring-report.xlsx`

Generated using the `xlsx` skill with the following columns:

| Column | Field | Required | Description |
|--------|-------|----------|-------------|
| A | Dimension | * | Scoring dimension name |
| B | Max Score | * | Maximum possible score |
| C | Actual Score | * | Awarded score |
| D | Score Rate | * | Percentage (Actual/Max) |
| E | Key Evidence | * | Primary evidence summary |
| F | Deduction Reasons | | Reasons for point deductions |
| G | Improvement Suggestions | | Actionable improvement advice |

XLSX formatting requirements:
- Header row: bold, light blue background, frozen first row
- Score Rate column: percentage format with conditional coloring (green >= 80%, yellow >= 60%, red < 60%)
- Auto-fit column widths
- Summary row at bottom with total score

## Anti-Patterns to Detect

The scoring system should flag the following negative patterns:

| Anti-Pattern | Impact | Detection |
|-------------|--------|-----------|
| False Completion | Deduct from Dim 3 | Claims "done" without test evidence |
| Premature Coding | Deduct from Dim 1 | Starts coding before any planning |
| Bug Loop | Deduct from Dim 3 | Same bug fixed 3+ times without resolution |
| Scope Creep | Note in report | Significant feature additions not in original spec |
| Ignored User Feedback | Deduct from Dim 3 | User reports issue, AI claims it's fixed without evidence |

## Scoring Calibration Notes

- Scoring is based on **evidence in the conversation**, not assumptions
- When evidence is ambiguous, score conservatively (lower)
- User statements about functionality override code analysis (user says "doesn't work" = it doesn't work)
- Compilation success alone is not sufficient evidence for "feature works"
- Each dimension is scored independently; high scores in one do not compensate for low scores in another
