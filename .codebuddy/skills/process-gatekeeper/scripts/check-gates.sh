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
  "devflow-ai.md"
  "issue-draft-pr.md"
  "parallel-delivery.md"
  "extend.md"
  "status.md"
  "brainstorm.md"
  "research.md"
  "testcase.md"
  "code-self-check.md"
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
  ".codebuddy/commands/devflow-ai.md"
  ".codebuddy/agents/devflow-ai.md"
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
  ".codebuddy/skills/process-gatekeeper/gate-matrix.md"
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
