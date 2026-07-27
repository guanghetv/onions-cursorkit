# move-aicr-to-check-phase

## 背景

- Onion SDD 当前只在提交门禁触发 AICR（见归档 change `2026-07-17` 对应的提交门禁工作）。审查意见在用户已经授权提交时才出现，返工成本高。
- `trellis-check` 负责 lint、typecheck、测试和 `.trellis/spec/` 对齐，但**不检查团队前后端规范文档，也不做安全风险检测**。check 阶段的人工 review 维度实际是空的。
- 用户诉求：Agent 实现完代码自动 check 时就用 AICR 审一遍，且不要因此把流程跑重。

## 目标

- 把 AICR 从提交门禁前移到 check 阶段，由 Agent 自动完成「暂存本次 change 改动 → `/cr` 审查暂存区 → 修复复审」，用户无需输入任何命令。
- 常规路径下同一份代码只审一遍：提交时暂存区未变化则直接 commit。
- 明确 `trellis-check` 与 `/cr` 的职责边界，避免两者重复展开同样的检查维度。

## 变更

- check 阶段由单一 `trellis-check` 改为四步复合阶段：`trellis-check`（含其修复）→ 暂存本次 change 改动 → `/cr` 审查暂存区 → 修复、回跑受影响门禁、重新暂存、复审。
- 顺序固定不可调换：`trellis-check` 会修改代码，必须在其完成后再暂存，否则审查对象与最终产物脱节。
- 放宽授权边界：check 阶段允许自动 `git add`（限本次 change 范围）与自动 `/cr`；仍禁止自动 `git commit`、push、创建 PR/MR。
- 提交门禁改为条件化：暂存区自 CR 通过后未变化则直接 commit，有任何变化（含新增暂存文件）或无法判定则重新 `/cr`。
- 审查基线统一为暂存区，与 `aicr-local` 既有 `staged` 模式一致，`/cr` 原样调用。

## 影响范围

- 页面/模块：`plugins/onion-sdd/rules/onion-sdd.mdc`、`skills/full-change`、`skills/auto-flow`、`commands/onsf-continue.md`、`README.md`、`USAGE.md`、`docs/feishu-wiki-onion-sdd-usage.md`。
- 数据/API：无。
- 权限/安全/资金：涉及 Git 写权限边界的调整——check 阶段新增自动 `git add` 能力，提交与推送权限不变。
- 兼容性：`aicr-local`、`/cr`、`trellis-check` 均零改动；`fe-specflow` / `be-specflow` 在提交边界用 `staged` 模式调 `/cr`，不受影响。

## 不做范围

- 不改造 `aicr-local`，不为其新增输入模式，不覆盖其任何步骤。
- 不修改 Trellis 源码、`.claude/skills/trellis-check/SKILL.md` 或 `.trellis/scripts/**`。
- 不使用 `git add -A`；不自动 `git reset` 或以任何方式移除用户已暂存的内容。
- 不引入审查指纹机制，不为此修改 `onion_state.py`。
- 不引入 Cursor Hook，维持「无 Hook，靠 command/skill 硬纪律」的既有决策。
- 不用 AICR 替代 `verify-change`、E2E 或 OpenSpec 归档门禁。

## 验收

- 规则中 check 阶段四步顺序、顺序理由、暂存范围、授权边界、提交门禁条件化五项均有明确描述。
- 走读四条路径均不阻塞：正常、`/cr` 不可用、`aicr-local` 未安装、暂存后暂存区为空。
- `git diff --stat -- plugins/common .claude/skills .trellis/scripts` 输出为空。
- `rg -n "aicr|/cr|trellis-check|暂存" plugins/onion-sdd/` 无「AICR 仅在提交前触发」「check 阶段不暂存」的残留口径。

## 风险与回滚

- **风险 1**：`git add` 破坏用户已有暂存意图。缓解：只增不减，禁止 `git reset`；暂存范围限本次 change，归属存疑需用户确认。
- **风险 2**：实现者把顺序调换（先暂存后 `trellis-check`），导致审查对象与产物脱节。缓解：规则中写明顺序理由而不只写顺序。
- **风险 3**：修复循环退化为每次全量重跑 `trellis-check`，流程变重。缓解：规则要求按修复影响面选择回跑范围。
- **风险 4**：提交门禁判定只看「代码有没有改」，遗漏 CR 通过后新增暂存的文件。缓解：判定条件显式覆盖新增暂存文件。
- **回滚**：撤掉规则与技能中的 check 阶段 CR 描述，提交门禁恢复为无条件审查即回到现状。纯文档还原，无状态迁移、无跨插件依赖。

## References

- 用户会话需求：「AI 开发完之后无感调用 aicr-local 做代码 CR，与 trellis-check 结合」。
- 前序工作：Trellis 归档任务 `.trellis/tasks/archive/2026-07/07-17-onion-aicr-gate`（提交门禁 AICR）。
- Trellis 任务：`.trellis/tasks/07-27-aicr-check-merge`。
