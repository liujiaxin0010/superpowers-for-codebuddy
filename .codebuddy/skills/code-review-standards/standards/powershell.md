PowerShell 编码规范

## 1 范围

本规范适用于 PowerShell 脚本（.ps1）和模块（.psm1）的编写和维护。

## 2 文件结构

### 2.1 文件类型

**规则2-1-1：脚本文件使用 `.ps1` 扩展名，模块使用 `.psm1`，模块清单使用 `.psd1`。**

### 2.2 文件命名

**规则2-2-1：脚本和模块文件使用 PascalCase 命名，遵循动词-名词格式。**

推荐：`Get-UserReport.ps1`、`Install-Service.ps1`
不推荐：`get_user_report.ps1`、`userReport.ps1`

### 2.3 版本声明

**规则2-3-1：脚本开头使用 `#Requires` 声明最低 PowerShell 版本和依赖模块。**

```powershell
#Requires -Version 5.1
#Requires -Modules ActiveDirectory
```

### 2.4 文件头注释

**规则2-4-1：每个脚本应包含基于注释的帮助（Comment-Based Help）。**

```powershell
<#
.SYNOPSIS
    简要描述脚本功能

.DESCRIPTION
    详细描述脚本功能和使用场景

.PARAMETER FilePath
    输入文件路径

.EXAMPLE
    .\Get-UserReport.ps1 -FilePath "C:\data\users.csv"

.NOTES
    作者: [name]
    日期: YYYY-MM-DD
#>
```

### 2.5 文件编码

**规则2-5-1：脚本文件使用 UTF-8 with BOM 编码，确保 PowerShell 正确识别。**

## 3 命名规范

### 3.1 函数和 Cmdlet 命名

**规则3-1-1：函数使用已批准的动词-名词格式（Verb-Noun），动词必须来自 `Get-Verb` 列表。**

推荐：
```powershell
function Get-UserInfo { }
function Set-Configuration { }
function Remove-TempFiles { }
```

不推荐：
```powershell
function Fetch-UserInfo { }    # Fetch 不是已批准动词
function DeleteTempFiles { }   # 缺少连字符
function get-userinfo { }      # 未使用 PascalCase
```

**规则3-1-2：使用 `Get-Verb` 命令查看所有已批准动词，常用动词包括：**
- 数据操作：Get, Set, New, Remove, Add, Clear
- 生命周期：Start, Stop, Restart, Enable, Disable
- 通信：Send, Receive, Connect, Disconnect
- 诊断：Test, Measure, Trace, Debug

### 3.2 变量命名

**规则3-2-1：变量使用 PascalCase。**

```powershell
$UserName = "admin"
$MaxRetryCount = 5
$OutputFilePath = "C:\reports\output.csv"
```

**规则3-2-2：布尔变量使用 Is/Has/Can 前缀。**

```powershell
$IsEnabled = $true
$HasPermission = $false
$CanWrite = Test-Path $FilePath
```

### 3.3 参数命名

**规则3-3-1：参数使用 PascalCase，带类型声明和验证属性。**

```powershell
param(
    [Parameter(Mandatory)]
    [ValidateNotNullOrEmpty()]
    [string]$FilePath,

    [ValidateRange(1, 100)]
    [int]$RetryCount = 3
)
```

## 4 代码风格

### 4.1 缩进

**规则4-1-1：使用 4 个空格缩进，禁止使用制表符。**

### 4.2 大括号

**规则4-2-1：左大括号 `{` 与语句同行（One True Brace Style）。**

推荐：
```powershell
if ($condition) {
    Do-Something
} else {
    Do-Other
}
```

不推荐：
```powershell
if ($condition)
{
    Do-Something
}
```

### 4.3 行宽

**规则4-3-1：每行最大 115 字符。长语句使用反引号 `` ` `` 或 splatting 换行。**

```powershell
# Splatting 方式（推荐）
$Params = @{
    Path        = $FilePath
    Destination = $TargetDir
    Force       = $true
    Recurse     = $true
}
Copy-Item @Params
```

### 4.4 管道

**规则4-4-1：管道操作每行一个 Cmdlet，管道符 `|` 放在行尾。**

```powershell
Get-ChildItem -Path $LogDir -Filter "*.log" |
    Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-30) } |
    Remove-Item -Force
```

### 4.5 Cmdlet 使用

**规则4-5-1：使用完整 Cmdlet 名称，禁止使用别名。**

推荐：`Get-ChildItem`、`Where-Object`、`ForEach-Object`
不推荐：`gci`、`?`、`%`

**规则4-5-2：使用命名参数，避免位置参数。**

推荐：`Get-Content -Path $file -Encoding UTF8`
不推荐：`gc $file UTF8`

## 5 安全性

### 5.1 严格模式

**规则5-1-1：脚本开头启用严格模式。**

```powershell
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
```

### 5.2 参数验证

**规则5-2-1：所有外部输入参数必须使用验证属性。**

```powershell
[ValidateNotNullOrEmpty()]
[ValidateScript({ Test-Path $_ })]
[ValidateSet('Dev', 'Staging', 'Prod')]
[ValidateRange(1, 65535)]
[ValidatePattern('^[a-zA-Z0-9]+$')]
```

### 5.3 凭据处理

**规则5-3-1：禁止硬编码密码，使用 `Get-Credential` 或 `SecureString`。**

```powershell
$Credential = Get-Credential
$SecurePassword = ConvertTo-SecureString $PlainText -AsPlainText -Force
```

**规则5-3-2：禁止在日志中输出敏感信息。**

### 5.4 危险操作

**规则5-4-1：禁止使用 `Invoke-Expression`，防止代码注入。**

**规则5-4-2：破坏性操作的函数必须支持 `ShouldProcess`。**

```powershell
function Remove-OldLogs {
    [CmdletBinding(SupportsShouldProcess)]
    param([string]$Path)

    if ($PSCmdlet.ShouldProcess($Path, "Delete")) {
        Remove-Item -Path $Path -Recurse
    }
}
```

## 6 错误处理

### 6.1 异常处理

**规则6-1-1：使用 `try/catch/finally` 处理异常，捕获具体异常类型。**

```powershell
try {
    $Content = Get-Content -Path $FilePath -ErrorAction Stop
} catch [System.IO.FileNotFoundException] {
    Write-Error "File not found: $FilePath"
} catch {
    Write-Error "Unexpected error: $_"
} finally {
    # 清理资源
}
```

### 6.2 错误操作首选项

**规则6-2-1：关键操作使用 `-ErrorAction Stop` 确保错误被捕获。**

**规则6-2-2：使用 `$ErrorActionPreference = 'Stop'` 设置全局错误行为。**

### 6.3 日志输出

**规则6-3-1：使用 `Write-Verbose`、`Write-Warning`、`Write-Error` 分级输出。**

**规则6-3-2：禁止使用 `Write-Host` 输出业务数据，它不可被管道传递。**

推荐：`Write-Output $result`
不推荐：`Write-Host $result`

## 7 函数设计

**规则7-1：使用 `[CmdletBinding()]` 声明高级函数。**

```powershell
function Get-Report {
    [CmdletBinding()]
    [OutputType([PSCustomObject])]
    param(
        [Parameter(Mandatory, ValueFromPipeline)]
        [string]$Name
    )

    process {
        [PSCustomObject]@{
            Name = $Name
            Date = Get-Date
        }
    }
}
```

**规则7-2：函数应单一职责，一个函数只做一件事。**

**规则7-3：输出使用 `[OutputType()]` 声明返回类型。**

**规则7-4：支持管道输入时实现 `process` 块。**

## 8 最佳实践

**规则8-1：使用 `PSScriptAnalyzer` 进行静态代码分析。**

**规则8-2：模块导出函数使用 `Export-ModuleMember` 显式声明。**

**规则8-3：避免使用 `$global:` 作用域，优先使用参数传递。**

**规则8-4：字符串拼接使用 `-f` 格式化或字符串插值。**

推荐：`"User: $UserName, Age: $Age"`
不推荐：`"User: " + $UserName + ", Age: " + $Age`

## 9 参考

1. PowerShell Practice and Style Guide: https://poshcode.gitbook.io/powershell-practice-and-style
2. PSScriptAnalyzer Rules: https://learn.microsoft.com/en-us/powershell/utility-modules/psscriptanalyzer/rules/readme
