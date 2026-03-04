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
