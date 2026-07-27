# AICR 前移到 check 阶段执行计划

只改 `plugins/onion-sdd/**` 与 `.trellis/spec/**`，全部是文档与规则改动。P1 是核心，P2 之后是收尾。

范围外（收尾时用 `git diff` 确认零改动）：`plugins/common/**`、`.claude/skills/**`、`.trellis/scripts/**`。

## P0 OpenSpec 产物落盘

本仓库自身走 Onion SDD，Tier 2 改动需落 OpenSpec 产物。

- 用 `openspec-change` 落 `proposal.md`、`specs/**/spec.md`、`tasks.md`。
- capability 归属：本次只涉及 Onion SDD 流程，落在 `onion-sdd-runtime` 或新建流程类 capability；**不要**动 `aicr-mr-mode`，那是 `aicr-local` 自己的 spec，本次不改它。
- 用 `onion_state.py` 绑定本 Trellis task 并写阶段。

**验证**：`openspec validate` 通过；`onion_state.py get` 能读到绑定关系。

**评审门禁**：capability 边界确认后再写 `tasks.md`。

## P1 规则层：重写审查章节

改 `plugins/onion-sdd/rules/onion-sdd.mdc` 的「提交前审查」章节，扩为覆盖 check 与提交两个触发点的审查章节。

**check 阶段四步**：

- 写明顺序：`trellis-check`（含其修复）→ 暂存本次 change 改动 → `/cr` 审查暂存区 → 修复复审循环。
- 写明顺序**不可调换的理由**：`trellis-check` 会改代码，先暂存会导致审查对象与最终产物脱节。只写顺序不写理由，后续实现者容易自行优化掉。
- 写明修复循环需**回跑门禁**：CR 提的修复若触及逻辑，会破坏第 1 步已通过的 lint / typecheck / 测试，须重跑受影响部分再重新暂存；纯格式调整可直接重新暂存。不要求每次全量重跑 `trellis-check`。
- 写明 Agent 自动执行，用户无需输入命令。

**暂存范围**：

- 限本次 change 涉及的改动，**禁止** `git add -A`。
- 归属存疑的文件列清单请用户确认，不默认纳入。
- 暂存区已含本次 change 之外内容时提示用户，**禁止** `git reset` 或任何移除已暂存内容的动作。

**授权边界**（两条分开写，避免被读成「check 可以自动提交」）：

- check 阶段允许自动 `git add`（限上述范围）与 `/cr`。
- 仍禁止自动 `git commit`、push、创建 PR/MR。

**提交门禁条件化**：

- 暂存区自 CR 通过后未变化 → 直接 commit；有任何变化（**含新增暂存文件**）→ 重新 `/cr`；无法判定 → 重审。
- 明示判定由 Agent 依据会话上下文完成，**不引入**指纹机制、不改 `onion_state.py`，避免后续实现者自行加一套状态机。

**职责切分与降级**：

- 与 `trellis-check` 的边界依据见 `prd.md` 能力边界表；注明切分是弱约束，重叠结论去重即可。
- 降级沿用现行第 91–92 行两条（`/cr` 不可用读 `SKILL.md`；未安装则 Agent 自审暂存区），均不阻塞 check。

**验证**：
- 走读四条路径：正常、`/cr` 不可用、`aicr-local` 未安装、暂存后为空，确认均不阻塞。
- 确认修复循环有回跑门禁的表述，且未要求每次全量重跑 `trellis-check`（否则循环成本失控）。
- 确认 `git add` 与 `git commit` 的授权表述分开且无歧义。
- 确认提交门禁的判定条件覆盖「新增暂存文件」，不只是「代码有没有改」。
- 确认未新增对 `aicr-local` 的硬依赖表述（对照本文件「不把其他插件作为执行依赖」）。

**回滚点**：撤掉本节并把提交门禁恢复为无条件审查，即回到现状。

## P2 技能与命令层口径对齐

改 `plugins/onion-sdd/skills/full-change/SKILL.md`「质量审查」章节、`skills/auto-flow/SKILL.md`（`Diff 自审` 与 `验证收束`）、`commands/onsf-continue.md`（check 行与恢复优先级）：

- check 阶段统一描述为四步复合阶段，指向规则而非各自复述细节。
- 派发 `trellis-check` 时声明聚焦可执行门禁与 `.trellis/spec/` 对齐。
- `auto-flow`：`/onsf-auto` 下暂存与 `/cr` 可自动执行；commit 仍在高风险清单内停止。现行「不暂存文件，也不调用 `aicr-local` 或 `/cr`」的表述需改写。
- `auto-flow` 的 `diff-review` 与 check 阶段 CR 的关系要理清，避免两者被读成重复动作。

**验证**：`rg -n "aicr|/cr|trellis-check|暂存" plugins/onion-sdd/` 逐条核对，确认无「AICR 仅在提交前触发」「check 阶段不暂存」的残留口径。

## P3 用户文档与发版

- 口径同步：`plugins/onion-sdd/README.md`、`USAGE.md`、`docs/feishu-wiki-onion-sdd-usage.md`。三处的 Commit review 段、扩展能力表、流程图都要改。
- 扩展能力表中 `aicr-local` 的「使用时机」从「用户授权提交后」改为「check 阶段自动执行；提交时按需复审」。
- USAGE 的收尾流程图（约 503–525 行）与飞书文档对应段落需同步为新顺序。
- 版本：`plugins/onion-sdd/.cursor-plugin/plugin.json` 0.1.4 → 0.1.5；`plugins/common` **不动**。
- CHANGELOG：追加条目，写明 CR 前移、暂存授权放宽边界、提交门禁条件化、未改造 `aicr-local`。
- `.cursor-plugin/marketplace.json` 的 onion-sdd description 按需同步。

**验证**：`rg -n -i "aicr|/cr" plugins/onion-sdd/ .cursor-plugin/` 全量核对口径一致。

## P4 Trellis spec 回写

现有 spec 明确写着「AICR 只审提交物」，与本次改动直接冲突：

- `.trellis/spec/backend/onion-sdd-runtime.md`「约定：提交前 AICR 与 trellis-check 分工」段（约 129–135 行）：改为 check 阶段四步 + 提交门禁条件化，更新职责切分表述。
- `.trellis/spec/guides/index.md` 的 Onion SDD 触发器清单（约第 70 行）：「用户授权提交时：暂存 → `/cr` → commit」改为新口径。

**验证**：`rg -n -i "aicr" .trellis/spec/` 无残留旧口径。

## 范围外零改动确认

收尾时执行：

```bash
git diff --stat -- plugins/common .claude/skills .trellis/scripts
```

预期输出为空。`plugins/fe-specflow` 与 `plugins/be-specflow` 同样应无改动——它们在提交边界用 `staged` 模式调 `/cr`，本次不触碰。

## 全局质量门禁

- 中文正文，路径 / 命令 / 标识符保留英文（`doc-writing-zh` 规则）。
- 最后一轮按本任务范围跑一次完整 check：`trellis-check` → 暂存 → `/cr`。本次改动全是 Markdown，CR 主要看口径一致性与规范表述。
- 用新流程自己走一遍收尾，顺带验证规则可执行（dogfooding）。
