#!/bin/bash
# 检查 docs/progress.md 中所有阶段是否完成
# 始终返回 0，通过 stdout 报告状态

PROGRESS_FILE="${1:-docs/progress.md}"

if [ ! -f "$PROGRESS_FILE" ]; then
    echo "[file-based-memory] 未找到 progress.md — 无活跃任务。"
    exit 0
fi

TOTAL=$(grep -c "### 阶段" "$PROGRESS_FILE" || true)
COMPLETE=$(grep -cF "**状态：** complete" "$PROGRESS_FILE" || true)
IN_PROGRESS=$(grep -cF "**状态：** in_progress" "$PROGRESS_FILE" || true)
PENDING=$(grep -cF "**状态：** pending" "$PROGRESS_FILE" || true)

: "${TOTAL:=0}" "${COMPLETE:=0}" "${IN_PROGRESS:=0}" "${PENDING:=0}"

if [ "$COMPLETE" -eq "$TOTAL" ] && [ "$TOTAL" -gt 0 ]; then
    echo "[file-based-memory] 所有阶段已完成 ($COMPLETE/$TOTAL)"
else
    echo "[file-based-memory] 进行中 ($COMPLETE/$TOTAL 阶段完成)"
    [ "$IN_PROGRESS" -gt 0 ] && echo "[file-based-memory] $IN_PROGRESS 个阶段进行中"
    [ "$PENDING" -gt 0 ] && echo "[file-based-memory] $PENDING 个阶段待开始"
fi
exit 0
