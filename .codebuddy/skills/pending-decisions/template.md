# 待决策事项（Pending Decisions）

<!--
本文件由 `.codebuddy/skills/pending-decisions/SKILL.md` 管理。
触发条件：一次回复出现 ≥ 2 个待决策项，或 Boss 未一次性全部回答。
不要把已收敛的决策只留在这里——`status=answered` 后必须同步回主文档。
-->

## 当前会话

- 会话开始：<!-- YYYY-MM-DD HH:MM -->
- 关联主文档：<!-- specPath / brainstormPath / planPath，可多条 -->

## 待决策项列表

<!--
每项独立一个 ### 块，按 PD-YYYYMMDD-NNN 升序排列。
status 取值：pending / partial / answered / deferred / dropped
-->

### PD-YYYYMMDD-001 <!-- 示例占位，正式使用时删除 -->

- **阶段**：brainstorm / spec-lite / write-plan / execute-plan / code-review / release / other
- **提出时间**：YYYY-MM-DD HH:MM
- **问题**：<!-- 原文，不要改写 -->
- **选项**：
  | 选项 | 收益 | 代价/风险 | 适用前提 |
  |---|---|---|---|
  | A. | | | |
  | B. | | | |
- **AI 推荐**：<!-- 推荐选项 + 一句话理由，可留空 -->
- **状态**：pending
- **Boss 决策**：<!-- 仅 answered 时填 -->
- **决策时间**：<!-- 仅 answered 时填 -->
- **关联文档**：<!-- 路径数组 -->
- **备注**：<!-- 讨论摘要、风险提示、supersede 关系 -->

---

## 已归档（按月滚动）

<!--
当 `status` 进入 answered/dropped/deferred 且条数 > 500 行时，
按月归档到 docs/pending-decisions/YYYY-MM.md，本节仅保留链接。
-->

-
