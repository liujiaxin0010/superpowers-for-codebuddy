# Unified Test 类型定义

## UnifiedTestInput

```typescript
interface UnifiedTestInput {
  targetFile: string;           // 被测文件路径（.vue 或 .go），必填
  testFile?: string;            // 已有测试文件路径（可选）
  mode?: string;                // full | generate | execute | coverage（默认 full）
  options?: {
    maxRetries?: number;        // 最大修复重试次数（默认 2）
    coverageThreshold?: number; // 覆盖率阈值（默认 80）
    maxIterations?: number;     // 最大覆盖率迭代次数（默认 5）
    collectCoverage?: boolean;  // 是否收集覆盖率（默认 true）
    enableModelSwitch?: boolean;// 是否启用模型切换建议（默认 true）
    goProfile?: string;         // Go 项目风格: auto | go_kit | generic_go（默认 auto，仅 .go 生效）
  };
}
```

## UnifiedTestResult

```typescript
interface UnifiedTestResult {
  status: "completed" | "partial" | "failed" | "stalled" | "unsupported";
  message: string;
  summary: {
    targetFile: string;
    testFile: string;
    language: "vue" | "go";
    timestamp: string;
  };
  execution: {
    total: number;
    passed: number;
    failed: number;
    duration?: number;
    success: boolean;
  };
  coverage?: {
    statements?: string;
    branches?: string;
    functions?: string;
    lines?: string;
    meetsThreshold: boolean;
    reportPath?: string;
  };
  fixAttempts: {
    count: number;
    details: Array<{
      round: number;
      failuresCount: number;
      result: string;
    }>;
  };
  iterations?: Array<{
    round: number;
    beforeCoverage: number;
    afterCoverage: number;
    improvement: number;
    newTestsGenerated: number;
  }>;
}
```
