---
alwaysApply: false
---

# 跨平台 Shell 命令规范（Windows / Linux / macOS）

**触发加载条件**：会话启动时检测到 `isWindows=true` 时自动加载；Linux/macOS 下按需加载（如需写跨平台脚本）。

## ⚠️ 铁律提醒

- 每次回复先称呼 **Boss**
- 不确定的设计决策**必须先问 Boss**
- **不写兼容性代码**，除非 Boss 主动要求（本规则的跨平台策略不属于"代码兼容性"，属于"工具使用正确性"，不在禁令范围内）

---

## 问题根因（为什么 Windows 命令经常失败）

| 类型 | 表现 | 根因 |
|---|---|---|
| 命令不存在 | `'find' 不是内部或外部命令` | POSIX 工具 `find` / `grep` / `sed` / `awk` / `rm` 在 Windows cmd.exe 无原生对应 |
| 重定向语法差异 | `2>/dev/null` 无效 | cmd.exe 用 `2>nul`，pwsh 用 `2>$null` |
| 命令链语义差异 | `a && b` 在 cmd 下有变化 | pwsh 推荐 `; if ($?) { b }` 或分拆步骤 |
| 路径分隔符 | `/` vs `\` | PowerShell 两者兼容，cmd.exe 有时只认 `\` |
| 环境变量语法 | `$VAR` vs `%VAR%` vs `$env:VAR` | bash 用 `$VAR`，cmd 用 `%VAR%`，pwsh 用 `$env:VAR` |
| Heredoc 不支持 | `cat <<EOF` 失败 | cmd.exe 和 pwsh 均不支持 bash heredoc |
| 编码乱码 | 中文输出乱码 | Windows 默认 GBK/CP936，需要 UTF-8 切换 |
| 执行策略受限 | `.ps1 无法加载` | PowerShell 默认 `Restricted` 策略 |
| 单/双引号差异 | 转义行为不同 | bash / pwsh / cmd 三套规则 |

AI 在 Windows 下的常见低级错误：**命令失败后"再试一次同样的命令"**，而不是切换到等价跨平台命令。

---

## 层 1：工具使用优先级（硬性）

```
1. Claude Code 专用工具（Glob / Grep / Read / Edit / Write）— 最优
2. Node.js / Python 脚本（跨平台）— 次优
3. PowerShell 7 (pwsh)                 — Windows/Linux/macOS 通用
4. POSIX shell (bash)                  — 仅在确认有 Git Bash / WSL 时用
5. cmd.exe                             — 禁用，除非别无选择
```

**执行前判断**：能用 Claude Code 内置工具的**不要**用 Shell。`find` → `Glob`、`grep` → `Grep`、`cat` → `Read`、`sed -i` → `Edit`、`echo >` → `Write`。

---

## 层 2：命令替换速查表

| POSIX（Windows 下禁用） | 跨平台替代 |
|---|---|
| `find . -name X` | Claude Code `Glob` 工具 |
| `grep -rn X .` | Claude Code `Grep` 工具 |
| `cat file` | Claude Code `Read` 工具 |
| `sed -i s/a/b/ file` | Claude Code `Edit` 工具 |
| `ls -la` | `Get-ChildItem -Force`（pwsh）或 `ls`（bash） |
| `rm -rf X` | `Remove-Item X -Recurse -Force`（pwsh），**操作前必须 Boss 确认** |
| `mkdir -p X` | `New-Item -ItemType Directory -Force X`（pwsh） |
| `cp -r a b` | `Copy-Item a b -Recurse`（pwsh） |
| `mv a b` | `Move-Item a b`（pwsh） |
| `touch X` | `New-Item X -ItemType File`（pwsh） |
| `2>/dev/null` | pwsh: `2>$null` / cmd: `2>nul` |
| `&& / \|\|` | pwsh: `; if ($?) {...}` 或拆分步骤 |
| heredoc `<<EOF` | 写临时文件 + 读取 |
| `export VAR=x` | pwsh: `$env:VAR = 'x'` |
| `$HOME` | pwsh: `$env:USERPROFILE` / bash: `$HOME` |
| `which X` | pwsh: `Get-Command X` |
| `pwd` | pwsh / bash 都支持 `pwd`；cmd 用 `cd` |

---

## 层 3：失败自愈流程（关键）

命令失败后**必须判断错误类型**并按以下决策树处理：

```
命令失败
  ↓
读取错误信息
  ↓
是否匹配下列 Windows 兼容性关键字？
  - "command not found"
  - "不是内部或外部命令"
  - "CreateProcess error=2"
  - "no such file or directory"（但命令确实存在时）
  - "cannot be loaded because running scripts is disabled"
  ↓ 是
自愈策略：
  1. 查速查表找等价跨平台命令
  2. 优先切到 Claude Code 专用工具
  3. 次选 pwsh 等价命令
  4. 切换后重试（**仅 1 次**，仍失败进入下一步）
  ↓ 仍失败
降级：
  5. 改用 Node.js / Python 脚本
  6. 或询问 Boss 是否在 Git Bash / WSL 下重试
  ↓ 权限类错误
  ❌ 绝不自动 bypass（不自动加 -ExecutionPolicy Bypass 之外的降权操作）
  ❌ 不跳过 hook、不禁用签名校验
  → 报告 Boss，由 Boss 决定
```

**禁止**：在同一错误下重复执行原命令 ≥ 2 次（低级重试浪费上下文）。

---

## 层 4：脚本双份强制

仓库内任何 shell 脚本**必须同时提供** `.sh` 和 `.ps1` 两份。已有惯例（见 `.codebuddy/skills/process-gatekeeper/scripts/check-gates.sh` + `check-gates.ps1`），本规则正式固化。

### 双份脚本要求

| 要求 | `.sh` | `.ps1` |
|---|---|---|
| 行尾 | LF | CRLF 或 LF 均可 |
| 首行 | `#!/usr/bin/env bash` + `set -euo pipefail` | `$ErrorActionPreference = 'Stop'` |
| 编码 | UTF-8 无 BOM | UTF-8（推荐带 BOM）+ `$OutputEncoding = [System.Text.Encoding]::UTF8` |
| 路径 | 用 `/` 正斜杠 | 用 `/`（pwsh 支持） |
| 退出码 | 用 `exit <code>` | 用 `exit <code>`，不要用 `throw` |

### `.gitattributes` 配合

在仓库根 `.gitattributes` 添加（若尚未配置）：

```
*.sh  text eol=lf
*.ps1 text eol=crlf
```

### 命令调用方式

调用方（如 `/execute-plan` 的质量门禁）按平台分流：

```
if (isWindows) {
    powershell -ExecutionPolicy Bypass -File path/to/script.ps1
} else {
    bash path/to/script.sh
}
```

**禁止**：同一命令同时调 `.ps1` 和 `.sh`（双执行）；禁止 Windows 下调 `.sh`（除非显式确认 Git Bash）。

---

## 层 5：编码规范

### PowerShell 脚本首段

所有 `.ps1` 脚本在第一行之后建议加入：

```powershell
$ErrorActionPreference = 'Stop'
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
```

否则中文输出容易在 Windows 终端乱码。

### Bash 脚本首段

```bash
#!/usr/bin/env bash
set -euo pipefail
export LANG=en_US.UTF-8
```

---

## 会话启动自动检测（由 CODEBUDDY.md §2 驱动）

会话启动时执行以下检测，记录到会话上下文：

```bash
# 首选：/usr/bin/uname（Linux/macOS/Git Bash 都有）
uname -s 2>/dev/null || ver

# 结果判定
isWindows = (输出包含 "Windows" / "Microsoft" / "MINGW" / "CYGWIN")
```

| 检测结果 | 加载策略 |
|---|---|
| `isWindows=true` | 自动加载本规则；后续命令默认走 pwsh / Claude Code 工具 |
| `isWindows=false`（Linux/macOS） | 按需加载；默认走 bash / Claude Code 工具 |
| 检测失败 | 记入 `docs/progress.md`，保守走 Claude Code 工具优先 |

---

## 路径规范

- 脚本内部**统一用 `/` 正斜杠**（pwsh 和 bash 都支持）
- 绝对路径用环境变量：
  - 用户目录：`$env:USERPROFILE`（pwsh）/ `$HOME`（bash），统一封装变量 `$USER_HOME`
  - 临时目录：`$env:TEMP`（pwsh）/ `/tmp`（bash），统一封装变量 `$TMP_DIR`
- 禁止硬编码 `C:\Users\xxx` 或 `/home/xxx`

---

## 禁用命令清单（Windows 下永不使用）

以下命令 Windows 下**永远不要用**，即使有 Git Bash 也优先替代：

- `find`（用 `Glob` 工具 / `Get-ChildItem -Recurse`）
- `grep`（用 `Grep` 工具 / `Select-String`）
- `sed -i`（用 `Edit` 工具）
- `awk`（写 Node.js / Python 脚本）
- `rm -rf /path`（必须改 `Remove-Item path -Recurse -Force` 且 Boss 确认）
- `cat X >>`（写 `Add-Content`）

---

## 自检触发点

`/code-self-check` 扫描项额外检查：

- 新增 `.sh` 脚本但**缺失对应 `.ps1`** → WARNING
- 脚本包含 POSIX-only 语法（heredoc、`2>/dev/null`、`awk` 等）但未声明平台 → WARNING
- 命令输出含中文但脚本未设置 UTF-8 编码 → WARNING

---

## 成效自检

Windows 下一次会话结束时，回答以下问题：

1. 本次会话是否存在"命令失败后重试相同命令 ≥ 2 次"的情况？
2. 是否有命令失败本可用 Claude Code 工具直接完成？
3. 新增的脚本是否都是 `.sh + .ps1` 双份？
4. 新增 `.ps1` 是否都设置了 UTF-8 输出编码？

四个问题都回答"否 / 是"时，本规则生效良好。
