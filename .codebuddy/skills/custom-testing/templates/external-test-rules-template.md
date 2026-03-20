# 项目测试规则模板

将本文件复制为如 `docs/test-rules.md` 或 `.codebuddy/test-rules.md` 后使用。

```yaml
framework: pytest
location: tests/
file_naming: "{SourceFileName}_test.py"
naming: "test_{behavior}_{condition}"
structure: AAA
min_cases_per_method: 3
required_scenarios:
  - normal
  - boundary
  - error
branch_coverage: 80%
mock_external: true
mock_database: true
mock_utils: false
assertion_style: plain
cleanup_strategy: after_each
```

## 项目特殊规则

- [在此写项目专属约束]
