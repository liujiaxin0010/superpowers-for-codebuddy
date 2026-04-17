#!/usr/bin/env bash
# lint-memory.sh - 校验 docs/progress.md 与 docs/findings.md 是否满足结构契约
#
# 用法：bash .codebuddy/skills/file-based-memory/scripts/lint-memory.sh
# 退出码：0 通过；1 校验失败；2 文件缺失

set -euo pipefail

PROGRESS_FILE="docs/progress.md"
FINDINGS_FILE="docs/findings.md"

exit_code=0

check_heading() {
  local file="$1"
  local pattern="$2"
  local label="$3"
  if ! grep -qE "$pattern" "$file"; then
    echo "  [FAIL] $file 缺少 $label（期望匹配：$pattern）"
    exit_code=1
  else
    echo "  [OK]   $file -> $label"
  fi
}

if [[ ! -f "$PROGRESS_FILE" ]]; then
  echo "[BLOCKED] $PROGRESS_FILE 不存在；请根据模板创建"
  exit 2
fi

if [[ ! -f "$FINDINGS_FILE" ]]; then
  echo "[BLOCKED] $FINDINGS_FILE 不存在；请根据模板创建"
  exit 2
fi

echo "=== lint docs/progress.md ==="
check_heading "$PROGRESS_FILE" "^## 会话：" "会话标题"
check_heading "$PROGRESS_FILE" "^### 阶段" "阶段分块（至少 1 个）"
check_heading "$PROGRESS_FILE" "## 测试结果" "测试结果表"
check_heading "$PROGRESS_FILE" "## 错误日志" "错误日志表"
check_heading "$PROGRESS_FILE" "## 五问重启检查" "五问重启检查表"

echo ""
echo "=== lint docs/findings.md ==="
check_heading "$FINDINGS_FILE" "## 需求摘要" "需求摘要"
check_heading "$FINDINGS_FILE" "## 研究发现" "研究发现"
check_heading "$FINDINGS_FILE" "## 技术决策" "技术决策"
check_heading "$FINDINGS_FILE" "## 遇到的问题" "遇到的问题"
check_heading "$FINDINGS_FILE" "## 资源链接" "资源链接"

echo ""
if [[ $exit_code -eq 0 ]]; then
  echo "[PASS] 记忆文档结构校验通过"
else
  echo "[FAIL] 记忆文档结构校验失败，请按模板补齐缺失段落"
fi

exit $exit_code
