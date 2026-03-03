#!/bin/bash
# ============================================================
# unified-test 通用清理脚本
# 用途: 清理测试流程中产生的临时文件
# 用法: bash cleanup.sh [vue|go|all] [项目根目录]
# ============================================================

set -e

ADAPTER=${1:-all}
PROJECT_ROOT=${2:-.}

echo "🧹 开始清理临时文件..."
echo "   适配器: $ADAPTER"
echo "   项目根目录: $PROJECT_ROOT"
echo ""

# 计数器
CLEANED=0

# 安全删除函数（文件不存在时不报错）
safe_rm() {
    local file="$1"
    if [ -f "$file" ]; then
        rm -f "$file"
        echo "   ✅ 已删除: $file"
        CLEANED=$((CLEANED + 1))
    fi
}

# ============================================================
# 前端 (Vue/Jest) 临时文件
# ============================================================
cleanup_vue() {
    echo "📦 清理前端临时文件..."

    local vue_temp_files=(
        "test_output.txt"
        "test_coverage_output.txt"
        "test_coverage_run.txt"
        "test_final_output.txt"
        "test_final_output2.txt"
        "test_final2_output.txt"
        "test_new_output.txt"
        "test_success_final.txt"
        "test_success_output.txt"
        "test_success_output2.txt"
        "test-report.html"
        "test_all_passed.txt"
        "test_iteration_output.txt"
        "coverage_iteration_output.txt"
    )

    for file in "${vue_temp_files[@]}"; do
        safe_rm "$PROJECT_ROOT/$file"
    done

    echo ""
}

# ============================================================
# 后端 (Go) 临时文件
# ============================================================
cleanup_go() {
    echo "📦 清理后端临时文件..."

    # 递归查找 mock_test 目录下的 coverage 文件
    if [ -d "$PROJECT_ROOT/code/src/mock_test" ]; then
        find "$PROJECT_ROOT/code/src/mock_test" -name "coverage.out" -type f | while read -r file; do
            safe_rm "$file"
        done
        find "$PROJECT_ROOT/code/src/mock_test" -name "coverage.html" -type f | while read -r file; do
            safe_rm "$file"
        done
    fi

    # 项目根目录下的 coverage 文件
    safe_rm "$PROJECT_ROOT/coverage.out"
    safe_rm "$PROJECT_ROOT/coverage.html"

    echo ""
}

# ============================================================
# 执行清理
# ============================================================
case "$ADAPTER" in
    vue)
        cleanup_vue
        ;;
    go)
        cleanup_go
        ;;
    all)
        cleanup_vue
        cleanup_go
        ;;
    *)
        echo "❌ 未知适配器类型: $ADAPTER"
        echo "   支持: vue | go | all"
        exit 1
        ;;
esac

echo "🏁 清理完成，共删除 $CLEANED 个临时文件"
