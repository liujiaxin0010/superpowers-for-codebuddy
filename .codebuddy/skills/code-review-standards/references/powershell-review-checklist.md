# PowerShell/Batch Code Review Checklist

Comprehensive checklist for reviewing PowerShell and Windows Batch scripts.

## PowerShell Security

### 1. Command Injection
```powershell
# ❌ WRONG - Invoke-Expression with user input
$userInput = Read-Host "Enter command"
Invoke-Expression $userInput

# ✅ CORRECT - Use parameterized commands
$fileName = Read-Host "Enter filename"
Get-Content -Path $fileName
```

### 2. Credential Handling
```powershell
# ❌ WRONG - Plaintext password
$password = "MyPassword123"
$cred = New-Object PSCredential("user", (ConvertTo-SecureString $password -AsPlainText -Force))

# ✅ CORRECT - Prompt for credentials
$cred = Get-Credential

# ✅ CORRECT - Use SecureString
$securePassword = Read-Host -AsSecureString "Enter password"
```

## Error Handling

### 1. Try-Catch
```powershell
# ❌ WRONG - No error handling
$content = Get-Content "file.txt"

# ✅ CORRECT - Proper error handling
try {
    $content = Get-Content "file.txt" -ErrorAction Stop
} catch {
    Write-Error "Failed to read file: $_"
    exit 1
}
```

### 2. ErrorAction
```powershell
# ❌ WRONG - Errors silently continue
Get-ChildItem "C:\NonExistent"

# ✅ CORRECT - Stop on error
$ErrorActionPreference = "Stop"
# Or per-command:
Get-ChildItem "C:\NonExistent" -ErrorAction Stop
```

## Batch Script (.bat/.cmd)

### 1. Variable Expansion
```batch
@echo off
:: ❌ WRONG - Delayed expansion not enabled
set count=0
for %%i in (1 2 3) do (
    set /a count+=1
    echo %count%  :: Always shows 0
)

:: ✅ CORRECT - Enable delayed expansion
setlocal EnableDelayedExpansion
set count=0
for %%i in (1 2 3) do (
    set /a count+=1
    echo !count!
)
```

### 2. Error Handling
```batch
:: ❌ WRONG - No error check
copy file.txt dest\

:: ✅ CORRECT - Check errorlevel
copy file.txt dest\
if %errorlevel% neq 0 (
    echo Copy failed
    exit /b 1
)
```

## Static Analysis Tools

Recommended tools:
- **PSScriptAnalyzer**: PowerShell static analysis
- **VS Code PowerShell Extension**: Real-time linting

Usage:
```powershell
Install-Module PSScriptAnalyzer
Invoke-ScriptAnalyzer -Path script.ps1
```
