param(
  [string]$TestReportPath = 'docs/quality/test-summary.json',
  [string]$DocSyncPath = 'docs/quality/doc-sync-report.json',
  [string]$ProgressPath = 'docs/progress.md',
  [string]$FindingsPath = 'docs/findings.md',
  [double]$PassRateThreshold = 100,
  [double]$CoverageThreshold = 80,
  [string]$OutputPath = 'docs/quality/last-quality-gate.json'
)

$ErrorActionPreference = 'Stop'

$root = Resolve-Path (Join-Path $PSScriptRoot '..\..\..\..\')
$zhQualityGate = [string]([char]36136) + ([char]37327) + ([char]38376) + ([char]31105)
$zhMissing = [string]([char]32570) + ([char]22833)
$zhFail = [string]([char]26410) + ([char]36798) + ([char]26631)

function Resolve-TargetPath {
  param([string]$PathLike)
  if ([string]::IsNullOrWhiteSpace($PathLike)) {
    return ''
  }
  if ([System.IO.Path]::IsPathRooted($PathLike)) {
    return $PathLike
  }
  return (Join-Path $root $PathLike)
}

function Try-ReadJson {
  param([string]$Path)
  try {
    return Get-Content -Path $Path -Raw -Encoding UTF8 | ConvertFrom-Json
  } catch {
    return $null
  }
}

$missing = @()
$failed = @()
$passRate = $null
$coverage = $null
$docSyncOk = $false
$docSyncState = 'unknown'

$testPath = Resolve-TargetPath $TestReportPath
if (-not (Test-Path $testPath)) {
  $missing += "test report missing: $TestReportPath"
} else {
  $testJson = Try-ReadJson -Path $testPath
  if ($null -eq $testJson) {
    $failed += "test report parse failed: $TestReportPath"
  } else {
    if ($null -ne $testJson.passRate) {
      $passRate = [double]$testJson.passRate
    } elseif (($null -ne $testJson.passed) -and ($null -ne $testJson.total) -and ([double]$testJson.total -gt 0)) {
      $passRate = ([double]$testJson.passed / [double]$testJson.total) * 100
    } else {
      $failed += 'pass rate missing (need passRate or passed/total)'
    }

    if ($null -ne $testJson.coverage) {
      if ($testJson.coverage -is [System.ValueType] -or $testJson.coverage -is [string]) {
        $coverage = [double]$testJson.coverage
      } elseif ($null -ne $testJson.coverage.branches) {
        $coverage = [double]$testJson.coverage.branches
      } elseif ($null -ne $testJson.coverage.statements) {
        $coverage = [double]$testJson.coverage.statements
      }
    }
    if ($null -eq $coverage) {
      $failed += 'coverage missing (need coverage or coverage.branches/statements)'
    }
  }
}

if (($null -ne $passRate) -and ($passRate -lt $PassRateThreshold)) {
  $failed += ('pass rate {0:N2}% < threshold {1:N2}%' -f $passRate, $PassRateThreshold)
}
if (($null -ne $coverage) -and ($coverage -lt $CoverageThreshold)) {
  $failed += ('coverage {0:N2}% < threshold {1:N2}%' -f $coverage, $CoverageThreshold)
}

$docSyncAbsPath = Resolve-TargetPath $DocSyncPath
if (-not (Test-Path $docSyncAbsPath)) {
  $missing += "doc sync report missing: $DocSyncPath"
} else {
  $docSyncJson = Try-ReadJson -Path $docSyncAbsPath
  if ($null -eq $docSyncJson) {
    $failed += "doc sync report parse failed: $DocSyncPath"
  } else {
    $status = ''
    if ($null -ne $docSyncJson.status) {
      $status = ([string]$docSyncJson.status).ToLowerInvariant()
    }
    $inSync = $false
    if ($null -ne $docSyncJson.inSync) {
      $inSync = [bool]$docSyncJson.inSync
    }

    if ($inSync -or @('pass', 'ok', 'synced') -contains $status) {
      $docSyncOk = $true
      $docSyncState = 'pass'
    } else {
      $docSyncState = if ([string]::IsNullOrWhiteSpace($status)) { 'blocked' } else { $status }
      $failed += "doc sync not pass: $docSyncState"
    }
  }
}

$progressAbsPath = Resolve-TargetPath $ProgressPath
if (-not (Test-Path $progressAbsPath)) {
  $missing += "missing progress file: $ProgressPath"
}
$findingsAbsPath = Resolve-TargetPath $FindingsPath
if (-not (Test-Path $findingsAbsPath)) {
  $missing += "missing findings file: $FindingsPath"
}

$status = if (($missing.Count -gt 0) -or ($failed.Count -gt 0)) { 'blocked' } else { 'pass' }
$checkedAt = (Get-Date).ToString('yyyy-MM-ddTHH:mm:ssK')

$output = [ordered]@{
  status = $status
  checkedAt = $checkedAt
  passRate = if ($null -eq $passRate) { $null } else { [Math]::Round([double]$passRate, 2) }
  passRateThreshold = $PassRateThreshold
  coverage = if ($null -eq $coverage) { $null } else { [Math]::Round([double]$coverage, 2) }
  coverageThreshold = $CoverageThreshold
  docSyncStatus = $docSyncState
  missing = $missing
  failed = $failed
}

$outputAbsPath = Resolve-TargetPath $OutputPath
$outputDir = Split-Path -Path $outputAbsPath -Parent
if (-not [string]::IsNullOrWhiteSpace($outputDir) -and -not (Test-Path $outputDir)) {
  New-Item -Path $outputDir -ItemType Directory -Force | Out-Null
}
$output | ConvertTo-Json -Depth 5 | Set-Content -Path $outputAbsPath -Encoding UTF8

if ($status -eq 'blocked') {
  Write-Host "${zhQualityGate}: BLOCKED"
  $missing | ForEach-Object { Write-Host " - ${zhMissing}: $_" }
  $failed | ForEach-Object { Write-Host " - ${zhFail}: $_" }
  Write-Host " - output: $OutputPath"
  exit 1
}

Write-Host "${zhQualityGate}: PASS"
Write-Host (" - passRate: {0:N2}% (>= {1:N2}%)" -f $passRate, $PassRateThreshold)
Write-Host (" - coverage: {0:N2}% (>= {1:N2}%)" -f $coverage, $CoverageThreshold)
Write-Host " - docSync: pass"
Write-Host " - output: $OutputPath"
exit 0
