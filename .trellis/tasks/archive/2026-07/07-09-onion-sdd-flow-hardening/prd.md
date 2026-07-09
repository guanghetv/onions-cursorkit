# onion-sdd 流程缺陷改进：状态可靠化、finish 门禁、0++ 超时与文档收敛

## Goal

让 Onion SDD 在真实跨会话使用中更稳：恢复状态可写可读、`/onsf-finish` 门禁可检查、Tier 0++ 超时可见，并收敛文档口径；用户对外只需要掌握 `/onsf-*`。

## Confirmed Facts

- 用户同意落地此前分析中的改进项，并澄清：
  - **对外命令面**：用户只关注 `/onsf-*`；Trellis 是内部衔接，不作为用户必学命令。
  - **`/onsf-auto`**：与手动路径的行为差异是刻意设计（给 AI 自动化用），不作为「对齐缺陷」去改。
- **范围决策**：本次一次交付四块：
  1. 状态写入可靠化（Trellis `meta.onion` 优先 + `current.json` 镜像/兜底）
  2. finish 可检查门禁（tasks / e2e / validate）
  3. Tier 0++ 超时可见
  4. 文档单一真相源与用户侧 `/onsf-*` 口径
- **状态可靠化形态**：在 `plugins/onion-sdd/` 内提供薄 helper 脚本 + skill/命令硬纪律；**写路径选项 A** — 已绑定 Trellis task 时主写 `task.json.meta.onion`，并镜像更新 `.onion-sdd/current.json`；无 Trellis / 未绑定时只写 `current.json`。读路径保持既有优先级：`meta.onion` → `current.json` → OpenSpec 扫描。不引入 Cursor Hook；不改 Trellis 源码。
- **finish 门禁形态**：在 `plugins/onion-sdd/scripts/` 提供可执行 finish 预检（tasks 未完成项、Tier 2+ 缺 `## 验收结论`、可选 `openspec validate`）；`/onsf-finish` 必须先跑脚本，失败则不归档；有 CLI 才跑 validate，无则降级记录不阻塞其它检查。不做本轮 `--force` 阻断式设计。
- **Tier 0++ 超时形态**：记录 `tier0pp_deadline`（或等价字段）；`/onsf-plan`、`/onsf-continue`、`/onsf-fix` 扫描并提示；逾期未补 mini OpenSpec 时给出硬提示，并阻止将该 0++ 当作已完成归档，直到补档或用户确认转 follow-up。不做一周超 2 次的强制审计系统。
- **0++ 逾期转 follow-up 例外**：选项 A — 仍须落盘才能归档：在当前 change 的 `proposal.md` 写 `## 带债项`（含 follow-up 说明），或先补最小 mini OpenSpec；仅口头确认不够。
- **文档收敛形态**：权威分层：`tier-triage` = Tier 判定权威；README = 能力/协议索引；USAGE = 用户只学 `/onsf-*`；DESIGN-SUPPLEMENT 标清「已实现 / 未做」并去掉过时 Phase 0 口吻；飞书 wiki 与 USAGE 对齐关键点。不做 DESIGN 大删重。
- **Multica**：本次不做任何 Multica 相关交付。
- 现状（仓库已确认）：
  - 插件目录目前仅有 skills/commands/docs/templates，**尚无 scripts/** helper。
  - `.onion-sdd/current.json` 协议已定义，**无自动写入运行时**；除 `/onsf-finish` 归档后切 `idle` 外不保证更新。
  - `task.json.meta.onion` 同步依赖 Agent 按 `trellis-adapter` 自觉执行。
  - `/onsf-finish` 门禁均为 skill 软检查，无独立可执行预检脚本。
  - Tier 0++ 的 24h 补档写在设计文档中，**未实现可见超时/提醒**。
  - Tier 决策树与「Phase 0」表述在多处文档重复，易漂移。
- 约束：不修改 Trellis 源码、`.trellis/scripts/**`、`.trellis/.runtime/**`；不把其他 SDD 插件作为硬依赖；不自动 git commit。

## Requirements

### R1 状态写入可靠化

- 在 `plugins/onion-sdd/scripts/` 提供可调用的状态 helper，统一封装读/写优先级：
  - **读**：已绑定且可信的 Trellis `meta.onion` → 否则 `current.json` → 再 OpenSpec 扫描。
  - **写**：已绑定 Trellis task 时**主写** `meta.onion`（change_id、path、tier、phase、last_action、source_hashes、tier0pp 相关字段），并**镜像**写入 `current.json`；无 Trellis / 未绑定时**只写** `current.json`。
- 各 `/onsf-*` 命令与 `trellis-adapter` / `auto-flow` / `full-change` 等关键 skill 将「阶段切换必须调用 helper」写成硬纪律，并在输出中可核对是否已同步、主写落点（Trellis / current）。
- `current.json` 是无 Trellis 或 metadata stale 时的兜底，不是有 Trellis 时的主状态源；helper 不得把 OpenSpec 正文复制进 Trellis。

### R2 finish 可检查门禁

- 提供 finish 预检脚本，检查至少：`tasks.md` 未完成项（未标注不做）、Tier 2+ 缺 `e2e-report.md` 的 `## 验收结论`（或明确的等价验收记录约定）、可选 `openspec validate`。
- `/onsf-finish` 必须先跑预检；预检失败则不执行 archive（含手工移动降级路径）。
- `openspec` CLI 不可用时：validate 记为降级/跳过；**tasks / e2e / 0++ 逾期为 hard**，**validate 为 soft**（不单独因 validate 缺失而失败，但须在报告中标明）。

### R3 Tier 0++ 超时可见

- 进入 Tier 0++ 时写入 deadline（默认修复完成时刻 + 24h，时区与现有 `last_action_at` 一致用 ISO 8601）。
- `/onsf-plan`、`/onsf-continue`、`/onsf-fix`（及会恢复状态的 auto recover）能发现逾期未补 mini OpenSpec 的 0++，输出硬提示。
- `/onsf-finish`（及预检）对逾期未补档的 0++ 默认不可归档，除非：
  1. 已补齐 mini OpenSpec；或
  2. 用户确认转 follow-up，且已在 `proposal.md` 落盘 `## 带债项`（含 follow-up 说明）——仅口头确认不够。

### R4 文档收敛

- 明确权威源分层，消除「Phase 0 未实现」与现状矛盾的表述。
- USAGE 主路径只教 `/onsf-*`；Trellis 降为内部衔接附录，不要求用户学 `/trellis:*`。
- 同步更新 README、DESIGN-SUPPLEMENT 状态标注、`docs/feishu-wiki-onion-sdd-usage.md` 关键点（状态写入、finish 预检、0++ 超时、命令面）。
- 不把 `/onsf-auto` 与手动差异写成缺陷。

## Acceptance Criteria

- [ ] `plugins/onion-sdd/scripts/` 存在可运行的状态 helper 与 finish 预检；README/USAGE 写明调用方式与「Trellis 主写 / current 镜像·兜底」优先级。
- [ ] 相关 commands/skills 已要求阶段切换调用状态 helper；有绑定 task 时主写 `meta.onion` 并镜像 `current.json`；`trellis-adapter` 不再写「不保证写入」。
- [ ] `/onsf-finish` 文档与纪律要求：预检失败不得 archive。
- [ ] Tier 0++ deadline 字段进入 `current.example.json`（及 meta 协议）；逾期未补档时 continue/plan/fix 有硬提示，finish/预检默认阻断归档；转 follow-up 须 `## 带债项` 落盘。
- [ ] 文档权威分层落地；USAGE 主路径仅 `/onsf-*`；DESIGN 标清已实现/未做；飞书 wiki 文档关键点与 USAGE 一致。
- [ ] 无 Multica 相关改动；未修改 Trellis 源码或 `.trellis/scripts/**`。

## Out of Scope

- 把 `/onsf-auto` 与手动路径行为「对齐」或弱化其无交互差异。
- 要求终端用户学习 `/trellis:*` 命令面。
- 完整 metrics 聚合、Spec Pack registry、一周超 2 次 0++ 的强制审计系统。
- 按变更类型拆前端/后端 skill 包。
- 修改试点目录外既有插件。
- 任何 Multica / `onion-multica-sdd` 适配或迁移工作。
- Cursor Hook 自动写状态。
- finish 预检的 `--force` 绕过开关。

## Notes

- 复杂任务：需 `design.md` + `implement.md` 后再 `task.py start`。
- Multica 迁移评估方案（不在本任务交付内）已写入飞书：https://guanghe.feishu.cn/wiki/CtZRwcqdbia6PXkKZFWclCSdn7b
