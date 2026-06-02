# CI 质量体系 7 原则（CE 14.8.2 适配）

`/ci-setup` 的基础流水线是 5 阶段强门禁（gate→build→test→quality→verify）。本文件提供把它**增强为完整质量流水线**的 7 条原则与 CE 14.8.2 可用的 YAML 片段。

> 所有片段严守 `ce-14.8.2-cicd-support.md` 安全子集。增强前先读该基线。

## 三级测试体系（覆盖率门禁）

| 层级 | 对应级别 | 覆盖率门槛 | CI 执行 |
|---|---|---|---|
| L1 单元测试 | 子模块 | ≥ 80% | 直接运行，无环境依赖 |
| L2 集成测试 | 子组件 | ≥ 40% | 直接运行（内存替代品：sqlite/嵌入式缓存）|
| L3 系统测试 | 子系统 | 关键业务流 | `services:` 启动真实依赖 |

## 原则 1：快速失败，逐层加严

lint → build → unit → integration → e2e，代价递增，低代价阶段先拦截。所有项目必须有 lint 阶段且先于 build；`gofmt -d` / 格式化不通过直接失败（零容忍）。

```yaml
lint:static:
  stage: lint
  script:
    - <格式检查命令，如 gofmt -l . / npm run lint>
    - <静态检查，如 go vet ./... / golangci-lint run>
```

## 原则 2：编译与执行分离

编译产出确定性高于执行。CGO 依赖 / 测试套件多的项目，build 阶段预编译（如 `go test -c`、`go build -cover`），test 阶段复用产物只关注测试逻辑。小项目（编译<1min）可合并。

## 原则 3：覆盖率分层治理

不同阶段不同目标。早期：快速测试低门禁(20-40%)；稳定期：快速 50% + 全量 70-80%；成熟期：统一 80%+。CE 14.8.2 正确写法：

```yaml
test:unit:
  stage: test
  script:
    - <测试命令，产出 cobertura + junit xml>
  coverage: '/total:\s+\(statements\)\s+(\d+\.\d+)%/'
  artifacts:
    when: always
    reports:
      junit: report.xml
      coverage_report:
        coverage_format: cobertura
        path: coverage.xml
```

> 用 job 级 `coverage:` 正则（项目级 regex 设置 15.0 已移除）。进阶：分支覆盖率比语句覆盖率更能暴露逻辑盲区。

## 原则 4：集成测试依赖策略是架构决策

Mock 还是真实中间件，由被测对象性质决定：

- 消费外部协议（HTTP/Thrift/MQ）→ Mock 模式，验证你的逻辑
- 依赖存储引擎行为（SQL 语义/向量检索）→ 真实中间件（`services:`），验证兼容性

```yaml
e2e-test:
  stage: e2e
  services:
    - name: postgres:15
      alias: postgres
  variables:
    POSTGRES_DB: testdb
    DB_HOST: postgres
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event"'
    - if: '$CI_PIPELINE_SOURCE == "schedule"'
```

并行 e2e job 必须资源隔离（`$CI_JOB_ID % 100` 做端口偏移），否则端口冲突产生间歇性失败。

## 原则 5：Lint 配置是团队契约

golangci-lint 等配置把代码审查中的机械性判断编码化，让机器处理机械规则、人专注逻辑审查。建议 30+ linters 覆盖安全(gosec)、SQL(sqlclosecheck)、性能(prealloc)、复杂度(gocyclo)。测试文件可放宽 dupl/gosec，但不放宽 errcheck/govet。

## 原则 6：竞态检测不是可选项

含并发代码（goroutine/channel/mutex）的项目，`-race` 应在单元测试默认启用——把「生产偶发故障」降级为「CI 确定性失败」。代价：测试耗时 2-5 倍，需 `-covermode=atomic`。纯计算/无并发可不启用。

```yaml
test:unit:
  script:
    - go test -race -covermode=atomic -coverprofile=cover.out ./...
```

## 原则 7：防御性 CI 脚本

CI 脚本假设每步都可能失败，确保失败不丢诊断信息：

1. 报告文件必须上传：`artifacts:when: always`
2. 服务必须清理：`after_script` 中 `docker-compose down -v`
3. 外部依赖容错：下载工具时本地已有则跳过，网络失败有回退

```yaml
e2e-test:
  after_script:
    - docker-compose down -v || true
  artifacts:
    when: always
    paths: [logs/, report.xml]
```

## 完整质量流水线（CE 14.8.2 可用，按需启用）

```
lint → build → unit-test(L1≥80%,-race) → integration-test(L2≥40%) → e2e-test(L3,services) → quality → verify
```

部署阶段（deploy-staging 自动 + deploy-production 手动 `when: manual`）由 `/release` 与 `scheduled-automation` Task#3 衔接；CE 14.8.2 生产部署仍需人工审批。
