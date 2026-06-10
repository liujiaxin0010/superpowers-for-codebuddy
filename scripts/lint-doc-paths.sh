#!/usr/bin/env bash
# lint-doc-paths.sh - 校验 markdown 里反引号引用的引擎路径真实存在，根治文档腐烂。
#
# 范围：所有纳管 *.md 中形如 `.codebuddy/...` 的反引号路径（引擎自有命名空间）。
# 豁免：
#   - docs/progress.md / docs/findings.md / docs/pr-summaries/ / docs/archive/ —— 历史台账
#     （含 file-based-memory 归档轮转产物），允许引用已删除的旧路径
#   - */templates/* —— 实例化素材，路径指向业务项目（落地后才存在）
#   - .codebuddy/state/ 与 .codebuddy-runtime —— 运行期才生成
#   - 含 <占位符>、通配符、$变量 的路径
# 锚点：`path §节名` / `path#anchor` 仅校验文件部分。
set -euo pipefail

cd "$(git rev-parse --show-toplevel)"

fail=0
checked=0

while IFS= read -r file; do
  case "$file" in
    docs/progress.md|docs/findings.md|docs/pr-summaries/*|docs/archive/*) continue ;;
    */templates/*) continue ;;
  esac
  while IFS= read -r raw; do
    p="${raw#\`}"; p="${p%\`}"
    p="${p%%#*}"
    p="${p%% §*}"; p="${p%% *}"
    case "$p" in
      *'<'*|*'>'*|*'*'*|*'$'*) continue ;;
      .codebuddy/state/*|.codebuddy-runtime*) continue ;;
    esac
    checked=$((checked + 1))
    if [ ! -e "$p" ]; then
      echo "BROKEN  $file -> $p"
      fail=1
    fi
  done < <(grep -oE '`\.codebuddy/[^`]+`' "$file" 2>/dev/null || true)
done < <(git ls-files '*.md')

echo "lint-doc-paths: checked ${checked} references."
if [ "$fail" -ne 0 ]; then
  echo "lint-doc-paths: broken engine path reference(s) found."
  exit 1
fi
echo "lint-doc-paths: all good."
