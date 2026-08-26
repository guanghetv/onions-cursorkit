---
name: onsf-auto
description: 自动化执行 Onion SDD 流程，按当前状态推断 new/continue/verify/finish-check，并在高风险门禁处停止。
---

# /onsf-auto

用于让 Agent 无交互执行 Onion SDD 流程的第一版自动驾驶层。它会自动判断当前请求或 change 应进入新建、继续、验证或收尾检查，并调用 `skills/auto-flow/SKILL.md` 编排现有 onion skills。

`/onsf-auto` 不替代手动命令；它复用 `/onsf-fix`、`/onsf-tweak`、`/onsf-plan`、`/onsf-continue`、`/onsf-finish` 的产物和门禁。手动命令仍可用于需要更强人工控制的场景。

## 用法

| 输入 | 行为 |
|------|------|
| `/onsf-auto` | 根据用户输入、Trellis metadata、`.onion-sdd/current.json` 和 OpenSpec 产物自动推断模式 |
| `/onsf-auto new` | 从当前需求输入开始新 change 或更新刚创建的 change |
| `/onsf-auto continue` | 恢复当前 change 并继续未完成任务 |
| `/onsf-auto verify` | 执行 spec/diff 自审、验证命令和验收报告更新 |
| `/onsf-auto finish-check` | 显式检查是否 ready for `/onsf-finish`，本模式只检查不归档 |

显式子模式优先于自动推断。未提供子模式时，`auto-flow` 按状态机推断下一步。

## 执行顺序

1. 读取 `skills/auto-flow/SKILL.md`。
2. **恢复上下文（必须）**：
   ```bash
   python3 <onion-sdd>/scripts/onion_state.py --repo-root . get
   ```
   再按需扫描 `openspec/changes/**`。若 `tier0pp_openspec_pending` 逾期，输出硬提示并优先处理补档/带债项，再推断模式。
3. 推断或采用显式子模式：`new` / `continue` / `verify` / `finish-check`。
4. 使用 `tier-triage` 产出 Tier、auto 模式、置信度、阻断原因和继续假设；阶段切换调用 `onion_state.py set`（0++ 用 `mark-tier0pp`）。
5. 按风险门禁执行：
   - 低/中风险缺口：写明假设后继续。
   - 高风险缺口：停止并输出 blocker。
6. 自动生成或更新 SDD 产物：
   - Tier 0+/0++：`mini-change`
   - Tier 1：`light-change`
   - Tier 2+：`full-change` + `openspec-change`
7. 做 spec 自审，修复低风险问题；高风险冲突停止。
8. 在已有 `tasks.md` 后执行实现、验证和 diff 自审；阶段结束更新 `onion_state.py`。
9. 必要时调用 `external-spec`、`pull-yapi`、`re-check`、`verify-change`。
10. `finish-check` 或准备归档前跑 `finish_check.py`；非 0 则 blocked，不 archive。
11. 输出完成状态：ready for user review / ready for commit / blocked / finish-ready。

## Auto 模式

| 模式 | 含义 |
|------|------|
| `全自动` | 信息充分，可从 SDD 产物推进到实现、验证和自审完成 |
| `半自动` | 存在低/中风险缺口，但可记录假设并继续 |
| `停止` | 存在高风险或关键阻断，不得无交互继续 |

每次执行都必须输出：

```markdown
## Onion Auto 判断

- 推断模式: <new | continue | verify | finish-check>
- Tier: <0 | 0+ | 0++ | 1 | 2 | 3>
- auto 模式: <全自动 | 半自动 | 停止>
- auto 置信度: <0.0-1.0>
- 继续假设: <无 / 列表>
- 阻断原因: <无 / 列表>
- 下一步: <将执行的阶段或停止说明>
```

## 停止条件

遇到以下情况必须停止，不得为了“无交互”继续猜：

- 权限、安全、支付、资金、审计或破坏性数据行为不清。
- 删除/重命名响应字段，或字段必填/可选变化影响校验。
- method/path/错误码变化与现有实现、YApi、后端 spec 或测试冲突。
- QA spec 与 YApi/backend spec 冲突，且无法按既有优先级裁决。
- 跨模块状态机、数据流或角色权限语义不清。
- 关键路径无法验证，也没有等价证据。
- 需要创建/启动/归档 Trellis task。
- 需要 `git commit`、Trellis task archive 或其它不可逆历史/归档操作。`/onsf-finish` 门禁通过后自动执行 `openspec archive <change-id>`，失败时停止。

## Trellis 边界

- 如果已有 active Trellis task，可以按 `trellis-adapter` 协议同步 `meta.onion`、phase、change-id、change path、source hashes 和 last action。
- 如果没有 active Trellis task，不自动创建；继续使用 OpenSpec 和可选 `.onion-sdd/current.json`。
- 不修改 Trellis 源码、`.trellis/scripts/**` 或 `.trellis/.runtime/**`。
- 不复制 OpenSpec 正文到 Trellis task 或 journal。
- 记录 journal（调用 `add_session.py`）和 spec 积累判断（加载 `trellis-update-spec`）都不算 task 生命周期操作——它们不创建、不启动、不归档 Trellis task。`/onsf-finish` 门禁通过且当前 change 未绑定 Trellis task 时，可按分支 C 规则自动执行，不在下方"停止条件"之列。
- `full-change/SKILL.md` 新增的"Trellis 缺失时询问是否安装并初始化"仅适用于手动入口（`/onsf-plan` 等触发的 `full-change`）；`/onsf-auto` 无交互场景不触发该询问，Trellis 不可用时继续按现状静默降级，不在「停止条件」中新增"是否安装 Trellis"。
- `full-change/SKILL.md` 的开新任务前遗留扫描与确认归档也仅适用于手动 Tier 2+/3 入口；`/onsf-auto` 不扫描、不询问、不归档遗留 Trellis task 或 leftover OpenSpec。

## 收束边界

`/onsf-auto` 在未显式指定 `finish-check` 且状态已满足 `/onsf-finish` 门禁时，可以自动执行到“实现、验证和归档完成”；显式 `/onsf-auto finish-check` 只输出检查结论，不归档。它不自动：

- `git commit`
- Trellis task archive
- 推送远程分支
- 创建 PR/MR

check 阶段的 `git add`（限本次 change 范围，禁止 `git add -A`）与 `/cr` 不在此限，可自动执行；前者可 `git reset` 撤销，后者只读。

`/onsf-finish` 门禁通过后自动执行 `openspec archive <change-id>`；CLI 不可用时使用等效手工归档；失败时停止并报告。

完成时只输出可执行建议，例如请求用户确认提交、继续 `/trellis:finish-work`，或补充 blocker 所需信息。
