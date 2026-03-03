Shell/Bash 编码规范

## 1 范围

本规范适用于 Shell/Bash 脚本的编写和维护，涵盖文件结构、命名、安全性、代码风格等方面。

## 2 文件结构

### 2.1 Shebang 声明

**规则2-1-1：每个脚本文件首行必须包含 shebang 声明。**

推荐：
```bash
#!/usr/bin/env bash
```

不推荐：
```bash
#!/bin/bash
```

使用 `env` 方式更具可移植性，能适应不同系统中 bash 的安装路径。

### 2.2 严格模式

**规则2-2-1：脚本开头应启用严格模式。**

```bash
set -euo pipefail
```

- `set -e`：命令失败时立即退出
- `set -u`：使用未定义变量时报错
- `set -o pipefail`：管道中任一命令失败则整个管道失败

### 2.3 文件命名

**规则2-3-1：脚本文件使用小写字母加下划线命名，扩展名为 `.sh`。**

推荐：`backup_database.sh`、`deploy_service.sh`
不推荐：`BackupDatabase.sh`、`backup-database`

### 2.4 文件头注释

**规则2-4-1：每个脚本文件应包含文件头注释，说明用途、作者、日期。**

```bash
#!/usr/bin/env bash
#
# 脚本用途：数据库备份脚本
# 作者：[name]
# 创建日期：YYYY-MM-DD
# 修改记录：
#   YYYY-MM-DD - 描述修改内容
```

### 2.5 文件编码

**规则2-5-1：脚本文件统一使用 UTF-8 编码，行尾使用 LF（Unix 风格）。**

## 3 命名规范

### 3.1 变量命名

**规则3-1-1：普通变量使用小写字母加下划线。**

推荐：
```bash
file_name="config.txt"
retry_count=3
```

不推荐：
```bash
FileName="config.txt"
RETRYCOUNT=3
```

**规则3-1-2：常量和环境变量使用全大写字母加下划线。**

```bash
readonly MAX_RETRY_COUNT=5
readonly DEFAULT_TIMEOUT=30
export APP_HOME="/opt/app"
```

**规则3-1-3：局部变量必须使用 `local` 关键字声明。**

```bash
my_function() {
  local result=""
  local temp_file
  temp_file=$(mktemp)
  # ...
}
```

### 3.2 函数命名

**规则3-2-1：函数名使用小写字母加下划线，动词开头。**

推荐：
```bash
process_file() { ... }
validate_input() { ... }
send_notification() { ... }
```

不推荐：
```bash
ProcessFile() { ... }
file_process() { ... }
```

**规则3-2-2：函数定义使用 `function_name()` 格式，不使用 `function` 关键字。**

推荐：
```bash
do_something() {
  # ...
}
```

不推荐：
```bash
function do_something {
  # ...
}
```

### 3.3 特殊命名

**规则3-3-1：以下划线开头的变量和函数表示内部使用，不对外暴露。**

```bash
_internal_helper() { ... }
_temp_value=""
```

## 4 代码风格

### 4.1 缩进

**规则4-1-1：使用 2 个空格缩进，禁止使用制表符。**

### 4.2 行宽

**规则4-2-1：每行最大 80 字符，硬限制 100 字符。**

长命令使用 `\` 续行，续行缩进 4 个空格：
```bash
curl --silent \
    --header "Content-Type: application/json" \
    --data '{"key": "value"}' \
    "https://api.example.com/endpoint"
```

### 4.3 控制结构

**规则4-3-1：`then`、`do` 与 `if`、`for`、`while` 写在同一行。**

推荐：
```bash
if [[ -f "$file" ]]; then
  echo "File exists"
fi

for item in "${array[@]}"; do
  process "$item"
done

while read -r line; do
  echo "$line"
done < "$input_file"
```

不推荐：
```bash
if [[ -f "$file" ]]
then
  echo "File exists"
fi
```

**规则4-3-2：`case` 语句每个分支缩进 2 个空格，`;;` 单独一行。**

```bash
case "$action" in
  start)
    start_service
    ;;
  stop)
    stop_service
    ;;
  *)
    echo "Unknown action: $action" >&2
    exit 1
    ;;
esac
```

### 4.4 空行与间距

**规则4-4-1：函数之间空一行，逻辑块之间空一行。**

**规则4-4-2：管道操作每行一个命令。**

```bash
find . -name "*.log" \
  | grep -v "debug" \
  | sort \
  | uniq -c \
  | sort -rn
```

## 5 安全性

### 5.1 变量引用

**规则5-1-1：所有变量引用必须加双引号，防止单词分割和通配符扩展。**

推荐：
```bash
echo "$file_name"
cp "$source" "$destination"
if [[ -d "$dir_path" ]]; then
```

不推荐：
```bash
echo $file_name
cp $source $destination
if [[ -d $dir_path ]]; then
```

**规则5-1-2：数组展开使用 `"${array[@]}"`。**

```bash
for item in "${my_array[@]}"; do
  echo "$item"
done
```

### 5.2 命令替换

**规则5-2-1：使用 `$()` 进行命令替换，禁止使用反引号。**

推荐：`current_date=$(date +%Y-%m-%d)`
不推荐：`` current_date=`date +%Y-%m-%d` ``

### 5.3 条件测试

**规则5-3-1：使用 `[[ ]]` 代替 `[ ]` 进行条件测试。**

`[[ ]]` 支持模式匹配、正则表达式，且不需要对变量加引号防止分词。

**规则5-3-2：字符串比较使用 `==`，数值比较使用 `-eq`、`-lt`、`-gt` 等。**

### 5.4 危险操作

**规则5-4-1：禁止使用 `eval`，除非有充分理由并加注释说明。**

**规则5-4-2：`rm` 操作必须使用完整路径或变量保护，禁止 `rm -rf /` 或 `rm -rf $var/`（变量为空时危险）。**

```bash
# 安全的删除操作
if [[ -n "$target_dir" && -d "$target_dir" ]]; then
  rm -rf "${target_dir:?}"
fi
```

**规则5-4-3：禁止在脚本中硬编码密码、密钥、Token 等敏感信息。**

### 5.5 临时文件

**规则5-5-1：临时文件使用 `mktemp` 创建，脚本退出时用 `trap` 清理。**

```bash
tmp_file=$(mktemp)
trap 'rm -f "$tmp_file"' EXIT

echo "data" > "$tmp_file"
```

## 6 错误处理

### 6.1 退出码

**规则6-1-1：脚本和函数应返回有意义的退出码。0 表示成功，非 0 表示失败。**

**规则6-1-2：自定义退出码应在脚本头部定义为常量。**

```bash
readonly E_SUCCESS=0
readonly E_INVALID_ARGS=1
readonly E_FILE_NOT_FOUND=2
```

### 6.2 错误输出

**规则6-2-1：错误信息输出到 stderr，使用 `>&2`。**

```bash
err() {
  echo "[ERROR] $(date +%Y-%m-%dT%H:%M:%S) $*" >&2
}

err "File not found: $file_path"
```

### 6.3 输入验证

**规则6-3-1：脚本入口处验证参数数量和格式。**

```bash
if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <config_file>" >&2
  exit 1
fi
```

## 7 注释

**规则7-1：文件头注释说明脚本用途、依赖、使用方式。**

**规则7-2：函数前注释说明功能、参数、返回值。**

```bash
# 处理日志文件并提取错误记录
# 参数:
#   $1 - 日志文件路径
#   $2 - 输出文件路径
# 返回:
#   0 - 成功
#   1 - 文件不存在
process_log() {
  local log_file="$1"
  local output_file="$2"
  # ...
}
```

**规则7-3：复杂逻辑段前添加行注释，避免废弃注释残留。**

## 8 最佳实践

**规则8-1：优先使用 bash 内置命令，减少外部进程调用。**

推荐：`[[ "$str" == *pattern* ]]`
不推荐：`echo "$str" | grep "pattern"`

**规则8-2：避免在循环中使用管道和子 shell，影响性能。**

**规则8-3：使用 `readonly` 声明不可变变量。**

**规则8-4：长脚本应拆分为函数，主逻辑放在 `main()` 函数中。**

```bash
main() {
  parse_args "$@"
  validate_env
  do_work
}

main "$@"
```

## 9 参考

1. Google Shell Style Guide: https://google.github.io/styleguide/shellguide.html
2. ShellCheck: https://www.shellcheck.net/
