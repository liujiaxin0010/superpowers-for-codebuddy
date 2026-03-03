BAT/Batch 编码规范

## 1 范围

本规范适用于 Windows BAT/Batch 批处理脚本的编写和维护。

## 2 文件结构

### 2.1 脚本头部

**规则2-1-1：脚本首行使用 `@echo off` 关闭命令回显。**

**规则2-1-2：紧接使用 `setlocal` 限制变量作用域，防止污染全局环境。**

```bat
@echo off
setlocal enabledelayedexpansion
```

**规则2-1-3：脚本结尾使用 `endlocal` 或 `exit /b` 清理环境。**

### 2.2 文件命名

**规则2-2-1：脚本文件使用小写字母加连字符命名，扩展名为 `.bat` 或 `.cmd`。**

推荐：`deploy-app.bat`、`backup-db.cmd`
不推荐：`DeployApp.BAT`、`backup db.bat`

**规则2-2-2：文件名不得包含空格和特殊字符。**

### 2.3 文件头注释

**规则2-3-1：每个脚本应包含头部注释说明用途。**

```bat
@echo off
REM ============================================
REM 脚本用途：自动化部署应用服务
REM 作者：[name]
REM 创建日期：YYYY-MM-DD
REM ============================================
```

### 2.4 文件编码

**规则2-4-1：脚本文件使用系统默认编码（GBK/GB2312），如需 UTF-8 需在脚本开头声明 `chcp 65001`。**

## 3 命名规范

### 3.1 变量命名

**规则3-1-1：普通变量使用驼峰命名或小写加下划线，避免与系统变量冲突。**

推荐：
```bat
set fileName=config.txt
set retry_count=3
```

不推荐：
```bat
set PATH=mypath
set ERRORLEVEL=0
```

**规则3-1-2：常量使用全大写加下划线。**

```bat
set MAX_RETRY=5
set DEFAULT_PORT=8080
```

**规则3-1-3：变量名不得包含空格，赋值 `=` 两侧不得有空格。**

推荐：`set name=value`
不推荐：`set name = value`

### 3.2 标签命名

**规则3-2-1：标签使用大写字母加下划线，以冒号开头。**

```bat
:MAIN
:PROCESS_FILES
:CHECK_ENV
:SHOW_USAGE
```

### 3.3 函数模拟

**规则3-3-1：使用 `call :LABEL` 模拟函数调用，标签名使用描述性动词。**

```bat
call :VALIDATE_INPUT %1
call :BACKUP_DATABASE
```

## 4 代码风格

### 4.1 缩进

**规则4-1-1：标签段内代码缩进 2 或 4 个空格，保持项目内一致。**

**规则4-1-2：`if`、`for` 嵌套块内代码缩进。**

```bat
if exist "%configFile%" (
    echo Config found
    call :LOAD_CONFIG "%configFile%"
) else (
    echo Config not found, using defaults
    call :USE_DEFAULTS
)
```

### 4.2 注释

**规则4-2-1：行注释使用 `REM` 或 `::`，推荐 `REM` 用于正式注释，`::` 用于临时注释。**

**规则4-2-2：`::` 注释不得用在 `()` 代码块内部，会导致语法错误。**

```bat
REM 这是正式注释
:: 这是临时注释

if defined var (
    REM 块内只能用 REM
    echo %var%
)
```

### 4.3 空行

**规则4-3-1：逻辑块之间用空行分隔，标签段之间空一行。**

## 5 安全性

### 5.1 路径处理

**规则5-1-1：所有路径变量必须加双引号，防止空格导致参数断裂。**

推荐：
```bat
if exist "%userprofile%\Documents" (
    copy "%sourceFile%" "%targetDir%\"
)
```

不推荐：
```bat
if exist %userprofile%\Documents (
    copy %sourceFile% %targetDir%\
)
```

### 5.2 变量安全

**规则5-2-1：在 `()` 代码块中修改和读取变量时，必须启用延迟变量扩展并使用 `!var!` 语法。**

```bat
setlocal enabledelayedexpansion
set count=0
for %%f in (*.txt) do (
    set /a count+=1
    echo Processing file !count!: %%f
)
```

**规则5-2-2：接收外部输入时必须验证，防止命令注入。**

### 5.3 敏感信息

**规则5-3-1：禁止在脚本中硬编码密码、密钥等敏感信息。**

**规则5-3-2：敏感信息通过环境变量或加密配置文件传入。**

### 5.4 危险操作

**规则5-4-1：`del`、`rmdir /s` 等删除操作前必须确认路径非空。**

```bat
if defined targetDir (
    if exist "%targetDir%" (
        rmdir /s /q "%targetDir%"
    )
)
```

## 6 错误处理

### 6.1 退出码

**规则6-1-1：使用 `exit /b N` 返回退出码，0 表示成功。**

**规则6-1-2：每个关键操作后检查 `%errorlevel%`。**

```bat
xcopy "%source%" "%dest%" /e /y
if %errorlevel% neq 0 (
    echo [ERROR] Copy failed with code %errorlevel%
    exit /b 1
)
```

### 6.2 错误输出

**规则6-2-1：错误信息带 `[ERROR]` 前缀，便于日志过滤。**

**规则6-2-2：关键操作记录日志文件。**

```bat
echo [%date% %time%] Starting backup >> "%logFile%"
```

## 7 最佳实践

**规则7-1：脚本入口处验证参数。**

```bat
if "%~1"=="" (
    echo Usage: %~nx0 ^<config_file^>
    exit /b 1
)
```

**规则7-2：使用 `%~dp0` 获取脚本所在目录，避免依赖当前工作目录。**

```bat
set scriptDir=%~dp0
set configFile=%scriptDir%config.ini
```

**规则7-3：长脚本使用标签组织为逻辑段，主流程在顶部。**

**规则7-4：避免使用 `goto` 实现循环，优先使用 `for` 循环。**

## 8 参考

1. Microsoft CMD Documentation: https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/
2. SS64 CMD Reference: https://ss64.com/nt/
