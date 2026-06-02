请按以下顺序阅读并严格遵循：
1. `.codebuddy/skills/ci-integration/SKILL.md`（CI 门禁集成）
2. `.codebuddy/skills/gitlab-bridge/SKILL.md`（GitLab 对接层）

**务必遵守三条铁律：**
1. 每次回复第一句话必须称呼 "Boss"
2. 遇到不确定设计必须先询问 Boss
3. 未经 Boss 明确要求，不得编写兼容性代码

**你的任务是：**
在当前业务项目里，把 Featureflow 的门禁接入 GitLab CI/CD，将「协议驱动」的软门禁升级为「系统强制」的硬门禁。目标平台 GitLab Community Edition 14.8.2。

执行步骤：

1. **环境确认**：
   - 确认当前项目根目录已含 `.codebuddy/`（Featureflow 引擎）
   - 确认项目是 git 仓库且远程指向内网 GitLab
   - 若缺失，输出 `BLOCKED` 并说明

2. **bridge 探测（可选但推荐）**：
   - 经 `gitlab-bridge` 执行 `bridge.probe`，确认 MCP server 可用性
   - 探测到 `ci.lint` 可用 → 后续第 5 步用它校验 `.gitlab-ci.yml`
   - MCP 不可用 → 继续执行，第 5 步改为提示人工校验，不阻断

3. **探测技术栈 + 采集参数**（探测后一次问清，不要逐项追问）：
   - 扫描项目特征文件推断构建/测试工具链：
     `pom.xml`→Maven、`build.gradle`→Gradle、`package.json`→Node、
     `CMakeLists.txt`→CMake、`*.pro`→qmake、`go.mod`→Go、`*.csproj`→.NET
   - 据探测结果预填，与 Boss 确认以下参数：
     * Runner executor（**决定是否需要 Docker**，见 `ci-integration/references/gitlab-server-setup.md`）：
       - `docker`（推荐，默认）→ 保留模板 `image:`/`services:`，需内网 registry 镜像
       - `shell` → 删除模板 `default: image:` 与 e2e `services:`，依赖主机预装工具链（不需要 Docker）
     * 内网 Docker registry 镜像地址（docker executor 时，含 bash、git 及构建工具链，替换 `<PLACEHOLDER:INTERNAL_REGISTRY_IMAGE>`）
     * 主分支名（`master` 或 `main`）
     * Runner OS/Shell（Linux/bash 默认，或 Windows/pwsh）
     * 编译命令 `<PLACEHOLDER:BUILD_COMMAND>`（按技术栈，如 `mvn -B compile`）
     * 测试命令 `<PLACEHOLDER:TEST_COMMAND>`（按技术栈，如 `mvn -B test`）——须产出
       `docs/quality/test-summary.json`；测试框架不直接产出该格式时，确认追加的转换步骤
     * 是否强制 commit message 工单号格式（默认否；是 → commit-msg-lint 设 `REQUIRE_TICKET=1`）

4. **生成产物**（实例化 `ci-integration/templates/` 下模板到业务项目）：
   - `.gitlab-ci.yml` ← `gitlab-ci.yml.template`，替换全部占位符
     （`INTERNAL_REGISTRY_IMAGE` / `BUILD_COMMAND` / `TEST_COMMAND`）；
     Windows runner 则把 `bash *.sh` 改为 `pwsh -File *.ps1`
   - `.gitlab/merge_request_templates/featureflow.md` ← `merge_request_template.md`
   - `scripts/commit-msg-lint.sh`（及 `.ps1`）← 对应模板；若强制工单号格式，
     在 CI job 或脚本环境设 `REQUIRE_TICKET=1`
   - `docs/gitlab-setup-checklist.md` ← `gitlab-setup-checklist.md.template`，按主分支名实例化

5. **校验 `.gitlab-ci.yml`**：
   - `ci.lint` 可用 → 经 `gitlab-bridge` 调用校验语法，报告结果
   - 不可用 → 提示 Boss 在 GitLab 项目 `CI/CD → Pipeline editor / CI Lint` 页面手动校验

6. **输出后续人工步骤清单**：
   - 安装并注册 GitLab Runner（**没有 Runner 流水线不会跑**），按选定 executor 准备 Docker/工具链——见 `.codebuddy/skills/ci-integration/references/gitlab-server-setup.md`
   - 部署 MCP server（见 `.codebuddy/skills/gitlab-bridge/references/mcp-setup.md`）
   - 按 `docs/gitlab-setup-checklist.md` 配置 GitLab 项目设置（Protected Branches、Pipelines must succeed 等）
   - 用一个测试 MR 验证五阶段流水线（gate/build/test/quality/verify）触发与阻断

补充约束：
- 本命令只生成文件与清单，**不替 Boss 修改 GitLab 项目设置**——AI 无此能力，必须人工执行
- 全部 `<PLACEHOLDER:...>`（镜像、BUILD_COMMAND、TEST_COMMAND）必须替换，不得留在产物中
- 不要在引擎仓库（superpowers-for-codebuddy）自身运行本命令——引擎托管在 GitHub，只提供模板
- 生成的文档内容默认中文（代码、命令、路径可保留英文）
- 产物已存在时，先 diff 再决定覆盖或合并，覆盖前向 Boss 确认

$ARGUMENTS
