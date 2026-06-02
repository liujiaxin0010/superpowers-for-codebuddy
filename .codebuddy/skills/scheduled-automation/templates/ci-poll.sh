#!/usr/bin/env bash
# CI 轮询助手（降级模式）
#
# 主路径：经 gitlab-bridge 的 pipeline.status 抽象动作轮询，不需要本脚本。
# 本脚本仅用于「MCP / gitlab-bridge 不可用，但本地装了 glab CLI」的降级场景。
#
# 用法：bash ci-poll.sh <mr_iid> [max_polls] [interval_sec]
#   mr_iid       Merge Request 的 IID
#   max_polls    最大轮询次数，默认 40
#   interval_sec 每次间隔秒数，默认 30
#
# 退出码：0=success，1=failed，2=超时未结束，3=glab 不可用

set -euo pipefail

MR_IID="${1:?用法: bash ci-poll.sh <mr_iid> [max_polls] [interval_sec]}"
MAX_POLLS="${2:-40}"
INTERVAL="${3:-30}"

if ! command -v glab >/dev/null 2>&1; then
  echo "降级轮询需要 glab CLI，但未找到。请改用 gitlab-bridge 的 pipeline.status。" >&2
  exit 3
fi

for i in $(seq 1 "$MAX_POLLS"); do
  echo "=== 轮询 $i/$MAX_POLLS (MR !$MR_IID) ==="
  status="$(glab api "projects/:id/merge_requests/${MR_IID}" | \
            grep -o '"status":"[^"]*"' | head -1 | cut -d'"' -f4 || echo "unknown")"

  case "$status" in
    success)
      echo "CI 通过。"
      exit 0
      ;;
    failed|canceled)
      echo "CI 失败（status=$status）。"
      exit 1
      ;;
    *)
      echo "CI 仍在运行（status=$status），等待 ${INTERVAL}s..."
      sleep "$INTERVAL"
      ;;
  esac
done

echo "达到最大轮询次数仍未结束。"
exit 2
