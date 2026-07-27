# AICR 前移到 check 阶段并与 trellis-check 职责切分

## 目标

把 AICR 从提交门禁前移到 check 阶段，让 Agent 实现完代码后自动完成「暂存本次 change 改动 → `/cr` 审查暂存区 → 修复复审」，补上团队规范、安全风险和影响范围这三个 `trellis-check` 覆盖不到的维度。

常规路径下同一份代码只审一遍，用户不需要输入任何命令。

## 背景

当前 AICR 只在提交门禁触发（见归档任务 `07-17-onion-aicr-gate`），存在两个问题：

1. 触发太晚。审查意见在用户已经授权提交时才出现，返工成本高。
2. 覆盖有缺口。`trellis-check` 不检查团队前后端规范文档，也不做安全风险检测；check 阶段的人工 review 维度实际是空的。

## 约束：不改造 `aicr-local`

只改 Onion SDD 自己的流程，不动 `plugins/common/**`，不影响 `fe-specflow` / `be-specflow` 等其他工作流。

审查基线统一为**暂存区**，与 `aicr-local` 既有的 `staged` 模式完全一致，因此 `/cr` 原样调用，不需要覆盖它的任何步骤。这是把 CR 前移到 check 阶段而不是新增一种审查——同一个能力，换了触发时机。

## 能力边界（切分依据）

| 维度 | 归属 | 说明 |
|---|---|---|
| lint / typecheck / 测试执行 | `trellis-check` | `aicr-local` 不跑测试 |
| `.trellis/spec/` 项目规范对齐 | `trellis-check` | `aicr-local` 不读该目录 |
| spec 回写（新约定写回 `.trellis/spec/`） | `trellis-check` | `aicr-local` 是只读审查 |
| 团队前后端规范 | `/cr` | `trellis-check` 完全没有 |
| 安全风险（XSS / SQL 注入 / 敏感信息） | `/cr` | `trellis-check` 完全没有 |
| 影响范围（调用方追踪、签名变更） | `/cr` | `trellis-check` Step 5 粗略覆盖，由 CR 承接 |
| 业务需求对齐 | `/cr` | 对 `openspec/specs/`，是 Onion SDD 的真源 |

## 需求

### R1 check 阶段自动完成暂存与 CR

- check 定义为复合阶段，由 Agent **自动串联**，用户无需输入任何命令：
  1. `trellis-check`（含其自身的修复）
  2. 暂存本次 change 范围内的改动
  3. `/cr` 审查暂存区
  4. 发现问题则修复、重跑受影响的门禁、重新暂存、复审，循环至通过
- 顺序不可调换。`trellis-check` 可能修改代码（如修 lint），必须在其完成后再暂存，否则暂存内容与最终产物不一致。
- 第 4 步的修复若触及逻辑（如抽共享常量、补边界判断），须重跑相关 lint / typecheck / 测试后再重新暂存；纯格式或命名调整可直接重新暂存。不要求每次全量重跑 `trellis-check`。
- 派发 `trellis-check` 时声明本次聚焦可执行门禁与 `.trellis/spec/` 对齐，人工 review 维度由 `/cr` 覆盖。

### R2 暂存范围限于本次 change

- 只暂存属于本次 change 的改动，不使用 `git add -A`，避免把用户无关的本地改动带入。
- 归属无法判断的文件，列出清单请用户确认，不默认纳入。
- 暂存区已存在本次 change 之外的内容时，提示用户但**不执行** `git reset`——移除他人已暂存内容才是真正的破坏性操作。

### R3 放宽暂存授权，但不放宽提交授权

- check 阶段允许自动 `git add`（限 R2 范围）与自动 `/cr`。
- 仍然**禁止**自动 `git commit`、push、创建 PR/MR。这两类动作的不可逆程度差一个量级，不能一起放开。

### R4 提交门禁条件化

- 用户授权提交时，判断暂存区自 CR 通过后是否发生变化。
- 未变化 → 直接 commit，不重复审查。
- 发生任何变化（含新增暂存文件）→ 重新 `/cr` 后再 commit。
- 无法判定是否变化（如跨会话）→ 按重审处理。
- 判定由 Agent 依据会话内上下文完成，**不引入**指纹机制，不修改 `onion_state.py`。

### R5 只改 Onion SDD

- 不修改 `plugins/common/**`（含 `aicr-local` 与 `/cr`）。
- 不修改 Trellis 源码、`.claude/skills/trellis-check/SKILL.md` 或 `.trellis/scripts/**`。

### R6 保持可降级，不成为硬依赖

- `/cr` slash command 不可用 → 读取并按 `aicr-local` 的 `SKILL.md` 审查暂存区。
- `aicr-local` 未安装 → Agent 对暂存区自审，并注明团队规范维度未覆盖。
- 两种降级均**不阻塞** check。该约束来自 `rules/onion-sdd.mdc`「不把其他插件作为执行依赖」。

## 不做范围

- **不改造 `aicr-local`**，不为其新增输入模式，不覆盖其任何步骤。
- **不用 `git add -A`**。
- **不自动 `git reset`** 或以任何方式移除用户已暂存的内容。
- **不引入审查指纹机制**，不为此修改 `onion_state.py`。
- 不引入 Cursor Hook。仓库既有决策是「无 Hook，靠 command/skill 硬纪律」，本次不推翻。
- 不用 AICR 替代 `verify-change`、E2E 或 OpenSpec 归档门禁。

## 验收标准

- [ ] `plugins/onion-sdd/rules/onion-sdd.mdc` 的审查章节定义 check 阶段的四步顺序，并写明 `trellis-check` 必须先于暂存完成。
- [ ] 规则写明放宽边界：check 阶段允许 `git add` 与 `/cr`，仍禁止自动 `commit` / push / PR。
- [ ] 规则写明暂存范围限于本次 change、归属存疑需用户确认、不得 `git reset`。
- [ ] 规则写明提交门禁的条件化判定，且「无法判定」回退为重审。
- [ ] `full-change`、`auto-flow`、`onsf-continue` 的 check 口径与规则一致，`/onsf-auto` 下暂存与 CR 可自动执行、commit 仍停止。
- [ ] 两条降级路径（`/cr` 不可用、`aicr-local` 未安装）有描述且不阻塞 check。
- [ ] `git diff` 确认 `plugins/common/**`、`.claude/skills/**`、`.trellis/scripts/**` 零改动。
- [ ] README、USAGE 与飞书同步文档中不残留「AICR 仅在提交前触发」的旧口径。
- [ ] `.trellis/spec/backend/onion-sdd-runtime.md` 与 `.trellis/spec/guides/index.md` 中「AICR 只审提交物」的旧约定已回写。
- [ ] `plugins/onion-sdd` 的 `plugin.json` 版本与 CHANGELOG 同步。
