#!/usr/bin/env bash
# test-commit-msg-lint.sh - commit-msg-lint.sh 的回归单测。
# 在临时 git 仓库里逐条构造提交信息，断言校验脚本的通过/拒绝行为。
# 约定：base 提交始终合规，使结果只由被测提交决定。
set -euo pipefail

LINT="$(git rev-parse --show-toplevel)/.codebuddy/skills/ci-integration/templates/commit-msg-lint.sh"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

pass=0
fail=0

# run_case <期望退出码> <提交信息>
run_case() {
  local expect="$1" msg="$2"
  local repo="$TMP/case-$((pass + fail))"
  git init -q "$repo"
  (
    cd "$repo"
    git config user.email t@t && git config user.name t
    git config commit.gpgsign false
    git commit -q --allow-empty -m "[AI-0] chore: base"
    git commit -q --allow-empty -m "$msg"
    set +e
    bash "$LINT" >/dev/null 2>&1
    echo $? > .exit
  )
  local got; got="$(cat "$repo/.exit")"
  if [ "$got" = "$expect" ]; then
    pass=$((pass + 1))
  else
    echo "FAIL expect=$expect got=$got msg='$msg'"
    fail=$((fail + 1))
  fi
}

# ── 合规（期望 0）──
run_case 0 "[AI-H] feat: 新增功能"
run_case 0 "[AI-100] fix(core): 修复崩溃"
run_case 0 "[AI-0] AC12345: 工单格式标题"
run_case 0 "[AI-H] docs: 文档更新

正文允许任意内容，但不能再出现第二个标签。"

# ── 拒绝（期望 1）──
run_case 1 "feat: 缺 AI 标签"
run_case 1 "[AI-H] [AI-0] feat: 两个标签"
run_case 1 "feat: [AI-H] 标签不在前缀位"
run_case 1 "[AI-H] 没有类型前缀的标题"
run_case 1 "[AI-H] unknown: 非法类型"
run_case 1 "[AI-50] feat: 非法标签值"

# ── merge 提交豁免：自动生成的合并消息（无 AI 标签）不得被拦 ──
merge_repo="$TMP/merge-case"
git init -q "$merge_repo"
(
  cd "$merge_repo"
  git config user.email t@t && git config user.name t
  git config commit.gpgsign false
  git commit -q --allow-empty -m "[AI-0] chore: base"
  git branch side
  git commit -q --allow-empty -m "[AI-H] feat: 主线提交"
  git checkout -q side
  git commit -q --allow-empty -m "[AI-H] feat: 支线提交"
  git checkout -q -
  git merge -q --no-ff --no-edit side   # 消息形如 "Merge branch 'side'"，无标签
  set +e
  bash "$LINT" >/dev/null 2>&1
  echo $? > .exit
)
if [ "$(cat "$merge_repo/.exit")" = "0" ]; then
  pass=$((pass + 1))
else
  echo "FAIL expect=0 got=$(cat "$merge_repo/.exit") msg='merge commit exemption'"
  fail=$((fail + 1))
fi

echo "test-commit-msg-lint: pass=$pass fail=$fail"
[ "$fail" -eq 0 ]
