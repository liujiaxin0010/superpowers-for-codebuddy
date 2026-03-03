# 检查 docs/progress.md 中所有阶段是否完成
param([string]$ProgressFile = "docs/progress.md")

if (-not (Test-Path $ProgressFile)) {
    Write-Host '[file-based-memory] 未找到 progress.md — 无活跃任务。'
    exit 0
}

$content = Get-Content $ProgressFile -Raw
$TOTAL = ([regex]::Matches($content, "### 阶段")).Count
$COMPLETE = ([regex]::Matches($content, "\*\*状态：\*\* complete")).Count
$IN_PROGRESS = ([regex]::Matches($content, "\*\*状态：\*\* in_progress")).Count
$PENDING = ([regex]::Matches($content, "\*\*状态：\*\* pending")).Count

if ($COMPLETE -eq $TOTAL -and $TOTAL -gt 0) {
    Write-Host ('[file-based-memory] 所有阶段已完成 (' + $COMPLETE + '/' + $TOTAL + ')')
} else {
    Write-Host ('[file-based-memory] 进行中 (' + $COMPLETE + '/' + $TOTAL + ' 阶段完成)')
    if ($IN_PROGRESS -gt 0) { Write-Host ('[file-based-memory] ' + $IN_PROGRESS + ' 个阶段进行中') }
    if ($PENDING -gt 0) { Write-Host ('[file-based-memory] ' + $PENDING + ' 个阶段待开始') }
}
exit 0
