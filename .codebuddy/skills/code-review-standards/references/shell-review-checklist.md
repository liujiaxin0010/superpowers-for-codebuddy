# Shell/Bash Code Review Checklist

Comprehensive checklist for reviewing Shell and Bash scripts, covering security, portability, and best practices.

## Security

### 1. Command Injection
```bash
# ❌ WRONG - Command injection
filename="$1"
cat $filename  # Unquoted variable

# ❌ WRONG - eval with user input
eval "echo $user_input"

# ✅ CORRECT - Quote variables
filename="$1"
cat "$filename"

# ✅ CORRECT - Use arrays for commands
cmd=("ls" "-la" "$dir")
"${cmd[@]}"
```

### 2. Path Traversal
```bash
# ❌ WRONG - No path validation
file="/data/$user_input"
cat "$file"  # ../../../etc/passwd

# ✅ CORRECT - Validate path
file="/data/$user_input"
realpath=$(realpath "$file")
if [[ "$realpath" != /data/* ]]; then
    echo "Invalid path"
    exit 1
fi
```

## Variable Handling

### 1. Unquoted Variables
```bash
# ❌ WRONG - Word splitting
file="my file.txt"
rm $file  # Tries to remove "my" and "file.txt"

# ✅ CORRECT - Quote variables
rm "$file"
```

### 2. Unset Variables
```bash
# ❌ WRONG - No error on unset
rm -rf "$DIRECTORY/"  # If unset, becomes "rm -rf /"

# ✅ CORRECT - Use set -u
set -u
rm -rf "${DIRECTORY:?Variable not set}/"
```

## Error Handling

### 1. Exit on Error
```bash
# ❌ WRONG - Continues after error
cd /nonexistent
rm -rf *  # Runs in wrong directory!

# ✅ CORRECT - Use set -e
set -e
cd /nonexistent  # Script exits here
rm -rf *
```

### 2. Pipeline Errors
```bash
# ❌ WRONG - Only checks last command
set -e
false | true  # No error!

# ✅ CORRECT - Use pipefail
set -eo pipefail
false | true  # Now fails
```

## Best Practices

### 1. Script Header
```bash
#!/usr/bin/env bash
set -euo pipefail
IFS=$'\n\t'
```

### 2. Conditional Syntax
```bash
# ❌ WRONG - Single brackets
if [ $var = "value" ]; then

# ✅ CORRECT - Double brackets (Bash)
if [[ "$var" == "value" ]]; then
```

## Static Analysis Tools

Recommended tools:
- **shellcheck**: Static analysis for shell scripts
- **shfmt**: Shell script formatter

Usage:
```bash
shellcheck script.sh
shfmt -w script.sh
```
