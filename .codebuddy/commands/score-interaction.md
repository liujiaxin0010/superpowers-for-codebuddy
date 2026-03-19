Please read and strictly follow the instructions in these files, in order:
1. `.codebuddy/skills/ai-interaction-scoring/SKILL.md` (scoring dimensions and rules)
2. `.codebuddy/skills/ai-interaction-scoring/scoring-rules.json` (scoring configuration)
3. `.codebuddy/skills/ai-interaction-scoring/templates/score-report-template.md` (report template)
4. `.codebuddy/skills/xlsx/SKILL.md` (XLSX output)

Your task is:
Evaluate an AI coding assistant conversation and produce a structured quality scoring report.

Execution steps:
1. Parse optional parameters: `task=<description>`, `outputDir=<path>`
2. Accept the conversation content (pasted text, file path, or current conversation context)
3. Identify the task type and determine 5 core deliverables specific to the task
4. Collect evidence for each of the 4 scoring dimensions:
   - **Dimension 1 (Spec-Coding, 10pts)**: Check for requirement clarification, direction evaluation, spec documents, implementation plans, persistent docs, and gate checks
   - **Dimension 2 (Skills/Agent, 5pts)**: Count distinct skill/agent invocations (de-duplicated)
   - **Dimension 3 (Project Completion, 10pts)**: Evaluate each deliverable against evidence levels (full/partial/none). User-reported failures override code evidence
   - **Dimension 4 (Extended Features & UI, 5pts)**: Check for features beyond basic requirements and UI polish
5. Detect anti-patterns: false completion, premature coding, bug loops, ignored user feedback
6. Calculate scores for each dimension and total
7. Identify highlights (strengths and weaknesses)
8. Generate improvement recommendations
9. Output `ai-interaction-scoring-report.md` using the template
10. Output `ai-interaction-scoring-report.xlsx` using the xlsx skill

Scoring constraints:
- Score based on **evidence in the conversation**, not assumptions
- When evidence is ambiguous, score conservatively (lower)
- User statements about functionality override code analysis
- Compilation success alone is NOT sufficient evidence for "feature works"
- Each dimension is scored independently
- The report must include specific evidence citations for every score awarded
- Anti-patterns are flagged even if they do not affect scoring

Output requirements:
- Report must be in the same language as the conversation (Chinese conversation = Chinese report)
- XLSX content must use Chinese headers and descriptions
- All scores must have traceable evidence
- Recommendations must be actionable and specific

$ARGUMENTS
