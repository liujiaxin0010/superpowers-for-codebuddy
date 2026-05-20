# MCP Server 内网部署指南（@zereight/mcp-gitlab）

本文件指导在内网环境部署 GitLab MCP server，供 `gitlab-bridge` 技能对接。

## 选型

- **包名**：`@zereight/mcp-gitlab`
- **锁定版本**：`2.1.12`（禁用 `latest`——版本漂移会导致工具集变化）
- **Docker 镜像**：`zereight050/gitlab-mcp`
- **目标 GitLab**：内网自建 Community Edition 14.8.2
- 提供约 156 个工具，支持 self-hosted GitLab

## 内网部署（二选一）

内网无法直连公网 npm / Docker Hub，必须先把依赖搬进内网。

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
