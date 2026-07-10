# onion-sdd

Onion SDD 是一个通用 SDD 插件，用 slash command 把变更按复杂度分层：小变更走轻量 OpenSpec 产物，中大型变更进入 onion 自有完整 SDD 基座能力。它保留成熟 SDD 闭环中的需求接入、OpenSpec、任务规划、外部 spec 接入、E2E/验收和归档门禁，同时降低小任务的流程厚度。

**使用说明（安装、命令、典型流程）见 [USAGE.md](./USAGE.md)**；[飞书知识库](https://guanghe.feishu.cn/wiki/XpetwuJJjitqYukZiPYc1atPn3c) 同步面向团队分发。

## 当前能力

- 承诺 slash command 触发；手动命令保持显式入口，`/onsf-auto` 提供无交互自动化入口。
- 通过 Tier 分级决定是否写 OpenSpec、写到什么粒度、何时升级到完整工作流。
- 提供 Tier 0+/Tier 1 的 mini/light OpenSpec 模板与验证纪律。
- Tier 2+ 使用 onion 自有完整 SDD skills，覆盖需求接入、完整 OpenSpec、任务规划、外部 spec 接入、E2E/验收和 finish 门禁。
- Tier 2+ 的前端场景补充前端专项纪律：Figma/局部改版边界、前端灰区决策、workspace-native spec 拉取、YApi 契约对齐、Browser 自动化约束和提交前审查。
- 按需读取与当前变更相关的需求、代码、OpenSpec、测试和验证材料，不设置全仓扫描硬约束。

## 目录

```text
plugins/onion-sdd/
├── .cursor-plugin/plugin.json
├── DESIGN-SUPPLEMENT.md
├── commands/
│   ├── onsf-fix.md
│   ├── onsf-tweak.md
│   ├── onsf-plan.md
│   ├── onsf-auto.md
│   ├── onsf-continue.md
│   └── onsf-finish.md
├── rules/
│   └── onion-sdd.mdc
├── scripts/
│   ├── onion_state.py      # 运行态：Trellis meta 主写 + current 镜像/兜底
│   └── finish_check.py     # /onsf-finish 归档前置预检
├── skills/
    ├── tier-triage/SKILL.md
    ├── mini-change/SKILL.md
    ├── light-change/SKILL.md
    ├── full-change/SKILL.md
    ├── openspec-change/SKILL.md
    ├── external-spec/SKILL.md
    ├── auto-flow/SKILL.md
    ├── pull-yapi/SKILL.md
    ├── re-check/SKILL.md
    ├── verify-change/SKILL.md
    └── trellis-adapter/SKILL.md
└── templates/
    └── current.example.json
```

## 命令地图

| 命令 | 用途 | 主要技能 |
|------|------|----------|
| `/onsf-fix` | Tier 0+/0++ : 小修复/低风险配置调整/紧急故障 | `tier-triage` → `mini-change` |
| `/onsf-tweak` | Tier 1 : 单点轻量体验或行为调整 | `tier-triage` → `light-change` |
| `/onsf-plan` | 判断变更层级并进入合适流程（主入口） | `tier-triage`，Tier 2+ 进入 `full-change` |
| `/onsf-auto` | 无交互自动化执行 Onion SDD 流程，到实现、验证和自审完成为止 | `auto-flow` + 对应 Tier skill |
| `/onsf-continue` | 从 Trellis active task、`.onion-sdd/current.json` 或 `openspec/changes/**` 恢复上下文 | `trellis-adapter` + OpenSpec 产物 + 对应 skill |
| `/onsf-finish` | 检查验证证据、任务完成度与归档条件 | `mini-change` / `light-change` / `verify-change` |

## Tier 路由

| Tier | 场景 | 默认处理 |
|------|------|----------|
| Tier 0 | 纯问答、排查、不需要修改 | 不创建 OpenSpec |
| Tier 0 (内部) | 纯内部修正（类型/lint/重构）或纯配置/文档 | 不创建 OpenSpec，commit 说明验证 |
| Tier 0+ | 明确且低风险的小改动 | 使用 mini change |
| Tier 0++ | 线上 P0/P1 紧急故障 | 先修后补，24h 内补 mini OpenSpec |
| Tier 1 | 单模块轻量行为或体验调整 | 使用 light change |
| Tier 2 | 跨模块、接口、状态流、数据契约或明显产品语义变化 | 转入 onion 完整 SDD 流程 |
| Tier 3 | 多仓、多角色、多阶段或需要拆分父子任务 | 先拆分，再按子任务进入完整流程 |

遇到风险红线时必须升级：需求不清、影响范围跨模块、数据契约变化、权限/安全/支付/资金相关、需要 E2E 门禁、或用户明确要求完整设计。

## 独立流程

`onion-sdd` 是独立的 SDD 插件流程，不要求安装其他 SDD 插件才能工作。所有用户可见的命令、技能、规则和产物口径都以 onion 自身为准；后续成熟能力应按 onion 的命名、模板和门禁沉淀到本插件内。

## 完整 SDD 基座

Tier 2+ 使用以下 onion 自有能力：

| Skill | 作用 |
|-------|------|
| `full-change` | 完整流程编排：需求接入、澄清、阶段推断、任务规划和事件路由 |
| `openspec-change` | 将设计结论写入 `proposal.md`、`specs/**/spec.md`、`tasks.md` |
| `external-spec` | 接入后端/API/QA/外部 spec，写入 `backend-*.md`、`qa-*.md` 并做差异分析 |
| `auto-flow` | `/onsf-auto` 的自动化编排：状态推断、风险门禁、spec 自审、diff 自审和验证收束 |
| `pull-yapi` | 通过 YApi MCP 读取接口契约，设计期只读参考或 T1 后写入 `backend-yapi-*.md` |
| `re-check` | YApi 契约到达后，对齐当前范围内的 mock、类型、API 层和测试 |
| `verify-change` | 生成验证清单，先做 TDD/静态验证前置门禁，再执行或记录 E2E/等价验收，写入 `e2e-report.md` |
| `trellis-adapter` | 同步 OpenSpec、`.onion-sdd/current.json` 和 Trellis task metadata |

完整流程仍遵循 OpenSpec 分工：Agent 负责变更目录中的 Markdown 产物；OpenSpec CLI 的创建、校验按当前环境与用户授权处理；归档由 `/onsf-finish` 在门禁通过后自动执行。

### 前端专项能力

当 Tier 2+ 变更涉及前端页面、组件、交互、样式或端到端验收时，onion 完整流程额外应用以下能力：

- Figma/设计稿：有设计稿时优先读取与本次范围相关的节点和视觉规格；局部改版只改用户指定区域，同页其它区域若稿码不一致，先二次确认。
- 前端灰区：在 OpenSpec 落盘前补齐与本次相关的空态、加载态、错误态、防重复提交、分页/大数据量、权限条件渲染、响应式和动效等决策；纯文案/样式微调或用户明确跳过时可以不展开。
- workspace-native spec：外部 spec 到达时，优先使用用户提供的工作区文件；若存在 `workspace-repos.json` 与 `proposal.md` frontmatter，可按 `requirement_ref` / `modules` 定位并切片；再降级到 GitLab/远程链接或用户粘贴。
- YApi 契约：飞书卡片/需求文档中出现 YApi 链接或 interfaceID 且需求涉及接口变更时，设计期使用 `pull-yapi` 只读提取字段、类型、必填、错误码和示例；T1 后 YApi 到达或用户说 re-check 时，使用 `re-check` 对齐 mock、类型、API 层和测试。
- 飞书卡片开发分支：飞书项目卡片和需求文档可以作为需求来源；进入实现前如需要创建开发分支，可调用 Common 插件的 `create-feature-branch` 扩展能力。onion-sdd 只记录卡片 ID、需求文档来源和分支名，不复制分支创建逻辑。
- Browser 自动化：`verify-change` 先输出 TDD/静态清单和验证依据摘要，再询问用户是否执行浏览器自动化；自动化优先使用产品内置浏览器能力，不把用户自配 DevTools MCP 作为默认执行通道。
- Commit review：onion 不自动提交。用户明确要求提交时，先检查/暂存目标改动，再做提交前审查；有团队本地审查命令或 skill 时优先使用，否则由 Agent 对暂存区自审，通过后再提交。

### 实现纪律与需求调整同步

Tier 2+ 实现阶段补充以下纪律（权威定义见 `rules/onion-sdd.mdc` 的「实现纪律」、`skills/full-change/SKILL.md` 与 `skills/openspec-change/SKILL.md`）：

- **TDD 红绿循环**：能写自动化测试的任务走 失败用例 → 最小实现 → 通过；不得先实现再补测试。
- **前端分层验证**：L1 契约/mock → L2 行为 Scenario → L3 联调/真实 API → L4 Browser 交叉验证；逐 task 在 `tasks.md` 勾选时附对应层级验证证据。
- **无测试工具降级**：纯配置/文档/紧急 Tier 0++ 等不适用 TDD 的场景，在 `tasks.md` 或验证报告中记录静态检查/手动验证/浏览器验证步骤，不得虚构已跑测试。
- **任务粒度约束**：`tasks.md` 按**可验证交付物**（组件、hook、store、页面、API 模块、能力）拆分，不按代码行数拆分；Tier 2 通常 3-8 个 task，每个 task 必须有独立可执行的验证点；优先按 OpenSpec `specs/**/spec.md` 的 Requirement / Scenario 边界对齐。
- **verify 前置门禁**：`verify-change` 先给出 TDD/静态验证清单结论（L1/L2 等逐项标注通过/失败/跳过），再进入浏览器自动化步骤；未给出前置结论前不进入浏览器步骤。
- **需求调整同步协议**：实现过程中用户**明确表达**需求或验收口径调整（新增、修改、废弃目标/范围/验收场景）时，暂停实现，按 `openspec-change` 的「已落盘产物的更新协议」回写 `proposal.md` / `specs/**/spec.md` / `tasks.md` 并追加 `## 需求调整记录`，再继续；触发升级红线则回到 `tier-triage` 重新分级。用户澄清已有需求、补充细节或回答 Agent 提问**不触发**本协议。`full-change`、`auto-flow`、`/onsf-continue` 均引用此协议。

### 可选扩展能力

`onion-sdd` 不把 Common 插件作为运行时硬依赖，但可以在团队常见开发场景中调用 Common 能力：

| 扩展能力 | 来源 | 使用时机 |
|----------|------|----------|
| `create-feature-branch` | `plugins/common/skills/create-feature-branch` | 飞书项目卡片需求进入实现前，需要按卡片 ID、任务名称和规划迭代创建并推送 feature 分支 |

若该扩展 skill 未安装或未同步，onion-sdd 应继续完成需求分析和 OpenSpec 产物，并提示用户安装 Common 插件、同步该 skill，或手动创建分支。

## 安装

`onion-sdd` 已注册到 `.cursor-plugin/marketplace.json`，source 为 `onion-sdd`。本地调试时仍可手动指定 `plugins/onion-sdd/` 路径。

YApi 能力是可选增强。需要本地可用 `user-yapi-common-mcp`，并配置 `YAPI_BASE_URL`、`YAPI_GLOBAL_TOKEN`；不可用时 onion-sdd 会要求用户粘贴接口文档，并按 `pull-yapi` 模板降级整理。

## Trellis Adapter

Phase 1 的 adapter 采用 onion 插件内 skill + 文档协议，不改造 Trellis 源码或 `.trellis/scripts/**`。

边界如下：

- OpenSpec 是变更正文唯一真相源。
- `.onion-sdd/current.json` 保存轻量恢复状态和 Trellis task 引用。
- Trellis task 保存 task runtime：status、`branch`、`base_branch`、parent/children、`task.json.meta.onion` 和 journal 摘要。
- `task.json.meta.onion` 只保存 onion/OpenSpec 专有引用，例如 `change_id`、`change_path`、tier、phase 和 source hashes；不要重复保存 Trellis 标准字段。
- 不复制 OpenSpec 正文到 `.trellis/tasks/**/prd.md`、`task.json` 或 journal。
- 如果后续发现必须改 Trellis 才能继续，先停止并向用户确认。

`/onsf-continue` 的恢复优先级：

1. Trellis active task 的 `task.json.meta.onion.change_id`。
2. `.onion-sdd/current.json` 的 `active_change_id`。
3. `openspec/changes/**` 产物扫描。

Tier 3 使用 Trellis 现有 parent/child task tree 承载运行时关系；child task 的 `meta.onion.parent_change_id` 指向 parent change。

OpenSpec 与 Trellis 的推荐分工：

| 内容 | 归属 |
|------|------|
| 需求正文、行为要求、验收证据 | OpenSpec `proposal.md`、`specs/**/spec.md`、`e2e-report.md` |
| 产品/验收维度任务 | OpenSpec `tasks.md` |
| 工程执行计划、验证命令、回滚点 | Trellis `implement.md` |
| 分支名、PR 目标分支、parent/child task | Trellis 标准字段 |
| change-id、change path、source hashes | `task.json.meta.onion` |
| 开发者 journal、会话摘要 | 绑定 Trellis task → `/trellis:finish-work` 或 workflow.md Phase 3.3 写入；未绑定但 Trellis 可用 → `/onsf-finish` 归档成功后自动调用 `add_session.py` 写入 |
| spec 经验积累（`.trellis/spec/`） | 绑定 Trellis task → workflow.md Phase 3.3（`trellis-update-spec`）写入；未绑定但 Trellis 可用 → `/onsf-finish` 归档成功后加载 `trellis-update-spec` 判断并按需写入 |

Trellis 检查（Tier 2+/3 进入 `full-change` 时，仅手动入口）：未安装时会询问是否安装并初始化（先探测 `trellis --version`，未装 CLI 才 `npm install -g`，再 `trellis init` 并追加 `.gitignore`）；已安装但检测到 `Trellis update available` 时会询问是否执行 `trellis upgrade` + `trellis update`。拒绝或失败不阻塞，`/onsf-auto` 不触发。

## 自动化边界

`/onsf-auto` 支持无交互执行 Onion SDD 流程：自动判断 new/continue/verify/finish-check，按 Tier 生成或更新 OpenSpec，执行实现、验证、归档、spec 自审和 diff 自审。它采用“高风险停止，低/中风险记录假设后继续”的策略。

`/onsf-auto` 不自动执行不可逆或跨系统生命周期动作：

- 不自动 `git commit`、push 或创建 PR/MR。
- `/onsf-finish` 门禁通过后自动 `openspec archive <change-id>`；CLI 不可用时使用等效手工归档；失败时停止。
- 不自动创建、启动或归档 Trellis task；已有 active task 时只同步 `meta.onion`。
- 不绕过权限、登录、关键路径不可验证、QA/YApi 冲突、接口删除/重命名等高风险 blocker。

## 当前不做

- metrics 聚合、Spec Pack registry 和 marketplace 完善可继续迭代；当前 Phase 1 主流程不依赖它们才能运行。
- 不自动提交 git commit。
- 不修改试点目录外的既有插件。
- 不修改 Trellis 源码、`.trellis/scripts/**` 或 `.trellis/.runtime/**`。

## 运行时状态与脚本

阶段切换、恢复与 finish 预检通过插件脚本执行（无 Cursor Hook；靠 `/onsf-*` 与 skill 硬纪律）：

```bash
SCRIPTS=plugins/onion-sdd/scripts   # 本仓开发；业务仓以 Cursor 插件安装目录/scripts 为准

python3 "$SCRIPTS/onion_state.py" --repo-root . get
python3 "$SCRIPTS/onion_state.py" --repo-root . set --change-id <id> --tier <t> --phase <p> --last-action "<摘要>"
python3 "$SCRIPTS/onion_state.py" --repo-root . mark-tier0pp --change-id <id>
python3 "$SCRIPTS/finish_check.py" --repo-root . [--change-id <id>]
```

| 方向 | 优先级 |
|------|--------|
| **读** | Trellis `meta.onion` → `.onion-sdd/current.json` → OpenSpec 扫描 |
| **写** | 已绑定 Trellis task：**主写** `meta.onion` 并**镜像** `current.json`；否则**只写** `current.json` |

`current.json` 在有 Trellis 时是镜像与降级兜底，不是主状态源。OpenSpec 仍是变更正文唯一真相源。

```jsonc
{
  "version": 1,
  "active_change_id": "2025-06-25-fix-payment-button",
  "tier": "0+",
  "phase": "implement",
  "last_action": "tasks.md 第 3 项已勾选完成，定向验证通过",
  "last_action_at": "2025-06-25T15:30:00+08:00",
  "upgrade_risk": false,
  "tier0pp_deadline": null,
  "tier0pp_openspec_pending": false,
  "trellis_task": {
    "task_dir": ".trellis/tasks/06-25-fix-payment-button",
    "status": "in_progress"
  },
  "metrics": {
    "created_at": "2025-06-25T14:00:00+08:00",
    "triage_completed_at": "2025-06-25T14:05:00+08:00",
    "tasks_completed_at": null,
    "verified_at": null,
    "finished_at": null
  }
}
```

`/onsf-finish` 必须先跑 `finish_check.py`；失败不得 archive。归档成功后 `onion_state.py set --idle`。没有活跃变更时 `phase=idle`，`/onsf-continue` 不恢复上一轮已完成变更。

模板见 `templates/current.example.json`；协议见 `skills/trellis-adapter/SKILL.md`。

## 带债归档

"债"指归档时已知但未解决的风险或未完成项。可以带债归档的：
- tasks.md 中已声明"不做"的项
- Tier 0+/1 只做了单浏览器定向验证（需标注）
- 已知兼容性问题已创建 follow-up issue

不可带债归档：
- Tier 2+ 跳过的 E2E
- 涉及升级红线的未同步接口契约
- 涉及支付/资金/权限的未验证变更

带债归档要求在 `proposal.md` 增加 `## 带债项` 章节逐条列明，并为每条债创建 follow-up issue。`/onsf-finish` 输出中标注债项数。

## Rollback/Revert

| Revert 场景 | 处理方式 |
|-------------|----------|
| 未归档 change | tasks.md 追加 revert 任务 + 验证，正常 finish |
| 已归档 change | 创建新 change（change-id 含 "revert-<原id>"），按内容重新定 Tier |
| Tier 0++ 修复引发新问题 | 使用 Tier 0++ 紧急回退；触发流程审计 |

## 完整设计文档

补充设计细节见 [DESIGN-SUPPLEMENT.md](./DESIGN-SUPPLEMENT.md)。

## 验证建议

```bash
find plugins/onion-sdd -type f | sort
python3 -m json.tool plugins/onion-sdd/.cursor-plugin/plugin.json
python3 -m json.tool plugins/onion-sdd/templates/current.example.json
python3 plugins/onion-sdd/scripts/onion_state.py --help
python3 plugins/onion-sdd/scripts/finish_check.py --help
rg -n "onion_state|finish_check|tier0pp_|auto-flow|trellis-adapter" plugins/onion-sdd
```
