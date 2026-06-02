# GitLab Runner 分步部署指导（Windows shell runner + Linux Docker runner）

本文件是 [gitlab-server-setup.md](./gitlab-server-setup.md) 的**操作篇**：那里讲"要不要 Runner / 要不要 Docker"（决策），这里讲"一步步怎么装、怎么注册、怎么配"（操作）。

> 目标平台：内网自建 **GitLab Community Edition 14.8.2**。内网通常**不能直连公网**——所有二进制 / 镜像都要先搬进内网（内网镜像站 / registry / 文件拷贝）。

## 0. 部署前必读（版本与令牌）

### 0.1 Runner 版本选择
- CE 14.8.2 用 **registration token（注册令牌）** 注册 Runner。建议 GitLab Runner 选 **14.10.x 或 15.x**（二者都原生支持 registration token）。本指南以 **15.11.0** 为例。
- **不要用 ≥ 16.0 的 Runner 配 14.8**：16.0 起弃用了 registration token、改用 authentication token（`glrt-`），而 14.8 的 UI 根本不产生那种令牌，会卡注册。

### 0.2 从哪里拿 registration token
- **项目专用 Runner**（推荐，权限最小）：项目 → **Settings → CI/CD → Runners** → 展开 "Specific runners"，记下 **URL** 和 **registration token**。
- **共享 Runner**（全实例可用）：**Admin Area → Runners** → 拿实例级 registration token。
- 两个值后面注册时都要用：`--url` 和 `--registration-token`。

### 0.3 选哪种 executor（决定要不要 Docker）
| 机器 | 推荐 executor | 要 Docker | 适合 |
|---|---|---|---|
| Windows PC | **shell**（PowerShell）| ❌ | 编译/单测（`.gitlab-ci.yml` 删 `image:`/`services:`）|
| Linux 主机 | **docker** | ✅ | 模板默认，支持 e2e `services:` 真实中间件 |

> Windows 也能跑 docker executor，但要 Docker Desktop / Windows 容器、镜像 OS 要匹配、还涉及授权，重且易错。**Windows 用 shell、Linux 用 docker** 是最省心组合。需要 `services:` 真集成只能走 Linux docker runner。

---

## A. Windows 电脑作为 GitLab Runner（shell executor）

shell executor 直接在本机 PowerShell 里跑 job，**不隔离**——所以工具链要预装在本机，且 `.gitlab-ci.yml` 不能用 `image:`/`services:`。

### A.1 下载 gitlab-runner.exe
在能上网的机器下载（或从内网镜像站取）64 位二进制，拷到目标机 `C:\GitLab-Runner\gitlab-runner.exe`：

```
https://gitlab-runner-downloads.s3.amazonaws.com/v15.11.0/binaries/gitlab-runner-windows-amd64.exe
```

下载后重命名为 `gitlab-runner.exe`，放到 `C:\GitLab-Runner\`。

### A.2 安装为 Windows 服务（管理员 PowerShell）
```powershell
# 以管理员身份打开 PowerShell
cd C:\GitLab-Runner

# 装成服务。建议用专用账号运行，使其 PATH 能看到构建工具链；
# 简单起见也可省略 --user 用内置 System 账号（但 System 的 PATH/权限受限）。
.\gitlab-runner.exe install --user ".\GitLab-Runner" --password "<该账号密码>"
.\gitlab-runner.exe start

# 确认服务在跑
Get-Service gitlab-runner
```
> 用专用本地账号（如 `GitLab-Runner`）运行服务时，**构建工具链必须在该账号的 PATH 里**，否则 job 里 `mvn`/`node` 找不到。

### A.3 注册 Runner（registration token 流程）
```powershell
.\gitlab-runner.exe register `
  --non-interactive `
  --url "https://<内网GitLab域名>/" `
  --registration-token "<REGISTRATION_TOKEN>" `
  --executor "shell" `
  --shell "powershell" `
  --description "win-shell-runner" `
  --tag-list "windows,shell" `
  --run-untagged="false" `
  --locked="true"
```
- `--shell "powershell"` 对应 Windows PowerShell 5.1；装了 PowerShell 7 用 `"pwsh"`。
- `--tag-list` 给 Runner 打标签；`.gitlab-ci.yml` 里对应 job 用 `tags: [windows]` 才会路由到它（混合机群必须打标签 + `--run-untagged=false`）。
- 注册成功后，项目 Settings → CI/CD → Runners 应能看到它且为绿色（online）。

### A.4 预装构建/测试工具链（shell executor 必做）
shell executor 不隔离，job 用什么工具，本机就得有什么。按技术栈装并加入**运行服务的账号的 PATH**：
- Git（必装）：`git --version`
- Java：JDK + Maven/Gradle
- Node：Node.js + npm
- Go / .NET / CMake+Qt 等按需

装完在**该账号上下文**验证（不是你当前登录用户）：可临时把 Runner 服务设为交互或用 `psexec`/计划任务验证，或先 `--user` 用当前已配好 PATH 的账号。

### A.5 适配 .gitlab-ci.yml（与 /ci-setup 一致）
Windows shell runner 上：
- 删除 `default: image:` 和 e2e 的 `services:`（shell executor 会忽略它们）。
- 把脚本从 `bash xxx.sh` 改为 `pwsh -File xxx.ps1`（仓库 `ci-integration/templates/` 提供了 `commit-msg-lint.ps1`）。
- `/ci-setup` 选择 Windows runner 时会自动做这些替换（见 `ci-setup` 命令步骤 4）。

### A.6 验证与排障
```powershell
.\gitlab-runner.exe verify        # 校验注册有效
.\gitlab-runner.exe status        # 服务状态
Get-Content C:\GitLab-Runner\config.toml   # 检查 shell="powershell"、tags
```
- 脚本被 ExecutionPolicy 拦：`Set-ExecutionPolicy -Scope LocalMachine RemoteSigned`（管理员）。
- job 一直 pending：检查标签是否匹配、Runner 是否 online、`--run-untagged` 设置。
- 找不到 `mvn`/`node`：PATH 不在服务账号下——重装服务到正确账号，或把工具加系统 PATH 后重启服务。
- 改了 config.toml 后：`.\gitlab-runner.exe restart`。

---

## B. Linux Runner 上 Docker 部署（docker executor）

docker executor 每个 job 在独立容器里跑，干净隔离，并支持 `services:` 真实中间件。分两段：先装 Docker，再装并注册 Runner。

### B.1 安装 Docker Engine
**联网环境**（Ubuntu/Debian 示例）：
```bash
# 卸旧 → 装 docker-ce（官方仓库；RHEL/CentOS 用 yum install docker-ce）
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg
# ……（按官方文档加 docker 源后）
sudo apt-get install -y docker-ce docker-ce-cli containerd.io
```
**内网/离线环境**：从内网镜像站取 `docker-ce` / `containerd` 的 `.deb`/`.rpm` 离线包，本地安装。

启用并自启：
```bash
sudo systemctl enable --now docker
sudo systemctl status docker
```
验证（内网拉不到 Docker Hub 的 hello-world，用内网 registry 的镜像验证）：
```bash
sudo docker run --rm <内网registry>/busybox:latest echo "docker ok"
```

### B.2 配置内网 registry 访问
docker executor 的 `image:` 必须能从**内网 registry** 拉到。若 registry 是 HTTP（非 TLS）或自签证书：
```bash
# /etc/docker/daemon.json
{
  "insecure-registries": ["<内网registry>"],          # HTTP registry 才需要
  "registry-mirrors": ["https://<内网registry>"]       # 可选：默认走内网
}
```
```bash
sudo systemctl restart docker
```
> TLS + 内网 CA 的 registry：把 CA 证书放 `/etc/docker/certs.d/<内网registry>/ca.crt`，无需 insecure。

### B.3 安装 GitLab Runner（Linux）
二进制方式（最适合离线，版本可控）：
```bash
# 从内网镜像站或公网下载，pin 15.11.0
sudo curl -L --output /usr/local/bin/gitlab-runner \
  "https://gitlab-runner-downloads.s3.amazonaws.com/v15.11.0/binaries/gitlab-runner-linux-amd64"
sudo chmod +x /usr/local/bin/gitlab-runner

# 建专用用户并装成 systemd 服务
sudo useradd --comment 'GitLab Runner' --create-home gitlab-runner --shell /bin/bash
sudo gitlab-runner install --user=gitlab-runner --working-directory=/home/gitlab-runner
sudo gitlab-runner start

# 关键：让 runner 用户能用 docker（docker executor 必需）
sudo usermod -aG docker gitlab-runner
sudo systemctl restart gitlab-runner
```

### B.4 注册 Runner（docker executor）
```bash
sudo gitlab-runner register \
  --non-interactive \
  --url "https://<内网GitLab域名>/" \
  --registration-token "<REGISTRATION_TOKEN>" \
  --executor "docker" \
  --docker-image "<内网registry>/<基础镜像>:<tag>" \
  --description "linux-docker-runner" \
  --tag-list "linux,docker" \
  --run-untagged="true" \
  --locked="true"
```
- `--docker-image` 是 job 未指定 `image:` 时的默认镜像；应含 bash、git 及构建/测试工具链（与 `/ci-setup` 填的 `<INTERNAL_REGISTRY_IMAGE>` 一致）。

### B.5 调优 config.toml（`/etc/gitlab-runner/config.toml`）
```toml
concurrent = 4                       # 并发 job 数

[[runners]]
  name = "linux-docker-runner"
  url = "https://<内网GitLab域名>/"
  executor = "docker"
  [runners.docker]
    image = "<内网registry>/<基础镜像>:<tag>"
    pull_policy = ["if-not-present"]  # 内网：本地有就不再拉，省带宽 / 防拉失败
    # privileged = true              # 仅 DinD（CI 内 build 镜像）才需要；跑 services: 不需要
    volumes = ["/cache"]             # 可选：缓存卷
    # 若 services: 镜像也在内网 registry，确保已镜像过去
```
改完重启：`sudo gitlab-runner restart`。

> **services: 真实中间件**（postgres/redis 等）：这些镜像同样要先搬进内网 registry，`.gitlab-ci.yml` 里 `services:` 引用内网镜像名。docker executor 会用 `pull_policy` 决定是否拉取。

### B.6（可选）让 Runner 自己跑在 Docker 容器里
不想在主机装 runner 二进制时，可用容器化 runner：
```bash
sudo docker run -d --name gitlab-runner --restart always \
  -v /srv/gitlab-runner/config:/etc/gitlab-runner \
  -v /var/run/docker.sock:/var/run/docker.sock \
  <内网registry>/gitlab-runner:v15.11.0
# 再 docker exec 进去执行上面的 register 命令
```
挂 `docker.sock` 让容器内 runner 复用宿主 Docker（socket binding 模式）。

### B.7 验证与排障
```bash
sudo gitlab-runner verify        # 校验注册
sudo gitlab-runner status        # 服务状态
sudo gitlab-runner list          # 已注册 runner
```
- job pending：Runner 是否 online、标签是否匹配、`--run-untagged`。
- `permission denied /var/run/docker.sock`：`gitlab-runner` 用户没进 `docker` 组（B.3 最后一步）→ 加组后重启。
- 拉不到 `image:`：内网 registry 不可达 / 未 mirror 该镜像 / insecure-registries 没配（B.2）。
- `services:` 起不来：检查 service 镜像是否在内网 registry、`alias` 与连接 host 是否一致（见 `ce-14.8.2-cicd-support.md §5`）。

---

## C. 接入 Featureflow 后的衔接

1. Runner 就绪后，回到 `/ci-setup`：docker runner 选 `docker` executor（保留模板 `image:`/`services:`）；Windows shell runner 选 `shell`（删 `image:`/`services:`、脚本切 `.ps1`）。
2. **AI 审查 job（P1-5）需要专用 runner**：若要把 AI 审查做成合并阻断 job（`ai-review-job.yml.template`），需一个 docker runner，镜像里含 CodeBuddy/Claude CLI + node，注册时 `--tag-list "ai-review"`，CLI 鉴权走 masked+protected CI 变量。
3. 验证整条链路：新建测试 MR → 5 阶段在 Runner 上跑起来（不是 pending）→ 故意推不合规 commit 让 `verify:commit-msg` 变红 → 确认 MR 合不了（见 `gitlab-server-setup.md §七`）。

## D. 最小组合建议

- **只要门禁（编译+单测+规范）**：1 台 Windows 或 Linux 机器，shell executor，主机装工具链，最快。
- **要 e2e 真集成（services:）/ AI 审查 job**：Linux + docker executor + 内网 registry，按 B 章部署。
