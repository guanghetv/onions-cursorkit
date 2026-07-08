---
name: auto-flow
description: 编排 /onsf-auto 的无交互 Onion SDD 自动化流程，覆盖状态推断、风险门禁、spec 自审、实现纪律、diff 自审和验证收束。
---

# Auto Flow

本技能是 `/onsf-auto` 的自动化编排层。目标是在不打断用户的情况下，让 Agent 按 Onion SDD 规则推进合适的变更流程，并在高风险或不可逆节点停止。

`auto-flow` 不替代现有 onion skills；它负责判断“现在该调用哪个 skill、能否自动继续、何时停止”。模板和具体阶段规则仍以 `mini-change`、`light-change`、`full-change`、`openspec-change`、`external-spec`、`pull-yapi`、`re-check`、`verify-change`、`trellis-adapter` 为准。

## 输入

- 用户对 `/onsf-auto` 的原始输入，可包含显式子模式：`new`、`continue`、`verify`、`finish-check`。
- 当前 git 状态和用户请求相关文件。
- Trellis active task 的 `task.json.meta.onion`（如存在）。
- `.onion-sdd/current.json`（如存在）。
- `openspec/changes/**` 中的活跃 change 产物。
- 外部 spec、YApi、QA、设计稿、截图或用户粘贴内容。

按需读取上下文；不要为了自动化重新引入全仓扫描硬门禁。

## 总体状态机

| 阶段 | 目标 | 主要依据 |
|------|------|----------|
| recover | 定位当前 change 和运行态 | Trellis meta → current.json → OpenSpec 扫描 |
| infer | 推断入口模式 | 显式子模式、用户意图、产物状态 |
| triage | 判断 Tier 和 auto 可行性 | `tier-triage`、风险门禁 |
| materialize | 生成/更新 SDD 产物 | mini/light/full + openspec-change |
| spec-review | 自审 spec 可执行性 | proposal/specs/tasks/external evidence |
| implement | 自动执行任务 | `tasks.md` 和验证点 |
| diff-review | 自审代码和产物 diff | git diff、OpenSpec、外部契约 |
| verify | 执行验证并写报告 | 测试命令、verify-change、e2e-report |
| close | 输出状态和下一步 | ready / blocked / finish-ready |

## 恢复上下文

按以下顺序恢复，任一步骤不可信时降级到下一项：

1. Trellis active task 的 `task.json.meta.onion.change_id` 和 `change_path`。
2. `.onion-sdd/current.json` 的 `active_change_id`、`tier`、`phase`。
3. 用户显式指定的 change-id。
4. `openspec/changes/**` 活跃产物扫描。

冲突处理：

- Trellis meta 与 `.onion-sdd/current.json` 指向不同 change：优先 Trellis active task；若用户显式指定，则用用户指定。
- Trellis meta 指向不存在的 change：标记 stale，降级。
- 多个候选且无法从用户输入或 active task 判断：停止，输出候选和 blocker。
- 没有 active Trellis task：不创建 task，继续 OpenSpec-only 自动化。

## 推断模式

显式子模式优先。没有显式子模式时按表推断：

| 状态 | 推断模式 |
|------|----------|
| 无 change，且用户提供新需求 | `new` |
| 有 change，`tasks.md` 有未完成项 | `continue` |
| `tasks.md` 完成，但缺验证报告或验证未通过 | `verify` |
| `e2e-report.md` 结论通过，或 Tier 0+/1 定向验证闭合 | `finish-check` |
| 用户表达 YApi 到了 / re-check | `continue`，进入接口契约对齐 |
| 用户表达只拉 YApi | `continue`，仅落盘契约，不改业务代码 |

## Tier 与 Auto 判断

先使用 `tier-triage` 判断 Tier，再补充 auto 字段：

```markdown
## Onion Auto 判断

- 推断模式: <new | continue | verify | finish-check>
- Tier: <0 | 0+ | 0++ | 1 | 2 | 3>
- 建议产物: <无 | mini change | light change | onion 完整 OpenSpec>
- auto 模式: <全自动 | 半自动 | 停止>
- auto 置信度: <0.0-1.0>
- 继续假设: <无 / 列表>
- 阻断原因: <无 / 列表>
- 下一步: <将执行的阶段或停止说明>
```

判断规则：

- `全自动`：上下文充分、风险低、验证路径清晰，可运行到实现和验证收束。
- `半自动`：存在低/中风险缺口，但可写明假设并继续。
- `停止`：存在高风险、关键缺失信息、多候选无法裁决，或需要不可逆操作。

## 风险门禁

### 可自动继续

以下低/中风险缺口可继续，但必须把假设写入 `proposal.md`、`tasks.md`、`e2e-report.md` 或最终输出：

- 文案、样式、布局细节可沿用项目既有模式。
- 新增可选字段、mock 补齐或非 breaking 类型补充。
- 局部组件行为可通过现有测试或手动步骤验证。
- 缺少 `.onion-sdd/current.json` 但 OpenSpec 产物唯一且完整。
- 没有 active Trellis task，但 OpenSpec-only 流程可继续。

### 必须停止

以下高风险或不可逆场景必须停止：

- 权限、安全、支付、资金、审计或破坏性数据行为不清。
- 删除/重命名请求或响应字段。
- 字段必填/可选变化会影响表单校验、权限或关键流程。
- method/path/错误码变化与实现、YApi、后端 spec 或测试冲突。
- QA spec 与 YApi/backend spec 冲突，且无法按既有优先级裁决。
- 跨模块状态机、数据流、角色权限语义不清。
- 用户在实现过程中**明确表达**需求或验收口径调整（新增、修改、废弃目标、范围或验收场景）时，必须停止实现并按 `openspec-change` 的「已落盘产物的更新协议」同步产物后再继续。用户澄清已有需求、补充细节或回答 Agent 提问**不触发**本条。
- 关键路径无法验证，也没有等价证据。
- 需要创建/启动/归档 Trellis task。
- 需要 `git commit`、推送、创建 PR/MR 或其它不可逆操作。`/onsf-finish` 门禁通过后自动执行 `openspec archive <change-id>`，失败时停止。

## 分支门禁（auto 特化）

进入 `materialize` 阶段前，按 `rules/onion-sdd.mdc`「写入门禁 > 分支门禁」的 auto 模式特化规则处理，覆盖两类触发条件：

- **受保护分支**：自动生成 `feat/<change-id>` 分支并切换，不停止、不拦截、无需确认；在「验证收束」的最终输出中说明已自动创建的分支名。
- **跨 change 分支复用**（检测依据见 `tier-triage/SKILL.md`「冲突检测 > 跨 change 分支复用检测」）：同样自动生成 `feat/<change-id>` 并切换，但必须在「验证收束」最终输出的风险/blocker 清单中单独点名"检测到当前分支绑定另一个 change `<change-id-A>`，已自动切换到 `feat/<change-id-B>`"，不能与受保护分支场景的提示合并成一句话。

## 产物生成

按 Tier 路由：

- Tier 0：只回答、排查或做内部修正；若产生可追踪代码变更，最终说明验证，不强制 OpenSpec。
- Tier 0+/0++：使用 `mini-change` 创建或更新 mini OpenSpec。
- Tier 1：使用 `light-change` 创建或更新 light OpenSpec。
- Tier 2+：使用 `full-change` 编排，并通过 `openspec-change` 落盘完整 OpenSpec。

如果已有 change，先读取并增量更新，不重建目录。不得覆盖用户或其它会话已有内容；冲突时停止并报告。

## Spec 自审

进入实现前必须自审当前 SDD 产物：

| 检查 | 失败处理 |
|------|----------|
| placeholder / TBD / 未填模板 | 低风险则补齐；无法补齐则停止 |
| 目标、范围、不做范围是否清晰 | 不清晰且影响实现则停止 |
| specs 场景是否可验证 | 能补则补；不能补则停止 |
| tasks 是否有验证点 | 自动补验证点 |
| 外部 spec / YApi / QA 是否冲突 | 高风险冲突停止 |
| 继续假设是否已记录 | 未记录则写入产物或最终输出 |

自审结果必须输出摘要，并在必要时写入 `tasks.md` 或 `e2e-report.md`。

## 实现纪律

- 修改业务代码前必须存在当前 change 的 `tasks.md`，纯 Tier 0 内部修正除外。
- 每个任务先明确验证点，再做最小实现。
- 优先按已有代码风格和本地 helper 实现。
- 自动实现只覆盖当前 change 范围；发现范围膨胀时停止。
- 外部/YApi/QA 到达时按 `external-spec`、`pull-yapi`、`re-check` 的规则处理。

## Diff 自审

实现完成后，进入验证前必须自审 diff：

- diff 是否只包含当前任务范围。
- 是否修改了无关插件、Trellis runtime、归档文件或生成文件。
- 实现是否满足 `proposal.md`、`specs/**/spec.md` 和 `tasks.md`。
- 接口字段是否符合 `backend-yapi-*.md`。
- QA 验收是否优先于普通 OpenSpec 场景。
- 是否有测试、静态检查、手工验证或浏览器验证证据。

发现问题时，低风险问题自动修复并重跑相关检查；高风险问题停止并报告 blocker。

## 验证收束

- 运行项目中可发现且与改动相关的 lint、typecheck、unit/component 测试。
- 无测试工具时记录“未配置 / 未执行”和替代验证步骤，不得虚构。
- Tier 2+ 使用 `verify-change` 生成或更新 `e2e-report.md`。
- 浏览器自动化需要环境、账号或权限时，不自动绕过；缺少条件则记录 blocker。
- 完成后输出：
  - 已执行阶段
  - 修改文件
  - 验证命令和结果
  - spec 自审结果
  - diff 自审结果
  - blockers
  - 是否 ready for user review / commit / finish-check

## Trellis 同步

如果存在 active Trellis task，可按 `trellis-adapter` 更新轻量 metadata：

- `task.json.meta.onion.change_id`
- `task.json.meta.onion.change_path`
- `task.json.meta.onion.tier`
- `task.json.meta.onion.phase`
- `task.json.meta.onion.last_action`
- `task.json.meta.onion.source_hashes`

禁止：

- 自动创建 Trellis task。
- 自动启动 planning task。
- 自动归档 task。
- 修改 `.trellis/scripts/**` 或 `.trellis/.runtime/**`。
- 把 OpenSpec 正文复制进 Trellis task 或 journal。

## 收束边界

`auto-flow` 的终点是“完成实现、验证和归档，但不替用户完成代码提交或远程同步”：

- 不自动 `git commit`。
- 不自动 Trellis archive。
- 不自动 push / PR / MR。
- `/onsf-finish` 门禁通过后自动执行 `openspec archive <change-id>`；CLI 不可用时使用等效手工归档；失败时停止并报告。

如需提交或远程同步，最终输出只提示下一步命令或建议用户明确授权。
