---
name: security-review
description: 安全审查技能。用于在鉴权变更、外部契约变更、依赖新增/升级、数据库 schema 变更、敏感信息处理等高危场景进入合并前，按威胁建模 + OWASP + 依赖审计清单做结构化安全审查。用户提到"安全审查 / 威胁建模 / 鉴权变更 / 依赖升级 / 密钥扫描 / 合规检查"时触发。
---

# 安全审查

回答的核心问题：**这次改动是否引入了可被利用的安全问题？哪些风险必须在合入前解决？**

安全审查是"一等公民门禁"而非可选步骤：命中任一触发条件即必须执行。

## 触发条件（命中任一即必须执行）

1. 新增 / 修改鉴权、授权、身份验证逻辑
2. 新增 / 修改对外 API / 事件 / 对内 RPC 的签名
3. `package.json` / `go.mod` / `requirements.txt` / `Cargo.toml` / `pom.xml` 出现依赖新增、版本变更
4. 数据库 schema 变更（新表 / 新字段 / 索引 / 触发器）
5. 处理敏感信息（密码、token、PII、支付、证件号）
6. 密码学、加解密、签名、证书相关改动
7. 文件上传、反序列化、模板渲染、SQL 拼接
8. 跨域 / CSP / Cookie 属性 / Session 策略变更
9. 权限最小化相关配置（IAM / 角色 / RBAC）
10. 新增或调整日志字段，可能落入敏感信息

## 何时不用

1. 纯文档 / 注释改动
2. 生成代码、测试数据、前端样式调整（不涉及 XSS 风险时）
3. 工具链配置变更且不触达发布链路

## 阻断条件（BLOCKED）

1. 未完成威胁建模草图（STRIDE 或等价）
2. 依赖新增但缺失漏洞扫描证据（如 `npm audit` / `pip-audit` / `govulncheck` 输出）
3. 鉴权 / 授权变更但缺失最小权限分析
4. 发现 🔴 严重级别问题未修复即声称通过

## 输入参数

`/security-review [scope=<paths>] [spec=<path>] [plan=<path>] [threatModelPath=<path>]`

## 审查维度（必须全覆盖）

### 1. 威胁建模（STRIDE）

| 威胁 | 含义 | 常见位置 |
|---|---|---|
| Spoofing | 身份伪造 | 登录 / SSO / Token |
| Tampering | 篡改 | 消息 / 数据库 / 文件 |
| Repudiation | 抵赖 | 审计日志 / 签名 |
| Information Disclosure | 信息泄漏 | 日志 / 响应 / 错误信息 |
| Denial of Service | 拒绝服务 | 限流 / 队列 / 资源耗尽 |
| Elevation of Privilege | 权限提升 | RBAC / 越权 / IDOR |

每个 STRIDE 类别至少给出一个"可能被利用的路径"或显式标记"不适用"。

### 2. OWASP Top 10 / CWE Top 25 对照

按当前改动涉及的语言与场景，对照 OWASP Top 10（Web）、OWASP API Top 10、或 CWE Top 25，逐项判定："不涉及 / 涉及但已缓解 / 涉及且有风险"。

### 3. 输入输出验证

1. 所有外部输入在边界处验证（长度、字符集、范围、格式）
2. 所有出站数据按上下文编码（HTML / JSON / SQL / Shell / LDAP）
3. 反序列化是否使用白名单类型
4. 文件上传是否限制类型、大小、存储路径

### 4. 鉴权与授权

1. 敏感接口是否强制鉴权
2. 授权是否在每个资源操作上重新校验（禁止"登录即可做一切"）
3. 越权检测：用户 A 能否访问 B 的数据
4. 管理员接口是否隔离

### 5. 加密与密钥管理

1. 是否使用弱算法（MD5/SHA1、DES、ECB）
2. 密钥是否硬编码 / 是否通过 KMS / 环境变量注入
3. 证书链是否校验
4. TLS 最低版本

### 6. 日志与审计

1. 敏感字段（密码、token、身份证、卡号）是否从日志中脱敏
2. 安全事件（登录失败、权限拒绝、异常请求）是否落审计日志
3. 日志保留与传输是否合规

### 7. 依赖审计

1. 执行依赖漏洞扫描：
   - Node: `npm audit --audit-level=high`
   - Python: `pip-audit` 或 `safety check`
   - Go: `govulncheck ./...`
   - Rust: `cargo audit`
   - Java: `mvn org.owasp:dependency-check-maven:check`
2. 出现 High/Critical 漏洞 → 阻断，必须升级或替换
3. 新增依赖需记录 License，禁止引入不兼容协议

### 8. 秘密扫描

1. 运行 `git diff | grep -E '(api[_-]?key|secret|token|password|-----BEGIN)'` 或等价工具
2. 推荐：`gitleaks detect --source . --log-opts='-1 HEAD'`
3. 命中任一高置信 → 阻断，需轮换并清理历史

### 9. 合规与隐私

1. 涉及 PII：是否做了最小化、加密存储、访问审计、删除路径
2. 涉及跨境数据：是否触发数据驻留要求
3. 涉及未成年人数据：是否有额外保护

## 输出

报告：`docs/quality/security-review-report.md`
缺陷汇总：`docs/quality/security-review-report.xlsx`（复用 `xlsx` 技能，沿用 `defect-classification.json` 的"安全"大类）

报告必须包含：

```markdown
# 安全审查报告

- 审查日期：YYYY-MM-DD
- 审查范围：<paths>
- 威胁建模：<threatModelPath 或嵌入摘要>
- 审查结论：通过 / 不通过

## 威胁建模摘要（STRIDE）
...

## OWASP / CWE 对照
...

## 问题清单（按严重度）

### 🔴 严重
1. <标题>
   - 位置：<file:line>
   - 风险：<描述>
   - 攻击路径：<复现>
   - 修复建议：<代码或配置示例>

### 🟡 警告
...

### 🔵 建议
...

## 依赖审计摘要
- 工具命令与输出摘要
- High/Critical 漏洞清单与处置

## 秘密扫描摘要
- 工具与结果

## 合规检查摘要

## 结论与下一步
- 通过 → 推荐命令
- 不通过 → 阻断项 + 修复回路
```

## 与其它技能的协作

| 技能 | 关系 |
|---|---|
| `code-review-standards` | 本技能聚焦安全；通用审查由 `/code-review` 承担；二者同时触发互不替代 |
| `code-self-check` | diff 级自检；本技能偏深度审查 |
| `requirement-coverage-check` | 本技能是其并列前置（系统测试前都要过） |
| `data-safety` | 本技能识别出数据相关高危改动时，推荐触发 `/data-safety-check` |

## 禁止事项

1. 不要以"应该没问题"代替审查——安全问题默认存在，直到被证明不存在
2. 不要跳过依赖审计——第三方漏洞是最常见的实际入口
3. 不要把敏感信息放在审查报告正文明文——需要引用时只给路径和脱敏摘要
4. 不要发现严重问题后仅标记"待修复"就放行——必须阻断，除非 Boss 显式接受风险并签字
