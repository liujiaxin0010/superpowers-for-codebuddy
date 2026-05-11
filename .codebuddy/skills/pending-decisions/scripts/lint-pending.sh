#!/usr/bin/env bash
# 校验 docs/pending-decisions.md 的最小结构契约。
# 退出码：0=通过 / 1=结构缺段落 / 2=文件缺失。

set -eu

FILE="${PENDING_FILE:-docs/pending-decisions.md}"

if [ ! -f "$FILE" ]; then
  echo "[pending-decisions] 文件缺失: $FILE" >&2
  echo "[pending-decisions] BLOCKED：请按 .codebuddy/skills/pending-decisions/template.md 创建。" >&2
  exit 2
fi

errors=0

check_section() {
  local pattern="$1"
  local hint="$2"
  if ! grep -qE "^${pattern}$" "$FILE"; then
    echo "[pending-decisions] 缺少段落: ${hint}" >&2
    errors=$((errors+1))
  fi
}

check_section "## 当前会话" "## 当前会话"
check_section "## 待决策项列表" "## 待决策项列表"

# 检查至少存在一条 PD-YYYYMMDD-NNN 形式的 ID（首次创建时允许仅模板示例存在）
if ! grep -qE "^### PD-[0-9]{8}-[0-9]{3}" "$FILE"; then
  echo "[pending-decisions] 提示：未发现任何 PD-YYYYMMDD-NNN 条目（模板示例已删除？）" >&2
fi

# 检查孤儿 status=answered 但缺 answer/answeredAt
awk '
  /^### PD-/ { id=$2; status=""; answer=""; answered_at=""; next }
  /\*\*状态\*\*/ { sub(/.*：[[:space:]]*/, ""); status=$0; next }
  /\*\*Boss 决策\*\*/ { sub(/.*：[[:space:]]*/, ""); answer=$0; next }
  /\*\*决策时间\*\*/ {
    sub(/.*：[[:space:]]*/, "")
    answered_at=$0
    if (status == "answered" && (answer == "" || answered_at == "")) {
      printf("[pending-decisions] %s 状态 answered 但缺 answer/answeredAt\n", id) > "/dev/stderr"
      exit 1
    }
  }
' "$FILE" || errors=$((errors+1))

if [ "$errors" -gt 0 ]; then
  exit 1
fi

echo "[pending-decisions] 通过：$FILE"
exit 0
