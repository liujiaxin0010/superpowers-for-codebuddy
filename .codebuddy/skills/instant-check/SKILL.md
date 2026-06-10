---
name: instant-check
description: 写完即检技能（质量左移）。通过 PostToolUse hook 在每次 Edit/Write 落盘后立即对被改文件做快速静态检查（JS/JSON/Shell/Python 语法层），错误当场反馈给 AI 修正，而不是堆到测试/评审阶段才发现。用户提到"写完即检/即时检查/保存时检查/lint hook/质量左移"时触发。
---

# 写完即检（Instant Check）

本技能回答的是：**怎样让语法级错误在写入那一刻就被打回，而不是污染后续阶段。**

## 核心心智

1. **质量左移到最左**：检查发生在 Edit/Write 之后毫秒级，AI 在上下文还热着的时候立刻收到错误并修正——比测试阶段才发现便宜一个数量级。
2. **机器强制而非散文嘱咐**：用 hook 下沉为硬机制（呼应"流程靠散文执行是脆弱的"），不依赖模型自觉。
3. **快与稳压倒全**：单文件、纯语法层（`node --check`/`JSON.parse`/`bash -n`/`py_compile`）；环境缺工具自动跳过；检查器自身异常一律放行——**宁可漏检不可挡路**。
4. **失败即回馈**：退出码 2 + stderr，按 hook 协议错误文本直接回到 AI 上下文。

## 资源加载规则

- 检查脚本：`scripts/post-write-check.js`（stdin hook 协议 / argv 直传文件两用）
- hook 配置样例：`templates/hooks-settings.sample.json`（合入项目的 CodeBuddy/Claude 设置；字段名以所用 CLI 文档为准）

## 接入方式

项目设置（如 `.claude/settings.json` 或 CodeBuddy 等价物）加：

```json
{
  "hooks": {
    "PostToolUse": [{
      "matcher": "Edit|Write",
      "hooks": [{ "type": "command", "command": "node .codebuddy/skills/instant-check/scripts/post-write-check.js" }]
    }]
  }
}
```

## 何时不用

1. 深度规范/风格检查 → 项目自己的 lint 工具链与 `/code-review`
2. 跨文件类型检查/编译 → 测试与 CI 阶段（本技能只做单文件语法层，保证毫秒级）

## 禁止事项

1. 不要把慢检查（全量 lint、编译、测试）塞进本 hook——写入路径上的延迟会拖垮整个会话
2. 不要让检查器失败挡住写入流程——任何意外（无工具/脚本异常）必须静默放行
3. 不要检查 `.codebuddy-runtime/`、`node_modules/` 等运行态/第三方目录
