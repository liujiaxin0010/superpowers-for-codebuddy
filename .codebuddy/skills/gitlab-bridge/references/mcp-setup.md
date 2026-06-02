# MCP Server 内网部署指南（@zereight/mcp-gitlab）

本文件指导在内网环境部署 GitLab MCP server，供 `gitlab-bridge` 技能对接。

## 选型

- **包名**：`@zereight/mcp-gitlab`
- **锁定版本**：`2.1.12`（禁用 `latest`——版本漂移会导致工具集变化）
- **Docker 镜像**：`zereight050/gitlab-mcp`
- **目标 GitLab**：内网自建 Community Edition 14.8.2
- 提供约 156 个工具，支持 self-hosted GitLab

## 内网部署（二选一）

若内网无法直连公网 npm / Docker Hub，需先把依赖搬进内网（二选一如下）。可直连 npm 时则无需此步，直接用 `npx`（见下「mcp.json 配置」）。

### 方式 A：自建 Docker 镜像（推荐）

1. 在能访问公网的机器拉取并锁定版本：
   ```
   docker pull zereight050/gitlab-mcp:<对应 2.1.12 的 tag>
   ```
2. 重新打 tag 推送到内网 registry：
   ```
   docker tag zereight050/gitlab-mcp:<tag> <内网registry>/gitlab-mcp:2.1.12
   docker push <内网registry>/gitlab-mcp:2.1.12
   ```
3. 内网 MCP 客户端配置指向 `<内网registry>/gitlab-mcp:2.1.12`

### 方式 B：内网 npm registry

1. 把 `@zereight/mcp-gitlab@2.1.12` 及其依赖发布到内网 npm registry
2. 配置 MCP 客户端用 `npx @zereight/mcp-gitlab@2.1.12`，并把 npm registry 指向内网

## 环境变量配置

```bash
# 核心连接
GITLAB_API_URL=https://<内网GitLab域名>/api/v4
GITLAB_PERSONAL_ACCESS_TOKEN=<PAT>

# 功能开关（默认关闭，必须显式开启）
USE_PIPELINE=true        # P0-1 CI 门禁强依赖
USE_GITLAB_WIKI=true     # 知识库阶段需要
USE_MILESTONE=true       # 可选

# 安全：初期接入必须只读
GITLAB_READ_ONLY_MODE=true
```

注意：

- `GITLAB_API_URL` 填到 `/api/v4` 为止。若 GitLab 装在子路径下（如 `https://host/gitlab/`），则为 `https://host/gitlab/api/v4`
- 不开 `USE_PIPELINE`，pipeline 类工具不会暴露——`bridge.probe` 会探测到 `pipeline.status` 不可用
- 写操作阶段才把 `GITLAB_READ_ONLY_MODE` 改为 `false`，且需经 Boss 确认

## Personal Access Token（CE 14.8.2）

1. 登录内网 GitLab，右上角头像 → **Preferences → Access Tokens**
2. 名称任填，scope 勾选 **`api`**（最小必要，不要勾管理员级 scope）
3. 设置合理过期时间，生成后立即复制（只显示一次）
4. 不要使用管理员账号的 token；用专用服务账号或个人受限 token

## 令牌最小权限与轮换（推荐）

PAT(scope=api) 是"个人级 + 长期 + 粗粒度"令牌——一旦泄露，攻击者拿到的是该用户在**所有项目**的 api 权限。按最小权限收敛：

| 方案 | 适用 | scope | 说明 |
|---|---|---|---|
| **Project Access Token**（首选）| 单项目接入 | 只勾 `api`（或更细：`read_api` + 必要写）| 项目级、可设过期、可单独吊销；需管理员开启「Allow project access tokens」|
| 专用 **bot / 服务账号** PAT | 跨项目 / 定时自动化 | `api` | 独立账号，权限只授到目标项目；绝不复用管理员或个人主账号 |
| 个人 PAT | 仅本地探测 / 只读试跑 | `read_api` 起步 | 初期只读阶段够用，放开写再升 `api` |

轮换与最小化要点：

1. **设过期时间**（如 90 天），到期前轮换；轮换 = 新令牌生效 → 更新 MCP env / CI 变量 → 吊销旧令牌。
2. **CI 侧**用 **masked + protected** CI/CD Variable 存令牌（只在 protected 分支可见、日志打码）；不要写进 `.gitlab-ci.yml` 或仓库。
3. **接收器 / MCP 侧**令牌走环境变量，不落配置文件、不进 git。
4. **读写分阶段**：初期 `GITLAB_READ_ONLY_MODE=true` + `read_api`；验证无误、经 Boss 确认后再升到可写令牌 + `GITLAB_READ_ONLY_MODE=false`。
5. **吊销演练**：记录每个令牌的用途 / 持有者 / 过期日；泄露时第一动作是在 GitLab 吊销该 token（Settings → Access Tokens → Revoke）。

> CE 14.8.2 **无 OIDC `id_tokens`**（16.4 才有），做不到 GitHub Actions 那种"无存储、自动轮换的短期令牌"。上面用"项目级令牌 + 过期轮换 + masked/protected"作为 CE 下的最小权限替代；升级到 16.4+ 后可改用 OIDC（见 `gitlab-version-support.md §7`）。

## mcp.json 配置

把 MCP server 接进 CodeBuddy 的 MCP 配置（项目级 `.mcp.json` 或全局 MCP 配置），用标准 `mcpServers` 结构；密钥放 `env`，不要写进 `args`。

### npx（可直连 npm 时最简单）

```json
{
  "mcpServers": {
    "gitlab": {
      "command": "npx",
      "args": ["-y", "@zereight/mcp-gitlab@2.1.12"],
      "env": {
        "GITLAB_API_URL": "https://<内网GitLab域名>/api/v4",
        "GITLAB_PERSONAL_ACCESS_TOKEN": "<PAT>",
        "USE_PIPELINE": "true",
        "USE_GITLAB_WIKI": "true",
        "USE_MILESTONE": "true",
        "GITLAB_READ_ONLY_MODE": "true"
      }
    }
  }
}
```

- 必须锁 `@2.1.12`，不要写成 `@zereight/mcp-gitlab`（默认拉 `latest` → 工具集漂移）。
- 纯内网无公网 npm：把包发布到内网 registry，并在 `env` 加 `"npm_config_registry": "https://<内网npm registry>"`（或用项目 `.npmrc`）。

### Docker（用内网 registry 镜像）

```json
{
  "mcpServers": {
    "gitlab": {
      "command": "docker",
      "args": [
        "run", "-i", "--rm",
        "-e", "GITLAB_API_URL",
        "-e", "GITLAB_PERSONAL_ACCESS_TOKEN",
        "-e", "USE_PIPELINE",
        "-e", "USE_GITLAB_WIKI",
        "-e", "USE_MILESTONE",
        "-e", "GITLAB_READ_ONLY_MODE",
        "<内网registry>/gitlab-mcp:2.1.12"
      ],
      "env": {
        "GITLAB_API_URL": "https://<内网GitLab域名>/api/v4",
        "GITLAB_PERSONAL_ACCESS_TOKEN": "<PAT>",
        "USE_PIPELINE": "true",
        "USE_GITLAB_WIKI": "true",
        "USE_MILESTONE": "true",
        "GITLAB_READ_ONLY_MODE": "true"
      }
    }
  }
}
```

`args` 用 `-e 变量名`（不带值）只声明透传，真实值放 `env`，避免 PAT 出现在进程命令行 / 日志。

> 多人共享常驻服务：用 `docker run -e SSE=true -e HOST=0.0.0.0 -p 3333:3002 ... <内网registry>/gitlab-mcp:2.1.12` 以 SSE 起服务，客户端再用 URL 连接。stdio（上面两种）最简单，是默认形态。

配置后重启客户端加载，再由 `gitlab-bridge` 执行 `bridge.probe` 确认实际暴露的工具清单。

## 连接验证

部署后，先用最基础的只读端点验证（不经 MCP，直接验证 GitLab 可达）：

```bash
curl --header "PRIVATE-TOKEN: <PAT>" "https://<内网GitLab域名>/api/v4/version"
```

预期返回 `{"version":"14.8.2",...}`。

随后由 `gitlab-bridge` 执行 `bridge.probe`，确认 MCP server 实际暴露的工具清单。

## 常见问题

| 现象 | 原因 | 处理 |
|---|---|---|
| `/api/v4` 直接访问 404 | `/api/v4` 是前缀不是端点 | 必须接具体资源路径，如 `/api/v4/version` |
| `/api/v4/version` 也 404 | base URL 错误 | 检查域名 / 子路径 |
| 端点返回 401 | 未认证或 token 失效 | 检查 PAT、scope、过期时间 |
| pipeline 工具探测不到 | `USE_PIPELINE` 未开 | 设 `USE_PIPELINE=true` 重启 MCP server |
| Work Items 工具调用失败 | CE 14.8.2 无此 API（GitLab 15+） | 正常，方案不依赖；`bridge.probe` 应标记 unavailable |
| npx 拉包失败 | 内网无公网 npm | 改用内网 registry 或自建 Docker 镜像 |
