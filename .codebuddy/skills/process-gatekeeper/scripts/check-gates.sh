#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
CMDS_DIR="$ROOT/.codebuddy/commands"
NEEDLE=".codebuddy/skills/process-gatekeeper/SKILL.md"

required_cmds=(
  "write-plan.md"
  "execute-plan.md"
  "test-gen.md"
  "unified-test.md"
  "code-review.md"
  "fix-bug.md"
  "Featureflow.md"
  "issue-draft-pr.md"
  "parallel-delivery.md"
  "extend.md"
  "status.md"
  "brainstorm.md"
  "research.md"
  "testcase.md"
  "code-self-check.md"
  "security-review.md"
  "data-safety-check.md"
  "release.md"
  "rollback.md"
  "perf-check.md"
  "system-test.md"
  "resume.md"
  "requirement-coverage.md"
)

missing=()
for name in "${required_cmds[@]}"; do
  path="$CMDS_DIR/$name"
  if [[ ! -f "$path" ]]; then
    missing+=("$name（缺少文件）")
    continue
  fi
  if ! grep -Fq "$NEEDLE" "$path"; then
    missing+=("$name（缺少 gatekeeper 引用）")
  fi
done

required_paths=(
  ".codebuddy/commands/spec-lite.md"
  ".codebuddy/commands/research.md"
  ".codebuddy/commands/testcase.md"
  ".codebuddy/commands/code-self-check.md"
  ".codebuddy/commands/issue-draft-pr.md"
  ".codebuddy/commands/parallel-delivery.md"
  ".codebuddy/commands/Featureflow.md"
  ".codebuddy/agents/Featureflow.md"
  ".codebuddy/skills/devflow-router/SKILL.md"
  ".codebuddy/skills/task-contracts/SKILL.md"
  ".codebuddy/skills/issue-draft-pr/SKILL.md"
  ".codebuddy/skills/parallel-delivery/SKILL.md"
  ".codebuddy/skills/spec-lite/SKILL.md"
  ".codebuddy/skills/research/SKILL.md"
  ".codebuddy/skills/testcase/SKILL.md"
  ".codebuddy/skills/code-self-check/SKILL.md"
  ".codebuddy/skills/spec-lite/template.md"
  ".codebuddy/skills/process-gatekeeper/SKILL.md"
  ".codebuddy/skills/process-gatekeeper/references/gate-matrix.md"
  ".codebuddy/skills/process-gatekeeper/references/command-gate-rules.md"
  ".codebuddy/skills/process-gatekeeper/templates/blocked-report.md"
  ".codebuddy/skills/process-gatekeeper/templates/pass-report.md"
  ".codebuddy/skills/process-gatekeeper/scripts/check-gates.sh"
  ".codebuddy/skills/process-gatekeeper/scripts/check-gates.ps1"
  ".codebuddy/skills/process-gatekeeper/scripts/check-quality.ps1"
  ".codebuddy/skills/process-gatekeeper/scripts/check-quality.sh"
  ".codebuddy/templates/task-contracts/README.md"
  ".codebuddy/templates/task-contracts/new-feature.md"
  ".codebuddy/templates/task-contracts/bugfix.md"
  ".codebuddy/templates/task-contracts/refactor.md"
  ".codebuddy/templates/task-contracts/test.md"
  ".codebuddy/templates/task-contracts/research.md"
  ".codebuddy/templates/task-contracts/review-pr.md"
  ".codebuddy/templates/task-contracts/issue-draft-pr.md"
  ".codebuddy/templates/task-contracts/parallel-delivery.md"
  ".codebuddy/skills/bug-fix/templates/regression-test-contract.md"
  ".codebuddy/skills/requirement-coverage-check/templates/coverage-matrix.schema.json"
  ".codebuddy/skills/security-review/SKILL.md"
  ".codebuddy/skills/data-safety/SKILL.md"
  ".codebuddy/skills/data-safety/templates/data-migration-plan.md"
  ".codebuddy/skills/release-and-rollback/SKILL.md"
  ".codebuddy/skills/release-and-rollback/templates/changelog-entry.md"
  ".codebuddy/skills/release-and-rollback/templates/release-notes.md"
  ".codebuddy/skills/release-and-rollback/templates/rollback-playbook.md"
  ".codebuddy/skills/performance-baseline/SKILL.md"
  ".codebuddy/skills/system-test/SKILL.md"
  ".codebuddy/skills/system-test/templates/system-test-scenarios.md"
  ".codebuddy/skills/system-test/templates/system-test-report.md"
  ".codebuddy/skills/session-handoff/SKILL.md"
  ".codebuddy/skills/session-handoff/schemas/session-handoff.schema.json"
  ".codebuddy/skills/file-based-memory/schemas/progress.schema.json"
  ".codebuddy/skills/file-based-memory/schemas/findings.schema.json"
  ".codebuddy/skills/file-based-memory/scripts/lint-memory.sh"
  ".codebuddy/state/perf-baseline/README.md"
  ".codebuddy/state/session-handoff.json.example"
)

for rel in "${required_paths[@]}"; do
  if [[ ! -f "$ROOT/$rel" ]]; then
    missing+=("$rel（缺失）")
  fi
done

if (( ${#missing[@]} > 0 )); then
  echo "门禁检查: BLOCKED"
  for item in "${missing[@]}"; do
    echo " - $item"
  done
  exit 1
fi

echo "门禁检查: PASS"
