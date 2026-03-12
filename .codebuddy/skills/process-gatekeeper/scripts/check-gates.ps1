$ErrorActionPreference = 'Stop'

$root = Resolve-Path (Join-Path $PSScriptRoot '..\..\..\..\')
$commandsDir = Join-Path $root '.codebuddy\commands'
$needle = '.codebuddy/skills/process-gatekeeper/SKILL.md'
$zhGateCheck = [string]([char]38376)+([char]31105)+([char]26816)+([char]26597)
$zhMissingFile = [string]([char]32570)+([char]23569)+([char]25991)+([char]20214)
$zhMissingRef = [string]([char]32570)+([char]23569)+' gatekeeper '+([char]24341)+([char]29992)
$zhMissing = [string]([char]32570)+([char]22833)

$required = @(
  'write-plan.md',
  'execute-plan.md',
  'test-gen.md',
  'unified-test.md',
  'code-review.md',
  'fix-bug.md',
  'Featureflow.md',
  'issue-draft-pr.md',
  'parallel-delivery.md',
  'extend.md',
  'status.md',
  'brainstorm.md',
  'research.md',
  'testcase.md',
  'code-self-check.md'
)

$escapedNeedle = [regex]::Escape($needle)
$missing = @()
foreach ($name in $required) {
  $path = Join-Path $commandsDir $name
  if (-not (Test-Path $path)) {
    $missing += "$name($zhMissingFile)"
    continue
  }
  $ok = Select-String -Path $path -Pattern $escapedNeedle -Quiet
  if (-not $ok) {
    $missing += "$name($zhMissingRef)"
  }
}

$requiredPaths = @(
  '.codebuddy\commands\spec-lite.md',
  '.codebuddy\commands\research.md',
  '.codebuddy\commands\testcase.md',
  '.codebuddy\commands\code-self-check.md',
  '.codebuddy\commands\issue-draft-pr.md',
  '.codebuddy\commands\parallel-delivery.md',
  '.codebuddy\commands\Featureflow.md',
  '.codebuddy\agents\Featureflow.md',
  '.codebuddy\skills\devflow-router\SKILL.md',
  '.codebuddy\skills\task-contracts\SKILL.md',
  '.codebuddy\skills\issue-draft-pr\SKILL.md',
  '.codebuddy\skills\parallel-delivery\SKILL.md',
  '.codebuddy\skills\spec-lite\SKILL.md',
  '.codebuddy\skills\research\SKILL.md',
  '.codebuddy\skills\testcase\SKILL.md',
  '.codebuddy\skills\code-self-check\SKILL.md',
  '.codebuddy\skills\spec-lite\template.md',
  '.codebuddy\skills\process-gatekeeper\SKILL.md',
  '.codebuddy\skills\process-gatekeeper\gate-matrix.md',
  '.codebuddy\skills\process-gatekeeper\templates\blocked-report.md',
  '.codebuddy\skills\process-gatekeeper\templates\pass-report.md',
  '.codebuddy\skills\process-gatekeeper\scripts\check-gates.ps1',
  '.codebuddy\skills\process-gatekeeper\scripts\check-gates.sh',
  '.codebuddy\skills\process-gatekeeper\scripts\check-quality.ps1',
  '.codebuddy\skills\process-gatekeeper\scripts\check-quality.sh',
  '.codebuddy\templates\task-contracts\README.md',
  '.codebuddy\templates\task-contracts\new-feature.md',
  '.codebuddy\templates\task-contracts\bugfix.md',
  '.codebuddy\templates\task-contracts\refactor.md',
  '.codebuddy\templates\task-contracts\test.md',
  '.codebuddy\templates\task-contracts\research.md',
  '.codebuddy\templates\task-contracts\review-pr.md',
  '.codebuddy\templates\task-contracts\issue-draft-pr.md',
  '.codebuddy\templates\task-contracts\parallel-delivery.md'
)

foreach ($rel in $requiredPaths) {
  $p = Join-Path $root $rel
  if (-not (Test-Path $p)) {
    $missing += "$rel($zhMissing)"
  }
}

if ($missing.Count -gt 0) {
  Write-Host "${zhGateCheck}: BLOCKED"
  $missing | ForEach-Object { Write-Host " - $_" }
  exit 1
}

Write-Host "${zhGateCheck}: PASS"
exit 0
