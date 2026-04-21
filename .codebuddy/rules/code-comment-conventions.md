---
alwaysApply: true
---

# 代码注释规范（中文 + 必要覆盖）

**常驻规则。** 所有新编写或修改的代码必须遵循本规范。本规则由 `Boss` 铁律层授权，优先级高于 `karpathy-guidelines.md §2 简洁优先`（见末尾层级协调）。

## ⚠️ 铁律提醒

- 每次回复先称呼 **Boss**
- 不确定的设计决策**必须先问 Boss**
- **不写兼容性代码**，除非 Boss 主动要求

---

## 五条硬约束

### 1. 语言规范：中文为主，保留技术术语英文

- ✅ 所有注释内容**默认用中文**
- ✅ 专有技术名词保留英文原词，不强制翻译：
  - 协议 / 框架名：HTTP / JWT / OAuth / gRPC / Kafka / Redis
  - 设计模式：Singleton / Strategy / Factory
  - 算法 / 数据结构：B-Tree / LRU / DAG / mutex
  - 行业缩写：API / SDK / CI/CD / K8s / QPS / TPS
- ❌ 禁止"一会儿英文一会儿中文"的混乱风格（如"这里 check 一下 user 的 status"）
- ❌ 禁止 Google 翻译式机器翻译注释

### 2. 必须有注释的 6 类位置（硬约束）

| 位置 | 要求 |
|---|---|
| **函数/方法头** | 功能（WHY）/ 参数含义 / 返回值 / 异常 / 关键调用方；使用项目原有风格（Javadoc / Godoc / JSDoc / Docstring） |
| **类/接口头** | 职责 / 协作者 / 关键不变量 |
| **关键业务规则块** | 业务规则的 **WHY**，例如"这里必须先校验 A 再校验 B——因为合同条款 §3.2 要求" |
| **复杂算法 / 正则 / 位运算** | 解释算法思路、正则分组含义、位运算意图 |
| **临时方案 / TODO** | **必须带工单号**（如 `TODO(JIRA-1234): xxx`），否则 `/code-review` BLOCKED |
| **边界条件 / 异常降级分支** | 解释边界的业务原因 / 降级策略 |

### 3. 禁止的 3 类注释（反 Karpathy §2 过度注释）

- ❌ 注释语法本身能表达的信息：`i++;  // i 自增 1`
- ❌ 注释与代码/函数名重复：`getUserById(id);  // 根据 id 获取用户`
- ❌ 过时注释——与代码不符**必须立刻修复或删除**；出现过时注释直接算 `code-review` 缺陷

### 4. 密度建议（软约束，可调）

| 模块类型 | 建议密度 | 说明 |
|---|---|---|
| 核心业务 Service / 领域核心 | ≥ 1 注释块 / 10 行 | 函数头必备，关键逻辑块带 WHY |
| Controller / Handler | 每函数头 + 路由语义说明 | 说明路由/权限/幂等性 |
| 工具类 / Utils | 每 public 函数头 | 说明边界条件和典型用法 |
| DTO / VO / POJO | 可仅字段注释 | 字段含义 + 取值范围 |
| 自动生成代码 | 不要求 | 按原工具输出原样保留 |
| 测试代码样板（setUp/tearDown） | 不要求 | Given/When/Then 用例本身带注释 |

### 5. 格式规范

- 函数头注释沿用项目原有风格（不强制改为中文风格，但**内容全中文**）
- 关键逻辑块使用项目语言的注释符：`//` / `#` / `<!-- -->`
- 注释格式推荐：
  - ✅ `// 业务原因：xxx`
  - ✅ `// 为什么这样处理：xxx`
  - ✅ `// 注意：xxx`（边界/陷阱警示）
  - ❌ `// 这里是 xxx`（无信息量）
  - ❌ `// TODO` 不带工单号

---

## 门禁策略（混合硬 + 软）

### 硬门禁（`/code-review` / `/code-self-check` 触发 BLOCKED）

仅在以下"高风险情形"命中时硬门禁：

1. **L1 核心模块**（Controller / Service / 领域核心，见 `code-documentation.md` L1 判定规则）：
   - 新增函数 > 5 行 缺函数头中文注释 → BLOCKED
   - 新增公共 API 缺注释 → BLOCKED
2. **TODO / FIXME 不带工单号** → BLOCKED（所有模块）
3. **英文注释**出现在新提交代码中（排除技术术语保留） → BLOCKED
4. **过时注释**（与代码语义不符） → BLOCKED

### 软门禁（WARNING，Boss 人工判断）

1. 工具类 / 样板代码缺注释 → WARNING
2. 注释密度低于建议值 → WARNING
3. 非核心模块新增函数缺函数头 → WARNING

### 自动生成代码 / 第三方代码

- 沿用 `code-documentation.md` 的识别规则
- 不做注释门禁（不强制中文，不强制密度）

---

## 与 Karpathy §2 简洁优先的层级协调

| 场景 | 冲突 | 裁决 |
|---|---|---|
| 核心业务函数的 WHY 注释 | Karpathy §2 说"少注释"，本规则要求"必须有中文 WHY 注释" | **本规则优先**——Boss 铁律层授权 |
| 简单赋值 / 循环的描述性注释 | 本规则的"3 类禁止"和 Karpathy §2 一致 | **一致，禁止** |
| 重复函数名的废话注释 | 本规则禁止、Karpathy §2 禁止 | **一致，禁止** |

**核心裁决**：Karpathy §2 的"简洁优先"不得用来**省略本规则要求的必要注释**；但仍可用来**删除重复/无信息量的注释**。

---

## 示例

### ✅ 正确示例

```java
/**
 * 用户注册。
 *
 * 业务流程：
 *   1. 校验用户名/密码格式（{@link UserValidator}）
 *   2. 密码 BCrypt 加密（合规要求，见 SEC-2023-07）
 *   3. 幂等性检查：同一手机号 5 秒内重复注册返回已有用户
 *   4. 发送 UserRegistered 事件到 Kafka（同步阻塞，强一致）
 *
 * @param dto 注册请求 DTO，必须包含 username/password/phone
 * @return 注册成功的 UserVO（不含密码字段）
 * @throws UserAlreadyExistsException 用户名或手机号已存在
 * @throws ValidationException 入参校验失败
 */
public UserVO register(UserRegisterDTO dto) {
    // 幂等性：相同手机号 5 秒内视为重复请求，直接返回已有用户
    // 参考合同条款 §3.2——避免用户重复点击导致多账户
    Optional<User> existing = userMapper.findByPhoneWithinSeconds(dto.getPhone(), 5);
    if (existing.isPresent()) {
        return UserVO.from(existing.get());
    }
    // ...
}
```

### ❌ 错误示例

```java
// 注册用户            ← 废话：函数名已经说了
public UserVO register(UserRegisterDTO dto) {
    // check user      ← 禁止：英文注释（不是技术术语保留）
    if (dto == null) {
        // TODO 改一下  ← 禁止：TODO 缺工单号
        throw new NullPointerException();
    }
    int i = 0;
    i++;  // i 加 1      ← 禁止：语法能表达
}
```

---

## 在各命令中的启用方式

| 命令 | 注释门禁生效方式 |
|---|---|
| `/code-review` | 扫描 diff，按硬/软门禁规则输出问题清单 |
| `/code-self-check` | 同上，默认生成 `code-self-check-report.md` |
| `/execute-plan` | 编码过程中自觉遵守，不做自动 BLOCKED |
| `/fix-bug` | 修改点周围的既有注释若过时必须更新 |
| `/simplify` | 删除重复/废话注释时保持必要中文 WHY 注释 |

---

## 成效自检（交付时回答）

1. 本次 diff 中新增/修改的函数**是否都有中文函数头注释**？
2. 是否存在 TODO/FIXME 不带工单号？
3. 是否存在过时注释？
4. 是否出现英文的非技术术语注释？

四个问题都是"是 / 否"明确可答；任何一项不合规，交付阶段必须补齐。
