# GitLab 服务器 / Runner 配置（CI/CD 生效前置）

本文件回答：要让 `/ci-setup` 生成的 `.gitlab-ci.yml` **真正跑起来并阻断 MR**，GitLab 服务器侧需要配什么、**需不需要 Docker**。

> 目标平台：GitLab Community Edition 14.8.2。

## 一、GitLab 服务器本身（通常无需额外配置）

GitLab CE 14.8.2 **自带 CI/CD 引擎，默认启用**。确认项：

- [ ] CI/CD 未被实例级禁用（Admin Area → Settings → CI/CD，默认开）
- [ ] 项目 Settings → CI/CD → 本项目 CI/CD 已启用
- [ ] （可选）Container Registry：仅当要在 CI 内 build/push 镜像才启用；纯门禁流水线**不需要**
- GitLab 自身是 Omnibus 还是 Docker 方式安装，与本方案无关（它已在运行）

## 二、GitLab Runner（必须 —— 没有 Runner 流水线不会跑）

**这是 CI 能跑的关键。** `.gitlab-ci.yml` 的每个 job 都在 Runner 上执行；没有注册可用的 Runner，流水线会一直 `pending`，「Pipelines must succeed」永远不满足，门禁形同虚设。

- [ ] 安装 GitLab Runner（可与 GitLab 同机或独立机器）
- [ ] 用注册令牌注册到内网 GitLab（项目级 / 群组级 / 实例级；指向内网 GitLab URL）
- [ ] 至少一个 Runner `enabled` 且对本项目可用（项目 → Settings → CI/CD → Runners 可见）
- [ ] 选定 executor —— **这一步决定要不要 Docker**（见三）

## 三、executor 选择 → 是否需要 Docker（核心决策）

| executor | 需要 Docker | job 运行环境 | 配套要求 | 与本模板契合度 |
|---|---|---|---|---|
| **docker**（推荐）| ✅ 需要 | 每个 job 在 `image:` 指定的容器里 | Runner 主机装 Docker + 能拉**内网 Docker registry** 镜像 | 模板默认（含 `default: image:` 与 `services:`），开箱即用 |
| **shell** | ❌ 不需要 | 直接在 Runner 主机 shell | 主机**预装**全部构建/测试工具链（jdk/maven/go/node…）；`image:`/`services:` 会被忽略 | 需从 `.gitlab-ci.yml` 删 `default: image:` 与 `e2e` 的 `services:` |
| kubernetes | ✅（容器）| k8s pod | k8s 集群 | 大规模时再考虑 |

### 结论 —— 需要 Docker 吗？

- 用 **docker executor**（推荐，模板默认）→ **是，Runner 主机需要 Docker**，并能访问内网 Docker registry 拉 `<INTERNAL_REGISTRY_IMAGE>`。
- 用 **shell executor** → **不需要 Docker**，但必须在 Runner 主机预装全部构建/测试工具，并删掉模板里的 `default: image:` 和 `services:`。
- **e2e 真实中间件（`services:` postgres/redis）只能在 docker executor 下用** → 要做 L3 真集成测试，Docker 是硬要求。

## 四、内网 Docker registry（docker executor 时需要）

内网无法直连 Docker Hub，`image:` 必须指向**内网 registry 镜像**（含 bash、git 及构建/测试工具链）。在能访问公网处构建基础镜像 → 推内网 registry → `/ci-setup` 时填入 `<INTERNAL_REGISTRY_IMAGE>`。

## 五、三类 Docker 用途澄清（避免混淆）

| 用途 | 是否需要 Docker | 说明 |
|---|---|---|
| GitLab 服务器本身 | 取决于安装方式（Omnibus 不需要 / Docker 安装方式需要）| 与本方案无关，已在运行 |
| **CI Runner 执行 job** | docker executor 需要 / shell executor 不需要 | **核心决策**，见三 |
| **MCP server（AI 访问 GitLab）** | 推荐 Docker（或 npx + 内网 npm）| AI 侧依赖，与 Runner 无关，见 `gitlab-bridge/references/mcp-setup.md` |

## 六、最小可行组合（二选一）

- **省事路线（推荐）**：1 台装 Docker 的机器 → 跑 docker-executor Runner + 内网 registry 放 1 个基础镜像。`.gitlab-ci.yml` 开箱即用，支持 e2e `services:`。
- **无 Docker 路线**：shell-executor Runner + 主机预装工具链 → `/ci-setup` 时声明 Runner 为 shell，删 `image:`/`services:`，放弃 e2e 真实中间件（或改用主机本地的 PG/Redis）。

## 七、验证

- [ ] 新建测试 MR，确认流水线 5 阶段 `gate / build / test / quality / verify` 被触发且在 Runner 上跑起来（不是 pending）
- [ ] 故意推不合规 commit message，确认 `verify:commit-msg` 失败且 MR 合不了
- [ ] 全绿后确认 MR 可合并
